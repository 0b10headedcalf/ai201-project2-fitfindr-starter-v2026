# Capstone criteria — before, run 3

- Started: 2026-11-17T05:46:03+00:00  ·  Finished: 2026-11-17T05:50:16+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_before_run3.jsonl`

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 1 | every photo ≥ 4/5 | 5/5 photos | MET |
| 2 | every photo 5/5 valid, ≥ 4/5 same pair | 2/3 photos | MISSED |
| 3 | every occasion ≥ 4/5 | 0/5 occasions | MISSED |
| 4 | every case 5/5 | 0/5 cases | MISSED |

## 1. Clothes photos → wardrobe entries

| Photo | Labeled | Trials passing | P / R per trial | Why trials failed |
|---|---|---|---|---|
| clothes_01.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 3} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_02.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_03.jpg | {'shoes': 1, 'accessories': 3} | 4/5 | 100%/100%, 100%/100%, 100%/75%, 100%/100%, 100%/100% | recall 75% < 80% |
| clothes_04.jpg | {'tops': 1, 'bottoms': 1, 'outerwear': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |
| clothes_05.jpg | {'tops': 1, 'bottoms': 1, 'shoes': 1, 'accessories': 1} | 5/5 | 100%/100%, 100%/100%, 100%/100%, 100%/100%, 100%/100% | — |

## 2. Person photo → stable profile

| Photo | Valid | (undertone, contrast) per trial | Most common | Count |
|---|---|---|---|---|
| person_01.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_02.jpg | 5/5 | warm/medium, warm/medium, warm/medium, warm/medium, warm/medium | warm/medium | 5/5 |
| person_03.jpg | 5/5 | warm/medium, warm/medium, warm/high, warm/medium, warm/high | warm/medium | 3/5 |

## 3. Occasion outfits

| Occasion | Trials passing | Words per trial | Why trials failed |
|---|---|---|---|
| job interview at a design studio | 0/5 | 100, 121, 116, 131, 135 | recommends an item outside the ** ** spans ×5 |
| outdoor summer wedding | 0/5 | 104, 126, 116, 95, 134 | wardrobe item(s) named without ** **: ['Vintage black denim jacket', 'White ribbed tank top', 'Brown leather belt', 'Wide-leg khaki trousers'] ×1; recommends an item outside the ** ** spans ×5; wardrobe item(s) named without ** **: ['Brown leather belt', 'Vintage black denim jacket', 'White ribbed tank top', 'Wide-leg khaki trousers', 'Black combat boots'] ×1 |
| rainy day errands | 0/5 | 140, 144, 132, 111, 115 | recommends an item outside the ** ** spans ×5; wardrobe item(s) named without ** **: ['Black crossbody bag', 'White ribbed tank top', 'Wide-leg khaki trousers', 'Oversized grey crewneck sweatshirt', 'Black combat boots'] ×1 |
| first date at a jazz bar | 2/5 | 129, 142, 129, 139, 125 | recommends an item outside the ** ** spans ×3; wardrobe item(s) named without ** **: ['Black crossbody bag', 'Vintage black denim jacket', 'White ribbed tank top', 'Wide-leg khaki trousers', 'Black combat boots'] ×1 |
| casual Friday at the office | 0/5 | 111, 124, 100, 110, 110 | recommends an item outside the ** ** spans ×5; wardrobe item(s) named without ** **: ['Black crossbody bag', 'Brown leather belt', 'White ribbed tank top', 'Wide-leg khaki trousers', 'Chunky white sneakers', 'Oversized grey crewneck sweatshirt'] ×1 |

Flagged sentences (garment words outside `**` spans), for the human check:

- *job interview at a design studio*, trial 1: “*Note: This look needs a structured blazer or button-down shirt to feel fully interview-appropriate.*” — blazer, shirt
- *job interview at a design studio*, trial 2: “*Note: This outfit really needs a tailored blazer or button-down shirt to elevate it to standard professional interview standards.*” — blazer, shirt
- *job interview at a design studio*, trial 3: “The wardrobe is missing a structured blazer or collared shirt to elevate the look for a formal interview setting.” — blazer, shirt
- *job interview at a design studio*, trial 4: “*Note: This look really needs a structured blazer or knit cardigan to elevate it to standard interview level.*” — blazer, cardigan
- *job interview at a design studio*, trial 5: “*Note: The wardrobe is missing a proper collared shirt or structured blazer to elevate the look for a formal professional setting.*” — blazer, shirt
- *outdoor summer wedding*, trial 1: “To complete this wedding-ready outfit, you really need a pair of dressy sandals or loafers instead of sneakers.” — sneakers, loafers, sandals
- *outdoor summer wedding*, trial 2: “The wardrobe is missing a pair of dress shoes or nice sandals, which this outfit really needs instead of sneakers or boots for a wedding.” — dress, shoes, shoe, sneakers, boots, boot, sandals
- *outdoor summer wedding*, trial 3: “One sentence at a time: This wardrobe is missing formal footwear and a dressier bag suitable for a wedding.” — bag
- *outdoor summer wedding*, trial 4: “*Note: This wardrobe is missing formal footwear and tailored outerwear suitable for a wedding dress code.*” — dress
- *outdoor summer wedding*, trial 5: “This wardrobe is missing formal footwear and a dressy bag appropriate for a wedding.” — bag
- *rainy day errands*, trial 1: “*(Note: This outfit really needs a waterproof rain jacket or trench coat to keep you dry!)*” — jacket, coat, trench
- *rainy day errands*, trial 2: “(White and grey near your face are neutral enough to work, but since icy pastels are off-limits, you could pop a rust or olive scarf around your neck to make your complexion really glow!)” — scarf
- *rainy day errands*, trial 2: “*Missing piece:* Waterproof rain boots or an umbrella.” — umbrella
- *rainy day errands*, trial 3: “*Note: This outfit really needs a waterproof rain jacket or trench coat to keep you dry during downpours.*” — jacket, coat, trench
- *rainy day errands*, trial 4: “*Note: Your wardrobe is missing a waterproof rain jacket or trench coat to keep you dry.*” — jacket, coat, trench
- *rainy day errands*, trial 5: “*Note: This rainy day wardrobe is missing a proper waterproof raincoat or umbrella to keep you fully dry.*” — raincoat, umbrella
- *first date at a jazz bar*, trial 1: “*Note: This outfit needs a delicate gold pendant necklace or hoop earrings to add a touch of intimate, romantic polish for a date.*” — necklace, earrings
- *first date at a jazz bar*, trial 3: “*Note: This outfit needs a delicate gold pendant necklace or statement earrings to elevate it for a romantic evening.*” — necklace, earrings
- *first date at a jazz bar*, trial 5: “*This wardrobe is missing a statement top or necklace to add a touch of evening sophistication near the face.*” — necklace
- *casual Friday at the office*, trial 1: “*To make this outfit truly office-ready, you really need to add a blazer or a collared shirt.*” — blazer, shirt
- *casual Friday at the office*, trial 2: “*Your wardrobe is missing a tailored blazer or button-down shirt to truly nail a polished office dress code.*” — blazer, shirt, dress
- *casual Friday at the office*, trial 3: “*Note: This wardrobe is missing a structured blazer or collared shirt to fully elevate the look for a standard office environment.*” — blazer, shirt
- *casual Friday at the office*, trial 4: “The wardrobe is missing a structured layering piece, like a blazer or cardigan, to instantly elevate the trousers for a more polished workplace feel.” — blazer, cardigan
- *casual Friday at the office*, trial 5: “*Note: This wardrobe is missing a proper collar shirt or blazer to make the outfit fully professional for most standard offices.*” — blazer, shirt

## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| text file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| 9 MiB JPEG magic + zeros | 413 | 0/5 | 413, 413, 413, 413, 413 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| white PNG → scan | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
| white PNG → profile | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
