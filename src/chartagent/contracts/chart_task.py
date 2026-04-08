from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ChartTaskIssue:
    level: str
    message: str


@dataclass
class ChartTaskValidationResult:
    valid: bool
    normalized: dict[str, Any]
    issues: list[ChartTaskIssue] = field(default_factory=list)


def load_and_normalize_chart_task(path: Path) -> ChartTaskValidationResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return normalize_chart_task(data)


def normalize_chart_task(data: dict[str, Any]) -> ChartTaskValidationResult:
    issues: list[ChartTaskIssue] = []
    dataset = data.get("dataset")
    if not isinstance(dataset, dict):
        issues.append(ChartTaskIssue(level="error", message="`dataset` must be an object."))
        dataset = {}

    preferred_output = _coerce_string_list(data.get("preferred_output"))
    if not preferred_output:
        preferred_output = ["chart_spec", "svg"]
    constraints = data.get("constraints") if isinstance(data.get("constraints"), dict) else {}
    theme_set = str(data.get("theme_set") or constraints.get("theme_set") or "").strip()
    theme_overrides = _coerce_object(data.get("theme_overrides") or constraints.get("theme_overrides"))
    theme_reset = _coerce_theme_reset(data.get("theme_reset") or constraints.get("theme_reset"))

    normalized = {
        "task_id": str(data.get("task_id") or "chart-task").strip() or "chart-task",
        "request_origin": str(data.get("request_origin") or "manual").strip() or "manual",
        "goal": str(data.get("goal") or "communicate_pattern").strip() or "communicate_pattern",
        "question": str(data.get("question") or "").strip(),
        "preferred_output": preferred_output,
        "dataset": dataset,
        "context": data.get("context") if isinstance(data.get("context"), dict) else {},
        "constraints": constraints,
        "source_hints": _coerce_string_list(data.get("source_hints")),
        "citation_requirements": _coerce_citation_requirements(data.get("citation_requirements")),
        "fallback_policy": _coerce_fallback_policy(data.get("fallback_policy")),
        "theme_set": theme_set,
        "theme_overrides": theme_overrides,
        "theme_reset": theme_reset,
    }

    if not normalized["question"]:
        issues.append(
            ChartTaskIssue(
                level="warning",
                message="`question` is empty; chart title will fall back to the goal or dataset title.",
            )
        )

    if not normalized["source_hints"]:
        issues.append(
            ChartTaskIssue(
                level="warning",
                message="No `source_hints` were provided; source-note output may be thin.",
            )
        )

    valid = not any(issue.level == "error" for issue in issues)
    return ChartTaskValidationResult(valid=valid, normalized=normalized, issues=issues)


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if item is None:
            continue
        stripped = str(item).strip()
        if stripped:
            normalized.append(stripped)
    return normalized


def _coerce_citation_requirements(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "required": bool(value.get("required", False)),
            "style": str(value.get("style") or "").strip(),
            "placement": str(value.get("placement") or "source_note").strip() or "source_note",
        }
    if isinstance(value, str) and value.strip():
        return {"required": True, "style": value.strip(), "placement": "source_note"}
    return {"required": False, "style": "", "placement": "source_note"}


def _coerce_fallback_policy(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            "prefer_table_when_ambiguous": bool(value.get("prefer_table_when_ambiguous", True)),
            "allow_chart_without_source": bool(value.get("allow_chart_without_source", False)),
            "max_categories": int(value.get("max_categories", 8) or 8),
        }
    return {
        "prefer_table_when_ambiguous": True,
        "allow_chart_without_source": False,
        "max_categories": 8,
    }


def _coerce_object(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _coerce_theme_reset(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    mode = str(value.get("mode") or "").strip()
    if mode not in {"reset_all", "reset_keys", "reset_groups"}:
        return {}
    reset: dict[str, Any] = {"mode": mode}
    if mode == "reset_keys":
        reset["keys"] = _coerce_string_list(value.get("keys"))
    if mode == "reset_groups":
        reset["groups"] = _coerce_string_list(value.get("groups"))
    return reset
