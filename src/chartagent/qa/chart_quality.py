from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ChartQualityIssue:
    level: str
    code: str
    message: str


def evaluate_chart_quality(
    task: dict[str, Any],
    dataset: dict[str, Any],
    chart_family: str,
) -> list[ChartQualityIssue]:
    issues: list[ChartQualityIssue] = []
    shape = str(dataset.get("shape") or "").strip()

    if not task.get("source_hints"):
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="missing_source",
                message="Source note is missing.",
            )
        )

    if shape in {"single_value", "label_value_list", "share_breakdown", "time_series"} and _is_unit_missing(dataset):
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="unit_missing",
                message="Unit is missing for numeric data.",
            )
        )

    if _has_mixed_units(dataset):
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="mixed_units",
                message="Mixed units are present without an explicit explanation.",
            )
        )

    if shape in {"label_value_list", "share_breakdown"}:
        record_count = len(dataset.get("records") or [])
        if record_count > int(task.get("fallback_policy", {}).get("max_categories", 8) or 8):
            issues.append(
                ChartQualityIssue(
                    level="warning",
                    code="too_many_categories",
                    message="Too many categories may reduce readability.",
                )
            )
        max_label_length = max((len(str(record.get("label") or "")) for record in dataset.get("records") or []), default=0)
        if max_label_length > 12:
            issues.append(
                ChartQualityIssue(
                    level="warning",
                    code="label_overflow_risk",
                    message="Some labels are long enough to risk overflow.",
                )
            )
        if chart_family in {"donut", "pie", "stacked_progress"} and record_count > 5:
            issues.append(
                ChartQualityIssue(
                    level="warning",
                    code="chart_worse_than_table",
                    message="This many share categories may read better as a table than a composition chart.",
                )
            )

    unsupported_targets = _unsupported_annotation_targets(task, chart_family)
    for target in unsupported_targets:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="unsupported_annotation_target",
                message=f"Unsupported annotation target for this family: {target}",
            )
        )
    return issues


def _is_unit_missing(dataset: dict[str, Any]) -> bool:
    if str(dataset.get("unit") or "").strip():
        return False
    shape = str(dataset.get("shape") or "").strip()
    if shape == "single_value":
        return True
    if shape in {"label_value_list", "share_breakdown"}:
        return not any(str(record.get("unit") or "").strip() for record in dataset.get("records") or [])
    if shape == "time_series":
        return not any(str(point.get("unit") or "").strip() for point in dataset.get("points") or [])
    return False


def _has_mixed_units(dataset: dict[str, Any]) -> bool:
    shape = str(dataset.get("shape") or "").strip()
    if shape in {"label_value_list", "share_breakdown"}:
        units = {
            str(record.get("unit") or "").strip()
            for record in dataset.get("records") or []
            if str(record.get("unit") or "").strip()
        }
        return len(units) > 1
    if shape == "time_series":
        units = {
            str(point.get("unit") or "").strip()
            for point in dataset.get("points") or []
            if str(point.get("unit") or "").strip()
        }
        return len(units) > 1
    return False


def _unsupported_annotation_targets(task: dict[str, Any], chart_family: str) -> list[str]:
    constraints = task.get("constraints") or {}
    annotations = constraints.get("annotations")
    if not isinstance(annotations, list):
        return []
    allowed_by_family = {
        "single_stat": {"primary_value"},
        "bar_horizontal": {"top_rank", "bar"},
        "line": {"latest_point", "point", "range"},
        "donut": {"dominant_slice", "slice"},
        "pie": {"dominant_slice", "slice"},
        "percentage_progress": {"primary_progress", "progress_bar"},
        "radial_gauge": {"current_value"},
        "semi_donut": {"current_value"},
        "stacked_progress": {"dominant_segment", "segment"},
        "metric_wall": {"card"},
        "comparison_table": {"row", "cell"},
        "fact_table": {"row", "cell"},
        "timeline_table": {"row", "event"},
    }
    allowed = allowed_by_family.get(chart_family, set())
    unsupported: list[str] = []
    for entry in annotations:
        if not isinstance(entry, dict):
            continue
        target = str(entry.get("target") or "").strip()
        if target and target not in allowed:
            unsupported.append(target)
    return unsupported
