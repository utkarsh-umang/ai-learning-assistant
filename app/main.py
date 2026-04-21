from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.graph import run_agent


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


app = FastAPI(title="Student Learning Assistant")

BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        answer = run_agent(req.message, student_id="S123")
        return ChatResponse(response=answer)
    except Exception as e:
        return ChatResponse(
            response=f"Server error: {type(e).__name__}: {e}. Set OPENAI_API_KEY in student-assistant/.env and restart."
        )
