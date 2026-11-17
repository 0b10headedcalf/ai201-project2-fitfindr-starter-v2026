# Capstone criteria — before, run 2

- Started: 2026-11-17T05:55:36+00:00  ·  Finished: 2026-11-17T05:58:43+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_before_run2_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 2.29s | 200 in 1.50s | 200 in 1.43s | 5.22s | yes |
| 2 | 200 | 200 in 2.15s | 200 in 1.49s | 200 in 1.31s | 4.95s | yes |
| 3 | 200 | 200 in 2.25s | 200 in 1.43s | 200 in 1.23s | 4.91s | yes |
| 4 | 200 | 200 in 2.43s | 200 in 1.58s | 200 in 1.45s | 5.46s | yes |
| 5 | 200 | 200 in 2.26s | 200 in 1.74s | 200 in 1.64s | 5.64s | yes |
