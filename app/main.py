from __future__ import annotations

from pathlib import Path
import traceback
import uuid

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.graph import run_agent
from app.conversations import append_turns, load_history


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


app = FastAPI(title="Student Learning Assistant")

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Simple single-session-per-app-start mechanism.
SESSION_ID = uuid.uuid4().hex


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        history = [(t.role, t.content) for t in load_history(BASE_DIR, SESSION_ID, max_turns=20)]
        answer = run_agent(req.message, student_id="S123", history=history)
        append_turns(BASE_DIR, SESSION_ID, [("user", req.message), ("assistant", answer)])
        return ChatResponse(response=answer)
    except Exception as e:
        # Ensure we can debug failures via container logs / traces.
        print(traceback.format_exc())
        if isinstance(e, RuntimeError) and "OPENAI_API_KEY" in str(e):
            return ChatResponse(response=f"Server error: {type(e).__name__}: {e}. Set OPENAI_API_KEY in .env and restart.")
        return ChatResponse(response=f"Server error: {type(e).__name__}: {e}.")
