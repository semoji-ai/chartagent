from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChartFamilySelectionResult:
    chart_family: str
    chart_variant: str
    base_chart_family: str | None = None
    why: list[str] = field(default_factory=list)
    table_fallback: str | None = None
    warnings: list[str] = field(default_factory=list)


def select_chart_family(task: dict[str, Any], dataset: dict[str, Any]) -> ChartFamilySelectionResult:
    shape = str(dataset.get("shape") or "unknown").strip()
    preferred_output = {value.lower() for value in task.get("preferred_output", [])}
    goal = str(task.get("goal") or "").lower()
    question = str(task.get("question") or "").lower()
    source_hints = task.get("source_hints") or []

    warnings: list[str] = []
    if not source_hints and not task.get("fallback_policy", {}).get("allow_chart_without_source", False):
        warnings.append("Source note is missing; render should include an explicit provenance placeholder.")

    if shape == "single_value":
        if _wants_semi_donut(task):
            return ChartFamilySelectionResult(
                chart_family="semi_donut",
                chart_variant="half_gauge",
                why=["The task explicitly asks for a half-ring gauge treatment."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if _wants_radial_gauge(task):
            return ChartFamilySelectionResult(
                chart_family="radial_gauge",
                chart_variant="full_gauge",
                why=["The task explicitly asks for a radial gauge treatment."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if _looks_like_percentage_progress(task=task, dataset=dataset):
            return ChartFamilySelectionResult(
                chart_family="percentage_progress",
                chart_variant="single_progress",
                why=["A single percent-like value is better read as progress than as a raw statistic."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        return ChartFamilySelectionResult(
            chart_family="single_stat",
            chart_variant="default",
            why=["The dataset contains a single numeric value, so a single statistic is clearest."],
            table_fallback="fact_table",
            warnings=warnings,
        )

    if shape == "time_series":
        if _needs_annotation(task):
            return ChartFamilySelectionResult(
                chart_family="annotated_chart",
                base_chart_family="line",
                chart_variant="line_callout",
                why=["The task implies a trend plus an explicit callout, so an annotated line chart fits best."],
                table_fallback="timeline_table",
                warnings=warnings,
            )
        return ChartFamilySelectionResult(
            chart_family="line",
            chart_variant="trend",
            why=["Ordered x values and numeric y values indicate a time-series trend."],
            table_fallback="timeline_table",
            warnings=warnings,
        )

    if shape == "ohlc_series":
        return ChartFamilySelectionResult(
            chart_family="stock_candlestick",
            chart_variant="ohlc",
            why=["Open, high, low, and close values indicate stock-style price movement data."],
            table_fallback="timeline_table",
            warnings=warnings,
        )

    if shape == "distribution_bins":
        return ChartFamilySelectionResult(
            chart_family="distribution_histogram",
            chart_variant="histogram",
            why=["Binned counts describe a distribution, so a histogram is the clearest fit."],
            table_fallback="fact_table",
            warnings=warnings,
        )

    if shape == "share_breakdown":
        if _wants_stacked_progress(task):
            return ChartFamilySelectionResult(
                chart_family="stacked_progress",
                chart_variant="stacked_share",
                why=["The task asks for a stacked progress-style composition bar."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if _wants_progress(task=task):
            return ChartFamilySelectionResult(
                chart_family="percentage_progress",
                chart_variant="multi_progress",
                why=["The task asks for progress-style percentage comparison rather than radial composition."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if _wants_pie(task=task):
            return ChartFamilySelectionResult(
                chart_family="pie",
                chart_variant="share",
                why=["The task explicitly asks for a pie-style share chart."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        return ChartFamilySelectionResult(
            chart_family="donut",
            chart_variant="share",
            why=["The task is framed as a share breakdown, so a donut is a compact default."],
            table_fallback="fact_table",
            warnings=warnings,
        )

    if shape == "label_value_list":
        records = dataset.get("records") or []
        long_labels = any(len(str(item.get("label") or "")) > 10 for item in records)
        short_labels = all(len(str(item.get("label") or "")) <= 10 for item in records)
        few_categories = len(records) <= 6
        wants_three_d = _needs_three_d_variant(task)
        if _looks_like_multi_percentage_progress(task=task, records=records):
            return ChartFamilySelectionResult(
                chart_family="percentage_progress",
                chart_variant="multi_progress",
                why=["Percent-like category values plus a progress framing fit progress bars best."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if _looks_like_metric_wall(task=task, records=records):
            return ChartFamilySelectionResult(
                chart_family="metric_wall",
                chart_variant="kpi_cards",
                why=["A small set of KPIs is better shown as a metric wall than as ranked bars."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if len(records) <= 1:
            return ChartFamilySelectionResult(
                chart_family="single_stat",
                chart_variant="default",
                why=["Only one category remains after normalization."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if "table" in preferred_output and "chart" not in preferred_output:
            return ChartFamilySelectionResult(
                chart_family="fact_table",
                chart_variant="lookup",
                why=["The task explicitly prefers a table output."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        if len(records) > task.get("fallback_policy", {}).get("max_categories", 8):
            warnings.append("Category count exceeds the preferred maximum; consider pruning or collapsing tails.")
        why = ["The dataset compares named categories with numeric values."]
        if long_labels:
            why.append("Labels are long enough that horizontal bars will read better than vertical bars.")
        if few_categories and short_labels:
            if _needs_annotation(task):
                return ChartFamilySelectionResult(
                    chart_family="annotated_chart",
                    base_chart_family="bar",
                    chart_variant="bar_callout",
                    why=["Few categories with short labels fit a vertical bar layout."] + ["The task also calls for an explicit callout."],
                    table_fallback="comparison_table",
                    warnings=warnings,
                )
            return ChartFamilySelectionResult(
                chart_family="bar",
                chart_variant="three_d" if wants_three_d else "vertical",
                why=[
                    "Few categories with short labels fit a vertical bar chart.",
                    "The visual can prioritize quick category comparison without rotating labels.",
                ],
                table_fallback="comparison_table",
                warnings=warnings,
            )
        if _needs_annotation(task):
            return ChartFamilySelectionResult(
                chart_family="annotated_chart",
                base_chart_family="bar_horizontal",
                chart_variant="bar_callout",
                why=why + ["The task also calls for an explicit callout rather than a raw ranking alone."],
                table_fallback="comparison_table",
                warnings=warnings,
            )
        return ChartFamilySelectionResult(
            chart_family="bar_horizontal",
            chart_variant="ranking",
            why=why,
            table_fallback="comparison_table",
            warnings=warnings,
        )

    if shape in {"row_column_table", "text_rich_table"}:
        headers = dataset.get("headers") or []
        numeric_columns = dataset.get("numeric_column_indexes") or []
        if _looks_like_timeline_table(headers=headers, rows=dataset.get("rows") or []):
            return ChartFamilySelectionResult(
                chart_family="timeline_table",
                chart_variant="chronology",
                why=["The first column reads like time and the rows carry event detail."],
                table_fallback="timeline_table",
                warnings=warnings,
            )
        if _should_use_fact_table(headers=headers, numeric_columns=numeric_columns, goal=goal, question=question):
            return ChartFamilySelectionResult(
                chart_family="fact_table",
                chart_variant="lookup",
                why=["The task looks more like exact lookup than shape-based visual comparison."],
                table_fallback="fact_table",
                warnings=warnings,
            )
        return ChartFamilySelectionResult(
            chart_family="comparison_table",
            chart_variant="matrix",
            why=["Multiple columns and row-wise comparison make a table clearer than a chart."],
            table_fallback="comparison_table",
            warnings=warnings,
        )

    warnings.append("Dataset shape is not fully supported; falling back to fact_table.")
    return ChartFamilySelectionResult(
        chart_family="fact_table",
        chart_variant="fallback",
        why=["Unsupported dataset shape fell back to a table-safe presentation."],
        table_fallback="fact_table",
        warnings=warnings,
    )


def _should_use_fact_table(
    headers: list[str],
    numeric_columns: list[int],
    goal: str,
    question: str,
) -> bool:
    if len(headers) <= 2:
        return True
    if len(numeric_columns) <= 1 and ("spec" in question or "fact" in goal or "lookup" in goal):
        return True
    return False


def _looks_like_timeline_table(headers: list[str], rows: list[list[str]]) -> bool:
    if not headers or not rows:
        return False
    first_header = str(headers[0]).lower()
    if any(token in first_header for token in ("year", "date", "time", "시기", "연도", "날짜")):
        return True
    first_column = [row[0] for row in rows if row]
    return bool(first_column) and all(_looks_time_like(value) for value in first_column if value)


def _looks_time_like(value: str) -> bool:
    text = str(value).strip()
    if len(text) == 4 and text.isdigit():
        return True
    return "-" in text or "/" in text or "." in text


def _looks_like_metric_wall(task: dict[str, Any], records: list[dict[str, Any]]) -> bool:
    if not (2 <= len(records) <= 4):
        return False
    goal = str(task.get("goal") or "").lower()
    question = str(task.get("question") or "").lower()
    context = task.get("context") or {}
    signals = " ".join(
        [
            goal,
            question,
            str(context.get("summary") or "").lower(),
            str(context.get("presentation_mode") or "").lower(),
        ]
    )
    return any(token in signals for token in ("kpi", "metric", "dashboard", "summary", "headline"))


def _wants_pie(task: dict[str, Any]) -> bool:
    signals = _task_signal_text(task)
    return any(token in signals for token in ("pie", "파이", "원형", "원그래프"))


def _wants_radial_gauge(task: dict[str, Any]) -> bool:
    signals = _task_signal_text(task)
    return any(token in signals for token in ("radial gauge", "gauge", "게이지", "원형 게이지", "원형게이지", "circular gauge"))


def _wants_semi_donut(task: dict[str, Any]) -> bool:
    signals = _task_signal_text(task)
    return any(
        token in signals
        for token in ("semi", "semi-donut", "semi donut", "half donut", "half gauge", "반원", "반도넛", "반원 게이지", "반원게이지")
    )


def _wants_stacked_progress(task: dict[str, Any]) -> bool:
    signals = _task_signal_text(task)
    return any(
        token in signals
        for token in ("stacked progress", "stacked", "누적", "구성 바", "구성바", "누적 바", "누적바", "stack bar")
    )


def _wants_progress(task: dict[str, Any]) -> bool:
    signals = _task_signal_text(task)
    return any(
        token in signals
        for token in ("progress", "진행률", "진척", "달성률", "완료율", "달성도", "게이지", "프로그레스", "채움")
    )


def _looks_like_percentage_progress(task: dict[str, Any], dataset: dict[str, Any]) -> bool:
    unit = str(dataset.get("unit") or "").strip()
    value = dataset.get("value")
    if value is None:
        return False
    numeric_value = float(value)
    return _wants_progress(task) or (unit == "%" and 0.0 <= numeric_value <= 100.0)


def _looks_like_multi_percentage_progress(task: dict[str, Any], records: list[dict[str, Any]]) -> bool:
    if not records:
        return False
    if _wants_progress(task):
        return True
    units = {str(record.get("unit") or "").strip() for record in records}
    if units != {"%"}:
        return False
    return all(0.0 <= float(record.get("value") or 0.0) <= 100.0 for record in records)


def _task_signal_text(task: dict[str, Any]) -> str:
    context = task.get("context") or {}
    return " ".join(
        [
            str(task.get("goal") or "").lower(),
            str(task.get("question") or "").lower(),
            str(context.get("summary") or "").lower(),
            str(context.get("presentation_mode") or "").lower(),
        ]
    )


def _needs_annotation(task: dict[str, Any]) -> bool:
    constraints = task.get("constraints") or {}
    if isinstance(constraints.get("annotations"), list) and constraints.get("annotations"):
        return True
    context = task.get("context") or {}
    if isinstance(context.get("events"), list) and context.get("events"):
        return True
    signals = " ".join(
        [
            str(task.get("goal") or "").lower(),
            str(task.get("question") or "").lower(),
            str(context.get("summary") or "").lower(),
        ]
    )
    keywords = (
        "peak",
        "dip",
        "policy",
        "event",
        "callout",
        "change",
        "정점",
        "최고",
        "최저",
        "급증",
        "급락",
        "정책",
        "전환",
        "이벤트",
        "강조",
    )
    return any(keyword in signals for keyword in keywords)


def _needs_three_d_variant(task: dict[str, Any]) -> bool:
    constraints = task.get("constraints") or {}
    context = task.get("context") or {}
    signals = " ".join(
        [
            str(task.get("goal") or "").lower(),
            str(task.get("question") or "").lower(),
            str(context.get("visual_style") or "").lower(),
            str(constraints.get("style_variant") or "").lower(),
        ]
    )
    return any(keyword in signals for keyword in ("3d", "three-d", "three d", "isometric", "입체"))
