# Frontend — Healthcare Assistant (hobby project)

A minimal React + Vite chat UI for testing the assistant. It talks to the FastAPI
backend at `/api/v1/chat` (the dev server proxies `/api` to `http://localhost:8000`).

## Run

Start the backend first (from the repo root, with `ANTHROPIC_API_KEY` set in `.env`):

```bash
python -m fastapi_app            # or: healthcare-assistant-api
```

Then the frontend:

```bash
cd frontend
npm install
npm run dev
```

Or, from the repo root, use the console script (installs deps on first run):

```bash
healthcare-assistant-frontend
```

Open http://localhost:5173.

## Config

- `VITE_API_URL` — override the API base (default `/api/v1`, proxied to port 8000).
