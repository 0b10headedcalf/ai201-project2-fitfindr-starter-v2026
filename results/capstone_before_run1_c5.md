# Capstone criteria — before, run 1

- Started: 2026-11-17T05:51:31+00:00  ·  Finished: 2026-11-17T05:54:51+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_before_run1_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 15.29s | 200 in 1.35s | 200 in 1.18s | 17.82s | yes |
| 2 | 200 | 200 in 2.33s | 200 in 1.60s | 200 in 1.45s | 5.39s | yes |
| 3 | 200 | 200 in 2.30s | 200 in 1.70s | 200 in 1.21s | 5.22s | yes |
| 4 | 200 | 200 in 2.34s | 200 in 1.36s | 200 in 1.20s | 4.91s | yes |
| 5 | 200 | 200 in 2.26s | 200 in 1.36s | 200 in 1.57s | 5.19s | yes |
