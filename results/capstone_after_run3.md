# Capstone criteria — after, run 3

- Started: 2026-11-17T06:12:43+00:00  ·  Finished: 2026-11-17T06:17:11+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_after_run3.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 1 | every photo ≥ 4/5 | 5/5 photos | MET |
| 2 | every photo 5/5 valid, ≥ 4/5 same pair | 2/3 photos | MISSED |
| 3 | every occasion ≥ 4/5 | 4/5 occasions | MISSED |
| 4 | every case 5/5 | 5/5 cases | MET |

## 1. Clothes photos → wardrobe entries

| Photo | Labeled | Trials passing | P / R per trial | Why trials failed |
|---|---|---|---|---|
| clothes_01.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 3} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_02.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_03.jpg | {'shoes': 1, 'accessories': 3} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_04.jpg | {'tops': 1, 'bottoms': 1, 'outerwear': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_05.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |

## 2. Person photo → stable profile

| Photo | Valid | (undertone, contrast) per trial | Most common | Count |
|---|---|---|---|---|
| person_01.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_02.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_03.jpg | 5/5 | warm/high, warm/medium, warm/high, warm/medium, warm/high | warm/high | 3/5 |

## 3. Occasion outfits

| Occasion | Trials passing | Words per trial | Why trials failed |
|---|---|---|---|
| job interview at a design studio | 5/5 | 118, 103, 129, 126, 135 | — |
| outdoor summer wedding | 5/5 | 98, 127, 113, 129, 105 | — |
| rainy day errands | 3/5 | 132, 107, 100, 123, 134 | recommends an item outside the ** ** spans ×2 |
| first date at a jazz bar | 5/5 | 116, 147, 119, 98, 133 | — |
| casual Friday at the office | 4/5 | 111, 105, 96, 124, 116 | recommends an item outside the ** ** spans ×1 |

Flagged sentences (garment words outside `**` spans), for the human check:

- *rainy day errands*, trial 1: “Add the   to keep your feet protected from puddles, and sling on the   to keep your hands free for bags and umbrellas.” — umbrella
- *rainy day errands*, trial 2: “Step into the   to keep your feet dry on wet sidewalks, and sling the   over your shoulder to keep your hands free for your umbrella.” — umbrella
- *casual Friday at the office*, trial 1: “The cream-friendly vibe of the white tank and shoes keeps the brightness away from your face without washing you out, avoiding icy pastels entirely.” — shoes, shoe

## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| text file | 400 | 5/5 | 400, 400, 400, 400, 400 | 0, 0, 0, 0, 0 | — |
| 9 MiB JPEG magic + zeros | 413 | 5/5 | 413, 413, 413, 413, 413 | 0, 0, 0, 0, 0 | — |
| white PNG → scan | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
| white PNG → profile | 422 | 5/5 | 422, 422, 422, 422, 422 | 1, 1, 1, 1, 1 | — |
