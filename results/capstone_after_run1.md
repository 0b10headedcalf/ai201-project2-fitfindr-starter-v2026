# Capstone criteria — after, run 1

- Started: 2026-11-17T06:03:42+00:00  ·  Finished: 2026-11-17T06:08:12+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_after_run1.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 1 | every photo ≥ 4/5 | 4/5 photos | MISSED |
| 2 | every photo 5/5 valid, ≥ 4/5 same pair | 3/3 photos | MET |
| 3 | every occasion ≥ 4/5 | 5/5 occasions | MET |
| 4 | every case 5/5 | 5/5 cases | MET |

## 1. Clothes photos → wardrobe entries

| Photo | Labeled | Trials passing | P / R per trial | Why trials failed |
|---|---|---|---|---|
| clothes_01.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 3} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_02.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_03.jpg | {'shoes': 1, 'accessories': 3} | 3/5 | 100%/100%, 100%/100%, 100%/75%, 100%/75%, 100%/100% | recall 75% < 80% |
| clothes_04.jpg | {'tops': 1, 'bottoms': 1, 'outerwear': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_05.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |

## 2. Person photo → stable profile

| Photo | Valid | (undertone, contrast) per trial | Most common | Count |
|---|---|---|---|---|
| person_01.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_02.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_03.jpg | 5/5 | warm/medium, warm/medium, warm/high, warm/medium, warm/medium | warm/medium | 4/5 |

## 3. Occasion outfits

| Occasion | Trials passing | Words per trial | Why trials failed |
|---|---|---|---|
| job interview at a design studio | 5/5 | 125, 130, 120, 102, 94 | — |
| outdoor summer wedding | 5/5 | 106, 103, 122, 113, 133 | — |
| rainy day errands | 5/5 | 129, 134, 130, 144, 132 | — |
| first date at a jazz bar | 5/5 | 117, 100, 99, 84, 122 | — |
| casual Friday at the office | 5/5 | 116, 108, 116, 99, 126 | — |

Flagged sentences (garment words outside `**` spans), for the human check:


## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| text file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| 9 MiB JPEG magic + zeros | 413 | 5/5 | 413, 413, 413, 413, 413 | 0, 0, 0, 0, 0 | — |
| white PNG → scan | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
| white PNG → profile | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
