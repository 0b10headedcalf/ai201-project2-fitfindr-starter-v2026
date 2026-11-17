# Capstone criteria — before, run 2

- Started: 2026-11-17T05:41:50+00:00  ·  Finished: 2026-11-17T05:46:02+00:00
- Model: `gemini-3.5-flash-lite`  ·  temperature as set in tools.py  ·  cache off
- Criteria 1–4: in-process (`serve.app.test_client()`); criterion 5: `not run`
- Raw responses: `results/capstone_before_run2.jsonl`

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
| clothes_03.jpg | {'shoes': 1, 'accessories': 3} | 3/5 | 100%/75%, 100%/100%, 100%/75%, 100%/100%, 100%/100% | recall 75% < 80% |
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
| job interview at a design studio | 0/5 | 98, 134, 129, 125, 114 | recommends an item outside the ** ** spans ×5 |
| outdoor summer wedding | 1/5 | 108, 121, 113, 92, 126 | wardrobe item(s) named without ** **: ['Vintage black denim jacket', 'Chunky white sneakers', 'Wide-leg khaki trousers', 'White ribbed tank top', 'Brown leather belt'] ×1; recommends an item outside the ** ** spans ×4; wardrobe item(s) named without ** **: ['Vintage black denim jacket', 'Wide-leg khaki trousers', 'White ribbed tank top', 'Brown leather belt'] ×1 |
| rainy day errands | 0/5 | 111, 119, 123, 112, 122 | recommends an item outside the ** ** spans ×5; wardrobe item(s) named without ** **: ['Oversized grey crewneck sweatshirt', 'White ribbed tank top', 'Black combat boots', 'Black crossbody bag'] ×1; wardrobe item(s) named without ** **: ['Baggy straight-leg jeans, dark wash', 'Black crossbody bag', 'Black combat boots', 'Oversized grey crewneck sweatshirt'] ×1 |
| first date at a jazz bar | 1/5 | 133, 132, 125, 128, 119 | wardrobe item(s) named without ** **: ['Vintage black denim jacket', 'Black crossbody bag', 'Black combat boots', 'Wide-leg khaki trousers', 'White ribbed tank top'] ×1; recommends an item outside the ** ** spans ×4; wardrobe item(s) named without ** **: ['Vintage black denim jacket', 'Black combat boots', 'Wide-leg khaki trousers', 'White ribbed tank top', 'Brown leather belt'] ×1 |
| casual Friday at the office | 0/5 | 135, 110, 109, 134, 105 | wardrobe item(s) named without ** **: ['Oversized grey crewneck sweatshirt', 'Chunky white sneakers', 'Black crossbody bag', 'Wide-leg khaki trousers', 'White ribbed tank top', 'Brown leather belt'] ×1; recommends an item outside the ** ** spans ×5 |

Flagged sentences (garment words outside `**` spans), for the human check:

- *job interview at a design studio*, trial 1: “The wardrobe is missing a structured blazer or smart button-down shirt to truly nail the interview dress code.” — blazer, shirt, dress
- *job interview at a design studio*, trial 2: “*Note: This wardrobe is missing a structured blouse or knit top to make the outfit fully interview-appropriate.*” — blouse
- *job interview at a design studio*, trial 3: “*Note: The wardrobe is missing a proper structured blazer or button-down shirt to elevate this to traditional interview standards.*” — blazer, shirt
- *job interview at a design studio*, trial 4: “To complete this for an interview, you really need a structured blazer or smart button-down shirt to add an extra layer of professional polish.” — blazer, shirt
- *job interview at a design studio*, trial 5: “*(Note: The wardrobe is missing a tailored button-down shirt or blazer to elevate the outfit to a fully professional standard.)*” — blazer, shirt
- *outdoor summer wedding*, trial 1: “The wardrobe is missing a pair of dress shoes or elevated sandals appropriate for a wedding.” — dress, shoes, shoe, sandals
- *outdoor summer wedding*, trial 2: “To complete this look for a wedding, the wardrobe is missing a pair of dressy sandals or loafers.” — loafers, sandals
- *outdoor summer wedding*, trial 3: “*Note: This wardrobe is missing dress shoes and formal accessories, which a wedding truly calls for.*” — dress, shoes, shoe
- *outdoor summer wedding*, trial 5: “The wardrobe is missing a pair of formal dress shoes suitable for a wedding.” — dress, shoes, shoe
- *rainy day errands*, trial 1: “This look is ideal for running errands because it’s comfortable, easy to move in, and the sturdy combat boots handle wet streets better than sneakers.” — sneakers
- *rainy day errands*, trial 1: “*Note: This outfit really needs a waterproof rain jacket to keep you dry.*” — jacket
- *rainy day errands*, trial 2: “*(Note: This wardrobe is missing a proper rain jacket or umbrella to keep you dry!)*” — jacket, umbrella
- *rainy day errands*, trial 3: “*Note: This look really needs a waterproof rain jacket to keep you dry during the downpour.*” — jacket
- *rainy day errands*, trial 4: “For your rainy errand run, layer the White ribbed tank top under the Oversized grey crewneck sweatshirt, paired with the Baggy straight-leg jeans, the Black combat boots, and the Black crossbody bag.” — jeans
- *rainy day errands*, trial 4: “This cozy sweatshirt and durable combat boots keep you comfortable and puddle-ready, while the practical crossbody leaves your hands free for bags and umbrellas.” — umbrella
- *rainy day errands*, trial 4: “*(Note: The wardrobe is missing a waterproof raincoat and an umbrella to keep you truly dry.)*” — raincoat, umbrella
- *rainy day errands*, trial 5: “Because this grey sweatshirt keeps cool tones close to your complexion, a rust- or olive-toned scarf would instantly make it more flattering.” — scarf
- *rainy day errands*, trial 5: “*Note: This rainy-day outfit is missing a proper waterproof raincoat or umbrella.*” — raincoat, umbrella
- *first date at a jazz bar*, trial 2: “The khaki trousers and brown leather belt (if you add one) lean into your warm undertones and dark brown hair, grounding your medium contrast.” — belt
- *first date at a jazz bar*, trial 2: “The wardrobe is missing a rich textured layer, like a rust or olive sweater, to elevate the romantic, cozy jazz club atmosphere.” — sweater
- *first date at a jazz bar*, trial 3: “*(Note: This outfit really needs a layer of delicate gold jewelry to elevate the neckline for a romantic date setting.)*” — jewelry
- *first date at a jazz bar*, trial 4: “*Note: The wardrobe is missing a dressy top layer, like a sleek blazer or textured cardigan, to elevate the look for an evening out.*” — blazer, cardigan
- *first date at a jazz bar*, trial 5: “This wardrobe is missing a sophisticated layering piece like a blazer or knit sweater to fully elevate the evening vibe.” — blazer, sweater
- *casual Friday at the office*, trial 1: “*Note: This wardrobe is missing a proper blazer or structured jacket to elevate the trousers for a standard office environment.*” — jacket, blazer
- *casual Friday at the office*, trial 2: “*To complete this look for an office setting, you really need a professional blazer or structured cardigan to swap in for the denim jacket.*” — blazer, cardigan
- *casual Friday at the office*, trial 3: “*To make this outfit fully office-appropriate, it really needs a blazer or structured button-down shirt to elevate the relaxed pieces.*” — blazer, shirt
- *casual Friday at the office*, trial 4: “To complete this look for the office, you really need a layer like a blazer or cardigan to elevate the tank top.” — blazer, cardigan
- *casual Friday at the office*, trial 5: “The wardrobe really needs a structured blazer or collared shirt to fully elevate the look for an office setting.” — blazer, shirt

## 4. Invalid uploads

| Case | Expected | Trials passing | Statuses | model_calls | Problems |
|---|---|---|---|---|---|
| empty file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| text file | 400 | 0/5 | 400, 400, 400, 400, 400 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| 9 MiB JPEG magic + zeros | 413 | 0/5 | 413, 413, 413, 413, 413 | None, None, None, None, None | /me status 503; log model_calls None, expected 0; something was stored |
| white PNG → scan | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
| white PNG → profile | 422 | 0/5 | 503, 503, 503, 503, 503 | None, None, None, None, None | /me status 503; something was stored; status 503, expected 422 |
