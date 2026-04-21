from __future__ import annotations

import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.observability.langfuse import langfuse_callbacks


load_dotenv()


def build_llm(model: str | None = None) -> ChatOpenAI:
    chosen_model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    return ChatOpenAI(
        model=chosen_model,
        temperature=0.2,
    )

def _sanitize_messages_for_tool_calling(messages: List[Any]) -> List[Any]:
    """
    Guard against invalid OpenAI payloads where a `tool` message is present
    without the immediately preceding assistant message that contained `tool_calls`.

    This can happen in some edge cases when message history is truncated or
    reducers/serializers drop the assistant tool-call message.
    """
    if not messages:
        return messages

    sanitized: List[Any] = []

    # Drop any leading ToolMessages (OpenAI rejects tool at index 0).
    i = 0
    while i < len(messages) and isinstance(messages[i], ToolMessage):
        i += 1

    expected_tool_call_ids: set[str] = set()
    for m in messages[i:]:
        if isinstance(m, AIMessage):
            tool_calls = getattr(m, "tool_calls", None) or []
            # `tool_calls` items are typically dict-like with an `id`.
            try:
                expected_tool_call_ids = {tc.get("id") for tc in tool_calls if isinstance(tc, dict) and tc.get("id")}  # type: ignore[union-attr]
            except Exception:
                expected_tool_call_ids = set()
            sanitized.append(m)
            continue

        if isinstance(m, ToolMessage):
            # Keep tool results only if they directly follow an AI tool call.
            tool_call_id = getattr(m, "tool_call_id", None)
            if tool_call_id and tool_call_id in expected_tool_call_ids:
                sanitized.append(m)
                expected_tool_call_ids.discard(tool_call_id)
            continue

        # Any other message type resets the expectation.
        expected_tool_call_ids = set()
        sanitized.append(m)

    return sanitized


def llm_invoke(llm: ChatOpenAI, messages: List[Any]) -> Any:
    messages = _sanitize_messages_for_tool_calling(messages)
    callbacks: Optional[List[object]] = langfuse_callbacks()
    if callbacks:
        return llm.invoke(messages, config={"callbacks": callbacks})
    return llm.invoke(messages)
