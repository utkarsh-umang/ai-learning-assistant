from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class DataStore:
    student_profile: Dict[str, Any]
    performance_history: Dict[str, Any]
    study_materials: Dict[str, Any]
    upcoming_tests: Dict[str, Any]


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_data(data_dir: str | Path | None = None) -> DataStore:
    """
    Load all dataset JSON files once and cache in memory.
    """
    base_dir = Path(__file__).resolve().parents[2]
    resolved_data_dir = Path(data_dir) if data_dir is not None else (base_dir / "data")

    return DataStore(
        student_profile=_read_json(resolved_data_dir / "student_profile.json"),
        performance_history=_read_json(resolved_data_dir / "performance_history.json"),
        study_materials=_read_json(resolved_data_dir / "study_materials.json"),
        upcoming_tests=_read_json(resolved_data_dir / "upcoming_tests.json"),
    )
