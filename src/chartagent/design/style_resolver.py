from __future__ import annotations

from typing import Any

from chartagent.design.pattern_formats import get_pattern_format
from chartagent.design.pattern_formats import resolve_pattern_format
from chartagent.design.reference_profiles import get_reference_profile
from chartagent.design.reference_profiles import resolve_reference_profile
from chartagent.design.style_combos import get_style_combo
from chartagent.design.style_combos import resolve_style_combo
from chartagent.design.theme_sets import (
    apply_theme_customization,
    get_theme_set_spec,
    infer_theme_set,
)
from chartagent.design.themes import get_theme_tokens


def resolve_style_spec(
    task: dict[str, Any],
    dataset: dict[str, Any],
    chart_family: str,
) -> dict[str, Any]:
    inferred_theme_name = _resolve_theme_name(task=task, dataset=dataset, chart_family=chart_family)
    inferred_style_combo = _resolve_style_combo_default(
        theme_name=inferred_theme_name,
        chart_family=chart_family,
        task=task,
        dataset=dataset,
    )
    requested_theme_set = str(task.get("theme_set") or "").strip()
    inferred_theme_set = infer_theme_set(inferred_theme_name, inferred_style_combo)
    theme_set = requested_theme_set or inferred_theme_set
    theme_set_spec = get_theme_set_spec(theme_set)
    theme_name = inferred_theme_name
    if requested_theme_set:
        theme_name = str(theme_set_spec.get("theme_name") or inferred_theme_name)
    visual_mode = theme_name
    density = _resolve_density(dataset=dataset, chart_family=chart_family)
    emphasis_level = _resolve_emphasis_level(chart_family=chart_family)
    tone = _resolve_tone(theme_name=theme_name)
    layout_preset = _resolve_layout_preset(chart_family=chart_family, theme_name=theme_name)
    legend_placement = _resolve_legend_placement(chart_family=chart_family, layout_preset=layout_preset)
    reference_profile = _resolve_reference_profile(
        theme_name=theme_name,
        chart_family=chart_family,
        theme_set_spec=theme_set_spec if requested_theme_set else {},
    )
    style_combo = _resolve_style_combo(
        theme_name=theme_name,
        chart_family=chart_family,
        task=task,
        dataset=dataset,
        theme_set_spec=theme_set_spec if requested_theme_set else {},
    )
    pattern_policy = _resolve_pattern_policy(task=task, dataset=dataset, chart_family=chart_family)
    pattern_format = _resolve_pattern_format(
        enabled=bool(pattern_policy.get("enabled")),
        theme_name=theme_name,
        style_combo_key=str(style_combo.get("key") or ""),
        theme_set_spec=theme_set_spec if requested_theme_set else {},
    )
    base_motif_tokens = _merge_motif_tokens(
        reference_profile.get("motif_tokens") or {},
        style_combo.get("motif_overrides") or {},
        pattern_format.get("motif_overrides") or {},
    )
    base_theme_tokens = get_theme_tokens(theme_name)
    base_layout_tokens = _layout_tokens(layout_preset)
    theme_customization = apply_theme_customization(
        theme_set=theme_set,
        theme_tokens=base_theme_tokens,
        motif_tokens=base_motif_tokens,
        layout_tokens=base_layout_tokens,
        theme_overrides=task.get("theme_overrides") or {},
        theme_reset=task.get("theme_reset") or {},
    )
    theme_customization["motif_tokens"] = _sanitize_motif_tokens_for_family(
        chart_family=chart_family,
        motif_tokens=theme_customization["motif_tokens"],
    )
    return {
        "theme_set": theme_set,
        "theme_set_label": theme_set_spec.get("label"),
        "theme_set_description": theme_set_spec.get("description"),
        "theme_artwork_signature": list(theme_set_spec.get("artwork_signature") or []),
        "theme_source_refs": list(theme_set_spec.get("source_refs") or []),
        "theme_name": theme_name,
        "visual_mode": visual_mode,
        "density": density,
        "emphasis_level": emphasis_level,
        "tone": tone,
        "layout_preset": layout_preset,
        "legend_placement": legend_placement,
        "reference_profile": reference_profile.get("key"),
        "reference_label": reference_profile.get("label"),
        "reference_archetype": reference_profile.get("archetype"),
        "style_combo_preset": style_combo.get("key"),
        "style_combo_label": style_combo.get("label"),
        "style_combo_description": style_combo.get("description"),
        "pattern_format_preset": pattern_format.get("key"),
        "pattern_format_label": pattern_format.get("label"),
        "pattern_format_scope": pattern_format.get("surface_scope"),
        "layout_tokens": theme_customization["layout_tokens"],
        "motif_tokens": theme_customization["motif_tokens"],
        "component_tokens": theme_customization["component_tokens"],
        "pattern_policy": pattern_policy,
        "theme_tokens": theme_customization["theme_tokens"],
        "theme_overrides": theme_customization["active_overrides"],
        "theme_reset": theme_customization["theme_reset"],
    }


def _resolve_theme_name(task: dict[str, Any], dataset: dict[str, Any], chart_family: str) -> str:
    haystack = " ".join(
        [
            str(task.get("goal") or ""),
            str(task.get("question") or ""),
            str(dataset.get("title") or ""),
            " ".join(str(item) for item in (task.get("source_hints") or [])),
        ]
    ).lower()
    if any(keyword in haystack for keyword in ("broadcast", "news", "breaking", "live", "속보", "뉴스", "방송")):
        return "broadcast"
    if chart_family in {"metric_wall", "comparison_table", "fact_table", "timeline_table", "percentage_progress", "radial_gauge", "stacked_progress", "stock_candlestick"}:
        return "dashboard"
    if chart_family in {"donut", "pie", "annotated_chart", "semi_donut"}:
        return "editorial"
    return "minimal"


def _resolve_style_combo_default(theme_name: str, chart_family: str, task: dict[str, Any], dataset: dict[str, Any]) -> str:
    style_combo = resolve_style_combo(theme_name=theme_name, chart_family=chart_family, task=task, dataset=dataset)
    return str(style_combo.get("key") or "neutral_system")


def _resolve_reference_profile(theme_name: str, chart_family: str, theme_set_spec: dict[str, Any]) -> dict[str, Any]:
    explicit_key = str(theme_set_spec.get("reference_profile") or "").strip()
    if explicit_key:
        return get_reference_profile(explicit_key)
    return resolve_reference_profile(theme_name=theme_name, chart_family=chart_family)


def _resolve_style_combo(
    theme_name: str,
    chart_family: str,
    task: dict[str, Any],
    dataset: dict[str, Any],
    theme_set_spec: dict[str, Any],
) -> dict[str, Any]:
    explicit_key = str(theme_set_spec.get("style_combo_preset") or "").strip()
    if explicit_key:
        return get_style_combo(explicit_key)
    return resolve_style_combo(theme_name=theme_name, chart_family=chart_family, task=task, dataset=dataset)


def _resolve_pattern_format(
    *,
    enabled: bool,
    theme_name: str,
    style_combo_key: str,
    theme_set_spec: dict[str, Any],
) -> dict[str, Any]:
    if not enabled:
        return {}
    explicit_key = str(theme_set_spec.get("pattern_format_preset") or "").strip()
    if explicit_key:
        return get_pattern_format(explicit_key)
    return resolve_pattern_format(enabled=enabled, theme_name=theme_name, style_combo_key=style_combo_key)


def _resolve_density(dataset: dict[str, Any], chart_family: str) -> str:
    shape = str(dataset.get("shape") or "")
    if chart_family in {"comparison_table", "fact_table", "timeline_table", "metric_wall"}:
        return "compact"
    if chart_family in {"donut", "pie", "annotated_chart", "semi_donut", "radial_gauge"}:
        return "airy"
    if shape in {"row_column_table", "text_rich_table"}:
        return "compact"
    return "balanced"


def _resolve_emphasis_level(chart_family: str) -> str:
    if chart_family in {"single_stat", "annotated_chart", "radial_gauge", "semi_donut"}:
        return "high"
    if chart_family in {"metric_wall", "percentage_progress", "donut", "pie", "stacked_progress"}:
        return "medium"
    return "low"


def _resolve_tone(theme_name: str) -> str:
    if theme_name == "dashboard":
        return "analytical"
    if theme_name == "editorial":
        return "warm"
    if theme_name == "broadcast":
        return "assertive"
    return "neutral"


def _resolve_layout_preset(chart_family: str, theme_name: str) -> str:
    if theme_name == "broadcast":
        return "flash_panel"
    if chart_family in {"comparison_table", "fact_table", "timeline_table"}:
        return "comparison_sheet"
    if chart_family in {"metric_wall", "single_stat", "percentage_progress", "radial_gauge", "stacked_progress"}:
        return "hero_panel"
    if chart_family in {"donut", "pie", "annotated_chart", "semi_donut"}:
        return "feature_stage"
    if chart_family == "stock_candlestick":
        return "market_terminal"
    return "balanced_canvas"


def _resolve_legend_placement(chart_family: str, layout_preset: str) -> str:
    if chart_family in {"donut", "pie"}:
        return "right_rail"
    if chart_family == "stacked_progress":
        return "bottom_stack"
    if chart_family in {"comparison_table", "fact_table", "timeline_table", "single_stat", "radial_gauge", "semi_donut"}:
        return "none"
    if layout_preset == "flash_panel":
        return "inline"
    return "implicit"


def _layout_tokens(layout_preset: str) -> dict[str, int]:
    presets: dict[str, dict[str, int]] = {
        "balanced_canvas": {
            "title_y": 52,
            "subtitle_y": 82,
            "content_top_with_subtitle": 126,
            "content_top_without_subtitle": 108,
            "plot_left": 80,
            "plot_right": 40,
            "plot_bottom": 90,
            "annotation_rail_width": 0,
            "annotation_rail_gap": 24,
        },
        "comparison_sheet": {
            "title_y": 50,
            "subtitle_y": 78,
            "content_top_with_subtitle": 118,
            "content_top_without_subtitle": 102,
            "plot_left": 60,
            "plot_right": 60,
            "plot_bottom": 70,
            "annotation_rail_width": 0,
            "annotation_rail_gap": 20,
        },
        "hero_panel": {
            "title_y": 52,
            "subtitle_y": 82,
            "content_top_with_subtitle": 126,
            "content_top_without_subtitle": 110,
            "plot_left": 60,
            "plot_right": 60,
            "plot_bottom": 80,
            "annotation_rail_width": 0,
            "annotation_rail_gap": 20,
        },
        "feature_stage": {
            "title_y": 52,
            "subtitle_y": 82,
            "content_top_with_subtitle": 126,
            "content_top_without_subtitle": 108,
            "plot_left": 110,
            "plot_right": 80,
            "plot_bottom": 80,
            "annotation_rail_width": 220,
            "annotation_rail_gap": 24,
        },
        "market_terminal": {
            "title_y": 50,
            "subtitle_y": 78,
            "content_top_with_subtitle": 122,
            "content_top_without_subtitle": 106,
            "plot_left": 84,
            "plot_right": 48,
            "plot_bottom": 92,
            "annotation_rail_width": 0,
            "annotation_rail_gap": 20,
        },
        "flash_panel": {
            "title_y": 56,
            "subtitle_y": 88,
            "content_top_with_subtitle": 134,
            "content_top_without_subtitle": 114,
            "plot_left": 110,
            "plot_right": 72,
            "plot_bottom": 84,
            "annotation_rail_width": 220,
            "annotation_rail_gap": 24,
        },
    }
    return dict(presets.get(layout_preset) or presets["balanced_canvas"])


def _resolve_pattern_policy(task: dict[str, Any], dataset: dict[str, Any], chart_family: str) -> dict[str, Any]:
    supported = chart_family in {"bar", "bar_horizontal", "donut", "pie", "stacked_progress", "percentage_progress"}
    haystack = " ".join(
        [
            str(task.get("goal") or ""),
            str(task.get("question") or ""),
            str(dataset.get("title") or ""),
            " ".join(str(item) for item in (task.get("source_hints") or [])),
        ]
    ).lower()
    notes = _collect_pattern_notes(dataset)
    explicit_pattern = _contains_any(haystack, ("pattern", "stripe", "texture", "hatch", "striped", "줄무늬", "패턴", "텍스처", "빗금", "해치"))
    explicit_outline = _contains_any(
        haystack,
        (
            "outline",
            "outlined",
            "hollow",
            "wireframe",
            "contour",
            "테두리",
            "외곽선",
            "속을 채우지",
            "비어있는",
            "빈 막대",
        ),
    )
    accessibility_mode = _contains_any(haystack, ("accessibility", "accessible", "color blind", "colour blind", "색맹", "고대비"))
    forecast_mode = any(_contains_any(text, ("forecast", "projected", "projection", "estimate", "estimated", "전망", "예상", "추정")) for text in [haystack, *notes])
    incomplete_mode = any(_contains_any(text, ("preliminary", "provisional", "incomplete", "draft", "잠정", "가결산", "미완", "임시")) for text in [haystack, *notes])
    range_mode = any(
        _contains_any(
            text,
            (
                "range",
                "band",
                "confidence",
                "interval",
                "corridor",
                "envelope",
                "구간",
                "범위",
                "신뢰구간",
                "밴드",
            ),
        )
        for text in [haystack, *notes]
    )

    if not supported:
        return {"enabled": False, "reason": "unsupported_family", "target_mode": "none", "pattern_kind": "", "fill_treatment": "solid"}
    if accessibility_mode:
        return {
            "enabled": True,
            "reason": "accessibility",
            "target_mode": "alternating",
            "pattern_kind": "dot_sparse",
            "fill_treatment": "pattern_overlay",
        }
    if range_mode:
        return {
            "enabled": True,
            "reason": "range",
            "target_mode": "tagged_or_secondary",
            "pattern_kind": "diagonal_hatch",
            "fill_treatment": "transparent_range_hatch",
        }
    if incomplete_mode:
        return {
            "enabled": True,
            "reason": "incomplete",
            "target_mode": "tagged_only",
            "pattern_kind": "vertical_stripe",
            "fill_treatment": "outline_only",
        }
    if forecast_mode:
        return {
            "enabled": True,
            "reason": "forecast",
            "target_mode": "tagged_only",
            "pattern_kind": "diagonal_hatch",
            "fill_treatment": "outline_plus_hatch",
        }
    if explicit_pattern and explicit_outline:
        return {
            "enabled": True,
            "reason": "explicit_outline_pattern",
            "target_mode": "tagged_or_secondary",
            "pattern_kind": "diagonal_hatch",
            "fill_treatment": "outline_plus_hatch",
        }
    if explicit_outline:
        return {
            "enabled": True,
            "reason": "explicit_outline",
            "target_mode": "tagged_or_secondary",
            "pattern_kind": "",
            "fill_treatment": "outline_only",
        }
    if explicit_pattern:
        return {
            "enabled": True,
            "reason": "explicit_pattern",
            "target_mode": "tagged_or_secondary",
            "pattern_kind": "",
            "fill_treatment": "pattern_overlay",
        }
    return {"enabled": False, "reason": "solid_default", "target_mode": "none", "pattern_kind": "", "fill_treatment": "solid"}


def _collect_pattern_notes(dataset: dict[str, Any]) -> list[str]:
    notes: list[str] = [str(item).lower() for item in (dataset.get("source_notes") or []) if str(item).strip()]
    for key in ("records", "points", "candles", "bins"):
        for item in dataset.get(key) or []:
            if isinstance(item, dict) and str(item.get("note") or "").strip():
                notes.append(str(item.get("note") or "").lower())
    return notes


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _merge_motif_tokens(base: dict[str, Any], *override_layers: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for overrides in override_layers:
        merged.update(overrides)
    return merged


def _sanitize_motif_tokens_for_family(chart_family: str, motif_tokens: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(motif_tokens)
    if chart_family not in {"line", "annotated_chart", "stock_candlestick"}:
        sanitized["marker_style"] = "none"
    return sanitized
