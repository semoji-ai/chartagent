from __future__ import annotations

from copy import deepcopy
from typing import Any


_STYLE_COMBOS: dict[str, dict[str, Any]] = {
    "neutral_system": {
        "key": "neutral_system",
        "label": "Neutral System",
        "description": "Quiet default system with restrained guides and solid fills.",
        "motif_overrides": {
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 10,
            "pattern_opacity": 0.2,
            "pattern_stroke_width": 1.1,
            "patterned_outline_width": 2.1,
            "outline_only_width": 2.0,
            "range_outline_width": 1.5,
            "legend_swatch_radius": 4,
        },
    },
    "analytical_panel": {
        "key": "analytical_panel",
        "label": "Analytical Panel",
        "description": "B2B dashboard composition with clean bars, restrained panels, and precise overlays.",
        "motif_overrides": {
            "guide_line_count": 3,
            "guide_dasharray": None,
            "guide_opacity": 0.36,
            "bar_radius": 8,
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 9,
            "pattern_opacity": 0.18,
            "pattern_stroke_width": 1.0,
            "patterned_outline_width": 2.0,
            "outline_only_width": 1.9,
            "range_outline_width": 1.45,
            "legend_swatch_radius": 5,
        },
    },
    "editorial_outline": {
        "key": "editorial_outline",
        "label": "Editorial Outline",
        "description": "Hollow bars, wide hatch spacing, and a single accent-driven focal point.",
        "motif_overrides": {
            "guide_line_count": 2,
            "guide_dasharray": "4 5",
            "guide_opacity": 0.3,
            "primary_stroke_width": 3,
            "marker_style": "dot",
            "bar_radius": 3,
            "pattern_kind_default": "wide_diagonal",
            "pattern_spacing": 14,
            "pattern_opacity": 0.52,
            "pattern_stroke_width": 1.5,
            "patterned_outline_width": 2.6,
            "outline_only_width": 2.4,
            "range_outline_width": 1.6,
            "legend_swatch_radius": 3,
        },
    },
    "broadcast_signal": {
        "key": "broadcast_signal",
        "label": "Broadcast Signal",
        "description": "High-contrast signal graphics with crisp outlines and urgent hatch cadence.",
        "motif_overrides": {
            "guide_line_count": 3,
            "guide_dasharray": "8 6",
            "guide_opacity": 0.32,
            "primary_stroke_width": 5,
            "marker_style": "ring",
            "marker_radius": 5,
            "bar_radius": 4,
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 8,
            "pattern_opacity": 0.42,
            "pattern_stroke_width": 1.4,
            "patterned_outline_width": 2.8,
            "outline_only_width": 2.5,
            "range_outline_width": 1.8,
            "legend_swatch_radius": 4,
        },
    },
    "gallery_infographic": {
        "key": "gallery_infographic",
        "label": "Gallery Infographic",
        "description": "Decorative but readable infographic treatment with bolder pattern identity.",
        "motif_overrides": {
            "guide_line_count": 1,
            "guide_dasharray": None,
            "guide_opacity": 0.2,
            "bar_radius": 10,
            "annotation_radius": 12,
            "pattern_kind_default": "crosshatch_light",
            "pattern_spacing": 12,
            "pattern_opacity": 0.34,
            "pattern_stroke_width": 1.25,
            "patterned_outline_width": 2.4,
            "outline_only_width": 2.2,
            "range_outline_width": 1.55,
            "legend_swatch_radius": 6,
        },
    },
    "poster_editorial": {
        "key": "poster_editorial",
        "label": "Poster Editorial",
        "description": "Type-led editorial poster treatment with stronger compositional contrast and roomier outline language.",
        "motif_overrides": {
            "guide_line_count": 1,
            "guide_dasharray": None,
            "guide_opacity": 0.16,
            "primary_stroke_width": 3,
            "marker_style": "dot",
            "marker_radius": 4,
            "bar_radius": 6,
            "annotation_style": "soft_card",
            "annotation_radius": 14,
            "pattern_kind_default": "wide_diagonal",
            "pattern_spacing": 18,
            "pattern_opacity": 0.46,
            "pattern_stroke_width": 1.45,
            "patterned_outline_width": 2.8,
            "outline_only_width": 2.5,
            "range_outline_width": 1.7,
            "legend_swatch_radius": 4,
        },
    },
    "market_technical": {
        "key": "market_technical",
        "label": "Market Technical",
        "description": "Dense technical charting language with thin overlays and terminal discipline.",
        "motif_overrides": {
            "guide_line_count": 4,
            "guide_dasharray": "3 5",
            "guide_opacity": 0.36,
            "primary_stroke_width": 3,
            "marker_style": "none",
            "bar_radius": 3,
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 7,
            "pattern_opacity": 0.22,
            "pattern_stroke_width": 1.0,
            "patterned_outline_width": 1.9,
            "outline_only_width": 1.8,
            "range_outline_width": 1.35,
            "legend_swatch_radius": 3,
        },
    },
}


def get_style_combo(combo_key: str) -> dict[str, Any]:
    return deepcopy(_STYLE_COMBOS.get(combo_key) or _STYLE_COMBOS["neutral_system"])


def resolve_style_combo(theme_name: str, chart_family: str, task: dict[str, Any], dataset: dict[str, Any]) -> dict[str, Any]:
    haystack = " ".join(
        [
            str(task.get("goal") or ""),
            str(task.get("question") or ""),
            str(dataset.get("title") or ""),
            " ".join(str(item) for item in (task.get("source_hints") or [])),
        ]
    ).lower()
    if chart_family == "stock_candlestick":
        key = "market_technical"
    elif any(keyword in haystack for keyword in ("broadcast", "signal", "breaking", "속보", "실시간", "긴급", "newsflash")):
        key = "broadcast_signal"
    elif any(keyword in haystack for keyword in ("editorial poster", "poster editorial", "poster spread", "pinterest board", "pinterest-style", "핀터레스트", "편집 포스터", "에디토리얼 포스터", "포스터 스프레드")):
        key = "poster_editorial"
    elif any(keyword in haystack for keyword in ("gallery", "infographic", "poster", "exhibition", "갤러리", "인포그래픽", "포스터", "전시")):
        key = "gallery_infographic"
    elif any(keyword in haystack for keyword in ("outline", "outlined", "hollow", "stripe", "hatch", "테두리", "외곽선", "빗금", "줄무늬", "속을 채우지")):
        key = "editorial_outline"
    elif theme_name == "dashboard" or chart_family in {"metric_wall", "comparison_table", "fact_table", "timeline_table", "percentage_progress", "stacked_progress", "radial_gauge"}:
        key = "analytical_panel"
    else:
        key = "neutral_system"
    return get_style_combo(key)
