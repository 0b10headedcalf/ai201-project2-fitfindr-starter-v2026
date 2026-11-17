#!/usr/bin/env python3
"""
Score the capstone against criteria.md — one run, every criterion, raw output kept.

    python criteria_eval.py --run 1 --label before                 # criteria 1-4, in-process
    python criteria_eval.py --run 1 --label before --only 5 \\
        --url https://fitfindr-vr9s.onrender.com                   # criterion 5, deployed

Milestone 5 wants three runs: --run 1, 2, 3 with nothing changed in between.

Criteria 1-4 run in-process through Flask's test client: the same serve.py
routes, no network. The per-IP abuse limiter is switched off for them
(AI201_IP_LIMIT_PER_MINUTE=0) because it limits visitors to the public site;
generate.py's model pacing (15/min) stays on, which is the limit criteria.md
means by "pace requests below configured rate limits". Criterion 5 is about
the deployed service, so it goes over HTTPS to --url and paces itself under
that service's per-IP limit; the pauses are excluded from the timing, as the
criterion says.

Writes, per run:
    results/capstone_<label>_run<N>.md      the scores, criterion by criterion
    results/capstone_<label>_run<N>.jsonl   every request and response, verbatim

This script measures. criteria.md decides what passes; every threshold below
is quoted from it.
"""

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
import uuid
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
PHOTOS = ROOT / "eval_photos"
RESULTS = ROOT / "results"
TRIALS = 5
CATEGORIES = ("tops", "bottoms", "outerwear", "shoes", "accessories")
UNDERTONES = ("warm", "cool", "neutral")
CONTRASTS = ("low", "medium", "high")
OCCASIONS = [
    "job interview at a design studio",
    "outdoor summer wedding",
    "rainy day errands",
    "first date at a jazz bar",
    "casual Friday at the office",
]
FLOW_OCCASION = "casual Friday at the office"

# Garment / shoe / accessory nouns. Criterion 3 fails a trial that recommends
# an item outside the **exact-name** spans; after removing those spans, any of
# these words left in the text flags the trial. The flagged sentences are
# written out so a person can overturn a false flag (criteria.md's self-check
# says outfit prose needs a human check as well as matching).
#
# Two rules make the flag mechanical, so two people get the same answer:
#   • A word that appears in the name of a wardrobe item the outfit already
#     named is a reference back to that item ("the sneakers keep it casual"),
#     not an additional recommendation, and is not flagged.
#   • Words with common non-garment senses are left out: top ("on top"), suit
#     ("suits the occasion"), tie ("ties the look together"), ring, watch,
#     cap, flats, tee.
GARMENT_WORDS = (
    "jacket coat blazer cardigan sweater jumper hoodie sweatshirt vest gilet "
    "shirt t-shirt tank blouse polo turtleneck dress skirt jeans trousers "
    "pants chinos shorts leggings joggers raincoat trench parka windbreaker "
    "shoes shoe sneakers trainers boots boot loafers heels sandals oxfords "
    "bag tote backpack purse clutch belt scarf hat beanie umbrella "
    "sunglasses necklace earrings bracelet jewelry jewellery socks"
).split()


# ── fixtures ──────────────────────────────────────────────────────────────────

def _png(w: int, h: int, rgb=(255, 255, 255)) -> bytes:
    """A valid solid-colour PNG — criterion 4's 'valid solid-white 64×64 PNG'."""
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    chunk = lambda t, d: (struct.pack(">I", len(d)) + t + d
                          + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


WHITE_PNG = _png(64, 64)
BAD_CASES = [  # (name, route, filename, bytes, expected status, must log model_calls 0)
    ("empty file", "/wardrobe/scan", "empty.jpg", b"", 400, True),
    ("text file", "/wardrobe/scan", "text-file.txt", b"definitely not an image", 400, True),
    ("9 MiB JPEG magic + zeros", "/wardrobe/scan", "too-big.jpg",
     b"\xff\xd8\xff" + b"\x00" * (9 * 1024 * 1024 - 3), 413, True),
    ("white PNG → scan", "/wardrobe/scan", "white.png", WHITE_PNG, 422, False),
    ("white PNG → profile", "/profile/analyze", "white.png", WHITE_PNG, 422, False),
]


def load_labels() -> tuple[dict | None, list[str]]:
    """labels.json, with every photo's SHA-256 checked. Problems → incomplete evidence."""
    path = PHOTOS / "labels.json"
    if not path.exists():
        return None, [f"{path} is missing — freeze the photos and labels first"]
    labels = json.loads(path.read_text())
    problems = []
    for group in ("wardrobe", "profile"):
        for entry in labels.get(group, []):
            photo = PHOTOS / entry["file"]
            if not photo.exists():
                problems.append(f"missing photo {entry['file']}")
            elif hashlib.sha256(photo.read_bytes()).hexdigest() != entry.get("sha256"):
                problems.append(f"{entry['file']} doesn't match its frozen SHA-256")
    if len(labels.get("wardrobe", [])) != 5:
        problems.append("criteria.md needs exactly five clothes photos")
    if len(labels.get("profile", [])) != 3:
        problems.append("criteria.md needs exactly three person photos")
    return labels, problems


def _mime(name: str) -> str:
    ext = name.lower().rsplit(".", 1)[-1]
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "webp": "image/webp", "heic": "image/heic"}.get(ext, "application/octet-stream")


# ── transport: in-process (criteria 1–4) or HTTPS (criterion 5) ──────────────

class InProcess:
    def __init__(self, log_path: Path, db_path: Path):
        os.environ["AI201_CACHE"] = "0"
        os.environ["AI201_IP_LIMIT_PER_MINUTE"] = "0"
        os.environ["AI201_LOG_PATH"] = str(log_path)
        os.environ["AI201_SQLITE_PATH"] = str(db_path)
        os.environ.pop("DATABASE_URL", None)
        sys.path.insert(0, str(ROOT))
        import serve  # noqa: E402 — env above must be set first
        self.client = serve.app.test_client()
        self.log_path = log_path

    def _log_mark(self) -> int:
        return sum(1 for _ in self.log_path.open()) if self.log_path.exists() else 0

    def _last_log(self, mark: int) -> dict | None:
        if not self.log_path.exists():
            return None
        lines = self.log_path.read_text().splitlines()[mark:]
        return json.loads(lines[-1]) if lines else None

    def upload(self, route, filename, data, user=None):
        import io
        headers = {"X-User-Id": user} if user else {}
        mark, started = self._log_mark(), time.perf_counter()
        r = self.client.post(route, headers=headers, content_type="multipart/form-data",
                             data={"image": (io.BytesIO(data), filename, _mime(filename))})
        return r.status_code, r.get_json(silent=True), time.perf_counter() - started, self._last_log(mark)

    def post_json(self, route, payload, user=None):
        headers = {"X-User-Id": user} if user else {}
        mark, started = self._log_mark(), time.perf_counter()
        r = self.client.post(route, json=payload, headers=headers)
        return r.status_code, r.get_json(silent=True), time.perf_counter() - started, self._last_log(mark)

    def get(self, route, user=None):
        headers = {"X-User-Id": user} if user else {}
        r = self.client.get(route, headers=headers)
        return r.status_code, r.get_json(silent=True)


class Remote:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def _send(self, req):
        """(status, json, seconds) — timed from just before sending until the whole body is read."""
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
                status = resp.status
        except urllib.error.HTTPError as exc:
            body, status = exc.read(), exc.code
        except Exception as exc:  # noqa: BLE001 — a timeout or reset is a failed request
            return None, {"error": f"{type(exc).__name__}: {exc}"}, time.perf_counter() - started
        elapsed = time.perf_counter() - started
        try:
            return status, json.loads(body or b"{}"), elapsed
        except ValueError:
            return status, {"raw": body[:300].decode("utf-8", "replace")}, elapsed

    def upload(self, route, filename, data):
        boundary = uuid.uuid4().hex
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {_mime(filename)}\r\n\r\n").encode() \
            + data + f"\r\n--{boundary}--\r\n".encode()
        return self._send(urllib.request.Request(
            self.base + route, data=body, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))

    def post_json(self, route, payload):
        return self._send(urllib.request.Request(
            self.base + route, data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json"}))

    def get(self, route):
        return self._send(urllib.request.Request(self.base + route))


# ── criterion 1 ──────────────────────────────────────────────────────────────

def score_scan(status, body, labeled: list[str]) -> dict:
    """One /wardrobe/scan trial against criterion 1."""
    out = {"status": status, "pass": False, "reasons": []}
    items = (body or {}).get("items")
    if status != 200:
        out["reasons"].append(f"status {status}")
    if not isinstance(items, list) or not items:
        out["reasons"].append("items missing or empty (zero predictions fail)")
        return out
    ids = [i.get("id") for i in items if isinstance(i, dict)]
    if len(ids) != len(items) or not all(isinstance(x, str) and x for x in ids) or len(set(ids)) != len(ids):
        out["reasons"].append("ids not unique nonempty strings")
    for i in items:
        if not (isinstance(i.get("name"), str) and i["name"].strip()):
            out["reasons"].append("empty name")
        if i.get("category") not in CATEGORIES:
            out["reasons"].append(f"bad category {i.get('category')!r}")
        for f in ("colors", "style_tags"):
            if not (isinstance(i.get(f), list) and all(isinstance(v, str) for v in i[f])):
                out["reasons"].append(f"{f} not a list of strings")
    predicted = Counter(i.get("category") for i in items)
    wanted = Counter(labeled)
    matches = sum(min(wanted[c], predicted[c]) for c in CATEGORIES)
    out["precision"] = round(matches / sum(predicted.values()), 3)
    out["recall"] = round(matches / sum(wanted.values()), 3)
    out["predicted"] = dict(predicted)
    if out["precision"] < 0.8:
        out["reasons"].append(f"precision {out['precision']:.0%} < 80%")
    if out["recall"] < 0.8:
        out["reasons"].append(f"recall {out['recall']:.0%} < 80%")
    out["reasons"] = sorted(set(out["reasons"]))
    out["pass"] = not out["reasons"]
    return out


def criterion_1(t: InProcess, labels, raw) -> dict:
    photos = []
    for entry in labels["wardrobe"]:
        data = (PHOTOS / entry["file"]).read_bytes()
        labeled = [i["category"] for i in entry["items"]]
        trials = []
        for n in range(TRIALS):
            status, body, secs, _ = t.upload("/wardrobe/scan", entry["file"], data)
            s = score_scan(status, body, labeled)
            trials.append(s)
            raw.append({"criterion": 1, "photo": entry["file"], "trial": n + 1, "status": status,
                        "seconds": round(secs, 2), "response": body, "score": s})
        passed = sum(s["pass"] for s in trials)
        photos.append({"file": entry["file"], "labeled": dict(Counter(labeled)),
                       "passed": passed, "ok": passed >= 4, "trials": trials})
    return {"photos": photos, "met": all(p["ok"] for p in photos),
            "cell": f"{sum(p['ok'] for p in photos)}/5 photos"}


# ── criterion 2 ──────────────────────────────────────────────────────────────

def criterion_2(t: InProcess, labels, raw) -> dict:
    photos = []
    for entry in labels["profile"]:
        data = (PHOTOS / entry["file"]).read_bytes()
        pairs, valid = [], 0
        for n in range(TRIALS):
            status, body, secs, _ = t.upload("/profile/analyze", entry["file"], data)
            body = body or {}
            ok = status == 200 and body.get("undertone") in UNDERTONES and body.get("contrast") in CONTRASTS
            valid += ok
            pairs.append((body.get("undertone"), body.get("contrast")) if ok else None)
            raw.append({"criterion": 2, "photo": entry["file"], "trial": n + 1, "status": status,
                        "seconds": round(secs, 2), "response": body})
        counts = Counter(p for p in pairs if p)
        top, top_n = counts.most_common(1)[0] if counts else (None, 0)
        photos.append({"file": entry["file"], "pairs": pairs, "valid": valid,
                       "modal": top, "modal_n": top_n, "ok": valid == TRIALS and top_n >= 4})
    return {"photos": photos, "met": all(p["ok"] for p in photos),
            "cell": f"{sum(p['ok'] for p in photos)}/3 photos"}


# ── criterion 3 ──────────────────────────────────────────────────────────────

def score_outfit(status, body, names: list[str]) -> dict:
    out = {"status": status, "pass": False, "reasons": [], "flags": []}
    body = body or {}
    text = body.get("outfit")
    if status != 200:
        out["reasons"].append(f"status {status}")
    if not isinstance(text, str) or not text.strip():
        out["reasons"].append("outfit empty")
        return out
    words = len(text.split())
    out["words"] = words
    if words > 170:
        out["reasons"].append(f"{words} words > 170")
    present = [n for n in names if n in text]          # exact, case-sensitive
    out["named"] = present
    if len(set(present)) < 2:
        out["reasons"].append(f"names {len(set(present))} wardrobe items (< 2)")
    used = body.get("items_used")
    if not isinstance(used, list) or len(used) != len(set(used)) or set(used) != set(present):
        out["reasons"].append("items_used ≠ set of names in the text")
    bold = re.findall(r"\*\*(.+?)\*\*", text, flags=re.S)
    stray_bold = [b for b in bold if b.strip() not in names]
    if stray_bold:
        out["reasons"].append(f"bold span(s) not an exact wardrobe name: {stray_bold}")
    unbolded = [n for n in set(present) if f"**{n}**" not in text]
    if unbolded:
        out["reasons"].append(f"wardrobe item(s) named without ** **: {unbolded}")
    # Additional item recommendations outside the spans (flagged for a human).
    stripped = re.sub(r"\*\*(.+?)\*\*", " ", text, flags=re.S)
    named_words = {w.rstrip("s") for n in present for w in re.findall(r"[a-z-]+", n.lower())}
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", stripped):
        hits = [w for w in GARMENT_WORDS
                if w.rstrip("s") not in named_words
                and re.search(rf"\b{re.escape(w)}s?\b", sentence, re.I)]
        if hits:
            out["flags"].append({"sentence": sentence.strip(), "words": hits})
    if out["flags"]:
        out["reasons"].append("recommends an item outside the ** ** spans")
    out["pass"] = not out["reasons"]
    return out


def criterion_3(t: InProcess, raw) -> dict:
    schema = json.loads((ROOT / "data" / "wardrobe_schema.json").read_text())
    wardrobe = schema["example_wardrobe"]
    profile = json.loads((PHOTOS / "labels.example.json").read_text())["outfit_profile"]
    names = [i["name"] for i in wardrobe["items"]]
    occasions = []
    for occ in OCCASIONS:
        trials = []
        for n in range(TRIALS):
            status, body, secs, _ = t.post_json("/outfit", {"occasion": occ, "wardrobe": wardrobe,
                                                            "profile": profile})
            s = score_outfit(status, body, names)
            trials.append(s)
            raw.append({"criterion": 3, "occasion": occ, "trial": n + 1, "status": status,
                        "seconds": round(secs, 2), "response": body, "score": s})
        passed = sum(s["pass"] for s in trials)
        occasions.append({"occasion": occ, "passed": passed, "ok": passed >= 4, "trials": trials})
    return {"occasions": occasions, "met": all(o["ok"] for o in occasions),
            "cell": f"{sum(o['ok'] for o in occasions)}/5 occasions"}


# ── criterion 4 ──────────────────────────────────────────────────────────────

def criterion_4(t: InProcess, raw) -> dict:
    cases = []
    for name, route, filename, data, expected, zero_calls in BAD_CASES:
        trials = []
        for n in range(TRIALS):
            user = str(uuid.uuid4())
            status, body, secs, log = t.upload(route, filename, data, user=user)
            me_status, me = t.get("/me", user=user)
            me = me or {}
            reasons = []
            if status != expected:
                reasons.append(f"status {status}, expected {expected}")
            if not (isinstance(body, dict) and isinstance(body.get("error"), str) and body["error"].strip()):
                reasons.append("no nonempty string error")
            if me_status != 200:
                reasons.append(f"/me status {me_status}")
            if me.get("photos") != [] or (me.get("wardrobe") or {}).get("items") != [] or me.get("profile", "x") is not None:
                reasons.append("something was stored")
            calls = (log or {}).get("model_calls")
            if zero_calls and calls != 0:
                reasons.append(f"log model_calls {calls}, expected 0")
            trials.append({"pass": not reasons, "reasons": reasons, "status": status, "model_calls": calls})
            raw.append({"criterion": 4, "case": name, "trial": n + 1, "status": status,
                        "seconds": round(secs, 2), "response": body, "log": log,
                        "me": {"status": me_status, "photos": me.get("photos"),
                               "items": (me.get("wardrobe") or {}).get("items"),
                               "profile": me.get("profile")}})
        passed = sum(x["pass"] for x in trials)
        cases.append({"case": name, "expected": expected, "passed": passed,
                      "ok": passed == TRIALS, "trials": trials})
    return {"cases": cases, "met": all(c["ok"] for c in cases),
            "cell": f"{sum(c['ok'] for c in cases)}/5 cases"}


# ── criterion 5 ──────────────────────────────────────────────────────────────

def criterion_5(r: Remote, labels, raw, pause: float) -> dict:
    clothes = labels["wardrobe"][0]["file"]
    person = labels["profile"][0]["file"]
    clothes_b, person_b = (PHOTOS / clothes).read_bytes(), (PHOTOS / person).read_bytes()
    flows = []
    for n in range(TRIALS):
        if n:
            time.sleep(pause)  # deliberate pause for the per-IP limit — excluded from timing
        h_status, _, h_secs = r.get("/health")
        healthy_at = time.monotonic()
        steps = []
        s1, scan, t1 = r.upload("/wardrobe/scan", clothes, clothes_b)
        steps.append(("/wardrobe/scan", s1, t1))
        s2, prof, t2 = r.upload("/profile/analyze", person, person_b)
        steps.append(("/profile/analyze", s2, t2))
        s3, outfit, t3 = r.post_json("/outfit", {
            "occasion": FLOW_OCCASION,
            "wardrobe": {"items": (scan or {}).get("items", [])},
            "profile": prof if s2 == 200 else None,
        })
        steps.append(("/outfit", s3, t3))
        total = t1 + t2 + t3
        started_in_time = h_status == 200 and (time.monotonic() - healthy_at - total) < 60
        ok = started_in_time and all(s == 200 for _, s, _ in steps) and total <= 30
        flows.append({"flow": n + 1, "health": h_status, "steps": steps,
                      "total": round(total, 2), "ok": ok})
        raw.append({"criterion": 5, "flow": n + 1, "health": [h_status, round(h_secs, 2)],
                    "steps": [{"route": a, "status": b, "seconds": round(c, 2)} for a, b, c in steps],
                    "total_seconds": round(total, 2), "pass": ok,
                    "errors": [x.get("error") for x in (scan, prof, outfit) if isinstance(x, dict) and x.get("error")]})
    passed = sum(f["ok"] for f in flows)
    return {"flows": flows, "met": passed >= 4, "cell": f"{passed}/5 flows"}


# ── report ────────────────────────────────────────────────────────────────────

def report(results: dict, meta: dict) -> str:
    lines = [f"# Capstone criteria — {meta['label']}, run {meta['run']}", "",
             f"- Started: {meta['started']}  ·  Finished: {meta['finished']}",
             f"- Model: `{meta['model']}`  ·  temperature as set in tools.py  ·  cache off",
             f"- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `{meta.get('url') or 'not run'}`",
             f"- Raw responses: `{meta['raw']}`", "",
             "| Criterion | Target | Result | Verdict |", "|---|---|---|---|"]
    targets = {1: "every photo ≥ 4/5", 2: "every photo 5/5 valid, ≥ 4/5 same pair",
               3: "every occasion ≥ 4/5", 4: "every case 5/5", 5: "≥ 4/5 flows ≤ 30 s"}
    for k in sorted(results):
        res = results[k]
        lines.append(f"| {k} | {targets[k]} | {res['cell']} | {'MET' if res['met'] else 'MISSED'} |")
    if 1 in results:
        lines += ["", "## 1. Clothes photos → wardrobe entries", "",
                  "| Photo | Labeled | Trials passing | P / R per trial | Why trials failed |", "|---|---|---|---|---|"]
        for p in results[1]["photos"]:
            pr = ", ".join(f"{t.get('precision', 0):.0%}/{t.get('recall', 0):.0%}" for t in p["trials"])
            why = "; ".join(sorted({r for t in p["trials"] for r in t["reasons"]})) or "—"
            lines.append(f"| {p['file']} | {p['labeled']} | {p['passed']}/5 | {pr} | {why} |")
    if 2 in results:
        lines += ["", "## 2. Person photo → stable profile", "",
                  "| Photo | Valid | (undertone, contrast) per trial | Most common | Count |", "|---|---|---|---|---|"]
        for p in results[2]["photos"]:
            pairs = ", ".join("/".join(x) if x else "invalid" for x in p["pairs"])
            lines.append(f"| {p['file']} | {p['valid']}/5 | {pairs} | {'/'.join(p['modal'] or ('—',))} | {p['modal_n']}/5 |")
    if 3 in results:
        lines += ["", "## 3. Occasion outfits", "",
                  "| Occasion | Trials passing | Words per trial | Why trials failed |", "|---|---|---|---|"]
        for o in results[3]["occasions"]:
            words = ", ".join(str(t.get("words", "—")) for t in o["trials"])
            why = Counter(r for t in o["trials"] for r in t["reasons"])
            lines.append(f"| {o['occasion']} | {o['passed']}/5 | {words} | "
                         f"{'; '.join(f'{r} ×{n}' for r, n in why.items()) or '—'} |")
        lines += ["", "Flagged sentences (garment words outside `**` spans), for the human check:", ""]
        for o in results[3]["occasions"]:
            for i, t in enumerate(o["trials"], 1):
                for f in t.get("flags", []):
                    lines.append(f"- *{o['occasion']}*, trial {i}: “{f['sentence']}” — {', '.join(f['words'])}")
    if 4 in results:
        lines += ["", "## 4. Invalid uploads", "",
                  "| Case | Expected | Trials passing | Statuses | model_calls | Problems |", "|---|---|---|---|---|---|"]
        for c in results[4]["cases"]:
            lines.append(f"| {c['case']} | {c['expected']} | {c['passed']}/5 | "
                         f"{', '.join(str(t['status']) for t in c['trials'])} | "
                         f"{', '.join(str(t['model_calls']) for t in c['trials'])} | "
                         f"{'; '.join(sorted({r for t in c['trials'] for r in t['reasons']})) or '—'} |")
    if 5 in results:
        lines += ["", "## 5. Warm deployed photo flow", "",
                  "| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |", "|---|---|---|---|---|---|---|"]
        for f in results[5]["flows"]:
            cells = " | ".join(f"{s} in {t:.2f}s" for _, s, t in f["steps"])
            lines.append(f"| {f['flow']} | {f['health']} | {cells} | {f['total']:.2f}s | {'yes' if f['ok'] else 'no'} |")
    return "\n".join(lines) + "\n"


def freeze() -> None:
    """Write each photo's SHA-256 into labels.json. Run once, before any model call."""
    path = PHOTOS / "labels.json"
    labels = json.loads(path.read_text())
    for group in ("wardrobe", "profile"):
        for entry in labels.get(group, []):
            entry["sha256"] = hashlib.sha256((PHOTOS / entry["file"]).read_bytes()).hexdigest()
            print(f"{entry['file']}: {entry['sha256'][:16]}…")
    labels["frozen_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(labels, indent=2, ensure_ascii=False) + "\n")
    print(f"froze {path} — commit it before the first run")


def main() -> None:
    if "--freeze" in sys.argv:
        return freeze()
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=int, required=True)
    ap.add_argument("--label", default="before")
    ap.add_argument("--only", default="1,2,3,4", help="criteria to run, e.g. 1,2 or 5")
    ap.add_argument("--url", help="deployed base URL, for criterion 5")
    ap.add_argument("--pause", type=float, default=40.0,
                    help="seconds between criterion-5 flows, to stay under the 6/min per-IP limit")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",")}

    labels, problems = load_labels()
    if problems:
        sys.exit("Incomplete evidence, not running:\n  " + "\n  ".join(problems))

    RESULTS.mkdir(exist_ok=True)
    suffix = "" if only == {1, 2, 3, 4} else "_c" + "".join(map(str, sorted(only)))
    stem = f"capstone_{args.label}_run{args.run}{suffix}"
    raw: list = []
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results = {}

    local = only & {1, 2, 3, 4}
    if local:
        logs = ROOT / "logs"
        logs.mkdir(exist_ok=True)
        t = InProcess(logs / f"{stem}.log.jsonl", logs / f"{stem}.db")
        for k, fn in ((1, lambda: criterion_1(t, labels, raw)), (2, lambda: criterion_2(t, labels, raw)),
                      (3, lambda: criterion_3(t, raw)), (4, lambda: criterion_4(t, raw))):
            if k in only:
                print(f"criterion {k}…", flush=True)
                results[k] = fn()
                print(f"  {results[k]['cell']} → {'MET' if results[k]['met'] else 'MISSED'}", flush=True)
    if 5 in only:
        if not args.url:
            sys.exit("criterion 5 needs --url (the deployed service)")
        print("criterion 5…", flush=True)
        results[5] = criterion_5(Remote(args.url), labels, raw, args.pause)
        print(f"  {results[5]['cell']} → {'MET' if results[5]['met'] else 'MISSED'}", flush=True)

    import config
    meta = {"label": args.label, "run": args.run, "started": started,
            "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model": config.MODEL, "url": args.url, "raw": f"results/{stem}.jsonl"}
    (RESULTS / f"{stem}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in raw))
    (RESULTS / f"{stem}.md").write_text(report(results, meta))
    print(f"wrote results/{stem}.md and .jsonl")


if __name__ == "__main__":
    main()
