# Wine Data Agent

Wine Data Agent is a FastAPI application that exposes a conversational agent to query wines from a local SQLite database.

The agent uses LangChain + Gemini, keeps conversation context by `thread_id`, and decides which tool to execute based on user intent (`id`, `designation`, or technical filters).

## What This Project Does

- Runs a REST API with FastAPI.
- Runs an agent powered by Gemini.
- Queries wine technical data from SQLite (`wines_table.db`, `wines` table).
- Generates and persists embeddings in Chroma (`data/processed/chroma_db`).
- Keeps per-thread conversation memory during runtime.

## Stack and Architecture

- Backend: FastAPI + Uvicorn
- Agent: LangChain / LangGraph + custom tools
- Model: Google Gemini (`ChatGoogleGenerativeAI`)
- Database: local SQLite
- Vector store: disk-persistent Chroma
- Containers: Docker + Docker Compose

General flow:

1. The CSV is ingested into SQLite and Chroma.
2. A client calls `POST /api/conversation`.
3. The agent interprets intent and calls SQL tools when needed.
4. The API returns an answer, `thread_id`, and the sources used.

## Requirements

- Python 3.11+
- Docker (optional, for containerized execution)
- Docker Compose v2 (optional)
- `GOOGLE_API_KEY` environment variable

## Environment Setup

Create a `.env` file in the repository root:

```env
GOOGLE_API_KEY=your_api_key
```

Alternative: set it as a session environment variable.

PowerShell:

```powershell
$env:GOOGLE_API_KEY="your_api_key"
```

Bash:

```bash
export GOOGLE_API_KEY="your_api_key"
```

## Run From Scratch (Local, Without Docker)

### 1) Create a Virtual Environment

Windows (Git Bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install Dependencies

Using `pip`:

```bash
pip install -U pip
pip install -e .
```

Optional with `uv`:

```bash
pip install uv
uv sync
```

### 3) Ingest Initial Data

This step creates/replaces `data/processed/wines_table.db` and generates Chroma in `data/processed/chroma_db`.

```bash
python scripts/ingests.py
```

### 4) Start the API

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

API available at:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Run With Docker (Image)

### 1) Build

```bash
docker build -t wine-data-agent:latest .
```

### 2) Run

```bash
docker run --rm -p 8000:8000 --env-file .env -v "${PWD}/data:/app/data" wine-data-agent:latest
```

Note: in PowerShell, if `${PWD}` does not resolve as expected, use an absolute Windows path.

## Run With Docker Compose

Current `docker-compose.yml`:

- builds from `.`
- exposes `8000:8000`
- loads variables from `.env`
- mounts `./data` into `/app/data`

Commands:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

## API

### POST `/api/conversation`

Request:

```json
{
	"query": "Find French wines with more than 90 points",
	"thread_id": null
}
```

Response (example):

```json
{
	"thread_id": "3f7f6d75-92b2-4c21-9a2c-130f0f9f79f4",
	"answer": "I found 3 wines...",
	"sources": ["Tool: query_by_specs"]
}
```

### GET `/`

Basic health response:

```json
{
	"message": "API is running. Please go to /docs for interactive Swagger documentation."
}
```

## Agent Tools

- `query_by_id(id)`
- `query_by_designation(designation)`
- `query_by_specs(country, designation, points, price, province, region_1, region_2, taster_name)`

Currently, `query_by_specs` returns up to 3 results (`LIMIT 3`).

## Important Notes

- The ingestion script uses `MAX_ROWS = 90` by default.
- If the CSV changes or you need to regenerate embeddings, run `python scripts/ingests.py` again.
- Without `GOOGLE_API_KEY`, the agent cannot answer.
- Conversation memory (`thread_id`) lives in process memory.

## Quick Troubleshooting

- API key errors: verify `.env` and ensure Docker/Compose is loading it.
- No query results: confirm ingestion ran and that `data/processed/wines_table.db` exists.
- Port already in use: switch to a different port in run/compose.

## Suggested Next Improvements

- Add integration tests for endpoints and tools.
- Extend semantic retrieval by using Chroma during response generation.
- Persist conversation memory outside process state for production.
