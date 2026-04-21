from __future__ import annotations

from langchain_core.tools import StructuredTool

from app.tools.functions import get_upcoming_tests, get_weak_topics, recommend_study_material
from app.tools.schemas import (
    GetUpcomingTestsInput,
    RecommendStudyMaterialInput,
    GetWeakTopicsInput,
)


TOOLS = [
    StructuredTool.from_function(
        name="get_weak_topics",
        description=(
            "Return the student's weak topics and subject scores. "
            "Use when asked about weak areas or what to study next."
        ),
        func=get_weak_topics,
        args_schema=GetWeakTopicsInput,
    ),
    StructuredTool.from_function(
        name="get_upcoming_tests",
        description=(
            "Return upcoming tests in a date window. "
            "Use for 'this week', 'upcoming test', or prep planning."
        ),
        func=get_upcoming_tests,
        args_schema=GetUpcomingTestsInput,
    ),
    StructuredTool.from_function(
        name="recommend_study_material",
        description="Recommend study materials for a given topic.",
        func=recommend_study_material,
        args_schema=RecommendStudyMaterialInput,
    ),
]
