# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr helps a user find thrift listings that fit their parameters. A user can ask for something such as "vintage graphic tee under $30,"
and the app searches the local listings dataset for relevant options. When it
finds one, it suggests an outfit using the user's saved wardrobe and writes a
short fit-card caption for the find.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the thrift-listing dataset by keyword, with optional exact size-token matching and an inclusive maximum price. Results with more matching keywords appear first.
- **Inputs:** `description: str`, `size: str | None`, `max_price: float | None`.
- **Returns:** A list of up to `SEARCH_RESULT_LIMIT` matching listing dictionaries, each containing item details such as title, price, size, tags, and platform.
- **When it has nothing:** Returns `[]` when no listing has a matching keyword or meets the supplied filters.

### `suggest_outfit`

- **What it does:** Uses the model to suggest one or two outfits around a selected thrift listing, naming compatible items from the user's wardrobe when available.
- **Inputs:** `new_item: dict`, `wardrobe: dict` with an `items` list.
- **Returns:** A non-empty styling suggestion string.
- **When it has nothing:** With an empty wardrobe, returns general styling ideas without claiming that the user owns specific pieces.

### `create_fit_card`

- **What it does:** Uses the model to turn an outfit suggestion and thrift listing into a short, social-media-style fit-card caption.
- **Inputs:** `outfit: str`, `new_item: dict`.
- **Returns:** A two-to-four sentence caption that mentions the listing's price and platform once each.
- **When it has nothing:** If the outfit is empty or only whitespace, returns a message explaining that an outfit suggestion is needed.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, store a helpful
message in `session["error"]` and stop. Otherwise, select the first matching
listing, call `suggest_outfit`, then call `create_fit_card` with that outfit
and listing.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** String splitting. `run_agent` removes a `size`
value and an `under $` price value from the search description before passing
the remaining words to `search_listings`.

**What moves through the session:** The parsed description, size, and price
ceiling go into `session["parsed"]`; search results go into
`session["search_results"]`; the first result becomes `session["selected_item"]`;
then the outfit and caption go into `session["outfit_suggestion"]` and
`session["fit_card"]`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here is a fun, Y2K-inspired outfit using your thrift find!

  Streetwear Contrast: Pair the butterfly baby tee with baggy straight-leg jeans, a black cropped zip hoodie, chunky white sneakers, and a black crossbody bag for an easy Y2K streetwear look.

  Fit card: I couldn't resist grabbing this pastel butterfly baby tee when I spotted it on Depop for just $18.00! To lean into that ultimate early 2000s proportion play, I'm pairing it with baggy straight-leg jeans and throwing an unzipped black hoodie right over top. Finished off with chunky white sneakers, it's the easiest way to mix a sweet graphic print with some effortless streetwear edge.

1 model call this session, 1 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(item['title'], item['price']) for item in search_listings('graphic tee', max_price=30)])"
[('Y2K Baby Tee — Butterfly Print', 18.0), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0), ('Mesh Long-Sleeve Top — Black', 15.0), ('Vintage Band Tee — Faded Grey', 19.0), ('Low-Rise Cargo Pants — Khaki', 27.0), ('Oversized Crewneck Sweatshirt — Vintage Navy', 20.0), ('Vintage Graphic Hoodie — Faded Black', 26.0)]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe()))"
Here is a fun, Y2K-inspired outfit using your thrift find!

**Streetwear Contrast:** Pair the butterfly baby tee with your **baggy straight-leg jeans** for that classic early 2000s proportion play (fitted top, loose bottoms). Layer the **black cropped zip hoodie** over top, leaving it partially unzipped to show off the graphic. Finish with the **chunky white sneakers** and the **black crossbody bag** for an effortless, everyday look.

**Why it works:** The fitted silhouette of the baby tee balances the volume of the baggy jeans, while the black hoodie and sneakers ground the cute, pastel butterfly print with an edgy streetwear vibe.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair it with baggy dark-wash jeans and clean white sneakers.', load_listings()[1]))"
I couldn't resist grabbing this pink and purple butterfly baby tee when I spotted it on depop for just $18.00. It instantly took me right back to the early 2000s, but I love dressing it down with baggy dark-wash jeans and clean white sneakers for that perfect effortless mix of sweet and slouchy.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Sample prompts and inputs for the functions that required calling the model.
- *What came back:* Well designed and structured prompts that produced better results than my original prompts.
- *What I changed:* I did change some of the wording and code that it tried to implement.

**Moment 2**

- *What I asked for:* Asked it to spruce up my regex usage
- *What came back:* Well structured regex that I would be way too lazy to look up
- *What I changed:* I ended up refactoring to not use regex for the time being as we can always refactor back later if the tools actually need them

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

     Moment 1:
     Used AI to help me produce code for scenarios and agent.py, mostly since I did not really have the time this week. I did a full review of the agent's outputs though and ensured every test was running properly.

     Moment 2:
     Used AI to help write out some of the prompts and informations for the MCP server, just so that everything that the agent does works a little more smoothly.

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 and names what to change | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on (at least 85% of characters) | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5 demonstrated) |
| 4. Fit card mentions the item's price and outfit vibe | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search returns nothing over the user's budget | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Run: `python run_eval.py --label before`, five tries per scenario with caching
off. Full output is saved in
[the evaluator report](results/run_2026-10-11_2325_before.md) and
[the terminal log](results/run_2026-10-11_2325_before_terminal.txt).
The extra empty-wardrobe diagnostic completed in all five tries; it is separate
from these five criteria.

Scoring: criterion 1 completed all three tools with a non-empty fit card in
every try. Criterion 2 returned no listings, traced an early stop before
`suggest_outfit`, and named keywords, size, and budget as things to change.
Criterion 4 selected the same $55 Mary Janes in every try; all five captions
included $55.00 and an outfit vibe consistent with the styling suggestion.
Criterion 5 returned only the $18 butterfly tee and $15 mesh top against an
$18 ceiling in every try, including the inclusive boundary.

Criterion 3 is marked FAIL for insufficient evidence, not an observed item
mismatch: the selected item is recorded, but `trace.py` abbreviates the tool's
input dictionary to its keys and never prints the `new_item` value. The run
therefore cannot demonstrate the 85% character-match check. Its original
4-of-5 target is preserved. Criterion 5 had no numerical target in
`criteria.md`; this table uses the 5-of-5 target supplied for the run log.

**Real output from one try for each criterion**

Source: [run_2026-10-11_2325_before.md](results/run_2026-10-11_2325_before.md), written by `run_eval.py::write_report` from `run_eval.py::run_once`. Each excerpt below is try 1 from the saved before run.

**Criterion 1 — try 1: matching query completes**

Query: `vintage graphic tee under $30`. Produced by `agent.py::run_agent`, calling `mcp_client.py::call_tool`, `tools.py::suggest_outfit`, and `tools.py::create_fit_card`; trace formatting/printing by `trace.py::step`.

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:

```
Here are two fun ways to style your butterfly baby tee!

**Outfit 1: Y2K Streetwear**
Pair the baby tee with the **baggy straight-leg jeans** and **chunky white sneakers**. Throw the **black cropped zip hoodie** over your shoulders and finish with the **black crossbody bag**.
*Why it works:* The fitted, ultra-femme crop of the tee balances out the slouchy, cool vibe of the baggy jeans and chunky sneakers for an effortless 2000s off-duty look.

**Outfit 2: Casual Grunge**
Tuck the baby tee into the **wide-leg khaki trousers**, cinched with the **brown leather belt**. Add the **black combat boots** and the **vintage black denim jacket** on top.
*Why it works:* The tough black boots and rugged denim jacket ground the sweet, pastel butterfly print, creating a cool contrast between edgy and playful elements.
```

Fit card:

```
I am completely obsessed with this dreamy little butterfly baby tee I just listed on Depop for $18.00! The pastel pink and purple print is giving major 2000s nostalgia, and it looks so cute tucked into wide-leg khaki trousers with chunky combat boots for that perfect edgy-meets-sweet vibe. Grab it before I change my mind and keep it for myself!
```

Trace:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: matches, continuing
[3] select_item
      in:  10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two fun ways to style your butterfly baby tee!  **Outfit 1: Y2K Streetwear** Pair the baby tee with t…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am completely obsessed with this dreamy little butterfly baby tee I just listed on Depop for $18.00! The pas…
```

**Criterion 2 — try 1: impossible query stops early**

Query: `intergalactic spacesuit size XXS under $1`. Produced by `agent.py::run_agent` (empty-search branch), after `mcp_client.py::call_tool`; trace formatting/printing by `trace.py::step`.

- stopped early: yes — No listings matched that search. Try broader keywords, a different size, or a higher budget.
- selected_item: (none)
- search_results: 0

Trace:

```
[1] parse_query
      in:  intergalactic spacesuit size XXS under $1
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping
```

**Criterion 3 — try 1: selected item reaches outfit suggestion**

Query: `corduroy wide-leg pants rust under $50`. Produced by `agent.py::run_agent` (item selection and handoff) and `tools.py::suggest_outfit`; trace formatting/printing by `trace.py::step`.

- stopped early: no
- selected_item: Corduroy Wide-Leg Pants — Rust ($32.0, depop)
- search_results: 3

Outfit suggestion:

```
Hey there! Those rust corduroy wide-leg pants are such a fun 70s find. Here is a cozy, earthy look you can pull right from your wardrobe:

Tuck the **white ribbed tank top** into the high-waisted rust cords to define your waist, and add the **brown leather belt** to tie in that warm vintage vibe. Throw the **oversized grey crewneck sweatshirt** on top for a relaxed, slouchy feel, and finish with your **chunky white sneakers** for a comfortable, modern contrast.

The soft grey and crisp white balance out the rich autumn tones of the pants, making it a super easy, stylish outfit for a casual day out!
```

Fit card:

```
Scoring these dreamy 70s-style rust corduroys on depop for just $32.00 honestly made my whole week. I love styling them with a tucked-in white tank, a slouchy grey crewneck, and chunky sneakers for the ultimate cozy, earthy vibe. It’s such an effortless look for running weekend errands while still feeling totally put-together.
```

Trace:

```
[1] parse_query
      in:  corduroy wide-leg pants rust under $50
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 3 items: Corduroy Wide-Leg Pants — Rust, Low-Rise Cargo Pants — Khaki, Wide-Leg Linen Trousers — Natural
      →    branch: matches, continuing
[3] select_item
      in:  3 items: Corduroy Wide-Leg Pants — Rust, Low-Rise Cargo Pants — Khaki, Wide-Leg Linen Trousers — Natural
      out: Corduroy Wide-Leg Pants — Rust ($32.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Hey there! Those rust corduroy wide-leg pants are such a fun 70s find. Here is a cozy, earthy look you can pul…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scoring these dreamy 70s-style rust corduroys on depop for just $32.00 honestly made my whole week. I love sty…
```

**Criterion 4 — try 1: repeated fit card includes price and outfit vibe**

Query: `mary janes under $60`. Produced by `tools.py::create_fit_card`, called by `agent.py::run_agent`; trace formatting/printing by `trace.py::step`.

- stopped early: no
- selected_item: Platform Mary Janes — Black Patent ($55.0, depop)
- search_results: 1

Outfit suggestion:

```
Here is a fun, Y2K-inspired outfit to rock your new platform Mary Janes!

Pair them with the **baggy straight-leg jeans** and the **white ribbed tank top**, then layer the **black cropped zip hoodie** on top. Finish the look with the **black crossbody bag**.

**Why it works:** The fitted white tank balances the volume of the baggy dark-wash jeans, while the cropped zip-hoodie plays into that effortless 90s streetwear vibe. The shiny black patent Mary Janes add a cool, edgy contrast to the casual denim, tying the whole black-and-white color palette together seamlessly. You look effortlessly chic and ready for the day!
```

Fit card:

```
I am still obsessing over these shiny patent Mary Janes I just scored on depop for $55.00! They add the ultimate edgy contrast when I style them with my favorite baggy jeans, a fitted white tank, and a cropped zip hoodie. It is giving major 90s streetwear energy and I am never taking them off.
```

Trace:

```
[1] parse_query
      in:  mary janes under $60
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 1 items: Platform Mary Janes — Black Patent
      →    branch: matches, continuing
[3] select_item
      in:  1 items: Platform Mary Janes — Black Patent
      out: Platform Mary Janes — Black Patent ($55.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here is a fun, Y2K-inspired outfit to rock your new platform Mary Janes!   Pair them with the **baggy straight…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still obsessing over these shiny patent Mary Janes I just scored on depop for $55.00! They add the ultima…
```

**Criterion 5 — try 1: search respects inclusive budget ceiling**

Query: `graphic tee under $18`. Produced by `tools.py::search_listings`, exposed by `mcp_server.py::search_listings` and called through `mcp_client.py::call_tool` in `agent.py::run_agent`; trace formatting/printing by `trace.py::step`.

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 2

Outfit suggestion:

```
Here are two fun, easy ways to style your new Y2K baby tee!

**Outfit 1: Streetwear Edge**
Pair the butterfly baby tee with the **baggy straight-leg jeans** and **chunky white sneakers**. Throw the **oversized grey crewneck sweatshirt** over your shoulders, and finish with the **black crossbody bag**.
*Why it works:* The fitted, girly tee balances the slouchy, cool shape of the baggy jeans for that classic Y2K skater vibe.

**Outfit 2: Casual Contrast**
Tuck the baby tee into the **wide-leg khaki trousers**, cinched with the **brown leather belt**. Add the **chunky white sneakers** and the **black crossbody bag**.
*Why it works:* The earthy khaki tones ground the playful pink and purple butterfly print, creating a cute, minimal look that feels effortless and modern.
```

Fit card:

```
I am still obsessed with the pastel butterfly print on this little Y2K tee I just scored on depop for $18.00. It is officially living in my daily rotation because it looks so good tucked into wide-leg khakis with a chunky belt for an effortless weekend vibe. When I want a more nostalgic skater look, I just swap the trousers for baggy denim and toss a slouchy grey crewneck over my shoulders.
```

Trace:

```
[1] parse_query
      in:  graphic tee under $18
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 2 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black
      →    branch: matches, continuing
[3] select_item
      in:  2 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two fun, easy ways to style your new Y2K baby tee!  **Outfit 1: Streetwear Edge** Pair the butterfly …
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I am still obsessed with the pastel butterfly print on this little Y2K tee I just scored on depop for $18.00. …
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Full three-tool run returns a fit card | 4 of 5 | MET (5/5) | All five tries completed search, outfit generation, and a non-empty fit card; five passes meet the four-pass target. |
| 2 | Empty search stops before tool 2 and names what to change | 5 of 5 | MET (5/5) | All five tries stopped after an empty MCP search, before suggest_outfit, and suggested changing keywords, size, or budget. |
| 3 | Item in session matches item passed on (at least 85% of characters) | 4 of 5 | MISSED (0/5 demonstrated) | None of the five traces exposes the passed new_item value, so none demonstrates the required comparison; zero verified passes do not meet the four-pass target. |
| 4 | Fit card mentions the item's price and outfit vibe | 5 of 5 | MET (5/5) | All five Mary Janes captions include $55.00 and the corresponding outfit vibe; every try meets the requirement. |
| 5 | Search returns nothing over the user's budget | 5 of 5 | MET (5/5) | Every try returned only the $18 butterfly tee and $15 mesh top under an inclusive $18 ceiling; all five pass the supplied target. |

**Diagnoses**

**Criterion 3 — session handoff to `suggest_outfit`:** The state criterion
missed with 0 of 5 demonstrated passes. In every try,
`agent.py::run_agent` stores the selected listing in
`session["selected_item"]` and passes it as `tool_inputs["new_item"]` to
`suggest_outfit`. However, `trace.py::step` formats that input through
`trace.py::_short`, which prints only the keys of a dictionary without a
top-level `title`. Because the listing is nested under `new_item`, the trace
prints `dict with keys: new_item, wardrobe` instead of the listing's identity
or title. `run_eval.py::write_report` records the selected item but does not
record the actual item received by the tool. This hides the second value
needed for the 85% character-match comparison in all five tries.

The failure is in observing the session handoff, rather than evidence that
the tool received a different item. Record the selected item's ID/title and
the ID/title received at the entry to `tools.py::suggest_outfit`, then compare
the titles against the original threshold. The branch and model output cannot
establish that comparison on their own.

**Pattern:** All five unverified tries belong to criterion 3 and lose the same
`new_item` value at the same trace-formatting step. This is one recurring
observability problem in the session handoff, so the fix should record the
actual tool input once rather than add five separate fixes or change the
styling prompt. The other four criteria met their targets in this run.

Passing those four does not establish that the targets are demanding. Criterion
1 only requires completion, and some of its captions describe the user as a
seller ("I just listed" or "my depop shop") even though the user is finding
an item to buy. I would tighten criterion 4 in a future evaluation to require
buyer-perspective captions with no invented ownership or selling claims, in
addition to the correct price and outfit vibe. That would expose a model-output
pattern the current targets allow. The original targets and before-run scores
remain unchanged.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```text
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: matches, continuing
[3] select_item
      in:  10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here is a fun, Y2K-inspired outfit using your thrift find!   **Streetwear Contrast:** Pair the butterfly baby …
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: I couldn't resist grabbing this pastel butterfly baby tee when I spotted it on Depop for just $18.00! To lean …
```

**Empty search**

```text
$ python app.py ask 'intergalactic spacesuit size XXS under $1' --trace
[1] parse_query
      in:  intergalactic spacesuit size XXS under $1
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

`agent.py::run_agent` now sends `description`, `size`, and `max_price` as an
arguments dictionary to `mcp_client.call_tool("search_listings", ...)` rather
than calling `tools.search_listings` directly. `mcp_server.py::search_listings`
receives those values and forwards them to the original implementation. The
MCP response is unwrapped back into the same list of listing dictionaries.

The behavior did not change: direct and MCP calls returned identical ordered
results for a matching query, a size-filtered query, and an empty query. The
end-to-end query selected the same $18 butterfly tee as before. In this
execution environment, the sandboxed stdio connection stalled; the same MCP
call succeeded when run outside that sandbox.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Updated `trace.py::_short` so an input dictionary holding
`new_item` now prints the item title, price, platform, and wardrobe item count.
For example, the `suggest_outfit` trace now records `new_item: Corduroy
Wide-Leg Pants — Rust ($32.0, depop)` instead of only `dict with keys:
new_item, wardrobe`.

**Which failure it was meant to fix:** Criterion 3 missed because its five
before-run traces could not show that `session["selected_item"]` was the same
listing passed into `suggest_outfit`. The change preserves concise traces while
making that session handoff observable and scoreable.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 and names what to change | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on (at least 85% of characters) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's price and outfit vibe | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search returns nothing over the user's budget | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Run: `python run_eval.py --label after`, five tries per scenario with caching
off. Full output is saved in
[the after evaluator report](results/run_2026-10-11_2352_after.md).

The selected `Corduroy Wide-Leg Pants — Rust ($32.0, depop)` appears both in
the `select_item` output and in the `suggest_outfit` input on every criterion
3 try. That is an exact title match, which exceeds the original 85%
character-match threshold. The other four criteria retained their before-run
scores: 5/5 each.

| Criterion | Before | After | Change |
|---|---|---|---|
| 1. Full three-tool run | MET (5/5) | MET (5/5) | No change |
| 2. Empty search branch | MET (5/5) | MET (5/5) | No change |
| 3. Session handoff | MISSED (0/5 demonstrated) | MET (5/5) | Trace now shows the passed item |
| 4. Fit card price and vibe | MET (5/5) | MET (5/5) | No change |
| 5. Budget ceiling | MET (5/5) | MET (5/5) | No change |

**Did it help, and how do I know:** Yes. Before the change, each criterion 3
trace reported only `dict with keys: new_item, wardrobe`, so the selected item
could not be compared with the item passed to `suggest_outfit`; the criterion
was therefore MISSED at 0/5 demonstrated. After the one trace-formatting
change, all five traces print both values and show the same Corduroy Wide-Leg
Pants listing. Criterion 3 changed from MISSED (0/5 demonstrated) to MET
(5/5), while the other criterion scores stayed the same.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

No acceptance criterion is still missed after the trace improvement. Criterion
3 now has five observable handoffs, each with matching selected and passed item
titles. A remaining quality concern is outside the current criteria: some model
fit cards describe the user as a seller (for example, "I just listed") even
though FitFindr helps them find an item to buy. I stopped here because the
measured improvement was the missing handoff evidence. A later criterion could
require buyer-perspective captions and drive a prompt change for that issue.

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

**The System**

FitFindr (units 3–4): the thrift-search agent in `agent.py::run_agent`, served over HTTP by `serve.py`.

**The Shape**

Shape C: extend one capability. FitFindr can now take **photos as input**. A single vision path (`generate.py::generate` with `images=`) gets two prompts. One turns a photo of clothes into wardrobe items in the existing `data/wardrobe_schema.json` format (`tools.py::scan_wardrobe`). The other turns a full-body photo into a color profile: undertone, contrast, hair and eye color, flattering colors (`tools.py::analyze_profile`). Both feed a new styling tool, `tools.py::outfit_for_occasion`, which builds an outfit for an occasion using only clothes the user owns. It is served from `serve.py` alongside a single-page demo at `/`. Each browser gets an anonymous ID, and that browser's photos, wardrobe and profile are stored in Postgres (`db.py`), so several people can use the deployed app at once. It is deployed on Render, and every request writes a structured log line.

**Out of Scope**

- **No monorepo, no separate frontend app.** The demo is one static HTML page served by the existing Flask app. Rebuilding the interface would be a new project.
- **No RAG / vector store.** A personal wardrobe (under about 100 items) fits in the prompt, so retrieval adds no value at this size.
- **No accounts or login.** Each browser gets a random ID, and everything it stores is keyed to that ID. That's enough to keep users apart for a demo. It is not real security: whoever has the ID has the data.
- **No separate file storage.** Photos are stored in Postgres, compressed in the browser first (about 1600 px WebP plus a 320 px thumbnail). At this size that's simpler than running a second service; a bucket would be the next step.
- **No body-shape analysis.** The profile covers coloring only, and the user can edit every field.
- The original `/ask` thrift loop is unchanged.

**Instrumentation**

Every request to `serve.py` writes one JSON line, success or failure, to stdout (Render's log view) and to `logs/runs.jsonl` (see RUNNING.md, "The log", for every field). The wrapper is `serve.py::logged`. It times the request, takes the token counts the model service reports and subtracts the before and after values, and turns any exception into a status code plus an `error` field, so a failed run leaves a record instead of a gap.

The entries below come from the **clean-clone test**: a fresh `git clone` of this branch into an empty folder, set up from RUNNING.md alone, started under `gunicorn serve:app --workers 1 --timeout 120` (the same command as Render) with the cache off. The first nine are three full runs of the measurement below (scan → profile → outfit). The `outfit` text and the item-name lists are shortened here; nothing else is edited.

```jsonl
{"ts": "2026-11-16T17:33:56.009+00:00", "route": "/wardrobe/scan", "user": null, "status": 200, "duration_ms": 3438, "input": {"bytes": 96147, "filename": "closet1.jpg", "mime": "image/jpeg"}, "output": {"items": 11, "categories": ["tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "outerwear"], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1227, "output_tokens": 767, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:33:57.799+00:00", "route": "/profile/analyze", "user": null, "status": 200, "duration_ms": 1789, "input": {"bytes": 208410, "filename": "person1.jpg", "mime": "image/jpeg"}, "output": {"undertone": "warm", "contrast": "medium", "hair_color": "dark brown"}, "model_calls": 1, "prompt_tokens": 1247, "output_tokens": 124, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:33:59.190+00:00", "route": "/outfit", "user": null, "status": 200, "duration_ms": 1389, "input": {"occasion": "job interview at a design studio", "wardrobe_items": 11, "has_profile": true}, "output": {"outfit": "Hello! For your design studio interview, let's keep it sharp…", "owned_items_named": 2}, "model_calls": 1, "prompt_tokens": 362, "output_tokens": 127, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:34:54.822+00:00", "route": "/wardrobe/scan", "user": null, "status": 200, "duration_ms": 37886, "input": {"bytes": 208410, "filename": "person1.jpg", "mime": "image/jpeg"}, "output": {"items": 3, "categories": ["tops", "bottoms", "shoes"], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1239, "output_tokens": 276, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:34:57.313+00:00", "route": "/profile/analyze", "user": null, "status": 200, "duration_ms": 2490, "input": {"bytes": 208410, "filename": "person1.jpg", "mime": "image/jpeg"}, "output": {"undertone": "warm", "contrast": "high", "hair_color": "dark brown"}, "model_calls": 1, "prompt_tokens": 1247, "output_tokens": 122, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:34:59.158+00:00", "route": "/outfit", "user": null, "status": 200, "duration_ms": 1844, "input": {"occasion": "job interview at a design studio", "wardrobe_items": 3, "has_profile": true}, "output": {"outfit": "Here is a chic, creative outfit for your design studio inter…", "owned_items_named": 3}, "model_calls": 1, "prompt_tokens": 232, "output_tokens": 123, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:35:02.156+00:00", "route": "/wardrobe/scan", "user": null, "status": 200, "duration_ms": 2996, "input": {"bytes": 96147, "filename": "closet1.jpg", "mime": "image/jpeg"}, "output": {"items": 13, "categories": ["tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "bottoms"], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1227, "output_tokens": 948, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:35:03.435+00:00", "route": "/profile/analyze", "user": null, "status": 200, "duration_ms": 1278, "input": {"bytes": 208410, "filename": "person1.jpg", "mime": "image/jpeg"}, "output": {"undertone": "warm", "contrast": "high", "hair_color": "dark brown"}, "model_calls": 1, "prompt_tokens": 1247, "output_tokens": 125, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:35:04.456+00:00", "route": "/outfit", "user": null, "status": 200, "duration_ms": 1019, "input": {"occasion": "rainy day errands", "wardrobe_items": 13, "has_profile": true}, "output": {"outfit": "Hey there! For your rainy day errands, let’s keep you comfor…", "owned_items_named": 2}, "model_calls": 1, "prompt_tokens": 406, "output_tokens": 142, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-16T17:35:05.732+00:00", "route": "/wardrobe/scan", "user": null, "status": 200, "duration_ms": 1275, "input": {"bytes": 106159, "filename": "closet2.jpg", "mime": "image/jpeg"}, "output": {"items": 4, "categories": ["tops", "tops", "tops", "tops"], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1227, "output_tokens": 332, "model": "gemini-3.5-flash-lite", "error": null}
```

Failed runs, sent on purpose to the same server right after:

```jsonl
{"ts": "2026-11-16T17:35:25.198+00:00", "route": "/wardrobe/scan", "user": null, "status": 400, "duration_ms": 0, "input": {"bytes": 12, "filename": "notimage.txt", "mime": null}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "That file isn't a JPEG, PNG, WebP or HEIC image."}
{"ts": "2026-11-16T17:35:54.531+00:00", "route": "/wardrobe/scan", "user": null, "status": 422, "duration_ms": 29328, "input": {"bytes": 2000, "filename": "truncated.jpg", "mime": "image/jpeg"}, "output": {"items": 0, "categories": [], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1227, "output_tokens": 22, "model": "gemini-3.5-flash-lite", "error": "The image is heavily obscured and lacks any clearly visible clothing items."}
{"ts": "2026-11-16T17:35:57.262+00:00", "route": "/profile/analyze", "user": null, "status": 422, "duration_ms": 2725, "input": {"bytes": 96147, "filename": "closet1.jpg", "mime": "image/jpeg"}, "output": {}, "model_calls": 1, "prompt_tokens": 1235, "output_tokens": 71, "model": "gemini-3.5-flash-lite", "error": "Expected exactly one person in the photo, found 0."}
{"ts": "2026-11-16T17:35:57.267+00:00", "route": "/outfit", "user": null, "status": 400, "duration_ms": 0, "input": {"occasion": "", "wardrobe_items": 10, "has_profile": false}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Send JSON with an 'occasion' field, e.g. {\"occasion\": \"outdoor summer wedding\"}"}
```

What the log already shows, worth coming back to in Milestone 5:

- **Same photo, different answers.** `person1.jpg` got `contrast: "medium"` in one run and `"high"` in the next two. `closet1.jpg` scanned as 11 items one time and 13 the next, and the last item was `outerwear` one time and `bottoms` the next. Temperature is 0.2, not 0.
- **A broken file still costs a model call.** A JPEG cut off after 2,000 bytes passed the magic-byte check, went to the model, and was billed 1,227 prompt tokens before coming back as 422. The text file was stopped before any call (`model_calls: 0`).
- **The 37.9 s and 29.3 s entries are the rate limiter, not the model.** `generate.py` holds to 15 requests a minute, and the server printed `[rate limit] 15 requests used this minute. Waiting 36s.` The token counts on those lines are normal.

**From the deployed service.** These lines were copied from Render's log view for <https://fitfindr-vr9s.onrender.com/> on 2026-11-17. They show one full run, a rejected file, a photo with no person in it, and the per-IP rate limiter refusing requests (429). Only the scan's `names` list is cut, to keep the line short.

```jsonl
{"ts": "2026-11-17T05:14:04.934+00:00", "route": "/wardrobe/scan", "user": null, "client": "14b8d63d", "status": 200, "duration_ms": 3677, "input": {"bytes": 96147, "filename": "closet1.jpg", "mime": "image/jpeg"}, "output": {"items": 12, "categories": ["tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "tops", "outerwear", "bottoms"], "dropped": 0}, "model_calls": 1, "prompt_tokens": 1227, "output_tokens": 862, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-17T05:14:08.108+00:00", "route": "/profile/analyze", "user": null, "client": "14b8d63d", "status": 200, "duration_ms": 2871, "input": {"bytes": 208410, "filename": "person1.jpg", "mime": "image/jpeg"}, "output": {"undertone": "warm", "contrast": "high", "hair_color": "dark brown"}, "model_calls": 1, "prompt_tokens": 1247, "output_tokens": 124, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-17T05:14:09.432+00:00", "route": "/outfit", "user": null, "client": "148fdc1b", "status": 200, "duration_ms": 1191, "input": {"occasion": "job interview at a design studio", "wardrobe_items": 12, "has_profile": true}, "output": {"outfit": "Hi there! For your design studio interview, we want to look creative yet professional. \n\nPair the **Brown t-shirt** with", "owned_items_named": 3}, "model_calls": 1, "prompt_tokens": 394, "output_tokens": 125, "model": "gemini-3.5-flash-lite", "error": null}
{"ts": "2026-11-17T05:14:09.566+00:00", "route": "/wardrobe/scan", "user": null, "client": "148fdc1b", "status": 400, "duration_ms": 3, "input": {"bytes": 12, "filename": "notimage.txt", "mime": null}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "That file isn't a JPEG, PNG, WebP or HEIC image."}
{"ts": "2026-11-17T05:14:10.964+00:00", "route": "/profile/analyze", "user": null, "client": "148fdc1b", "status": 422, "duration_ms": 1220, "input": {"bytes": 96147, "filename": "closet1.jpg", "mime": "image/jpeg"}, "output": {}, "model_calls": 1, "prompt_tokens": 1235, "output_tokens": 112, "model": "gemini-3.5-flash-lite", "error": "Expected exactly one person in the photo, found 0."}
{"ts": "2026-11-17T05:14:45.137+00:00", "route": "/outfit", "user": null, "client": "148fdc1b", "status": 400, "duration_ms": 1, "input": {"occasion": "", "wardrobe_items": 10, "has_profile": false}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Send JSON with an 'occasion' field, e.g. {\"occasion\": \"outdoor summer wedding\"}"}
{"ts": "2026-11-17T05:14:45.300+00:00", "route": "/outfit", "user": null, "client": "148fdc1b", "status": 429, "duration_ms": 0, "input": {}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Too many requests from your connection. Try again in 23 seconds."}
{"ts": "2026-11-17T05:14:45.470+00:00", "route": "/outfit", "user": null, "client": "14b8d63d", "status": 400, "duration_ms": 0, "input": {"occasion": "", "wardrobe_items": 10, "has_profile": false}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Send JSON with an 'occasion' field, e.g. {\"occasion\": \"outdoor summer wedding\"}"}
{"ts": "2026-11-17T05:14:45.656+00:00", "route": "/outfit", "user": null, "client": "f8454015", "status": 400, "duration_ms": 0, "input": {"occasion": "", "wardrobe_items": 10, "has_profile": false}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Send JSON with an 'occasion' field, e.g. {\"occasion\": \"outdoor summer wedding\"}"}
{"ts": "2026-11-17T05:14:45.772+00:00", "route": "/outfit", "user": null, "client": "148fdc1b", "status": 429, "duration_ms": 0, "input": {}, "output": {}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "error": "Too many requests from your connection. Try again in 23 seconds."}
```

**What these lines caught: the rate limiter was counting Render's load balancers, not visitors.** Every request above came from one machine, yet the log shows three `client` values. Each one is the hash of one of Render's internal load balancers: `14b8d63d` = 10.26.70.248, `148fdc1b` = 10.28.24.5 and `f8454015` = 10.31.224.135, the addresses gunicorn's access log printed next to each request. Requests rotate between them, so each visitor got about three times the limit, and all visitors shared the same three counts. You can see it in the burst: 429s came only through `148fdc1b`, while requests through the other two in the same second still got 400. Locally there is no proxy, so the test client couldn't show this. The first version used `werkzeug`'s `ProxyFix` with `X-Forwarded-For`, which was wrong in two ways: it still saw the balancers, and Render's proxy adds to an `X-Forwarded-For` the caller sent instead of replacing it, so a caller could fake their address. The fix keys on Cloudflare's `CF-Connecting-IP`, which Cloudflare overwrites on every request (`serve.py::_client_ip`).

**What It Costs**

**$0.0027 per run** at paid Standard rates, about 370 full runs per dollar. One run is **2,774 prompt + 743 output tokens** (mean of 10), in **3 model calls**. On a free-tier key the bill is $0, and what runs out first is the rate limit, not money.

How it was measured:

- **One run** = the full flow for a new user: `POST /wardrobe/scan` (a clothes photo) → `POST /profile/analyze` (one full-body person) → `POST /outfit` (an occasion, plus the wardrobe and profile the first two calls returned). It is scripted in [`measure_cost.py`](measure_cost.py), so it can be run again.
- **Tokens** are the counts the Gemini API reports for each response (`usage_metadata`). `serve.py` writes them into each log line, and the script sums the lines each run added. They come from the API, not from estimating.
- **Cache off** (`AI201_CACHE=0`). Otherwise runs 2–10 would be cache hits costing 0 tokens.
- **Setup:** the clean-clone install, gunicorn with 1 worker, `gemini-3.5-flash-lite`, 2026-11-16. Photos: two clothes-rack photos and one full-body photo (free Unsplash images, kept out of the repo), rotated across runs. Occasions rotated across five.
- **Dollars** = mean tokens × [Google's published Standard rate](https://ai.google.dev/gemini-api/docs/pricing) for this model: $0.30 per 1M input tokens (image input included), $2.50 per 1M output tokens. 2,774 × $0.30/1M + 743 × $2.50/1M = $0.00083 + $0.00186 = **$0.0027**. The tokens are measured; only the price per token comes from the pricing page.

| | mean | min | max |
|---|---|---|---|
| Prompt tokens | 2,774 | 2,713 | 2,880 |
| Output tokens | 743 | 486 | 1,215 |
| Model calls | 3 | 3 | 3 |
| Server time per run | 8.5 s | 3.7 s | 42.2 s |

The server time is skewed by one run: run 6 waited 36 s on the rate limiter. The **median is 4.9 s**, and that's the more honest "how long does it take" number. Output tokens vary the most, and they follow the item count: a scan that finds 13 items writes about three times as much as one that finds 3. Since output costs 8× more than input, **busy closet photos cost the most**. The image itself is a nearly fixed ~1,200 prompt tokens whatever its size (96 KB and 208 KB photos cost almost the same).
