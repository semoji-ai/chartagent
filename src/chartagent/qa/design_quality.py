from __future__ import annotations

from typing import Any

from chartagent.qa.chart_quality import ChartQualityIssue


def evaluate_design_quality(
    task: dict[str, Any],
    dataset: dict[str, Any],
    chart_family: str,
    style_spec: dict[str, Any],
) -> list[ChartQualityIssue]:
    issues: list[ChartQualityIssue] = []
    density = str(style_spec.get("density") or "")
    visual_mode = str(style_spec.get("visual_mode") or "")
    emphasis_level = str(style_spec.get("emphasis_level") or "")
    layout_preset = str(style_spec.get("layout_preset") or "")
    legend_placement = str(style_spec.get("legend_placement") or "")
    theme_tokens = style_spec.get("theme_tokens") or {}
    motif_tokens = style_spec.get("motif_tokens") or {}
    pattern_policy = style_spec.get("pattern_policy") or {}
    record_count = len(dataset.get("records") or [])
    header_count = len(dataset.get("headers") or [])
    requested_annotations = task.get("constraints", {}).get("annotations") or []
    label_lengths = [len(str(record.get("display_label") or record.get("label") or "")) for record in dataset.get("records") or []]

    if chart_family in {"donut", "pie", "stacked_progress"} and record_count > 5:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="dense_legend_risk",
                message="Legend density is high for the chosen composition style.",
            )
        )

    if legend_placement in {"right_rail", "bottom_stack"} and record_count >= 5 and max(label_lengths or [0]) >= 10:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="legend_crowding_risk",
                message="Legend labels are long enough to crowd the current legend layout.",
            )
        )

    if isinstance(requested_annotations, list) and len(requested_annotations) > 1:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="overannotation_risk",
                message="Too many explicit annotations may weaken the focal point.",
            )
        )

    if chart_family == "metric_wall" and record_count >= 4 and density != "compact":
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="weak_hierarchy_risk",
                message="Metric walls with many KPI cards need tighter hierarchy than the current density suggests.",
            )
        )

    if chart_family == "metric_wall" and emphasis_level != "medium":
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="weak_hierarchy_risk",
                message="Metric walls should keep a medium emphasis profile so the KPI values stay dominant.",
            )
        )

    if chart_family in {"comparison_table", "timeline_table"} and header_count >= 5 and visual_mode == "broadcast":
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="scan_speed_risk",
                message="Broadcast styling can reduce scan speed for dense table views.",
            )
        )

    if layout_preset == "balanced_canvas" and chart_family == "annotated_chart":
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="annotation_space_risk",
                message="Annotated charts need a stronger stage layout than a neutral canvas.",
            )
        )

    if chart_family in {"line", "annotated_chart"} and motif_tokens.get("primary_dasharray"):
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="primary_line_dash_risk",
                message="Primary trend lines should stay solid; reserve dash patterns for guide lines or connectors.",
            )
        )

    if chart_family not in {"line", "annotated_chart", "stock_candlestick"} and motif_tokens.get("marker_style") not in {None, "", "none", "dot"}:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="marker_language_risk",
                message="Marker styles richer than simple dots should be limited to line or market charts.",
            )
        )

    if pattern_policy.get("enabled"):
        if chart_family in {"donut", "pie"} and record_count > 4:
            issues.append(
                ChartQualityIssue(
                    level="warning",
                    code="pattern_overuse_risk",
                    message="Pattern fills on composition charts should stay limited to a small number of slices.",
                )
            )
        if chart_family in {"bar", "bar_horizontal", "stacked_progress", "percentage_progress"} and record_count > 6:
            issues.append(
                ChartQualityIssue(
                    level="warning",
                    code="pattern_overuse_risk",
                    message="Pattern fills should be reserved for only a few highlighted categories, not dense category sets.",
                )
            )

    if _contrast_ratio(
        str(theme_tokens.get("text_primary") or "#0f172a"),
        str(theme_tokens.get("bg") or "#ffffff"),
    ) < 4.5:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="low_contrast_risk",
                message="Primary text contrast is lower than the desired readability threshold.",
            )
        )

    if _contrast_ratio(
        str(theme_tokens.get("text_secondary") or "#334155"),
        str(theme_tokens.get("bg") or "#ffffff"),
    ) < 3.0:
        issues.append(
            ChartQualityIssue(
                level="warning",
                code="secondary_contrast_risk",
                message="Secondary text contrast may be too soft for extended reading.",
            )
        )

    return issues


def _contrast_ratio(foreground: str, background: str) -> float:
    fg = _relative_luminance(_hex_to_rgb(foreground))
    bg = _relative_luminance(_hex_to_rgb(background))
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return (lighter + 0.05) / (darker + 0.05)


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    def _channel(value: int) -> float:
        normalized = value / 255.0
        if normalized <= 0.03928:
            return normalized / 12.92
        return ((normalized + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    normalized = value.strip().lstrip("#")
    if len(normalized) == 3:
        normalized = "".join(ch * 2 for ch in normalized)
    if len(normalized) != 6:
        return (15, 23, 42)
    return (
        int(normalized[0:2], 16),
        int(normalized[2:4], 16),
        int(normalized[4:6], 16),
    )
