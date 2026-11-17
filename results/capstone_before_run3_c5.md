# Capstone criteria — before, run 3

- Started: 2026-11-17T05:59:28+00:00  ·  Finished: 2026-11-17T06:02:34+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `https://fitfindr-vr9s.onrender.com`
- Raw responses: `results/capstone_before_run3_c5.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 5 | ≥ 4/5 flows ≤ 30 s | 5/5 flows | MET |

## 5. Warm deployed photo flow

| Flow | /health | scan | profile | outfit | Total | ≤ 30 s, all 200 |
|---|---|---|---|---|---|---|
| 1 | 200 | 200 in 2.08s | 200 in 1.50s | 200 in 1.59s | 5.17s | yes |
| 2 | 200 | 200 in 2.22s | 200 in 1.31s | 200 in 1.36s | 4.89s | yes |
| 3 | 200 | 200 in 2.08s | 200 in 1.41s | 200 in 1.33s | 4.82s | yes |
| 4 | 200 | 200 in 2.16s | 200 in 1.51s | 200 in 1.36s | 5.03s | yes |
| 5 | 200 | 200 in 2.30s | 200 in 1.43s | 200 in 1.35s | 5.08s | yes |
