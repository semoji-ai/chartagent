from __future__ import annotations

from copy import deepcopy
from typing import Any


_REFERENCE_PROFILES: dict[str, dict[str, Any]] = {
    "notion_minimal": {
        "key": "notion_minimal",
        "label": "Notion Minimal",
        "archetype": "Product minimal documentation charts",
        "motif_tokens": {
            "guide_line_count": 2,
            "guide_dasharray": None,
            "guide_opacity": 0.55,
            "guide_stroke_width": 1,
            "axis_stroke_width": 2,
            "primary_stroke_width": 4,
            "marker_style": "dot",
            "marker_radius": 5,
            "bar_radius": 6,
            "annotation_style": "soft_card",
            "annotation_radius": 8,
            "annotation_connector_dasharray": None,
            "candlestick_wick_width": 2,
            "candlestick_body_stroke_width": 0,
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 10,
            "pattern_opacity": 0.22,
            "pattern_stroke_width": 1.2,
        },
    },
    "financial_times_editorial": {
        "key": "financial_times_editorial",
        "label": "Financial Times Editorial",
        "archetype": "Warm editorial charts with restrained hierarchy",
        "motif_tokens": {
            "guide_line_count": 3,
            "guide_dasharray": "5 5",
            "guide_opacity": 0.48,
            "guide_stroke_width": 1,
            "axis_stroke_width": 2,
            "primary_stroke_width": 4,
            "marker_style": "dot",
            "marker_radius": 5,
            "bar_radius": 6,
            "annotation_style": "soft_card",
            "annotation_radius": 8,
            "annotation_connector_dasharray": "4 4",
            "candlestick_wick_width": 2,
            "candlestick_body_stroke_width": 0,
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 10,
            "pattern_opacity": 0.24,
            "pattern_stroke_width": 1.2,
        },
    },
    "stripe_analytics": {
        "key": "stripe_analytics",
        "label": "Stripe Analytics",
        "archetype": "Clean B2B dashboard panels and balanced guide lines",
        "motif_tokens": {
            "guide_line_count": 3,
            "guide_dasharray": None,
            "guide_opacity": 0.42,
            "guide_stroke_width": 1,
            "axis_stroke_width": 2,
            "primary_stroke_width": 4,
            "marker_style": "dot",
            "marker_radius": 4,
            "bar_radius": 8,
            "annotation_style": "signal_chip",
            "annotation_radius": 10,
            "annotation_connector_dasharray": None,
            "candlestick_wick_width": 2,
            "candlestick_body_stroke_width": 1,
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 9,
            "pattern_opacity": 0.2,
            "pattern_stroke_width": 1.1,
        },
    },
    "bloomberg_flash": {
        "key": "bloomberg_flash",
        "label": "Bloomberg Flash",
        "archetype": "Broadcast urgency with strong line weight and crisp callouts",
        "motif_tokens": {
            "guide_line_count": 3,
            "guide_dasharray": "8 6",
            "guide_opacity": 0.34,
            "guide_stroke_width": 1,
            "axis_stroke_width": 2,
            "primary_stroke_width": 5,
            "marker_style": "ring",
            "marker_radius": 5,
            "bar_radius": 4,
            "annotation_style": "news_tag",
            "annotation_radius": 6,
            "annotation_connector_dasharray": None,
            "candlestick_wick_width": 2,
            "candlestick_body_stroke_width": 1,
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 11,
            "pattern_opacity": 0.2,
            "pattern_stroke_width": 1.25,
        },
    },
    "tradingview_terminal": {
        "key": "tradingview_terminal",
        "label": "TradingView Terminal",
        "archetype": "Market charts with dense guides and no decorative markers",
        "motif_tokens": {
            "guide_line_count": 4,
            "guide_dasharray": "3 5",
            "guide_opacity": 0.4,
            "guide_stroke_width": 1,
            "axis_stroke_width": 2,
            "primary_stroke_width": 3,
            "marker_style": "none",
            "marker_radius": 0,
            "bar_radius": 4,
            "annotation_style": "signal_chip",
            "annotation_radius": 8,
            "annotation_connector_dasharray": "3 4",
            "candlestick_wick_width": 2,
            "candlestick_body_stroke_width": 1,
            "pattern_kind_default": "vertical_stripe",
            "pattern_spacing": 8,
            "pattern_opacity": 0.18,
            "pattern_stroke_width": 1.0,
        },
    },
}


def get_reference_profile(profile_key: str) -> dict[str, Any]:
    return deepcopy(_REFERENCE_PROFILES.get(profile_key) or _REFERENCE_PROFILES["notion_minimal"])


def resolve_reference_profile(theme_name: str, chart_family: str) -> dict[str, Any]:
    if chart_family == "stock_candlestick":
        key = "tradingview_terminal"
    elif theme_name == "broadcast":
        key = "bloomberg_flash"
    elif theme_name == "dashboard":
        key = "stripe_analytics"
    elif theme_name == "editorial":
        key = "financial_times_editorial"
    else:
        key = "notion_minimal"
    return get_reference_profile(key)
