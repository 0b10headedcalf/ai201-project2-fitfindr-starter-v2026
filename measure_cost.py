"""
Measure what one FitFindr photo run costs, against a running server.

One run = the full photo flow a new user goes through:
    POST /wardrobe/scan     (a clothes photo)
    POST /profile/analyze   (a full-body photo of one person)
    POST /outfit            (an occasion + the wardrobe and profile just returned)

Calls are stateless (no X-User-Id), so nothing is stored. Token counts are the
ones the model service reports back (usage_metadata), read from the server's
structured log — not estimated from a pricing page. Start the server with the
cache OFF, or every run after the first costs zero tokens:

    AI201_CACHE=0 AI201_LOG_PATH=logs/cost.jsonl python -m gunicorn serve:app --workers 1 --timeout 120
    python measure_cost.py --log logs/cost.jsonl --clothes a.jpg b.jpg --person me.jpg

Against the deployed service (--base https://...onrender.com) there is no
local log file, so skip --log: you get wall-clock time per run, and the token
counts are in Render's log view, one JSON line per request.
"""

import argparse
import json
import mimetypes
import statistics
import time
import urllib.request
import uuid
from pathlib import Path

OCCASIONS = [
    "job interview at a design studio",
    "rainy day errands",
    "outdoor summer wedding",
    "first date at a wine bar",
    "weekend farmers market",
]


def _post_image(base: str, route: str, path: Path) -> tuple[int, dict]:
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
        f"filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        base + route, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    return _send(req)


def _post_json(base: str, route: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        base + route, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _send(req)


def _send(req) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def _log_lines(log: Path | None) -> int:
    return sum(1 for _ in log.open()) if log and log.exists() else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:5000")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--clothes", nargs="+", type=Path, required=True)
    ap.add_argument("--person", type=Path, required=True)
    ap.add_argument("--log", type=Path, help="the server's AI201_LOG_PATH, for token counts")
    args = ap.parse_args()

    rows = []
    for i in range(args.runs):
        start_line = _log_lines(args.log)
        started = time.perf_counter()

        s1, scan = _post_image(args.base, "/wardrobe/scan", args.clothes[i % len(args.clothes)])
        s2, profile = _post_image(args.base, "/profile/analyze", args.person)
        wardrobe = {"items": scan.get("items", [])}
        s3, outfit = _post_json(args.base, "/outfit", {
            "occasion": OCCASIONS[i % len(OCCASIONS)],
            "wardrobe": wardrobe,
            "profile": profile if s2 == 200 else None,
        })
        wall = time.perf_counter() - started

        row = {"run": i + 1, "status": [s1, s2, s3], "wall_s": round(wall, 2),
               "items": len(wardrobe["items"])}
        if args.log:
            records = [json.loads(l) for l in args.log.open().readlines()[start_line:]]
            row["model_calls"] = sum(r["model_calls"] for r in records)
            row["prompt_tokens"] = sum(r["prompt_tokens"] for r in records)
            row["output_tokens"] = sum(r["output_tokens"] for r in records)
            row["server_ms"] = sum(r["duration_ms"] for r in records)
        rows.append(row)
        print(json.dumps(row), flush=True)

    print("\n── average over", len(rows), "runs ──")
    for key in ("wall_s", "server_ms", "model_calls", "prompt_tokens", "output_tokens"):
        values = [r[key] for r in rows if key in r]
        if values:
            print(f"{key:>14}: mean {statistics.mean(values):,.1f}  "
                  f"min {min(values):,}  max {max(values):,}")


if __name__ == "__main__":
    main()
