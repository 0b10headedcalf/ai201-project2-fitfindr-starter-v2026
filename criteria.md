# Capstone acceptance criteria — FitFindr photo input

These five criteria cover the extension: photos become wardrobe entries and a
color profile, which feed occasion-based outfits. Earlier units' criteria are
preserved verbatim in [criteria-unit3.md](criteria-unit3.md).

**Order of work:** No system runs or evaluation results were generated while
writing this file. Earlier unit results already exist in `results/`, and the
README contains capstone deployment and cost measurements. These criteria
precede the next capstone acceptance evaluation, not all historical measurements.
Commit this file before that evaluation, then commit its first results separately
with a message naming capstone results.

**Evaluation setup:** Before any new model calls, freeze the photos and manual
labels in `eval_photos/labels.json`, recording a SHA-256 for each image. Use five
clothes photos, each showing 3–10 distinct, unobscured items, and three daylight
photos each containing exactly one person. Label each visible garment, shoe
pair, or accessory once using `tops`, `bottoms`, `outerwear`, `shoes`, or
`accessories`; a pair of shoes counts as one item. Do not replace photos or
labels after seeing predictions. Disable the model cache (`AI201_CACHE=0`).
Record model, configuration, raw responses, and request durations. Run five
sequential trials per case. Pace requests below configured rate limits;
unexpected rejections still count as failures. Missing fixtures or responses
mean incomplete evidence, never a pass.

## 1. Clothes photos produce usable wardrobe entries (extension)

For each of the five clothes photos posted to `/wardrobe/scan`, at least 4 of
5 trials must return HTTP 200, category precision and recall both at least
80%, and a nonempty `items` array whose entries each have a unique nonempty
string `id`, a nonempty string `name`, an allowed category, and `colors` and
`style_tags` arrays containing only strings. For each category, match at most
the smaller of its labeled and predicted item counts; precision is total
matches / total predictions, and recall is total matches / total labels.
Zero predictions fail. Every photo must meet the 4-of-5 target separately.

**Why this target:** Invalid fields can break the downstream outfit tool, so
every entry must satisfy the schema in a passing response. Precision penalizes
extra items and recall penalizes omissions. An 80% threshold allows limited
vision mistakes a user can edit in a crowded photo; a lower threshold leaves
too much manual correction. Four successes allow one stochastic lapse, whereas
five would require perfect repetition. This measures category counts, not
item identity or color accuracy.

## 2. A repeated person photo gives a stable color profile (extension)

For each of the three one-person photos posted to `/profile/analyze`, all
5 trials must return HTTP 200 with `undertone` in `warm`, `cool`, `neutral`
and `contrast` in `low`, `medium`, `high`. For each photo separately, the
same `(undertone, contrast)` pair must occur in at least 4 of its 5 responses.

**Why this target:** Both fields guide clothing colors, so changes on repeat
uploads can produce conflicting advice. Four identical pairs allow one outlier;
three would allow nearly half the answers to disagree. Unanimity is stricter
than needed for an editable profile. Valid enums in every response are an
interface requirement. Consistency does not establish that a person's coloring
was analyzed correctly; this criterion makes no color-accuracy claim.

## 3. Occasion outfits use the supplied wardrobe (extension)

Post to `/outfit` with `example_wardrobe` from `data/wardrobe_schema.json`,
`outfit_profile` from `eval_photos/labels.example.json`, and each of these
occasions: `job interview at a design studio`, `outdoor summer wedding`,
`rainy day errands`, `first date at a jazz bar`, and `casual Friday at the office`.
For each occasion, at least 4 of 5 trials must return HTTP 200 and a nonempty
`outfit` string of at most 170 whitespace-separated words naming at least two
distinct wardrobe items by their exact case-sensitive names. `items_used` must
equal the set of those names present in the text, with no duplicates. Every
recommended garment, shoe, or accessory must appear as an exact wardrobe name
enclosed in `**`; any other bold span or additional garment, shoe, or accessory
recommendation outside those spans fails the trial. Styling actions such as
tucking or rolling sleeves do not count as additional items.

**Why this target:** Invented pieces make an owned-clothes outfit unusable
without shopping. Exact names make ownership and the response's item list
checkable, and two items require a combination. The existing prompt asks for
fewer than 170 words; this ceiling keeps the result readable on the demo page.
Four successes per occasion allow one prose-generation lapse without letting
an easy occasion hide repeated failures on another. Requiring all 25 responses
to pass would allow no variation in generated prose.

## 4. Invalid uploads return errors without storing data (extension, bad path)

Repeat each of these cases 5 times with a fresh valid `X-User-Id` UUID per
request. Every case must meet its expected status in 5 of 5 trials and return
JSON with a nonempty string `error`: multipart uploads (field `image`) to
`/wardrobe/scan` of an empty file (400), the bytes `definitely not an image`
named `text-file.txt` (400), a 9 MiB file consisting of JPEG magic bytes
`FF D8 FF` followed by zero bytes (413), and a valid solid-white 64×64 PNG
(422); upload that same PNG to `/profile/analyze` (422). After each request,
`GET /me` with that UUID must return HTTP 200 with empty `photos` and
`wardrobe.items` arrays and a null `profile`. The first three cases must also
log `model_calls: 0` for the rejected request.

**Why this target:** Bad uploads must not become saved wardrobe entries or
profiles, and obviously invalid bytes must not consume paid model calls.
Five of five is required because accepting even one violates that boundary;
a lower rate would excuse persistent bad data. Blank images require vision
to identify their content, so zero model calls applies only to the three
cases rejectable before inference. No requirement stricter than complete
rejection is needed for these cases.

## 5. The warm deployed photo flow completes within 30 seconds (extension)

On the deployed service, first receive HTTP 200 from `/health`, then run
five sequential flows, each starting within 60 seconds of a successful health
check. Each flow posts the first frozen clothes photo to `/wardrobe/scan`,
posts the first frozen person photo to `/profile/analyze`, then passes those
responses as `wardrobe` and `profile` to `/outfit` with occasion
`casual Friday at the office`. At least 4 of 5 flows must return HTTP 200 for
all three requests with their summed client-observed durations at most
30 seconds. Measure each request from immediately before sending until the
entire response body is received; include upload, network, server queueing,
and retry time, but exclude deliberate pauses between requests. An error,
timeout, or missing response fails the flow. Disable the cache on the deployed
server as well as the evaluator.

**Why this target:** A user waits through three model calls before seeing an
outfit. Thirty seconds bounds the complete interaction on the small hosted
service, including network overhead; a much shorter limit leaves little room
for uploads and inference, while a longer one makes the demo difficult to use.
Four successes permit one transient delay but require most attempts to finish
within the bound. Cold starts are excluded explicitly because waking the free
host is a different wait from generating an outfit on an awake service.

## Criteria self-check — document review before execution

Review prompt: For each criterion, how exactly would you test it using only
the sentence itself, would two people score it the same way, and what would
have to happen for it to fail? Do not rewrite it.

This is a self-review of the written criteria, not a Claude review or a record
of system test outcomes.

| Criterion | How to test from the text | Would two people agree? | What makes it fail? |
|---|---|---|---|
| 1 | Upload each labeled photo five times; validate fields and compute the defined category-count precision and recall. | Yes, using frozen labels and the explicit formulas and per-photo aggregation. | Any photo has fewer than four trials satisfying status, both 80% thresholds, and every schema check. |
| 2 | Analyze each person photo five times; validate enums and count identical field pairs per photo. | Yes; compare literal pairs without judging color accuracy. | Any invalid enum or non-200, or any photo with no pair occurring at least four times. |
| 3 | Send the fixed wardrobe/profile for the five named occasions five times each; count words, exact names, bold spans, and compare name sets. | The counts are mechanical; reviewers must also inspect prose for additional recommended pieces using the stated garment/action distinction. | Any occasion has fewer than four trials meeting every condition, including no extra recommended piece. |
| 4 | Send each specified upload five times under fresh IDs; inspect status, error, matching log entry, and `/me` state. | Yes; statuses, bytes, call counts, and empty state are explicit. | Any wrong status, empty error, saved object, failed state check, or forbidden model call. |
| 5 | Warm the deployed host; use a monotonic client clock to time the five specified three-request flows and sum durations. | Yes; warm conditions, cache state, timing boundaries, and error treatment are explicit. | Fewer than four flows return three HTTP 200 responses within 30 seconds. |

The self-check identifies limits: category counts cannot prove item identity;
stable profiles cannot prove color accuracy; outfit prose needs a human check
as well as exact-name matching. The existing `capstone_eval.py` does not enforce
all these criteria: its default is three trials, its outfit-name heuristic is
looser, and its latency summary is per request. The next evaluation must use
five trials and score raw responses against this file rather than treating
those summaries as automatic acceptance verdicts.
