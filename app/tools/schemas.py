from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class GetWeakTopicsInput(BaseModel):
    student_id: str = Field(..., description="Student identifier, e.g. S123")


class SubjectScore(BaseModel):
    subject: str
    overall_score_percentage: float


class GetWeakTopicsOutput(BaseModel):
    student_id: str
    weak_topics: List[str]
    strong_topics: List[str] = []
    subject_scores: List[SubjectScore] = []


class GetUpcomingTestsInput(BaseModel):
    student_id: str = Field(..., description="Student identifier, e.g. S123")
    reference_date: Optional[date] = Field(
        default=None, description="Interpret 'upcoming/this week' relative to this date."
    )
    days_ahead: int = Field(default=7, ge=1, le=60, description="Lookahead window in days.")


class UpcomingTest(BaseModel):
    test_id: str
    subject: str
    test_name: str
    date: str  # keep as ISO string for simplicity
    topics: List[str]


class GetUpcomingTestsOutput(BaseModel):
    student_id: str
    window: dict
    upcoming_tests: List[UpcomingTest]


class RecommendStudyMaterialInput(BaseModel):
    topic: str = Field(..., description="Topic name, e.g. Algebra")


class StudyMaterial(BaseModel):
    material_id: str
    title: str


class RecommendStudyMaterialOutput(BaseModel):
    topic: str
    materials: List[StudyMaterial]
