from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from app.data.loader import load_data


def get_weak_topics(student_id: str) -> Dict[str, Any]:
    data = load_data()
    profile = data.student_profile
    perf = data.performance_history

    if profile.get("student_id") != student_id:
        return {
            "student_id": student_id,
            "weak_topics": [],
            "strong_topics": [],
            "subject_scores": [],
            "error": f"student_id {student_id} not found in student_profile.json",
        }

    subject_scores = []
    if perf.get("student_id") == student_id:
        subject_scores = perf.get("subject_performance", []) or []

    return {
        "student_id": student_id,
        "weak_topics": profile.get("weak_topics", []) or [],
        "strong_topics": profile.get("strong_topics", []) or [],
        "subject_scores": subject_scores,
    }


def get_upcoming_tests(
    student_id: str, reference_date: str | None = None, days_ahead: int = 7
) -> Dict[str, Any]:
    data = load_data()
    tests_doc = data.upcoming_tests

    if tests_doc.get("student_id") != student_id:
        return {
            "student_id": student_id,
            "window": {},
            "upcoming_tests": [],
            "error": f"student_id {student_id} not found in upcoming_tests.json",
        }

    if reference_date:
        ref = datetime.fromisoformat(reference_date).date()
    else:
        ref = date.today()

    end = ref + timedelta(days=days_ahead)

    upcoming: List[Dict[str, Any]] = []
    for t in tests_doc.get("upcoming_tests", []) or []:
        try:
            t_date = datetime.fromisoformat(t.get("date")).date()
        except Exception:
            continue
        if ref <= t_date <= end:
            upcoming.append(t)

    return {
        "student_id": student_id,
        "window": {"start_date": ref.isoformat(), "end_date": end.isoformat()},
        "upcoming_tests": upcoming,
    }


def recommend_study_material(topic: str) -> Dict[str, Any]:
    data = load_data()
    materials = data.study_materials.get("materials", []) or []

    matches = []
    for m in materials:
        if (m.get("topic") or "").strip().lower() == topic.strip().lower():
            matches.append({"material_id": m.get("material_id"), "title": m.get("title")})

    return {"topic": topic, "materials": matches}
