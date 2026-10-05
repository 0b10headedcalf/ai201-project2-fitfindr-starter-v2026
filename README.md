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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

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
