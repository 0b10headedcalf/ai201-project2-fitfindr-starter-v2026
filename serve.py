#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Two routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

⚠️ There is deliberately NO logging, NO timing and NO request counting in this
file. That is unit 9's follow-along: you instrument this yourself, first, and
then deploy it. A structured log you were handed teaches you nothing about
what belongs in one — and the timing field is the one everybody skips.
"""

import os
import sys
import threading

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

import functools
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

import db
import generate
from agent import run_agent
from generate import InvalidInput, ModelUnavailable
from tools import analyze_profile, outfit_for_occasion, scan_wardrobe
from utils.data_loader import get_example_wardrobe

STATIC_DIR = Path(__file__).parent / "static"
LOG_PATH = Path(os.getenv("AI201_LOG_PATH", Path(__file__).parent / "logs" / "runs.jsonl"))
MAX_UPLOAD_MB = 8

app = Flask(__name__)
# Anything bigger is refused before it's read: werkzeug raises 413, which the
# logged() wrapper below turns into JSON and a log line.
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


# ── structured log (capstone) ────────────────────────────────────────────────
# One JSON object per request, every request, including the ones that fail.
# Written to stdout (what Render's log view shows) and appended to LOG_PATH
# (what survives locally). Images are never logged — only their type and size.

def _write_log(record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False, default=str)
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass  # a full or read-only disk must not turn a good answer into a 500


def logged(route: str):
    """Time the request, diff the token counters, and log the outcome."""
    def decorator(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            g.log_input, g.log_output, g.log_error = {}, {}, None
            g.user_id = db.valid_user_id(request.headers.get("X-User-Id"))
            started = time.perf_counter()
            calls_before = generate.call_count()
            tokens_before = generate.token_counts()
            try:
                response = app.make_response(view(*args, **kwargs))
            except HTTPException as exc:
                g.log_error = f"{exc.code} {exc.name}"
                if exc.code == 413:
                    _drain_upload()
                response = jsonify({"error": exc.description})
                response.status_code = exc.code
            except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
                g.log_error = f"{type(exc).__name__}: {exc}"
                if type(exc).__name__ == "OperationalError":
                    # sqlite3 and psycopg both name "can't reach / can't open
                    # the database" this way. The caller can retry; say so.
                    response = jsonify({"error": "Storage is unavailable right now. "
                                                 "Try again in a moment."})
                    response.status_code = 503
                else:
                    response = jsonify({"error": g.log_error})
                    response.status_code = 500
            tokens_after = generate.token_counts()
            _write_log({
                "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "route": route,
                # First 8 characters only: the full ID is the user's only key.
                "user": g.user_id[:8] if g.user_id else None,
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000),
                "input": g.log_input,
                "output": g.log_output,
                "model_calls": generate.call_count() - calls_before,
                "prompt_tokens": tokens_after["prompt"] - tokens_before["prompt"],
                "output_tokens": tokens_after["output"] - tokens_before["output"],
                "model": config.MODEL,
                "error": g.log_error,
            })
            return response
        return wrapper
    return decorator


def _drain_upload(limit: int = 64 * 1024 * 1024) -> None:
    """
    Read and discard a refused upload before answering it.

    Werkzeug raises 413 without reading the body. If the server replies and
    closes while the client is still sending, many clients (Python's urllib,
    and browsers on a slow link) report a broken pipe / network error instead
    of the 413 and its message. Draining costs bandwidth, capped at `limit`.
    """
    stream = request.environ.get("wsgi.input")
    if stream is None:
        return
    remaining = limit
    try:
        while remaining > 0:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
    except Exception:  # noqa: BLE001 — a client that hung up early is fine
        pass


def _fail(status: int, message: str):
    g.log_error = message
    return jsonify({"error": message}), status


# ── image upload checks ──────────────────────────────────────────────────────
# The type comes from the file's first bytes, not from the filename or the
# browser's Content-Type — both of which are whatever the client says.

def _sniff_mime(data: bytes) -> str | None:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[4:8] == b"ftyp" and data[8:12] in (b"heic", b"heix", b"mif1", b"msf1"):
        return "image/heic"
    return None


def _read_image():
    """(bytes, mime) from the multipart 'image' field, or (None, error message)."""
    upload = request.files.get("image")
    if upload is None:
        return None, "Send the photo as multipart form data in a field called 'image'."
    data = upload.read()
    g.log_input = {"bytes": len(data), "filename": upload.filename}
    if not data:
        return None, "The uploaded image was empty."
    mime = _sniff_mime(data)
    g.log_input["mime"] = mime
    if mime is None:
        return None, "That file isn't a JPEG, PNG, WebP or HEIC image."
    return (data, mime), None


def _read_thumb() -> bytes | None:
    """The optional 'thumb' field the page sends (a small WebP/JPEG), or None."""
    upload = request.files.get("thumb")
    if upload is None:
        return None
    data = upload.read()
    if not data or len(data) > 512 * 1024 or _sniff_mime(data) not in ("image/webp", "image/jpeg"):
        return None  # a bad thumbnail isn't worth failing the upload over
    g.log_input["thumb_bytes"] = len(data)
    return data


def _require_user():
    """The caller's user ID, or a ready-made 400 response."""
    if g.user_id is None:
        return None, _fail(400, "Send your browser ID in the X-User-Id header (a UUID).")
    return g.user_id, None


def _quota_full() -> str | None:
    """A message if this user can't store another photo — checked BEFORE the model call."""
    used = db.storage_used(g.user_id)
    if used["photos"] >= used["max_photos"]:
        return (f"You've stored {used['photos']} photos, the limit is {used['max_photos']}. "
                "Delete some to add more.")
    return None


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make

_one_at_a_time = threading.Lock()


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.post("/ask")
@logged("/ask")
def ask():
    """
    Run the agent on one query.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.
    """
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    g.log_input = {"query": query}
    if not query:
        # 400 rather than a stack trace: the caller can act on this one.
        return _fail(400, "Send JSON with a 'query' field, e.g. "
                          '{"query": "vintage graphic tee under $30"}')

    wardrobe = payload.get("wardrobe")
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    # A queued request should look like a queued request. Without this the
    # second caller just sits there, and "slow" and "waiting its turn" are
    # indistinguishable from the outside — which is how people conclude the
    # deployment is broken when it is behaving exactly as designed.
    #
    # This is NOT the logging you add in the follow-along. It prints nothing
    # on the normal path, carries no timing and counts nothing; it says only
    # that this request had to wait. `locked()` can be a moment out of date,
    # so the note is occasionally missed — which costs nothing, because
    # nothing depends on it.
    if _one_at_a_time.locked():
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    failure = None
    session = None
    with _one_at_a_time:
        try:
            session = run_agent(query, wardrobe)
        except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
            failure = f"{type(exc).__name__}: {exc}"

    # Outside the lock: building a response is not work the next caller should
    # be waiting on.
    if failure is not None:
        return _fail(500, failure)

    item = session.get("selected_item") or {}
    g.log_output = {
        "results": len(session.get("search_results") or []),
        "selected": item.get("title"),
        "fit_card": (session.get("fit_card") or "")[:120],
    }
    g.log_error = session.get("error")
    return jsonify(session)


# ── capstone routes: photo input ─────────────────────────────────────────────

def _run_model(fn, *args):
    """Run a model-calling tool under the lock; map its failures to statuses."""
    with _one_at_a_time:
        try:
            return fn(*args), None
        except InvalidInput as exc:
            return None, (400, str(exc))
        except ModelUnavailable as exc:
            return None, (503, str(exc))


@app.post("/wardrobe/scan")
@logged("/wardrobe/scan")
def wardrobe_scan():
    """
    In: multipart 'image' (+ optional 'thumb'). Out: {"items": [...]} in the
    wardrobe schema. With an X-User-Id header, the photo and its items are
    stored for that user and the response carries their ids and "photo_id".
    Without one it's stateless — which is how capstone_eval.py calls it.
    """
    image, problem = _read_image()
    if problem:
        return _fail(400, problem)
    thumb = _read_thumb()
    if g.user_id and (full := _quota_full()):
        return _fail(409, full)

    result, failure = _run_model(scan_wardrobe, *image)
    if failure:
        return _fail(*failure)

    g.log_output = {
        "items": len(result["items"]),
        "categories": [item["category"] for item in result["items"]],
        "names": [item["name"] for item in result["items"]],
        "dropped": result.get("dropped", 0),
    }
    if not result["items"]:
        # Nothing worth keeping: the photo is NOT stored.
        return _fail(422, result.get("reason", "No clothing found in the photo."))

    if g.user_id:
        try:
            photo_id = db.save_photo(g.user_id, "wardrobe", image[0], image[1], thumb)
        except db.QuotaExceeded as exc:
            return _fail(409, str(exc))
        result["items"] = db.add_items(g.user_id, result["items"], photo_id)
        result["photo_id"] = photo_id
        g.log_output["stored"] = True
    return jsonify(result)


@app.post("/profile/analyze")
@logged("/profile/analyze")
def profile_analyze():
    """In: multipart 'image' (one person, full body). Out: a color profile."""
    image, problem = _read_image()
    if problem:
        return _fail(400, problem)
    thumb = _read_thumb()
    if g.user_id and (full := _quota_full()):
        return _fail(409, full)

    result, failure = _run_model(analyze_profile, *image)
    if failure:
        return _fail(*failure)

    if "error" in result:
        return _fail(422, result["error"])
    g.log_output = {k: result[k] for k in ("undertone", "contrast", "hair_color")}

    if g.user_id:
        # One profile per user: the new photo replaces (and deletes) the old one.
        try:
            photo_id = db.save_photo(g.user_id, "profile", image[0], image[1], thumb)
        except db.QuotaExceeded as exc:
            return _fail(409, str(exc))
        db.save_profile(g.user_id, result, photo_id)
        result["photo_id"] = photo_id
        g.log_output["stored"] = True
    return jsonify(result)


@app.post("/outfit")
@logged("/outfit")
def outfit():
    """In: {"occasion": "...", "wardrobe": {...}?, "profile": {...}?}. Out: {"outfit": "..."}."""
    payload = request.get_json(silent=True) or {}
    occasion = str(payload.get("occasion") or "").strip()
    wardrobe = payload.get("wardrobe")
    profile = payload.get("profile") if isinstance(payload.get("profile"), dict) else None
    # A browser ID with no wardrobe in the body means "use what I've stored".
    if g.user_id and not isinstance(wardrobe, dict):
        wardrobe = db.get_wardrobe(g.user_id)
        profile = profile or db.get_profile(g.user_id)
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()

    g.log_input = {
        "occasion": occasion,
        "wardrobe_items": len(wardrobe.get("items", [])),
        "has_profile": profile is not None,
    }
    if not occasion:
        return _fail(400, "Send JSON with an 'occasion' field, e.g. "
                          '{"occasion": "outdoor summer wedding"}')

    text, failure = _run_model(outfit_for_occasion, wardrobe, profile, occasion)
    if failure:
        return _fail(*failure)

    owned = [item["name"] for item in wardrobe.get("items", []) if item["name"] in text]
    g.log_output = {"outfit": text[:120], "owned_items_named": len(owned)}
    return jsonify({"outfit": text, "items_used": owned})


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/example-wardrobe")
def example_wardrobe():
    return jsonify(get_example_wardrobe())


# ── per-user storage routes ──────────────────────────────────────────────────
# Every one of these needs X-User-Id and only ever touches that user's rows.

@app.get("/me")
@logged("/me")
def me():
    """Everything the page needs on load: wardrobe, profile, photos, usage."""
    user_id, err = _require_user()
    if err:
        return err
    data = {
        "wardrobe": db.get_wardrobe(user_id),
        "profile": db.get_profile(user_id),
        "photos": db.list_photos(user_id, "wardrobe"),
        "storage": db.storage_used(user_id),
    }
    g.log_output = {"items": len(data["wardrobe"]["items"]), "photos": len(data["photos"]),
                    "has_profile": data["profile"] is not None, "db": db.backend()}
    return jsonify(data)


@app.delete("/me")
@logged("DELETE /me")
def forget_me():
    user_id, err = _require_user()
    if err:
        return err
    db.delete_user(user_id)
    return jsonify({"deleted": True})


@app.get("/photos/<photo_id>")
@logged("/photos")
def photo(photo_id):
    """The image bytes. ?thumb=1 for the small version. Own photos only."""
    user_id, err = _require_user()
    if err:
        return err
    found = db.get_photo(user_id, photo_id, thumb=request.args.get("thumb") == "1")
    if found is None:
        return _fail(404, "No such photo.")
    data, mime = found
    g.log_output = {"bytes": len(data)}
    response = app.response_class(data, mimetype=mime)
    response.headers["Cache-Control"] = "private, max-age=86400"
    return response


@app.delete("/photos/<photo_id>")
@logged("DELETE /photos")
def delete_photo(photo_id):
    """Delete a photo and every item scanned from it."""
    user_id, err = _require_user()
    if err:
        return err
    if not db.delete_photo(user_id, photo_id):
        return _fail(404, "No such photo.")
    return jsonify({"deleted": True, "wardrobe": db.get_wardrobe(user_id)})


@app.delete("/wardrobe/items/<item_id>")
@logged("DELETE /wardrobe/items")
def delete_item(item_id):
    user_id, err = _require_user()
    if err:
        return err
    if not db.delete_item(user_id, item_id):
        return _fail(404, "No such item.")
    return jsonify({"deleted": True})


@app.delete("/wardrobe")
@logged("DELETE /wardrobe")
def clear_wardrobe():
    user_id, err = _require_user()
    if err:
        return err
    db.clear_wardrobe(user_id)
    return jsonify({"wardrobe": {"items": []}})


@app.post("/wardrobe/example")
@logged("/wardrobe/example")
def load_example():
    """Copy the example wardrobe into this user's stored wardrobe."""
    user_id, err = _require_user()
    if err:
        return err
    db.add_items(user_id, get_example_wardrobe()["items"])
    return jsonify({"wardrobe": db.get_wardrobe(user_id)})


@app.put("/profile")
@logged("PUT /profile")
def edit_profile():
    """Save the user's edits (e.g. a corrected undertone), keeping the photo."""
    user_id, err = _require_user()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    current = db.get_profile(user_id)
    if current is None:
        return _fail(404, "No profile yet. Upload a photo first.")
    from tools import CONTRASTS, UNDERTONES
    if body.get("undertone") not in (None, *UNDERTONES) or body.get("contrast") not in (None, *CONTRASTS):
        return _fail(400, "undertone must be warm/cool/neutral; contrast low/medium/high.")
    current.pop("photo_id", None)
    current.update({k: body[k] for k in ("undertone", "contrast") if body.get(k)})
    db.save_profile(user_id, current, keep_photo=True)
    return jsonify(db.get_profile(user_id))


@app.delete("/profile")
@logged("DELETE /profile")
def delete_profile():
    user_id, err = _require_user()
    if err:
        return err
    db.delete_profile(user_id)
    return jsonify({"deleted": True})


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5000"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
