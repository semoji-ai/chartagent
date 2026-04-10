from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any

from chartagent.contracts.chart_task import normalize_chart_task
from chartagent.contracts.dataset_schema import normalize_dataset
from chartagent.design.style_resolver import resolve_style_spec
from chartagent.normalizers.display_simplifier import simplify_dataset_for_display
from chartagent.qa.chart_quality import evaluate_chart_quality
from chartagent.qa.design_quality import evaluate_design_quality
from chartagent.renderers.svg_renderer import render_chart_svg
from chartagent.selectors.chart_family_selector import select_chart_family


@dataclass
class ChartAgentBuildResult:
    valid: bool
    chart_task: dict[str, Any]
    dataset_normalized: dict[str, Any]
    chart_spec: dict[str, Any]
    render_svg: str
    notes_md: str
    issues: list[dict[str, str]] = field(default_factory=list)


def build_chart_artifacts(chart_task_data: dict[str, Any]) -> ChartAgentBuildResult:
    task_result = normalize_chart_task(chart_task_data)
    dataset_result = normalize_dataset(task_result.normalized.get("dataset") or {})
    simplified_dataset, simplification_issues = simplify_dataset_for_display(
        task=task_result.normalized,
        dataset=dataset_result.normalized,
    )
    issues = [
        {"level": issue.level, "message": issue.message}
        for issue in [*task_result.issues, *dataset_result.issues]
    ]
    issues.extend(simplification_issues)
    if not task_result.valid or not dataset_result.valid:
        return ChartAgentBuildResult(
            valid=False,
            chart_task=task_result.normalized,
            dataset_normalized=simplified_dataset,
            chart_spec={},
            render_svg="",
            notes_md=_build_notes(task=task_result.normalized, chart_spec={}, issues=issues),
            issues=issues,
        )

    selection = select_chart_family(task_result.normalized, simplified_dataset)
    style_spec = resolve_style_spec(
        task=task_result.normalized,
        dataset=simplified_dataset,
        chart_family=selection.chart_family,
    )
    quality_issues = evaluate_chart_quality(
        task=task_result.normalized,
        dataset=simplified_dataset,
        chart_family=selection.chart_family,
    )
    design_issues = evaluate_design_quality(
        task=task_result.normalized,
        dataset=simplified_dataset,
        chart_family=selection.chart_family,
        style_spec=style_spec,
    )
    issues.extend(
        {"level": issue.level, "message": issue.message}
        for issue in [*quality_issues, *design_issues]
    )
    chart_spec = _build_chart_spec(
        task=task_result.normalized,
        dataset=simplified_dataset,
        selection=selection,
        quality_issues=quality_issues,
        design_issues=design_issues,
        style_spec=style_spec,
    )
    render_svg = render_chart_svg(chart_spec, simplified_dataset)
    return ChartAgentBuildResult(
        valid=True,
        chart_task=task_result.normalized,
        dataset_normalized=simplified_dataset,
        chart_spec=chart_spec,
        render_svg=render_svg,
        notes_md=_build_notes(
            task=task_result.normalized,
            chart_spec=chart_spec,
            issues=issues,
        ),
        issues=issues,
    )


def write_chart_outputs(chart_task_path: Path, output_dir: Path) -> dict[str, str]:
    chart_task_data = json.loads(Path(chart_task_path).read_text(encoding="utf-8"))
    result = build_chart_artifacts(chart_task_data)
    output_dir.mkdir(parents=True, exist_ok=True)

    task_out = output_dir / "chart_task.normalized.json"
    dataset_json_out = output_dir / "dataset.normalized.json"
    dataset_csv_out = output_dir / "dataset.normalized.csv"
    chart_spec_out = output_dir / "chart_spec.json"
    notes_out = output_dir / "notes.md"

    task_out.write_text(json.dumps(result.chart_task, ensure_ascii=False, indent=2), encoding="utf-8")
    dataset_json_out.write_text(
        json.dumps(result.dataset_normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    chart_spec_out.write_text(json.dumps(result.chart_spec, ensure_ascii=False, indent=2), encoding="utf-8")
    dataset_csv_out.write_text(_dataset_to_csv(result.dataset_normalized), encoding="utf-8")
    notes_out.write_text(result.notes_md, encoding="utf-8")

    outputs = {
        "chart_task_normalized": str(task_out),
        "dataset_normalized_json": str(dataset_json_out),
        "dataset_normalized_csv": str(dataset_csv_out),
        "chart_spec": str(chart_spec_out),
        "notes": str(notes_out),
    }
    if result.render_svg:
        svg_out = output_dir / "render.svg"
        svg_out.write_text(result.render_svg, encoding="utf-8")
        outputs["render_svg"] = str(svg_out)
    return outputs


def _build_chart_spec(
    task: dict[str, Any],
    dataset: dict[str, Any],
    selection: Any,
    quality_issues: list[Any],
    design_issues: list[Any],
    style_spec: dict[str, Any],
) -> dict[str, Any]:
    chart_family = selection.chart_family
    return {
        "task_id": task.get("task_id"),
        "chart_family": chart_family,
        "base_chart_family": selection.base_chart_family,
        "chart_variant": selection.chart_variant,
        "title_mode": "question_first" if task.get("question") else "goal_first",
        "title_text": _build_title(task=task, dataset=dataset, chart_family=chart_family),
        "subtitle_text": _build_subtitle(dataset=dataset),
        "annotation_strategy": _annotation_strategy(chart_family),
        "label_strategy": _label_strategy(chart_family, dataset),
        "legend_strategy": _legend_strategy(chart_family),
        "axis_strategy": _axis_strategy(chart_family, dataset),
        "color_strategy": "single_accent",
        "style_spec": style_spec,
        "source_strategy": "source_note" if task.get("source_hints") else "provenance_placeholder",
        "source_note_text": _source_note_text(task),
        "annotations": _build_annotations(task=task, chart_family=chart_family, base_chart_family=selection.base_chart_family, dataset=dataset),
        "font_roles": {
            "chart_title": "chart_title",
            "chart_subtitle": "chart_subtitle",
            "axis_label": "axis_label",
            "axis_tick": "axis_tick",
            "legend_label": "legend_label",
            "value_label": "value_label",
            "callout_label": "callout_label",
            "table_header": "table_header",
            "table_cell": "table_cell",
            "source_note": "source_note",
        },
        "render_hints": _render_hints(chart_family, dataset),
        "table_fallback": selection.table_fallback,
        "why": selection.why,
        "warnings": selection.warnings
        + [issue.message for issue in quality_issues if issue.level == "warning"]
        + [issue.message for issue in design_issues if issue.level == "warning"],
    }


def _build_title(task: dict[str, Any], dataset: dict[str, Any], chart_family: str) -> str:
    if task.get("question"):
        return str(task.get("question"))
    if dataset.get("title"):
        return str(dataset.get("title"))
    goal = str(task.get("goal") or "chart").replace("_", " ").strip()
    if chart_family in {"comparison_table", "fact_table", "timeline_table"}:
        return f"{goal.title()} table"
    return goal.title()


def _build_subtitle(dataset: dict[str, Any]) -> str:
    unit = str(dataset.get("unit") or "").strip()
    return f"단위: {unit}" if unit else ""


def _source_note_text(task: dict[str, Any]) -> str:
    sources = task.get("source_hints") or []
    if not sources:
        return "Source note pending"
    return f"Source: {sources[0]}"


def _annotation_strategy(chart_family: str) -> str:
    if chart_family == "annotated_chart":
        return "essential_callout"
    if chart_family == "stock_candlestick":
        return "latest_move"
    if chart_family in {"donut", "pie"}:
        return "highlight_dominant_slice"
    if chart_family in {"radial_gauge", "semi_donut"}:
        return "highlight_current_value"
    if chart_family == "stacked_progress":
        return "highlight_primary_segment"
    if chart_family == "percentage_progress":
        return "highlight_primary_progress"
    if chart_family == "line":
        return "highlight_latest_point"
    if chart_family == "bar_horizontal":
        return "highlight_top_rank"
    return "minimal"


def _label_strategy(chart_family: str, dataset: dict[str, Any]) -> str:
    if chart_family == "annotated_chart":
        base = str(dataset.get("shape") or "")
        return "callout_with_short_labels" if base in {"label_value_list", "share_breakdown"} else "callout_with_ticks"
    if chart_family == "bar":
        return "short_labels_bottom"
    if chart_family == "distribution_histogram":
        return "bin_labels_bottom"
    if chart_family == "stock_candlestick":
        return "sparse_date_ticks"
    if chart_family in {"radial_gauge", "semi_donut"}:
        return "center_value_with_bounds"
    if chart_family == "stacked_progress":
        return "segment_labels_with_legend"
    if chart_family == "percentage_progress":
        return "labels_with_percentage_fill"
    if chart_family == "bar_horizontal":
        return "long_labels_left"
    if chart_family == "line":
        return "ticks_with_latest_value"
    if dataset.get("shape") in {"row_column_table", "text_rich_table"}:
        return "table_headers"
    return "compact"


def _legend_strategy(chart_family: str) -> str:
    if chart_family == "annotated_chart":
        return "implicit"
    return "none" if chart_family in {"bar", "bar_horizontal", "line", "single_stat", "distribution_histogram", "stock_candlestick", "percentage_progress", "radial_gauge", "semi_donut"} else "implicit"


def _axis_strategy(chart_family: str, dataset: dict[str, Any]) -> str:
    if chart_family == "annotated_chart" and dataset.get("shape") == "time_series":
        return f"x:{dataset.get('x_label', 'x')} y:{dataset.get('y_label', 'y')}"
    if chart_family == "annotated_chart" and dataset.get("shape") in {"label_value_list", "share_breakdown"}:
        return "quantitative_x_only"
    if chart_family == "bar":
        return "categorical_x_quantitative_y"
    if chart_family == "distribution_histogram":
        return "bin_x_frequency_y"
    if chart_family == "stock_candlestick":
        return f"x:{dataset.get('x_label', 'time')} y:{dataset.get('y_label', 'price')}"
    if chart_family == "line":
        return f"x:{dataset.get('x_label', 'x')} y:{dataset.get('y_label', 'y')}"
    if chart_family == "stacked_progress":
        return "stacked_percentage_fill_0_to_100"
    if chart_family == "percentage_progress":
        return "percentage_fill_0_to_100"
    if chart_family == "bar_horizontal":
        return "quantitative_x_only"
    return "none"


def _render_hints(chart_family: str, dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "backend": "svg",
        "preferred_width": 960,
        "preferred_height": 560 if chart_family in {"bar", "line", "annotated_chart", "distribution_histogram", "stock_candlestick", "pie", "stacked_progress"} else 520,
        "normalized_shape": dataset.get("shape"),
    }


def _build_annotations(
    task: dict[str, Any],
    chart_family: str,
    base_chart_family: str | None,
    dataset: dict[str, Any],
) -> list[dict[str, Any]]:
    effective_family = base_chart_family or chart_family
    if chart_family == "annotated_chart":
        return _build_annotated_callouts(task=task, base_chart_family=effective_family, dataset=dataset)
    if chart_family == "bar_horizontal":
        records = dataset.get("records") or []
        if not records:
            return []
        top_record = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [{"target": "top_rank", "label": top_record.get("label"), "value": top_record.get("value")}]
    if chart_family == "bar":
        records = dataset.get("records") or []
        if not records:
            return []
        top_record = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [{"target": "top_rank", "label": top_record.get("label"), "value": top_record.get("value")}]
    if chart_family == "line":
        points = dataset.get("points") or []
        if not points:
            return []
        latest = points[-1]
        return [{"target": "latest_point", "x": latest.get("x"), "y": latest.get("y")}]
    if chart_family == "distribution_histogram":
        bins = dataset.get("bins") or []
        if not bins:
            return []
        dominant = max(bins, key=lambda item: float(item.get("count") or 0.0))
        return [{"target": "dominant_bin", "label": dominant.get("label"), "count": dominant.get("count")}]
    if chart_family == "stock_candlestick":
        candles = dataset.get("candles") or []
        if not candles:
            return []
        latest = candles[-1]
        return [{"target": "latest_candle", "x": latest.get("x"), "close": latest.get("close")}]
    if chart_family in {"donut", "pie"}:
        records = dataset.get("records") or []
        if not records:
            return []
        dominant = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [{"target": "dominant_slice", "label": dominant.get("label"), "value": dominant.get("value")}]
    if chart_family in {"radial_gauge", "semi_donut"}:
        return [{"target": "current_value", "label": dataset.get("label"), "value": dataset.get("value")}]
    if chart_family == "stacked_progress":
        records = dataset.get("records") or []
        if not records:
            return []
        dominant = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [{"target": "dominant_segment", "label": dominant.get("label"), "value": dominant.get("value")}]
    if chart_family == "percentage_progress":
        if dataset.get("shape") == "single_value":
            return [{"target": "primary_progress", "label": dataset.get("label"), "value": dataset.get("value")}]
        records = dataset.get("records") or []
        if not records:
            return []
        primary = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [{"target": "primary_progress", "label": primary.get("label"), "value": primary.get("value")}]
    if chart_family == "metric_wall":
        return [
            {"target": "card", "label": record.get("label"), "value": record.get("value")}
            for record in (dataset.get("records") or [])
        ]
    return []


def _build_annotated_callouts(
    task: dict[str, Any],
    base_chart_family: str,
    dataset: dict[str, Any],
) -> list[dict[str, Any]]:
    explicit = _coerce_annotation_constraints(task)
    if base_chart_family == "line":
        points = dataset.get("points") or []
        if not points:
            return []
        if explicit and explicit.get("target") in {"point", "latest_point", "peak", "dip"}:
            return [_resolve_line_annotation(explicit=explicit, points=points)]
        context = task.get("context") or {}
        if isinstance(context.get("events"), list) and context.get("events"):
            event = context["events"][0]
            return [_resolve_line_annotation(explicit=event, points=points)]
        signal_text = " ".join([str(task.get("goal") or "").lower(), str(task.get("question") or "").lower()])
        target = "peak" if any(token in signal_text for token in ("peak", "최고", "정점", "급증")) else "dip" if any(token in signal_text for token in ("dip", "최저", "급락")) else "latest_point"
        return [_resolve_line_annotation(explicit={"target": target}, points=points)]
    if base_chart_family in {"bar_horizontal", "bar"}:
        records = dataset.get("records") or []
        if not records:
            return []
        if explicit and explicit.get("target") in {"bar", "top_rank"}:
            match_label = str(explicit.get("match_label") or "").strip()
            if match_label:
                matched = next((record for record in records if str(record.get("label") or "") == match_label), None)
                if matched:
                    return [
                        {
                            "target": "bar",
                            "label": matched.get("label"),
                            "value": matched.get("value"),
                            "label_text": str(explicit.get("label") or matched.get("label") or "Highlighted bar"),
                        }
                    ]
        top_record = max(records, key=lambda record: float(record.get("value") or 0.0))
        return [
            {
                "target": "top_rank",
                "label": top_record.get("label"),
                "value": top_record.get("value"),
                "label_text": str(top_record.get("label") or "Top rank"),
            }
        ]
    return []


def _coerce_annotation_constraints(task: dict[str, Any]) -> dict[str, Any] | None:
    constraints = task.get("constraints") or {}
    annotations = constraints.get("annotations")
    if isinstance(annotations, list) and annotations:
        first = annotations[0]
        if isinstance(first, dict):
            return first
    return None


def _resolve_line_annotation(explicit: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    target = str(explicit.get("target") or "").strip() or "latest_point"
    match_x = str(explicit.get("match_x") or explicit.get("x") or "").strip()
    if match_x:
        matched = next((point for point in points if str(point.get("x") or "") == match_x), None)
        if matched:
            return {
                "target": "point",
                "x": matched.get("x"),
                "y": matched.get("y"),
                "label": str(explicit.get("label") or matched.get("x") or "Key point"),
            }
    if target == "peak":
        matched = max(points, key=lambda point: float(point.get("y") or 0.0))
        return {"target": "point", "x": matched.get("x"), "y": matched.get("y"), "label": f"Peak: {matched.get('x')}"}
    if target == "dip":
        matched = min(points, key=lambda point: float(point.get("y") or 0.0))
        return {"target": "point", "x": matched.get("x"), "y": matched.get("y"), "label": f"Dip: {matched.get('x')}"}
    matched = points[-1]
    return {
        "target": "latest_point",
        "x": matched.get("x"),
        "y": matched.get("y"),
        "label": str(explicit.get("label") or f"Latest: {matched.get('x')}"),
    }


def _dataset_to_csv(dataset: dict[str, Any]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    shape = dataset.get("shape")
    if shape == "single_value":
        writer.writerow(["label", "value", "unit"])
        writer.writerow([dataset.get("label", ""), dataset.get("value", ""), dataset.get("unit", "")])
    elif shape in {"label_value_list", "share_breakdown"}:
        writer.writerow(["label", "value", "unit", "note"])
        for record in dataset.get("records") or []:
            writer.writerow(
                [record.get("label", ""), record.get("value", ""), record.get("unit", ""), record.get("note", "")]
            )
    elif shape == "time_series":
        writer.writerow(["x", "y", "unit", "note"])
        for point in dataset.get("points") or []:
            writer.writerow([point.get("x", ""), point.get("y", ""), point.get("unit", ""), point.get("note", "")])
    elif shape in {"row_column_table", "text_rich_table"}:
        writer.writerow(dataset.get("headers") or [])
        for row in dataset.get("rows") or []:
            writer.writerow(row)
    return buffer.getvalue()


def _build_notes(task: dict[str, Any], chart_spec: dict[str, Any], issues: list[dict[str, str]]) -> str:
    lines = [
        "# ChartAgent Notes",
        "",
        f"- task_id: {task.get('task_id', 'unknown')}",
    ]
    if chart_spec:
        lines.extend(
            [
                f"- chart_family: {chart_spec.get('chart_family', 'unknown')}",
                f"- chart_variant: {chart_spec.get('chart_variant', 'unknown')}",
                f"- theme_set: {chart_spec.get('style_spec', {}).get('theme_set', 'unknown')}",
                f"- theme: {chart_spec.get('style_spec', {}).get('theme_name', 'unknown')}",
                f"- visual_mode: {chart_spec.get('style_spec', {}).get('visual_mode', 'unknown')}",
                f"- layout_preset: {chart_spec.get('style_spec', {}).get('layout_preset', 'unknown')}",
                f"- reference_profile: {chart_spec.get('style_spec', {}).get('reference_profile', 'unknown')}",
                f"- style_combo_preset: {chart_spec.get('style_spec', {}).get('style_combo_preset', 'unknown')}",
                f"- pattern_format_preset: {chart_spec.get('style_spec', {}).get('pattern_format_preset', 'none')}",
            ]
        )
        for source_ref in chart_spec.get("style_spec", {}).get("theme_source_refs") or []:
            lines.append(f"- source_ref: {source_ref}")
        for reason in chart_spec.get("why") or []:
            lines.append(f"- why: {reason}")
        for warning in chart_spec.get("warnings") or []:
            lines.append(f"- warning: {warning}")
    for issue in issues:
        lines.append(f"- {issue.get('level', 'info')}: {issue.get('message', '')}")
    return "\n".join(lines) + "\n"
