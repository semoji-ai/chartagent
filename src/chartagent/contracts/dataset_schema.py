from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetNormalizationIssue:
    level: str
    message: str


@dataclass
class DatasetNormalizationResult:
    valid: bool
    normalized: dict[str, Any]
    issues: list[DatasetNormalizationIssue] = field(default_factory=list)


def normalize_dataset(data: dict[str, Any]) -> DatasetNormalizationResult:
    issues: list[DatasetNormalizationIssue] = []
    title = str(data.get("title") or "").strip()
    unit = str(data.get("unit") or "").strip()
    explicit_shape = str(data.get("shape") or "").strip()

    if explicit_shape == "single_value" or "value" in data:
        value = _coerce_number(data.get("value"))
        if value is None:
            issues.append(
                DatasetNormalizationIssue(level="error", message="`value` must be numeric for single_value data.")
            )
            value = 0.0
        normalized = {
            "shape": "single_value",
            "title": title,
            "unit": unit,
            "label": str(data.get("label") or title or "Value").strip() or "Value",
            "value": value,
            "source_notes": _coerce_string_list(data.get("source_notes")),
        }
        return DatasetNormalizationResult(
            valid=not any(issue.level == "error" for issue in issues),
            normalized=normalized,
            issues=issues,
        )

    candles = data.get("candles") or data.get("points")
    if isinstance(candles, list) and candles and (explicit_shape == "ohlc_series" or _looks_like_ohlc_series(candles)):
        normalized_candles = _normalize_ohlc_series(candles, default_unit=unit)
        if normalized_candles:
            normalized = {
                "shape": "ohlc_series",
                "title": title,
                "unit": unit,
                "x_label": str(data.get("x_label") or "date").strip() or "date",
                "y_label": str(data.get("y_label") or "price").strip() or "price",
                "candles": normalized_candles,
                "source_notes": _coerce_string_list(data.get("source_notes")),
            }
            return DatasetNormalizationResult(valid=True, normalized=normalized, issues=issues)

    bins = data.get("bins")
    if isinstance(bins, list) and bins and (explicit_shape == "distribution_bins" or _looks_like_distribution_bins(bins)):
        normalized_bins = _normalize_distribution_bins(bins, default_unit=unit)
        if normalized_bins:
            normalized = {
                "shape": "distribution_bins",
                "title": title,
                "unit": unit,
                "x_label": str(data.get("x_label") or "bin").strip() or "bin",
                "y_label": str(data.get("y_label") or "count").strip() or "count",
                "bins": normalized_bins,
                "source_notes": _coerce_string_list(data.get("source_notes")),
            }
            return DatasetNormalizationResult(valid=True, normalized=normalized, issues=issues)

    items = data.get("items")
    if isinstance(items, list) and items:
        records = _normalize_label_value_records(items, default_unit=unit)
        if records:
            shape = (
                "share_breakdown"
                if explicit_shape == "share_breakdown" or _looks_like_share_breakdown(records)
                else "label_value_list"
            )
            normalized = {
                "shape": shape,
                "title": title,
                "unit": unit,
                "records": records,
                "source_notes": _coerce_string_list(data.get("source_notes")),
            }
            if len(records) > 8:
                issues.append(
                    DatasetNormalizationIssue(
                        level="warning",
                        message="More than 8 categories may reduce readability.",
                    )
                )
            return DatasetNormalizationResult(valid=True, normalized=normalized, issues=issues)

    points = data.get("points") or data.get("series")
    if isinstance(points, list) and points:
        normalized_points = _normalize_time_series(points, default_unit=unit)
        if normalized_points:
            normalized = {
                "shape": "time_series",
                "title": title,
                "unit": unit,
                "x_label": str(data.get("x_label") or "x").strip() or "x",
                "y_label": str(data.get("y_label") or "y").strip() or "y",
                "points": normalized_points,
                "source_notes": _coerce_string_list(data.get("source_notes")),
            }
            return DatasetNormalizationResult(valid=True, normalized=normalized, issues=issues)

    headers = data.get("headers")
    rows = data.get("rows")
    if isinstance(rows, list) and rows:
        table = _normalize_table(headers=headers, rows=rows, title=title)
        if table:
            return DatasetNormalizationResult(valid=True, normalized=table, issues=issues)

    issues.append(
        DatasetNormalizationIssue(
            level="error",
            message="Unsupported dataset shape. Provide `value`, `items`, `points`, or `headers` + `rows`.",
        )
    )
    return DatasetNormalizationResult(valid=False, normalized={"shape": "unknown", "title": title}, issues=issues)


def _normalize_label_value_records(items: list[Any], default_unit: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or item.get("name") or f"Item {index}").strip() or f"Item {index}"
        value = _coerce_number(item.get("value"))
        if value is None:
            continue
        records.append(
            {
                "label": label,
                "value": value,
                "unit": str(item.get("unit") or default_unit).strip(),
                "note": str(item.get("note") or "").strip(),
            }
        )
    return records


def _normalize_time_series(points: list[Any], default_unit: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, point in enumerate(points, start=1):
        if not isinstance(point, dict):
            continue
        x_value = point.get("x", point.get("label", point.get("date", point.get("time"))))
        y_value = _coerce_number(point.get("y", point.get("value")))
        if x_value is None or y_value is None:
            continue
        normalized.append(
            {
                "x": str(x_value).strip() or f"Point {index}",
                "y": y_value,
                "unit": str(point.get("unit") or default_unit).strip(),
                "note": str(point.get("note") or "").strip(),
            }
        )
    return normalized


def _normalize_ohlc_series(candles: list[Any], default_unit: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, candle in enumerate(candles, start=1):
        if not isinstance(candle, dict):
            continue
        x_value = candle.get("x", candle.get("date", candle.get("time", candle.get("label"))))
        open_value = _coerce_number(candle.get("open"))
        high_value = _coerce_number(candle.get("high"))
        low_value = _coerce_number(candle.get("low"))
        close_value = _coerce_number(candle.get("close"))
        if x_value is None or None in {open_value, high_value, low_value, close_value}:
            continue
        normalized.append(
            {
                "x": str(x_value).strip() or f"Candle {index}",
                "open": open_value,
                "high": high_value,
                "low": low_value,
                "close": close_value,
                "unit": str(candle.get("unit") or default_unit).strip(),
                "note": str(candle.get("note") or "").strip(),
            }
        )
    return normalized


def _normalize_distribution_bins(bins: list[Any], default_unit: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, bin_item in enumerate(bins, start=1):
        if not isinstance(bin_item, dict):
            continue
        count_value = _coerce_number(bin_item.get("count", bin_item.get("value", bin_item.get("y"))))
        if count_value is None:
            continue
        start_value = _coerce_number(bin_item.get("start"))
        end_value = _coerce_number(bin_item.get("end"))
        label = str(bin_item.get("label") or "").strip()
        if not label:
            if start_value is not None and end_value is not None:
                label = f"{_format_number(start_value)}-{_format_number(end_value)}"
            else:
                label = f"Bin {index}"
        normalized.append(
            {
                "label": label,
                "start": start_value,
                "end": end_value,
                "count": count_value,
                "unit": str(bin_item.get("unit") or default_unit).strip(),
                "note": str(bin_item.get("note") or "").strip(),
            }
        )
    return normalized


def _normalize_table(headers: Any, rows: list[Any], title: str) -> dict[str, Any] | None:
    normalized_headers: list[str] = []
    normalized_rows: list[list[str]] = []

    if isinstance(rows[0], dict):
        if not isinstance(headers, list) or not headers:
            headers = list(rows[0].keys())
        normalized_headers = [str(header).strip() for header in headers if str(header).strip()]
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized_rows.append([str(row.get(header, "")).strip() for header in normalized_headers])
    else:
        if not isinstance(headers, list) or not headers:
            return None
        normalized_headers = [str(header).strip() for header in headers if str(header).strip()]
        for row in rows:
            if not isinstance(row, list):
                continue
            cells = [str(cell).strip() for cell in row]
            if len(cells) < len(normalized_headers):
                cells.extend([""] * (len(normalized_headers) - len(cells)))
            normalized_rows.append(cells[: len(normalized_headers)])

    if not normalized_headers or not normalized_rows:
        return None

    numeric_column_indexes = _numeric_column_indexes(normalized_rows)
    first_column_values = [row[0] for row in normalized_rows if row]
    shape = "row_column_table"
    if any(len(cell) > 24 for row in normalized_rows for cell in row[1:]):
        shape = "text_rich_table"
    elif all(_looks_time_like(value) for value in first_column_values if value):
        shape = "text_rich_table"

    return {
        "shape": shape,
        "title": title,
        "headers": normalized_headers,
        "rows": normalized_rows,
        "numeric_column_indexes": numeric_column_indexes,
        "source_notes": [],
    }


def _numeric_column_indexes(rows: list[list[str]]) -> list[int]:
    if not rows:
        return []
    max_width = max(len(row) for row in rows)
    numeric_indexes: list[int] = []
    for index in range(max_width):
        numeric_count = 0
        total = 0
        for row in rows:
            if index >= len(row):
                continue
            total += 1
            if _coerce_number(row[index]) is not None:
                numeric_count += 1
        if total and numeric_count >= max(1, total // 2):
            numeric_indexes.append(index)
    return numeric_indexes


def _looks_like_ohlc_series(points: list[Any]) -> bool:
    first = points[0]
    if not isinstance(first, dict):
        return False
    return all(key in first for key in ("open", "high", "low", "close"))


def _looks_like_distribution_bins(bins: list[Any]) -> bool:
    first = bins[0]
    if not isinstance(first, dict):
        return False
    return "count" in first or ("start" in first and "end" in first and ("value" in first or "y" in first))


def _looks_like_share_breakdown(records: list[dict[str, Any]]) -> bool:
    if len(records) < 2:
        return False
    total = sum(float(record.get("value") or 0.0) for record in records)
    return 95.0 <= total <= 105.0


def _format_number(value: float) -> str:
    return f"{int(value)}" if float(value).is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _looks_time_like(value: str) -> bool:
    text = str(value).strip()
    if len(text) == 4 and text.isdigit():
        return True
    if "-" in text or "/" in text or "." in text:
        return True
    return False


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    text = value.strip().replace(",", "")
    if not text:
        return None
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return None
