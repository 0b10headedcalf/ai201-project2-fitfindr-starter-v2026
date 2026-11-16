# Running FitFindr

Everything about how the starter works and how to use it.

---

## Before your first class

Setup happens **before class**. The [environment setup page](../pages/ide_setup)
has the per-operating-system commands and the exact versions.

**Same API key you set up in unit 1.** Nothing new to sign up for. There is one
new package — the MCP SDK, for unit 4 — and it installs with everything else.

From inside this repo after you've forked and cloned it:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your key into .env
python test.py
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env         # then paste your key into .env
python test.py
```

**You're ready when `python test.py` passes.**

If it doesn't and you've made one honest attempt at the error, post the
**whole** output in the help channel.

> Activate the virtual environment every time you open a new terminal. You
> should see `(.venv)` at the start of your prompt.

---

## Your first five minutes

Start with the data. Your tools will only be as good as your understanding of
what they're reading, and ten minutes here saves an hour of confused debugging.

```bash
python app.py fields                    # what a listing and a wardrobe item hold
python app.py listings --full -n 6      # read six listings all the way through
python app.py examples                  # queries worth trying
python app.py ask 'vintage graphic tee under $30'
```

> **Quote your queries with single quotes**, on every operating system. In
> PowerShell, `"vintage graphic tee under $30"` in double quotes silently
> becomes `vintage graphic tee under ` — PowerShell reads `$30` as a variable
> and substitutes nothing. You get results with no price ceiling and no error
> saying so. Single quotes are literal in PowerShell, bash and zsh alike.

That last one runs the loop. All three tools are stubs, so it will tell you the
loop isn't built yet. **That's the correct starting position** — it runs, and it
does nothing.

---

## Every command

| Command | What it does |
|---|---|
| `python test.py` | Checks your environment. Run it whenever something feels off |
| `python app.py fields` | The fields a listing and a wardrobe item have — **Milestone 1** |
| `python app.py listings` | Browse the data. `--full` for whole records, `-n` for how many |
| `python app.py examples` | Queries worth trying, including one that matches nothing |
| `python app.py ask '...'` | Run the agent on one query — **single quotes** |
| `python app.py ask` | Keep asking until you press Enter on an empty line |
| `python agent.py` | Runs both example paths — one that matches, one that can't |
| `python mcp_server.py` | Starts your MCP server — **unit 4** |
| `python mcp_client.py` | Asks the server what it offers — **unit 4** |
| `python run_eval.py --label before` | Runs every scenario five times and writes the run log — **unit 4** |
| `python serve.py` | Serves the agent over HTTP instead of exiting — **unit 9** |

Useful flags on `ask`:

| Flag | What it does |
|---|---|
| `--trace` | Print the loop step by step, once you've added the trace calls |
| `--empty-wardrobe` | Run as a user with nothing saved — one of unit 4's failure modes |

---

## Which command goes with which milestone

### Unit 3 — the build

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Read the data, run the starter | `app.py fields`, `app.py listings --full`, `app.py ask` |
| 2 | Spec your three tools | README, **Tool Inventory** |
| 3 | Write your acceptance criteria | `criteria.md` |
| 4 | Build the three tools | `tools.py`, tested one at a time from a terminal |
| 5 | Wire the loop and the state | `agent.py::run_agent` |
| 6 | Write it up | README |

### Unit 4 — the test

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Move one tool onto MCP | `mcp_server.py`, then `mcp_client.call_tool` in `run_agent` |
| 2 | Break it on purpose, then trace it | `trace.py`, `app.py ask --trace` |
| 3 | Run your test | `scenarios.py`, then `run_eval.py --label before` |
| 4 | Call each criterion, diagnose the misses | README |
| 5 | Fix one thing and re-run | `run_eval.py --label after` |
| 6 | Say what's still broken | README |

---

## Running it somewhere else — **unit 9**

Everything above exits when the command finishes. A host has nothing to keep
running, so before you can deploy this you need something that stays up.
`serve.py` is that: the same `run_agent()`, behind two HTTP routes.

On your machine:

```bash
python serve.py
curl -X POST http://localhost:5000/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
```

On a host, the start command is:

```bash
gunicorn serve:app
```

| Thing | What it means |
|---|---|
| `PORT` | The host tells your app which port to listen on by setting this. Both `serve.py` and `gunicorn` read it, and `serve.py` falls back to `5000` on your machine. Don't hard-code a port |
| `POST /ask` | `{"query": "...", "wardrobe": {...}}` — wardrobe optional. Returns the session dict, `error` and all |
| `GET /health` | Says `ok` if the app is awake |
| It answers one request at a time | On purpose. A second request waits for the first to finish, and prints `[serve] another request is still running` while it waits. An MCP tool call starts a whole second Python process, and the free tier's 512 MB has no room for two of those at once — and `generate.py`'s rate-limit counting assumes one caller. The reasoning is written out in `serve.py` |
| `gunicorn serve:app`, exactly | Not `-k gevent`, not `-k eventlet`, not wrapped for uvicorn. `mcp_client.call_tool` uses `asyncio.run()`, which won't start inside a running event loop, so an async worker breaks **every** MCP call — and only once you've deployed it |
| The first request is slow | The free tier puts your app to sleep after about fifteen minutes of nothing. The next request wakes it up and waits for it — around a minute. Not a bug, and worth knowing before you demo it |

`serve.py` ships with **no logging and no timing in it**, on purpose. You add
that yourself in the follow-along, before you deploy — instrumenting first is
the point of the session.

---

## Capstone — photo input, deployed

### Hosted (Path A)

- **URL:** `https://<your-service>.onrender.com` ← fill in after the first deploy
- **Platform:** Render, free web service (512 MB, sleeps after ~15 min idle)
- **Config:** [`render.yaml`](render.yaml)
  - build: `pip install -r requirements.txt`
  - start: `gunicorn serve:app --workers 1 --timeout 120`

How it got there:

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, pick the repo. Render reads `render.yaml`.
3. When it asks, paste your key into `GEMINI_API_KEY`, and a Postgres connection string into `DATABASE_URL`. A free [Neon](https://neon.tech) database works: create a project, then copy the connection string from the dashboard. Both are secrets and never go in the repo. Tables are created on the first request.
4. Wait for "Live", then open the URL. `GET /health` should say `ok`.

The first request after a quiet period takes about a minute while the service wakes up. Latency numbers in the README say whether they are **warm** (the service already answered within the last few minutes) or **cold**.

### Local (the same app, one command)

From a clean checkout:

```bash
git clone -b capstone https://github.com/0b10headedcalf/ai201-project2-fitfindr-starter-v2026.git
cd ai201-project2-fitfindr-starter-v2026
python3 --version               # must say 3.11, 3.12 or 3.13 — see below if it says 3.14
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # paste GEMINI_API_KEY
python test.py                  # every line PASS before you go on
python serve.py                 # → http://localhost:5000
```

> **Check the Python version first.** The clean-clone test of these steps failed here the first time. The repo's `.python-version` asks pyenv for `3.13`. On a machine where pyenv doesn't have 3.13 installed, `python3` silently fell back to the system's **3.14**, and `pip install` completed without an error. Only `test.py` caught it afterwards. If `python3 --version` says 3.14, build the venv with a supported version directly, e.g. `python3.13 -m venv .venv`, or `PYENV_VERSION=3.12.13 python3 -m venv .venv` with pyenv, or `uv venv -p 3.13`.

Open `http://localhost:5000` for the demo page. To run it the way Render does: `python -m gunicorn serve:app --workers 1 --timeout 120`.

### Local emulation of the deployed setup (Docker)

```bash
docker compose up --build       # → http://localhost:10000
docker compose logs -f app      # the structured log, as Render's log view shows it
docker compose down             # stop; data is kept (add -v to wipe the database)
```

`docker-compose.yml` runs two containers:

- **app:** the same Python (3.13.1), the same `pip install -r requirements.txt` and the same gunicorn start command as `render.yaml`, limited to Render's free-tier **512 MB and 0.1 CPU**.
- **db:** Postgres 16, standing in for Neon, connected through `DATABASE_URL`.

The log file is mounted to `./logs/runs.jsonl`. Render itself doesn't use the Dockerfile; it's only here so the local run matches the hosted one.

Measured locally (2026-11-14):

| Measurement | Result |
|---|---|
| Startup to first `/health` | ~2 s |
| Idle memory | ~37 MB |
| Peak memory during `/ask` (MCP starts a second process) | ~96 MB |
| `/outfit` | 6.5 s |
| `/ask` | 5.1 s |

The timings were taken under the 0.1 CPU limit.

### Environment

| | |
|---|---|
| Python | 3.11, 3.12 or 3.13 (Render: 3.13.1). **Not 3.14.** |
| Dependencies | `requirements.txt`, pinned with both bounds. Tested with Flask 3.1.3, google-genai 1.75.0, gunicorn 23.0.0, mcp 1.30.0, python-dotenv 1.1.1 |
| Model files | **None.** Image analysis runs on `gemini-3.5-flash-lite` through the API, so nothing loads locally and memory stays well under 512 MB |
| Secrets | `GEMINI_API_KEY`; `DATABASE_URL` for Postgres (optional locally) |
| Storage | `DATABASE_URL` set → Postgres (`psycopg`). Unset → SQLite at `data/fitfindr.db` (gitignored), so the local run needs no database account |

### Routes

| Route | In | Out |
|---|---|---|
| `GET /` | | The demo page (`static/index.html`) |
| `POST /wardrobe/scan` | multipart `image` (JPEG/PNG/WebP/HEIC, ≤ 8 MB) | `{"items": [...]}` in the `data/wardrobe_schema.json` shape |
| `POST /profile/analyze` | multipart `image`, one person | `{"undertone", "contrast", "hair_color", "eye_color", "flattering_colors", "avoid_colors"}` |
| `POST /outfit` | `{"occasion", "wardrobe"?, "profile"?}` | `{"outfit": "...", "items_used": [...]}` |
| `POST /ask` | unchanged from unit 4 | unchanged |
| `GET /example-wardrobe` | | the example wardrobe |
| `GET /me` | | this browser's wardrobe, profile, photo list and storage use |
| `GET /photos/<id>` | `?thumb=1` for the small one | the image, only if it belongs to this browser |
| `DELETE /photos/<id>` | | deletes the photo and the items scanned from it |
| `DELETE /wardrobe/items/<id>`, `DELETE /wardrobe` | | delete one item, or the whole wardrobe |
| `POST /wardrobe/example` | | copies the example wardrobe into this browser's wardrobe |
| `PUT /profile`, `DELETE /profile` | `{"undertone"?, "contrast"?}` | edit (keeps the photo), or delete profile and photo |
| `DELETE /me` | | everything this browser stored |

**Per-user storage.** Send the browser's ID as an `X-User-Id: <uuid>` header; the page does this for you. With the header, a successful scan or profile analysis is **stored** (photo, thumbnail, items or profile). Without it, those routes stay stateless, which is how `capstone_eval.py` calls them. Each browser can store at most 60 photos (`AI201_MAX_PHOTOS`); past that, uploads return **409**. Photos that fail (422) are never stored.

**Abuse limits.** The API key is the app's, and the routes are public, so the four routes that call the model (`/ask`, `/wardrobe/scan`, `/profile/analyze`, `/outfit`) are limited **per client IP**: 6 requests a minute and 60 an hour (`AI201_IP_LIMIT_PER_MINUTE`, `AI201_IP_LIMIT_PER_HOUR`; `0` per minute turns it off). Past that they return **429** with a `Retry-After` header. When several photos are uploaded at once, the page waits out a short limit and retries by itself. On Render the client IP comes from `X-Forwarded-For`, trusting one proxy hop (`AI201_TRUSTED_PROXIES`, which is 1 when Render's `RENDER` variable is set and 0 otherwise). Behind that, `generate.py` paces every caller together at 15 model calls a minute and stops after 300 calls per process (**503**, until the service restarts). Neither limit replaces the Google-side ones: use a key from a project **without billing**, or set a budget alert and a daily quota for the Generative Language API.

Status codes:

- **400**: no image, not an image, a file the model can't decode, an empty query/occasion, or a missing/invalid `X-User-Id` on a storage route
- **413**: over 8 MB
- **422**: no clothing found, or not exactly one person
- **409**: photo limit reached for this browser
- **429**: too many requests from this IP, try again after `Retry-After` seconds
- **503**: the model can't be reached, the database can't, or the service has used its model budget (300 calls) since it last started
- **500**: anything unexpected (logged with the exception)

```bash
curl -F image=@closet.jpg http://localhost:5000/wardrobe/scan
curl -F image=@me.jpg     http://localhost:5000/profile/analyze
curl -X POST http://localhost:5000/outfit -H 'Content-Type: application/json' \
  -d '{"occasion": "outdoor summer wedding"}'
```

### The log

Every request writes one JSON line, including failures. It goes to **stdout** (shown under Logs in Render's dashboard) and to **`logs/runs.jsonl`** locally (gitignored; set `AI201_LOG_PATH` to move it).

Fields:

- `ts`, `route`, `user` (the first 8 characters of the browser ID; the full ID is never logged), `client` (8 characters of a hash of the IP; the IP itself is never logged), `status`, `duration_ms`
- `input`: the query/occasion, or an image's mime and byte size. The image itself is never logged.
- `output`: an item count and categories, the undertone, or the first 120 characters of the outfit
- `model_calls`, `prompt_tokens`, `output_tokens`, `model`, `error`

Render's disk is wiped when the service sleeps, so copy the lines you need into the README in the same session.

### Measuring the cost of a run

```bash
# terminal 1: cache OFF (or runs 2–10 cost nothing), per-IP limit OFF (30 requests in ~1 min)
AI201_CACHE=0 AI201_IP_LIMIT_PER_MINUTE=0 AI201_LOG_PATH=logs/cost.jsonl python -m gunicorn serve:app --workers 1 --timeout 120
# terminal 2
python measure_cost.py --base http://localhost:8000 --log logs/cost.jsonl \
  --clothes closet1.jpg closet2.jpg --person me.jpg
```

Ten runs of scan → profile → outfit by default. It prints each run's tokens and time, then the mean, min and max. The results and the method are in the README under **What It Costs**.

### Running the capstone eval

```bash
AI201_CACHE=0 python capstone_eval.py --label before   # writes results/capstone_<ts>_before.md
```

---

## Where everything lives

| File | What it does |
|---|---|
| `config.py` | Every setting worth changing — **TEMPERATURE and the cache are at the top** |
| `tools.py` | Your three tools. **Stubs — you build these** |
| `agent.py` | The planning loop and the session. **Stub — you build this** |
| `generate.py` | The only thing that calls out to a service. Handles pacing and quota |
| `trace.py` | The trace helper, and the loop's stop condition |
| `app.py` | The command line |
| `serve.py` | The same agent over HTTP, for deploying — **unit 9** |
| `mcp_server.py` | Your MCP server — **unit 4, you register the tool** |
| `mcp_client.py` | Calling an MCP tool from your agent. Given to you |
| `scenarios.py` | What your test runs. **You fill this in** |
| `run_eval.py` | Runs the scenarios repeatedly and writes the run log |
| `criteria.md` | Your five acceptance criteria. **You fill this in** |
| `data/` | 40 listings and the wardrobe schema |
| `utils/data_loader.py` | Loading the data. Use this rather than reading the files yourself |
| `results/` | Run logs. **Commit these** — they're your evidence |

---

## The two settings people go looking for

Both are at the top of `config.py`, and the brief points at them by name.

If your fit cards come out **word-for-word identical** every time, it is one of:

- **`CACHE_ENABLED`** — while you build, identical prompts reuse the answer
  already received. That's deliberate; it makes debugging free. `run_eval.py`
  turns it off automatically.
- **`TEMPERATURE`** — at `0.0` the model gives you the same words every time.
  It ships at `0.9`.

---

## About rate limits

**This is the heaviest pair in the course for call volume.** Two of your three
tools call the model, so one agent run is several requests, and a few runs back
to back while debugging can cross the per-minute limit.

`generate.py` handles it:

- **It paces itself** and says when it's waiting. **A pause is the starter
  doing its job, not a bug.**
- **It reuses answers** to prompts already sent, while you build.
- **It stops** if a session makes an unreasonable number of calls, rather than
  draining your day's allowance. For an agent, that usually means a loop isn't
  ending — look for that before raising the number.
- **It counts your calls** and prints the total when you exit.

`config.MAX_ITERATIONS` is the loop's own stop condition. Your loop this unit
is short enough that you may never hit it. Keep it — a missing stop condition
is the most common architectural failure in production agents.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `The planning loop isn't built yet` | Correct, at the start. That's the TODO in `agent.py` |
| `No GEMINI_API_KEY found` | No `.env`, or the key wasn't pasted in. On Windows check it didn't save as `.env.txt` |
| A message saying the model couldn't be reached | Usually a bad key. This is also **exactly what unit 4 Milestone 2 asks you to trigger on purpose** |
| `[rate limit] ... Waiting 34s` | Working as intended. Leave it |
| `[serve] another request is still running` | Also working as intended. `serve.py` answers one request at a time; yours is queued behind one that's mid-run |
| `QuotaGuard: This session has made 300 requests` | A loop isn't ending. Find it before raising the budget |
| `The loop ran 11 times, past MAX_ITERATIONS` | Same thing, caught earlier |
| `The server doesn't offer a tool called '...'` | Nothing registered in `mcp_server.py` yet, or the name doesn't match |
| MCP returns a string where you expected a list | You're not going through `mcp_client.call_tool`, which unwraps it |
| Fit cards identical every run | `CACHE_ENABLED` or `TEMPERATURE`. See above |
| `--trace` prints nothing | You haven't added `trace.step()` calls yet — unit 4, Milestone 2 |
| `IncompleteFieldDefinitionWarning: Field 'lifespan'` | Harmless noise from the MCP library's dependencies. Not your code, not an error. Ignore it |
| A price ceiling you typed is being ignored | You used double quotes in PowerShell. `$30` vanished. Use single quotes |
| `UnicodeEncodeError: 'charmap' codec can't encode` | Shouldn't happen — `config.py` sets the console to UTF-8. If you see it, you're running a file that doesn't import `config` |

Still stuck after one honest attempt? Post in the help channel with the full
error, what you ran, and what you expected.

---

## A note on committing

At least four new commits in unit 3, at least four more in unit 4. Your commit
history is what shows your criteria existed before your results did.

**Do not delete and recreate this repository.** You submit the same URL both
units.

`results/` is deliberately **not** in `.gitignore`.
