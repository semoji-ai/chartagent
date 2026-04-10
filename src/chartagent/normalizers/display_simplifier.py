from __future__ import annotations

from typing import Any


def simplify_dataset_for_display(
    task: dict[str, Any],
    dataset: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    shape = str(dataset.get("shape") or "").strip()
    if shape in {"label_value_list", "share_breakdown"}:
        return _simplify_label_value_dataset(task=task, dataset=dataset)
    return dict(dataset), []


def _simplify_label_value_dataset(
    task: dict[str, Any],
    dataset: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    records_in = dataset.get("records") or []
    records = [
        {
            **dict(record),
            "full_label": str(record.get("full_label") or record.get("label") or "").strip(),
            "display_label": _shorten_label(str(record.get("label") or "").strip()),
        }
        for record in records_in
    ]
    preserve_order = bool((task.get("constraints") or {}).get("preserve_order", False))
    if not preserve_order:
        records.sort(key=lambda item: float(item.get("value") or 0.0), reverse=True)

    issues: list[dict[str, str]] = []
    max_categories = int(task.get("fallback_policy", {}).get("max_categories", 8) or 8)
    allow_full_ranking = bool((task.get("constraints") or {}).get("preserve_full_ranking", False))
    shape = str(dataset.get("shape") or "").strip()

    if not allow_full_ranking and len(records) > max_categories:
        if shape == "share_breakdown":
            kept = records[: max_categories - 1]
            tail = records[max_categories - 1 :]
            tail_value = sum(float(item.get("value") or 0.0) for item in tail)
            tail_unit = _common_unit(tail) or _common_unit(records)
            kept.append(
                {
                    "label": "기타",
                    "full_label": "기타",
                    "display_label": "기타",
                    "value": tail_value,
                    "unit": tail_unit,
                    "note": f"{len(tail)} categories collapsed",
                    "is_collapsed_tail": True,
                }
            )
            records = kept
            issues.append(
                {
                    "level": "info",
                    "message": f"Collapsed {len(tail)} small categories into 기타 for readability.",
                }
            )
        else:
            trimmed = len(records) - max_categories
            records = records[:max_categories]
            issues.append(
                {
                    "level": "info",
                    "message": f"Trimmed {trimmed} lower-ranked categories to keep the chart readable.",
                }
            )

    simplified = dict(dataset)
    simplified["records"] = records
    simplified["simplification"] = {
        "record_count_before": len(records_in),
        "record_count_after": len(records),
        "max_categories": max_categories,
        "label_shortening_applied": any(
            str(record.get("display_label") or "") != str(record.get("full_label") or "")
            for record in records
        ),
    }
    return simplified, issues


def _shorten_label(label: str, max_len: int = 14) -> str:
    text = label.strip()
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3].rstrip()}..."


def _common_unit(records: list[dict[str, Any]]) -> str:
    units = {
        str(record.get("unit") or "").strip()
        for record in records
        if str(record.get("unit") or "").strip()
    }
    if len(units) == 1:
        return next(iter(units))
    return ""
