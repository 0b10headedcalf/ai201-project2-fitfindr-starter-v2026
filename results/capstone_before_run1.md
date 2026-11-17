# Capstone criteria — before, run 1

- Started: 2026-11-17T05:37:34+00:00  ·  Finished: 2026-11-17T05:41:49+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_before_run1.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 1 | every photo ≥ 4/5 | 4/5 photos | MISSED |
| 2 | every photo 5/5 valid, ≥ 4/5 same pair | 3/3 photos | MET |
| 3 | every occasion ≥ 4/5 | 0/5 occasions | MISSED |
| 4 | every case 5/5 | 0/5 cases | MISSED |

## 1. Clothes photos → wardrobe entries

| Photo | Labeled | Trials passing | P / R per trial | Why trials failed |
|---|---|---|---|---|
| clothes_01.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 3} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_02.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_03.jpg | {'shoes': 1, 'accessories': 3} | 1/5 | 100%/75%, 100%/75%, 100%/100%, 100%/75%, 100%/75% | recall 75% < 80% |
| clothes_04.jpg | {'tops': 1, 'bottoms': 1, 'outerwear': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_05.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |

## 2. Person photo → stable profile

| Photo | Valid | (undertone, contrast) per trial | Most common | Count |
|---|---|---|---|---|
| person_01.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_02.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_03.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |

## 3. Occasion outfits

| Occasion | Trials passing | Words per trial | Why trials failed |
|---|---|---|---|
| job interview at a design studio | 0/5 | 126, 123, 126, 129, 132 | recommends an item outside the ** ** spans ×5 |
| outdoor summer wedding | 1/5 | 123, 137, 101, 110, 113 | wardrobe item(s) named without ** **: ['White ribbed tank top', 'Wide-leg khaki trousers', 'Vintage black denim jacket', 'Brown leather belt'] ×1; recommends an item outside the ** ** spans ×3; wardrobe item(s) named without ** **: ['White ribbed tank top', 'Brown leather belt', 'Wide-leg khaki trousers', 'Black combat boots', 'Vintage black denim jacket', 'Black crossbody bag'] ×1; wardrobe item(s) named without ** **: ['White ribbed tank top', 'Wide-leg khaki trousers', 'Brown leather belt'] ×1; wardrobe item(s) named without ** **: ['White ribbed tank top', 'Wide-leg khaki trousers', 'Brown leather belt', 'Chunky white sneakers'] ×1 |
| rainy day errands | 0/5 | 117, 109, 125, 112, 122 | recommends an item outside the ** ** spans ×5; wardrobe item(s) named without ** **: ['White ribbed tank top', 'Oversized grey crewneck sweatshirt', 'Wide-leg khaki trousers', 'Black combat boots', 'Black crossbody bag'] ×1 |
| first date at a jazz bar | 0/5 | 108, 152, 126, 126, 135 | wardrobe item(s) named without ** **: ['White ribbed tank top', 'Brown leather belt', 'Wide-leg khaki trousers', 'Black combat boots', 'Vintage black denim jacket'] ×3; recommends an item outside the ** ** spans ×5 |
| casual Friday at the office | 0/5 | 118, 125, 102, 113, 128 | recommends an item outside the ** ** spans ×5 |

Flagged sentences (garment words outside `**` spans), for the human check:

- *job interview at a design studio*, trial 1: “*Note: This wardrobe is missing a structured blouse or knit layer to elevate the outfit for a formal interview setting.*” — blouse
- *job interview at a design studio*, trial 2: “To complete this look for an interview, you really need a structured blazer or tailored shirt to elevate the casual layers.” — blazer, shirt
- *job interview at a design studio*, trial 3: “However, this wardrobe is missing a polished button-down shirt or structured blazer to elevate the outfit to full interview-appropriateness.” — blazer, shirt
- *job interview at a design studio*, trial 4: “The khaki tan pants and brown belt honor your warm undertone, drawing flattering earthy warmth near your face.” — pants
- *job interview at a design studio*, trial 4: “The wardrobe is missing a structured button-down shirt or blazer to elevate the outfit to full professional polish.” — blazer, shirt
- *job interview at a design studio*, trial 5: “*Note: The wardrobe is missing a professional structured layer or blouse to elevate the outfit to standard interview formality.*” — blouse
- *outdoor summer wedding*, trial 1: “*Note: This wardrobe is missing dress shoes, as sneakers and combat boots are too casual for a wedding.*” — dress, shoes, shoe, sneakers, boots, boot
- *outdoor summer wedding*, trial 2: “Note: This wardrobe is missing formal dress shoes or sandals, which a summer wedding truly needs.” — dress, shoes, shoe, sandals
- *outdoor summer wedding*, trial 3: “To complete this wedding-ready guest look, you really need a pair of dressy dress shoes or sandals instead of sneakers or boots.” — dress, shoes, shoe, sneakers, boots, boot, sandals
- *rainy day errands*, trial 1: “*Note: This outfit really needs a waterproof rain jacket to keep you dry in a downpour.*” — jacket
- *rainy day errands*, trial 2: “*Note: This outfit really needs a waterproof rain jacket or trench coat to keep you dry.*” — jacket, coat, trench
- *rainy day errands*, trial 3: “*Note: This look is missing a waterproof raincoat or umbrella to truly protect you from a downpour.*” — raincoat, umbrella
- *rainy day errands*, trial 4: “*Note: This outfit really needs a waterproof rain jacket or trench coat to keep you dry.*” — jacket, coat, trench
- *rainy day errands*, trial 5: “*(Note: This wardrobe is missing a waterproof raincoat to keep you dry in a downpour!)*” — raincoat
- *first date at a jazz bar*, trial 1: “The rich khaki pants introduce an earth tone that flatters your warm undertone, while keeping white and black away from your face lets your dark brown hair and medium contrast stand out naturally.” — pants
- *first date at a jazz bar*, trial 2: “*Note: The wardrobe is missing a more elevated top option, like a silky blouse or fitted knit, to truly match the moody, upscale ambiance of a jazz bar.*” — blouse
- *first date at a jazz bar*, trial 3: “*Note: This outfit really needs a piece of statement jewelry or a scarf to add a touch of romance and personality for a date.*” — scarf, jewelry
- *first date at a jazz bar*, trial 4: “However, this wardrobe is missing a richer top color—swapping the white tank for a rust or olive shirt would instantly take this date-night outfit to the next level.” — shirt
- *first date at a jazz bar*, trial 5: “However, this outfit is really missing a piece of warm-toned statement jewelry to truly elevate the look for a date night.” — jewelry
- *casual Friday at the office*, trial 1: “*Note: This look really needs a structured blazer or knit cardigan to elevate the tank top for a standard office environment.*” — blazer, cardigan
- *casual Friday at the office*, trial 2: “*To complete this office-appropriate look, a structured blazer or collared shirt is missing.*” — blazer, shirt
- *casual Friday at the office*, trial 3: “The wardrobe is missing a structured blazer or smart button-down shirt to truly elevate the look for an office environment.” — blazer, shirt
- *casual Friday at the office*, trial 4: “*Note: This wardrobe is missing a structured blazer or collared shirt to fully elevate the look for a traditional office setting.*” — blazer, shirt
- *casual Friday at the office*, trial 5: “*Note: This wardrobe is missing a proper collared shirt or blouse to elevate the look for a traditional office setting.*” — shirt, blouse

## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| text file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| 9 MiB JPEG magic + zeros | 413 | 0/5 | 413, 413, 413, 413, 413 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| white PNG → scan | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
| white PNG → profile | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
