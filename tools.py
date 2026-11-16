"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """

    if not description and not size and not max_price:
        return []

    raw_listings = load_listings()
    requested_size = size.strip().upper() if size else None
    keywords = description.lower().split() if description else []
    scored_results = []

    for item in raw_listings:
        if max_price is not None and item["price"] > max_price:
            continue

        if requested_size:
            normalized = item["size"].upper()
            for delimiter in ("/", "(", ")", ","):
                normalized = normalized.replace(delimiter, " ")
            size_tokens = normalized.split()
            if requested_size not in size_tokens:
                continue

        searchable_text = " ".join(
            [
                item["title"],
                item["description"],
                item["category"],
                *item["style_tags"],
                *item["colors"],
                item["brand"] or "",
                item["platform"],
            ]
        ).lower()
        score = sum(keyword in searchable_text for keyword in keywords)
        if keywords and score == 0:
            continue

        scored_results.append((score, item))

    scored_results.sort(key=lambda result: result[0], reverse=True)
    return [item for _, item in scored_results[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """

    item_details = (
        f"{new_item['title']} (${new_item['price']:.2f} on "
        f"{new_item['platform']})\n"
        f"Category: {new_item['category']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}\n"
        f"Description: {new_item['description']}"
    )
    wardrobe_items = wardrobe.get("items", [])

    system = (
        "You are a thoughtful personal stylist. Give one or two practical, "
        "specific outfit ideas in a friendly tone. Keep the response under "
        "150 words."
    )
    if not wardrobe_items:
        prompt = (
            "Suggest general styling ideas for this thrift find. Recommend "
            "complementary types of pieces, colors, shoes, and accessories; "
            "do not pretend the user owns particular items.\n\n"
            f"Thrift find:\n{item_details}"
        )
    else:
        formatted_wardrobe = "\n".join(
            f"- {item['name']} ({item['category']}; "
            f"colors: {', '.join(item['colors'])}; "
            f"style: {', '.join(item['style_tags'])})"
            for item in wardrobe_items
        )
        prompt = (
            "Build one or two outfits around the thrift find using only "
            "pieces named in the wardrobe below. Name the specific wardrobe "
            "pieces you choose and briefly explain why they work together.\n\n"
            f"Thrift find:\n{item_details}\n\n"
            f"Wardrobe:\n{formatted_wardrobe}"
        )

    return generate(prompt, system=system)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "I need an outfit suggestion first!"

    item_details = (
        f"Title: {new_item['title']}\n"
        f"Price: ${new_item['price']:.2f}\n"
        f"Platform: {new_item['platform']}\n"
        f"Colors: {', '.join(new_item['colors'])}\n"
        f"Style tags: {', '.join(new_item['style_tags'])}"
    )
    prompt = (
        "Write a two-to-four sentence social caption for a thrift find. "
        "Make it sound personal and specific, not like a product listing. "
        "Mention the item's price and platform exactly once each, and connect "
        "the caption to the outfit idea.\n\n"
        f"Thrift find:\n{item_details}\n\n"
        f"Outfit idea:\n{outfit.strip()}"
    )
    system = (
        "You write concise, upbeat thrift-fashion captions. Do not use "
        "headings, bullet points, or hashtags unless they fit naturally."
    )
    return generate(prompt, system=system)


# ══ Capstone: photo input ═════════════════════════════════════════════════════
#
#   scan_wardrobe(image, mime)                     → {"items": [...], "reason"?}
#   analyze_profile(image, mime)                   → profile dict | {"error": ...}
#   outfit_for_occasion(wardrobe, profile, occ)    → str
#
# Both photo tools go through the same generate(images=..., json_mode=True)
# path and then validate in Python. The model is asked for the schema, but the
# code is what guarantees it: a sixth category or a missing name never reaches
# the wardrobe.

import json as _json

ALLOWED_CATEGORIES = ("tops", "bottoms", "outerwear", "shoes", "accessories")

# Things the model says instead of one of the five categories, mapped back.
_CATEGORY_ALIASES = {
    "top": "tops", "shirt": "tops", "shirts": "tops", "tee": "tops",
    "t-shirt": "tops", "blouse": "tops", "sweater": "tops", "knitwear": "tops",
    "dress": "tops", "dresses": "tops",
    "bottom": "bottoms", "pants": "bottoms", "jeans": "bottoms",
    "trousers": "bottoms", "shorts": "bottoms", "skirt": "bottoms",
    "skirts": "bottoms",
    "jacket": "outerwear", "jackets": "outerwear", "coat": "outerwear",
    "coats": "outerwear", "hoodie": "outerwear",
    "shoe": "shoes", "sneakers": "shoes", "boots": "shoes", "footwear": "shoes",
    "accessory": "accessories", "bag": "accessories", "bags": "accessories",
    "hat": "accessories", "jewelry": "accessories", "belt": "accessories",
}

UNDERTONES = ("warm", "cool", "neutral")
CONTRASTS = ("low", "medium", "high")


def _parse_json(text: str) -> dict | None:
    """The model's JSON, or None. Tolerates a ```json fence around it."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned[4:] if cleaned.lower().startswith("json") else cleaned
    try:
        parsed = _json.loads(cleaned)
    except (ValueError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _normalize_category(raw) -> str | None:
    value = str(raw or "").strip().lower()
    if value in ALLOWED_CATEGORIES:
        return value
    return _CATEGORY_ALIASES.get(value)


def _str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip().lower() for v in value if str(v).strip()]


def scan_wardrobe(image: bytes, mime: str) -> dict:
    """
    Turn a photo of clothes into wardrobe items in the wardrobe_schema.json shape.

    Returns:
        {"items": [...]} with every item validated: a non-empty name, a category
        from ALLOWED_CATEGORIES, lists for colors/style_tags, and an id
        scan_<n>. Items the code can't make valid are dropped and counted in
        "dropped". When there is no clothing in the photo — or the model's
        answer can't be parsed — returns {"items": [], "reason": "..."}.
    """
    system = (
        "You catalogue clothing from photos for a personal wardrobe app. "
        "List only garments, shoes and accessories you can actually see. "
        "Never invent items. Respond with JSON only."
    )
    prompt = (
        "List every distinct clothing item visible in this photo.\n"
        "Return JSON exactly in this shape:\n"
        '{"items": [{"name": "short description, e.g. \'Baggy straight-leg '
        'jeans, dark wash\'", "category": "one of: tops, bottoms, outerwear, '
        'shoes, accessories", "colors": ["..."], "style_tags": ["..."], '
        '"notes": "fit or material details, optional"}]}\n'
        'If there is no clothing in the photo, return {"items": [], '
        '"reason": "what the photo shows instead"}.'
    )
    text = generate(
        prompt, system=system, temperature=0.2,
        images=[(image, mime)], json_mode=True,
    )
    parsed = _parse_json(text)
    if parsed is None:
        return {"items": [], "reason": "The model's answer wasn't valid JSON."}

    items, dropped = [], 0
    for raw in parsed.get("items") or []:
        if not isinstance(raw, dict):
            dropped += 1
            continue
        name = str(raw.get("name") or "").strip()
        category = _normalize_category(raw.get("category"))
        if not name or category is None:
            dropped += 1
            continue
        items.append({
            "id": f"scan_{len(items) + 1:03d}",
            "name": name,
            "category": category,
            "colors": _str_list(raw.get("colors")),
            "style_tags": _str_list(raw.get("style_tags")),
            "notes": str(raw.get("notes") or "").strip(),
        })

    result = {"items": items}
    if dropped:
        result["dropped"] = dropped
    if not items:
        result["reason"] = str(
            parsed.get("reason") or "No clothing items were found in the photo."
        )
    return result


def analyze_profile(image: bytes, mime: str) -> dict:
    """
    Read a person's coloring from a full-body photo, for choosing colors.

    Coloring only — no body shape, no judgments about appearance.

    Returns:
        {"undertone": warm|cool|neutral, "contrast": low|medium|high,
         "hair_color": str, "eye_color": str,
         "flattering_colors": [...], "avoid_colors": [...]}
        or {"error": "..."} when there isn't exactly one person visible or the
        answer can't be validated.
    """
    system = (
        "You are a color-analysis assistant for a styling app. You describe "
        "coloring (skin undertone, hair, eyes, contrast) only to recommend "
        "clothing colors. Do not comment on body shape, weight, attractiveness, "
        "age, or ethnicity. Respond with JSON only."
    )
    prompt = (
        "Analyze the coloring of the person in this photo.\n"
        "Return JSON exactly in this shape:\n"
        '{"person_count": <number of people visible>, '
        '"undertone": "warm | cool | neutral", '
        '"contrast": "low | medium | high (between hair, skin and eyes)", '
        '"hair_color": "...", "eye_color": "... or \'not visible\'", '
        '"flattering_colors": ["5-8 clothing colors"], '
        '"avoid_colors": ["2-4 colors"]}'
    )
    text = generate(
        prompt, system=system, temperature=0.2,
        images=[(image, mime)], json_mode=True,
    )
    parsed = _parse_json(text)
    if parsed is None:
        return {"error": "The model's answer wasn't valid JSON."}

    count = parsed.get("person_count")
    if count != 1:
        return {"error": f"Expected exactly one person in the photo, found {count}."}

    undertone = str(parsed.get("undertone") or "").strip().lower()
    contrast = str(parsed.get("contrast") or "").strip().lower()
    if undertone not in UNDERTONES or contrast not in CONTRASTS:
        return {"error": "The model returned an undertone or contrast outside the allowed values."}

    return {
        "undertone": undertone,
        "contrast": contrast,
        "hair_color": str(parsed.get("hair_color") or "").strip(),
        "eye_color": str(parsed.get("eye_color") or "").strip(),
        "flattering_colors": _str_list(parsed.get("flattering_colors")),
        "avoid_colors": _str_list(parsed.get("avoid_colors")),
    }


def outfit_for_occasion(wardrobe: dict, profile: dict | None, occasion: str) -> str:
    """
    Build an outfit for an occasion from clothes the user already owns.

    Args:
        wardrobe: a wardrobe dict with an 'items' list (may be empty).
        profile:  analyze_profile()'s result, or None to skip color guidance.
        occasion: what the user is dressing for, in plain language.

    Returns:
        A non-empty string. An empty wardrobe gets general advice rather than
        an invented closet; an empty occasion gets a message asking for one.
    """
    occasion = (occasion or "").strip()
    if not occasion:
        return "Tell me what the occasion is first!"

    wardrobe_items = (wardrobe or {}).get("items", [])
    profile_text = ""
    if profile and not profile.get("error"):
        profile_text = (
            f"\n\nThe user's coloring: {profile.get('undertone')} undertone, "
            f"{profile.get('contrast')} contrast, {profile.get('hair_color')} hair. "
            f"Colors that flatter them: {', '.join(profile.get('flattering_colors', []))}. "
            f"Colors to keep away from the face: {', '.join(profile.get('avoid_colors', []))}."
        )

    system = (
        "You are a thoughtful personal stylist. Be specific and practical, "
        "friendly in tone, and keep the response under 170 words."
    )
    if not wardrobe_items:
        prompt = (
            f"Suggest what to wear for this occasion: {occasion}.\n"
            "The user hasn't added any clothes yet, so describe types of pieces "
            "rather than pretending they own particular items."
            f"{profile_text}"
        )
    else:
        formatted = "\n".join(
            f"- {item['name']} ({item['category']}; "
            f"colors: {', '.join(item.get('colors', []))}; "
            f"style: {', '.join(item.get('style_tags', []))})"
            for item in wardrobe_items
        )
        prompt = (
            f"Build one outfit for this occasion: {occasion}.\n"
            "Use ONLY pieces from the wardrobe below and name each one exactly "
            "as written. Say why the outfit suits the occasion"
            + (" and how its colors work with the user's coloring." if profile_text else ".")
            + " If the wardrobe is missing something the occasion really needs, "
            "say what in one sentence at the end."
            f"{profile_text}\n\nWardrobe:\n{formatted}"
        )
    return generate(prompt, system=system)
