# Student Learning Assistant (AI-powered)

An AI assistant that helps a student understand what to study next using:
- **LangGraph** for the agent/tool loop
- **LangChain** (`ChatOpenAI`) as the LLM wrapper
- **FastAPI** for a simple `/chat` API
- Optional **Langfuse** tracing for observability

## Quickstart

### 1) Install

```bash
cd student-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

Create `student-assistant/.env`:

```bash
OPENAI_API_KEY=...

# Optional (Langfuse)
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3) Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/` for the minimal UI.

## API

### `POST /chat`

Body:

```json
{ "message": "What should I study this week?" }
```

Response:

```json
{ "response": "..." }
```

## Data

The sample dataset lives in `student-assistant/data/`.

For now the app uses a single hardcoded student: `S123`.

## Architecture (high level)

- `app/data/loader.py` loads all JSON files into memory once at startup.
- `app/tools/functions.py` implements:
  - `get_weak_topics(student_id)`
  - `get_upcoming_tests(student_id, reference_date, days_ahead)`
  - `recommend_study_material(topic)`
- `app/graph.py` builds a LangGraph that loops:
  - LLM node → (optional) tool calls → tools node → LLM node → … until done.
- `app/main.py` exposes `/chat` and serves `static/index.html`.

## Limitations / next improvements

- Topic matching is exact-string; can be improved with embeddings + fuzzy matching.
- No per-user auth / multi-student routing yet.
- Basic UI only.
