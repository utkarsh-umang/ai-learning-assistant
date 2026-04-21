from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal, List


Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class ConversationTurn:
    role: Role
    content: str
    ts: str  # ISO timestamp


def ensure_conversations_dir(base_dir: Path) -> Path:
    conv_dir = base_dir / "conversations"
    conv_dir.mkdir(parents=True, exist_ok=True)
    return conv_dir


def conversation_path(base_dir: Path, session_id: str) -> Path:
    conv_dir = ensure_conversations_dir(base_dir)
    return conv_dir / f"{session_id}.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_turns(base_dir: Path, session_id: str, turns: Iterable[tuple[Role, str]]) -> None:
    path = conversation_path(base_dir, session_id)
    with path.open("a", encoding="utf-8") as f:
        for role, content in turns:
            rec = {"role": role, "content": content, "ts": _now_iso()}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_history(base_dir: Path, session_id: str, *, max_turns: int = 20) -> List[ConversationTurn]:
    """
    Load the most recent turns for the session.
    We only persist user/assistant text turns (no tool messages) to keep this simple.
    """
    path = conversation_path(base_dir, session_id)
    if not path.exists():
        return []

    turns: List[ConversationTurn] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                role = rec.get("role")
                content = rec.get("content")
                ts = rec.get("ts") or ""
                if role in ("user", "assistant") and isinstance(content, str):
                    turns.append(ConversationTurn(role=role, content=content, ts=str(ts)))
            except Exception:
                continue

    return turns[-max_turns:]

