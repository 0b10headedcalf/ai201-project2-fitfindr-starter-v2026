#!/usr/bin/env python3
"""
Capstone eval: run the photo-input routes N times and record what happened.

    AI201_CACHE=0 python capstone_eval.py --label before
    python capstone_eval.py --label after --url https://<you>.onrender.com
    python capstone_eval.py --label before --trials 3 --only bad,outfit

In-process by default (Flask test client — same code, no network). With --url
it hits a running server instead, which is what a latency criterion about the
deployed app needs; the deployed app needs AI201_CACHE=0 set too, or repeats
will come back from its cache.

Reads eval_photos/labels.json (you write it — see eval_photos/README.md).
Writes results/capstone_<ts>_<label>.md (tables) and _raw.jsonl (every
request). This script MEASURES; criteria.md decides what counts as passing.
"""

import argparse
import io
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
from datetime import datetime
from pathlib import Path

os.environ.setdefault("AI201_CACHE", "0")  # five tries must be five real answers

ROOT = Path(__file__).parent
PHOTOS = Path(os.getenv("AI201_PHOTOS_DIR", ROOT / "eval_photos"))
RESULTS = Path(os.getenv("AI201_RESULTS_DIR", ROOT / "results"))


# ── synthetic bad inputs: need no photos ─────────────────────────────────────

def _png(w: int, h: int, rgb=(240, 240, 240)) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    chunk = lambda t, d: (struct.pack(">I", len(d)) + t + d
                          + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


SYNTHETIC_BAD = [
    ("/wardrobe/scan", "text-file.txt", b"definitely not an image"),
    ("/wardrobe/scan", "empty.jpg", b""),
    ("/wardrobe/scan", "too-big.jpg", b"\xff\xd8\xff" + b"0" * (9 * 1024 * 1024)),
    ("/wardrobe/scan", "blank.png", _png(64, 64)),
    ("/wardrobe/scan", "corrupt.jpg", b"\xff\xd8\xff\xe0" + os.urandom(2048)),
    ("/profile/analyze", "blank.png", _png(64, 64)),
]


# ── transport: test client or real URL ───────────────────────────────────────

class Client:
    def __init__(self, url: str | None):
        self.url = url.rstrip("/") if url else None
        if not self.url:
            from serve import app
            self.app = app.test_client()

    def post_image(self, route: str, filename: str, data: bytes):
        if not self.url:
            r = self.app.post(route, data={"image": (io.BytesIO(data), filename)})
            return r.status_code, r.get_json(silent=True) or {}
        boundary = uuid.uuid4().hex
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
                f"filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n"
                ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
        return self._send(route, body, f"multipart/form-data; boundary={boundary}")

    def post_json(self, route: str, payload: dict):
        if not self.url:
            r = self.app.post(route, json=payload)
            return r.status_code, r.get_json(silent=True) or {}
        return self._send(route, json.dumps(payload).encode(), "application/json")

    def _send(self, route, body, ctype):
        req = urllib.request.Request(self.url + route, data=body, method="POST",
                                     headers={"Content-Type": ctype})
        try:
            with urllib.request.urlopen(req, timeout=180) as res:
                return res.status, json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, json.loads(exc.read() or b"{}")
            except ValueError:
                return exc.code, {}


# ── scoring helpers ──────────────────────────────────────────────────────────

def category_match(labeled: list[str], predicted: list[str]) -> tuple[int, int]:
    """How many labeled items got a predicted item of the same category (multiset)."""
    want, got = Counter(labeled), Counter(predicted)
    return sum(min(n, got[c]) for c, n in want.items()), len(labeled)


def invented_names(outfit: str, wardrobe: dict) -> list[str]:
    """Bolded names in the outfit that aren't in the wardrobe."""
    owned = {i["name"].lower() for i in wardrobe.get("items", [])}
    bolded = [m.strip() for m in re.findall(r"\*\*(.+?)\*\*", outfit)]
    return [b for b in bolded if b.lower() not in owned
            and not any(b.lower() in o or o in b.lower() for o in owned)]


# ── one trial ────────────────────────────────────────────────────────────────

def run_trial(client: Client, labels: dict, only: set[str], raw: list) -> dict:
    out = {}

    def timed(kind, fn, **meta):
        t = time.perf_counter()
        status, body = fn()
        ms = round((time.perf_counter() - t) * 1000)
        raw.append({"kind": kind, "status": status, "ms": ms, **meta, "body": body})
        return status, body, ms

    latencies = []

    if "wardrobe" in only:
        matched = total = schema_ok = scans = 0
        for photo in labels.get("wardrobe", []):
            data = (PHOTOS / photo["file"]).read_bytes()
            status, body, ms = timed("wardrobe", lambda: client.post_image(
                "/wardrobe/scan", photo["file"], data), file=photo["file"])
            latencies.append(ms)
            scans += 1
            items = body.get("items", []) if status == 200 else []
            m, n = category_match([i["category"] for i in photo["items"]],
                                  [i["category"] for i in items])
            matched, total = matched + m, total + n
            schema_ok += status == 200 and all(
                i.get("name") and i.get("category") and isinstance(i.get("colors"), list)
                for i in items)
        out["wardrobe_category_match"] = f"{matched}/{total}"
        out["wardrobe_schema_valid"] = f"{schema_ok}/{scans}"

    if "profile" in only:
        undertones = {}
        for photo in labels.get("profile", []):
            data = (PHOTOS / photo["file"]).read_bytes()
            status, body, ms = timed("profile", lambda: client.post_image(
                "/profile/analyze", photo["file"], data), file=photo["file"])
            latencies.append(ms)
            undertones[photo["file"]] = body.get("undertone") if status == 200 else f"HTTP {status}"
        out["profile_undertones"] = undertones

    if "bad" in only:
        cases = list(SYNTHETIC_BAD) + [
            (b.get("route", "/wardrobe/scan"), b["file"], (PHOTOS / b["file"]).read_bytes())
            for b in labels.get("bad", [])
        ]
        handled = 0
        statuses = []
        for route, name, data in cases:
            status, body, _ = timed("bad", lambda: client.post_image(route, name, data),
                                    route=route, file=name)
            ok = 400 <= status < 500 and bool(body.get("error"))
            handled += ok
            statuses.append(f"{name}→{status}")
        out["bad_input_4xx_with_message"] = f"{handled}/{len(cases)}"
        out["bad_statuses"] = statuses

    if "outfit" in only:
        from utils.data_loader import get_example_wardrobe
        wardrobe = get_example_wardrobe()
        profile = labels.get("outfit_profile")
        clean = 0
        occasions = labels.get("occasions", [])
        for occ in occasions:
            status, body, ms = timed("outfit", lambda: client.post_json(
                "/outfit", {"occasion": occ, "wardrobe": wardrobe, "profile": profile}),
                occasion=occ)
            latencies.append(ms)
            text = body.get("outfit", "")
            invented = invented_names(text, wardrobe)
            raw[-1]["invented"] = invented
            clean += status == 200 and len(body.get("items_used", [])) >= 2 and not invented
        out["outfit_owned_only"] = f"{clean}/{len(occasions)}"

    if latencies:
        s = sorted(latencies)
        out["latency_ms_p50"] = s[len(s) // 2]
        out["latency_ms_max"] = s[-1]
        out["under_10s"] = f"{sum(ms < 10_000 for ms in s)}/{len(s)}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="before / after / anything")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--url", help="hit a running server instead of in-process")
    ap.add_argument("--only", default="wardrobe,profile,bad,outfit")
    args = ap.parse_args()

    labels_path = PHOTOS / "labels.json"
    labels = json.loads(labels_path.read_text()) if labels_path.exists() else {}
    if not labels:
        print(f"  no {labels_path} — running synthetic bad inputs only",
              file=sys.stderr)
    only = set(args.only.split(","))

    import generate
    client = Client(args.url)
    raw, trials = [], []
    tokens0, calls0 = generate.token_counts(), generate.call_count()
    for n in range(1, args.trials + 1):
        print(f"  trial {n}/{args.trials}…", file=sys.stderr, flush=True)
        start = len(raw)
        trials.append(run_trial(client, labels, only, raw))
        for r in raw[start:]:
            r["trial"] = n

    # profile consistency across trials (needs ≥2 trials)
    files = [p["file"] for p in labels.get("profile", [])] if "profile" in only else []
    consistent = sum(len({t["profile_undertones"].get(f) for t in trials}) == 1 for f in files)

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    RESULTS.mkdir(exist_ok=True)
    base = RESULTS / f"capstone_{stamp}_{args.label}"
    with open(f"{base}_raw.jsonl", "w") as fh:
        for r in raw:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    keys = [k for k in trials[0] if k not in ("profile_undertones", "bad_statuses")]
    lines = [f"# Capstone eval: {args.label}", "",
             f"- when: {stamp}  · target: {args.url or 'in-process'}  · trials: {args.trials}",
             f"- model: {os.getenv('AI201_MODEL', 'gemini-3.5-flash-lite')} · cache: {os.getenv('AI201_CACHE')}",
             "", "| Metric | " + " | ".join(f"Run {i}" for i in range(1, len(trials) + 1)) + " |",
             "|---|" + "---|" * len(trials)]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(t.get(k, "")) for t in trials) + " |")
    if files:
        lines.append(f"| profile_same_undertone_all_trials | {consistent}/{len(files)} |"
                     + " |" * (len(trials) - 1))
    if not args.url:
        tok = generate.token_counts()
        calls = generate.call_count() - calls0
        lines += ["", f"- model calls: {calls} · prompt tokens: {tok['prompt'] - tokens0['prompt']}"
                      f" · output tokens: {tok['output'] - tokens0['output']}"]
    for i, t in enumerate(trials, 1):
        if "profile_undertones" in t:
            lines.append(f"- run {i} undertones: {t['profile_undertones']}")
        if "bad_statuses" in t:
            lines.append(f"- run {i} bad statuses: {', '.join(t['bad_statuses'])}")
    Path(f"{base}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n  wrote {base}.md and _raw.jsonl", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
