# Capstone criteria — after, run 2

- Started: 2026-11-17T06:21:30+00:00  ·  Finished: 2026-11-17T06:24:36+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_after_run2_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 2.18s | 200 in 1.64s | 200 in 1.02s | 4.84s | yes |
| 2 | 200 | 200 in 2.05s | 200 in 1.18s | 200 in 0.87s | 4.10s | yes |
| 3 | 200 | 200 in 3.25s | 200 in 2.19s | 200 in 1.03s | 6.47s | yes |
| 4 | 200 | 200 in 2.10s | 200 in 1.24s | 200 in 1.30s | 4.64s | yes |
| 5 | 200 | 200 in 2.27s | 200 in 2.15s | 200 in 1.24s | 5.66s | yes |
