# Capstone criteria — after, run 1

- Started: 2026-11-17T06:17:37+00:00  ·  Finished: 2026-11-17T06:20:45+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_after_run1_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 2.26s | 200 in 1.67s | 200 in 1.09s | 5.02s | yes |
| 2 | 200 | 200 in 2.47s | 200 in 1.44s | 200 in 1.22s | 5.14s | yes |
| 3 | 200 | 200 in 2.19s | 200 in 1.57s | 200 in 1.16s | 4.92s | yes |
| 4 | 200 | 200 in 2.24s | 200 in 2.15s | 200 in 1.23s | 5.62s | yes |
| 5 | 200 | 200 in 3.52s | 200 in 1.29s | 200 in 1.09s | 5.90s | yes |
