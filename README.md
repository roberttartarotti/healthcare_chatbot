# Healthcare Assistant

> ⚠️ **Hobby project — no medical value.** A personal demo of a LangGraph
> multi-agent system. No doctor was involved; nothing it says is medical advice,
> a diagnosis, or treatment. Do not use it for any health decision. In an
> emergency, call your local emergency number.

## What it is

A multi-agent healthcare chat assistant built with **LangGraph** (Anthropic
Claude) and a **FastAPI** backend, with a small **React** frontend for testing.

A supervisor **orchestrator** routes each message to the right specialist agent,
which answers using free, no-registration public health APIs:

| Specialist | Source(s) |
|---|---|
| 💊 Medication | openFDA, RxNorm |
| 🩺 Conditions & symptoms | MedlinePlus, NIH Clinical Tables |
| 🥗 Nutrition | Open Food Facts |
| 🏃 Fitness | free-exercise-db |
| 🧭 General | MedlinePlus |

Each turn is **orchestration → specialist → orchestration → user**. It also has
input/output **guardrails** (off-topic + emergency detection, safety screening),
a mandatory disclaimer on the first reply, per-user memory (one thread per user),
and automatic **summarization** of older messages to keep the context small.

## Requirements

- Python 3.11+
- Node.js 18+ (only for the frontend)
- An **Anthropic API key** — the only key required.

## Install

```bash
python -m venv .venv && source .venv/bin/activate   # recommended
cp .env.example .env        # then set ANTHROPIC_API_KEY
pip install -e .            # installs the app + the console commands
```

> The `healthcare-assistant-*` console commands below only exist **after**
> `pip install -e .`. If you skip that step, use the `python -m …` / `npm`
> equivalents shown alongside each command.

## Run the backend (API)

```bash
python -m fastapi_app              # always works
# healthcare-assistant-api        # same thing, after `pip install -e .`
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/api/v1/docs

Send a message (reuse the same `user_id` to keep the conversation):

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "me", "message": "What are common side effects of ibuprofen?"}'
```

Response: `{ "reply": "...", "specialty": "medication", "blocked": false }`

## Run the frontend

Start the backend first (the dev server proxies `/api` to it). Then, any of:

```bash
cd frontend && npm install && npm run dev    # plain npm (simplest)
python -m fastapi_app.frontend               # no install needed
# healthcare-assistant-frontend              # after `pip install -e .`
```

Open http://localhost:5173.

## Tests

```bash
pip install -e ".[dev]"
pytest
```
