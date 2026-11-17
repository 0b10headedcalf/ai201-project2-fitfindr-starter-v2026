# Capstone criteria — before, run 2

- Started: 2026-11-17T05:51:04+00:00  ·  Finished: 2026-11-17T05:51:15+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_before_run2_c4.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 4 | every case 5/5 | 5/5 cases | MET |

## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| text file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| 9 MiB JPEG magic + zeros | 413 | 5/5 | 413, 413, 413, 413, 413 | 0, 0, 0, 0, 0 | — |
| white PNG → scan | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
| white PNG → profile | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
