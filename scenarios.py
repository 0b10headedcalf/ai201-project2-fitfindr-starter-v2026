"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "intergalactic spacesuit size XXS under $1",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3: compare the selected listing with the item passed to
        # suggest_outfit in the trace; apply the 85% character-match target.
        "name": "selected item reaches outfit suggestion",
        "query": "corduroy wide-leg pants rust under $50",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4: run_eval repeats this same query five times with cache
        # off. Check each caption for the selected item's price and outfit vibe.
        "name": "repeated fit card includes price and outfit vibe",
        "query": "mary janes under $60",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5: $18 is an inclusive boundary (the butterfly tee costs
        # exactly $18). Check ALL search results and the selected item's price
        # against session['parsed']['max_price'], not just the caption.
        "name": "search respects inclusive budget ceiling",
        "query": "graphic tee under $18",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
