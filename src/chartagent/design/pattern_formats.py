from __future__ import annotations

from copy import deepcopy
from typing import Any


_PATTERN_FORMATS: dict[str, dict[str, Any]] = {
    "signal_outline_dashboard": {
        "key": "signal_outline_dashboard",
        "label": "Signal Outline Dashboard",
        "description": "Clean analytical outline system with restrained hatch contrast and moderate spacing.",
        "surface_scope": "chart_wide",
        "motif_overrides": {
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 12,
            "pattern_opacity": 0.18,
            "pattern_stroke_width": 1.1,
            "patterned_outline_width": 2.2,
            "outline_only_width": 2.05,
            "range_outline_width": 1.45,
            "legend_swatch_radius": 4,
        },
    },
    "signal_outline_editorial": {
        "key": "signal_outline_editorial",
        "label": "Signal Outline Editorial",
        "description": "More spacious editorial hatch system with slightly warmer outline contrast.",
        "surface_scope": "chart_wide",
        "motif_overrides": {
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 14,
            "pattern_opacity": 0.24,
            "pattern_stroke_width": 1.3,
            "patterned_outline_width": 2.45,
            "outline_only_width": 2.25,
            "range_outline_width": 1.55,
            "legend_swatch_radius": 3,
        },
    },
    "signal_outline_poster": {
        "key": "signal_outline_poster",
        "label": "Signal Outline Poster",
        "description": "Poster-scale outline and hatch system with stronger type-led spacing and fewer guide lines.",
        "surface_scope": "chart_wide",
        "motif_overrides": {
            "pattern_kind_default": "wide_diagonal",
            "pattern_spacing": 18,
            "pattern_opacity": 0.28,
            "pattern_stroke_width": 1.45,
            "patterned_outline_width": 2.8,
            "outline_only_width": 2.45,
            "range_outline_width": 1.7,
            "legend_swatch_radius": 4,
        },
    },
    "signal_outline_broadcast": {
        "key": "signal_outline_broadcast",
        "label": "Signal Outline Broadcast",
        "description": "High-contrast broadcast hatch system with tighter cadence and stronger outline edges.",
        "surface_scope": "chart_wide",
        "motif_overrides": {
            "pattern_kind_default": "diagonal_hatch",
            "pattern_spacing": 10,
            "pattern_opacity": 0.32,
            "pattern_stroke_width": 1.4,
            "patterned_outline_width": 2.75,
            "outline_only_width": 2.45,
            "range_outline_width": 1.7,
            "legend_swatch_radius": 4,
        },
    },
}


def get_pattern_format(format_key: str) -> dict[str, Any]:
    if not format_key:
        return {}
    return deepcopy(_PATTERN_FORMATS.get(format_key) or {})


def resolve_pattern_format(enabled: bool, theme_name: str, style_combo_key: str) -> dict[str, Any]:
    if not enabled:
        return {}
    if style_combo_key == "broadcast_signal" or theme_name == "broadcast":
        key = "signal_outline_broadcast"
    elif style_combo_key == "poster_editorial":
        key = "signal_outline_poster"
    elif style_combo_key in {"editorial_outline", "gallery_infographic"}:
        key = "signal_outline_editorial"
    else:
        key = "signal_outline_dashboard"
    return get_pattern_format(key)
