from __future__ import annotations

from datetime import date
import os
from functools import lru_cache
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import MessagesState, add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from app.llm import build_llm, llm_invoke
from app.prompts import SYSTEM_PROMPT, context_prompt
from app.tools import TOOLS


class AssistantState(MessagesState):
    # MessagesState already provides `messages: list`
    # add_messages reducer ensures appends
    messages: Any = add_messages


def build_graph() -> Any:
    llm = build_llm().bind_tools(TOOLS)

    tool_node = ToolNode(TOOLS)

    def assistant_node(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state["messages"]
        result = llm_invoke(llm, messages)
        return {"messages": [result]}

    graph = StateGraph(AssistantState)
    graph.add_node("assistant", assistant_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("assistant")
    graph.add_conditional_edges("assistant", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "assistant")

    return graph.compile()


@lru_cache(maxsize=1)
def get_graph() -> Any:
    return build_graph()


def initial_state(user_message: str, *, today: str | None = None, student_id: str = "S123") -> Dict[str, Any]:
    today_iso = today or date.today().isoformat()
    return {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            SystemMessage(content=context_prompt(today_iso=today_iso, student_id=student_id)),
            HumanMessage(content=user_message),
        ]
    }


def run_agent(user_message: str, *, today: str | None = None, student_id: str = "S123") -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")
    state = initial_state(user_message, today=today, student_id=student_id)
    final = get_graph().invoke(state, config={"recursion_limit": 6})

    # Find the last AI message content.
    last_ai = None
    for m in reversed(final["messages"]):
        if isinstance(m, AIMessage):
            last_ai = m
            break
    return (last_ai.content if last_ai else "").strip()
