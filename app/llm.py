from __future__ import annotations

import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.observability.langfuse import langfuse_callbacks


load_dotenv()


def build_llm(model: str | None = None) -> ChatOpenAI:
    chosen_model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    return ChatOpenAI(
        model=chosen_model,
        temperature=0.2,
    )


def llm_invoke(llm: ChatOpenAI, messages: List[Any]) -> Any:
    callbacks: Optional[List[object]] = langfuse_callbacks()
    if callbacks:
        return llm.invoke(messages, config={"callbacks": callbacks})
    return llm.invoke(messages)
