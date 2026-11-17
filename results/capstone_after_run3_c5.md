# Capstone criteria — after, run 3

- Started: 2026-11-17T06:25:21+00:00  ·  Finished: 2026-11-17T06:28:28+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_after_run3_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 2.05s | 200 in 1.64s | 200 in 1.33s | 5.02s | yes |
| 2 | 200 | 200 in 2.15s | 200 in 1.64s | 200 in 1.42s | 5.21s | yes |
| 3 | 200 | 200 in 2.25s | 200 in 1.43s | 200 in 1.33s | 5.02s | yes |
| 4 | 200 | 200 in 2.24s | 200 in 1.36s | 200 in 1.51s | 5.11s | yes |
| 5 | 200 | 200 in 2.27s | 200 in 1.50s | 200 in 1.40s | 5.17s | yes |
