from __future__ import annotations

from copy import deepcopy
from typing import Any


_THEME_SETS: dict[str, dict[str, Any]] = {
    "neutral_white": {
        "key": "neutral_white",
        "label": "Neutral White",
        "description": "Clean white analytical surface with restrained accents.",
        "source_refs": ["vercel", "apple", "notion"],
        "theme_name": "minimal",
        "reference_profile": "notion_minimal",
        "style_combo_preset": "neutral_system",
        "pattern_format_preset": "signal_outline_dashboard",
        "artwork_signature": [
            "quiet white panel",
            "restrained accent use",
            "clean analytical spacing",
        ],
        "component_defaults": {
            "pattern_mode": "solid",
            "label_weight": 600,
            "source_mode": "bottom_right",
            "source_opacity": 0.78,
            "table_header_weight": 700,
            "table_cell_padding": 16,
            "table_row_divider_opacity": 0.22,
        },
        "theme_token_overrides": {
            "bg": "#fcfdff",
            "panel": "#ffffff",
            "panel_alt": "#f4f7fb",
            "plot_bg": "#fbfdff",
            "text_secondary": "#314155",
            "text_muted": "#64748b",
            "accent": "#2563eb",
            "accent_alt": "#0f766e",
            "header_fill": "#e8eef5",
            "radius_card": 20,
            "radius_chip": 12,
        },
        "motif_token_overrides": {
            "bar_radius": 8,
            "guide_line_count": 2,
        },
    },
    "editorial_outline": {
        "key": "editorial_outline",
        "label": "Editorial Outline",
        "description": "Warm editorial charts with outline-led surface language.",
        "source_refs": ["notion", "claude", "financial_times"],
        "theme_name": "editorial",
        "reference_profile": "financial_times_editorial",
        "style_combo_preset": "editorial_outline",
        "pattern_format_preset": "signal_outline_editorial",
        "artwork_signature": [
            "warm paper surface",
            "outline-led bars and slices",
            "airy editorial rhythm",
        ],
        "component_defaults": {
            "pattern_mode": "outline_plus_hatch",
            "label_weight": 650,
            "source_mode": "bottom_left",
            "source_opacity": 0.82,
            "table_header_weight": 700,
            "table_cell_padding": 16,
            "table_row_divider_opacity": 0.18,
        },
        "theme_token_overrides": {
            "bg": "#f8efe3",
            "panel": "#fff8f0",
            "panel_alt": "#f2e6d4",
            "plot_bg": "#fffaf3",
            "text_primary": "#241c16",
            "text_secondary": "#5a483c",
            "text_muted": "#8a7464",
            "accent": "#b45309",
            "accent_alt": "#7c2d12",
            "series": ["#b45309", "#7c2d12", "#c2410c", "#9a3412", "#0f766e", "#6d28d9"],
            "header_fill": "#eadcc8",
            "radius_card": 18,
            "radius_chip": 10,
        },
        "motif_token_overrides": {
            "bar_radius": 3,
            "guide_dasharray": "4 6",
            "pattern_spacing": 16,
            "pattern_opacity": 0.56,
        },
    },
    "broadcast_signal": {
        "key": "broadcast_signal",
        "label": "Broadcast Signal",
        "description": "High-contrast broadcast panels with strong urgency.",
        "source_refs": ["clickhouse", "vercel", "broadcast_news_graphics"],
        "theme_name": "broadcast",
        "reference_profile": "bloomberg_flash",
        "style_combo_preset": "broadcast_signal",
        "pattern_format_preset": "signal_outline_broadcast",
        "artwork_signature": [
            "high-contrast dark panel",
            "crisp signal outlines",
            "urgent broadcast accent cadence",
        ],
        "component_defaults": {
            "pattern_mode": "outline_plus_hatch",
            "label_weight": 700,
            "source_mode": "edge_rail",
            "source_opacity": 0.9,
            "table_header_weight": 700,
            "table_cell_padding": 14,
            "table_row_divider_opacity": 0.3,
        },
        "theme_token_overrides": {
            "bg": "#07101c",
            "panel": "#0c1730",
            "panel_alt": "#12203a",
            "plot_bg": "#0a152b",
            "text_primary": "#f8fafc",
            "text_secondary": "#dbeafe",
            "text_muted": "#93c5fd",
            "grid": "#314159",
            "grid_strong": "#4b5d78",
            "accent": "#f97316",
            "accent_alt": "#22d3ee",
            "series": ["#f97316", "#22d3ee", "#4ade80", "#facc15", "#a78bfa", "#fb7185"],
            "header_fill": "#16243f",
            "radius_card": 14,
            "radius_chip": 8,
        },
        "motif_token_overrides": {
            "bar_radius": 4,
            "pattern_spacing": 8,
            "pattern_opacity": 0.42,
        },
    },
    "dashboard_analytical": {
        "key": "dashboard_analytical",
        "label": "Dashboard Analytical",
        "description": "Dense but orderly dashboard system for decision support.",
        "source_refs": ["coinbase", "clickhouse", "stripe"],
        "theme_name": "dashboard",
        "reference_profile": "stripe_analytics",
        "style_combo_preset": "analytical_panel",
        "pattern_format_preset": "signal_outline_dashboard",
        "artwork_signature": [
            "dense information grid",
            "balanced KPI panels",
            "clean operational signal language",
        ],
        "component_defaults": {
            "pattern_mode": "solid",
            "label_weight": 650,
            "source_mode": "bottom_right",
            "source_opacity": 0.8,
            "table_header_weight": 700,
            "table_cell_padding": 14,
            "table_row_divider_opacity": 0.22,
        },
        "theme_token_overrides": {
            "bg": "#eef6f7",
            "panel": "#ffffff",
            "panel_alt": "#e3f0f2",
            "plot_bg": "#f7fbfc",
            "text_secondary": "#0f4c5c",
            "text_muted": "#5a6c78",
            "accent": "#0f766e",
            "accent_alt": "#0284c7",
            "series": ["#0f766e", "#0284c7", "#2563eb", "#d97706", "#14b8a6", "#7c3aed"],
            "header_fill": "#dceff0",
            "radius_card": 18,
            "radius_chip": 10,
        },
        "motif_token_overrides": {
            "bar_radius": 10,
            "guide_line_count": 3,
            "pattern_spacing": 10,
        },
    },
    "gallery_infographic": {
        "key": "gallery_infographic",
        "label": "Gallery Infographic",
        "description": "Decorative infographic surface with stronger visual character.",
        "source_refs": ["pinterest", "claude", "editorial_infographics"],
        "theme_name": "editorial",
        "reference_profile": "financial_times_editorial",
        "style_combo_preset": "gallery_infographic",
        "pattern_format_preset": "signal_outline_editorial",
        "artwork_signature": [
            "decorative surface identity",
            "gallery-like spacing",
            "bold pattern presence",
        ],
        "component_defaults": {
            "pattern_mode": "outline_plus_hatch",
            "label_weight": 650,
            "source_mode": "bottom_left",
            "source_opacity": 0.8,
            "table_header_weight": 700,
            "table_cell_padding": 16,
            "table_row_divider_opacity": 0.18,
        },
        "theme_token_overrides": {
            "bg": "#fff6ea",
            "panel": "#fff0de",
            "panel_alt": "#ffe8cc",
            "plot_bg": "#fff8ef",
            "text_primary": "#2a1d16",
            "text_secondary": "#5f463c",
            "text_muted": "#8a6f63",
            "accent": "#7c3aed",
            "accent_alt": "#0f766e",
            "series": ["#7c3aed", "#0f766e", "#ea580c", "#db2777", "#2563eb", "#ca8a04"],
            "header_fill": "#ffe4c1",
            "radius_card": 28,
            "radius_chip": 16,
        },
        "motif_token_overrides": {
            "bar_radius": 14,
            "annotation_radius": 16,
            "pattern_spacing": 10,
            "pattern_opacity": 0.4,
        },
    },
    "poster_editorial": {
        "key": "poster_editorial",
        "label": "Poster Editorial",
        "description": "Type-led editorial poster surface with warm paper tone and stronger composition contrast.",
        "source_refs": ["pinterest", "notion", "claude"],
        "theme_name": "editorial",
        "reference_profile": "financial_times_editorial",
        "style_combo_preset": "poster_editorial",
        "pattern_format_preset": "signal_outline_poster",
        "artwork_signature": [
            "type-led poster hierarchy",
            "warm paper-like field",
            "editorial spread contrast",
        ],
        "component_defaults": {
            "pattern_mode": "outline_plus_hatch",
            "label_weight": 650,
            "source_mode": "bottom_left",
            "source_opacity": 0.84,
            "table_header_weight": 700,
            "table_cell_padding": 18,
            "table_row_divider_opacity": 0.14,
        },
        "theme_token_overrides": {
            "bg": "#fff7ee",
            "panel": "#fff3e5",
            "panel_alt": "#f6e5d1",
            "plot_bg": "#fff9f1",
            "text_primary": "#211814",
            "text_secondary": "#5b4638",
            "text_muted": "#8d7260",
            "accent": "#c2410c",
            "accent_alt": "#7c3aed",
            "series": ["#c2410c", "#7c3aed", "#0f766e", "#1d4ed8", "#d97706", "#be185d"],
            "header_fill": "#f1dcc2",
            "radius_card": 26,
            "radius_chip": 14
        },
        "motif_token_overrides": {
            "bar_radius": 8,
            "guide_line_count": 1,
            "pattern_spacing": 18,
            "pattern_opacity": 0.46,
            "annotation_radius": 16,
        },
    },
    "market_technical": {
        "key": "market_technical",
        "label": "Market Technical",
        "description": "Terminal-like technical surface with disciplined density.",
        "source_refs": ["clickhouse", "coinbase", "vercel", "tradingview"],
        "theme_name": "dashboard",
        "reference_profile": "tradingview_terminal",
        "style_combo_preset": "market_technical",
        "pattern_format_preset": "signal_outline_dashboard",
        "artwork_signature": [
            "terminal density",
            "thin technical lines",
            "compressed market signal layout",
        ],
        "component_defaults": {
            "pattern_mode": "solid",
            "label_weight": 600,
            "source_mode": "bottom_right",
            "source_opacity": 0.72,
            "table_header_weight": 700,
            "table_cell_padding": 12,
            "table_row_divider_opacity": 0.24,
        },
        "theme_token_overrides": {
            "bg": "#eff4f7",
            "panel": "#f9fbfd",
            "panel_alt": "#ebf1f5",
            "plot_bg": "#eef4f8",
            "text_primary": "#111827",
            "text_secondary": "#243243",
            "text_muted": "#526070",
            "grid": "#c4d2de",
            "grid_strong": "#90a3b8",
            "accent": "#2563eb",
            "accent_alt": "#0ea5e9",
            "series": ["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"],
            "header_fill": "#dde7ef",
            "font_body": "'IBM Plex Mono', 'JetBrains Mono', monospace",
            "radius_card": 12,
            "radius_chip": 8,
        },
        "motif_token_overrides": {
            "bar_radius": 2,
            "guide_line_count": 4,
            "pattern_spacing": 7,
            "pattern_opacity": 0.24,
        },
    },
}

_GROUP_TO_KEYS: dict[str, set[str]] = {
    "color": {
        "accent_color",
        "accent_alt_color",
        "positive_color",
        "negative_color",
        "neutral_color",
        "series_palette",
        "grid_color",
        "panel_color",
        "plot_bg_color",
        "table_header_fill",
        "annotation_fill",
        "annotation_stroke",
    },
    "geometry": {
        "corner_radius",
        "chip_radius",
        "bar_gap",
        "group_gap",
        "panel_padding",
        "rail_width",
    },
    "pattern": {
        "pattern_mode",
        "pattern_density",
        "pattern_angle",
        "pattern_opacity",
        "pattern_spacing",
    },
    "stroke": {
        "stroke_width",
        "outline_width",
        "grid_width",
        "axis_width",
    },
    "label": {
        "title_scale",
        "subtitle_scale",
        "body_scale",
        "tick_scale",
        "source_scale",
        "label_weight",
    },
    "annotation": {
        "annotation_fill",
        "annotation_stroke",
        "annotation_radius",
        "annotation_rail_width",
    },
    "table": {
        "table_header_fill",
        "table_header_weight",
        "table_cell_padding",
        "table_row_divider_opacity",
    },
    "source": {
        "source_mode",
        "source_opacity",
    },
}

_OVERRIDE_TO_GROUP: dict[str, str] = {
    override_key: group_name
    for group_name, override_keys in _GROUP_TO_KEYS.items()
    for override_key in override_keys
}


def get_theme_set_spec(theme_set: str) -> dict[str, Any]:
    return deepcopy(_THEME_SETS.get(theme_set) or _THEME_SETS["neutral_white"])


def infer_theme_set(theme_name: str, style_combo_preset: str) -> str:
    if style_combo_preset == "broadcast_signal" or theme_name == "broadcast":
        return "broadcast_signal"
    if style_combo_preset == "poster_editorial":
        return "poster_editorial"
    if style_combo_preset == "gallery_infographic":
        return "gallery_infographic"
    if style_combo_preset == "market_technical":
        return "market_technical"
    if style_combo_preset == "editorial_outline":
        return "editorial_outline"
    if style_combo_preset == "analytical_panel" or theme_name == "dashboard":
        return "dashboard_analytical"
    return "neutral_white"


def apply_theme_customization(
    *,
    theme_set: str,
    theme_tokens: dict[str, Any],
    motif_tokens: dict[str, Any],
    layout_tokens: dict[str, Any],
    theme_overrides: dict[str, Any],
    theme_reset: dict[str, Any],
) -> dict[str, Any]:
    spec = get_theme_set_spec(theme_set)
    base_theme_tokens = deepcopy(theme_tokens)
    base_motif_tokens = deepcopy(motif_tokens)
    base_layout_tokens = deepcopy(layout_tokens)
    base_component_tokens = deepcopy(spec.get("component_defaults") or {})

    base_theme_tokens.update(spec.get("theme_token_overrides") or {})
    base_motif_tokens.update(spec.get("motif_token_overrides") or {})
    base_layout_tokens.update(spec.get("layout_token_overrides") or {})

    active_overrides = _active_overrides(theme_overrides=theme_overrides, theme_reset=theme_reset)
    current_theme_tokens = deepcopy(base_theme_tokens)
    current_motif_tokens = deepcopy(base_motif_tokens)
    current_layout_tokens = deepcopy(base_layout_tokens)
    current_component_tokens = deepcopy(base_component_tokens)

    for key, value in active_overrides.items():
        _apply_override(
            key=key,
            value=value,
            theme_tokens=current_theme_tokens,
            motif_tokens=current_motif_tokens,
            layout_tokens=current_layout_tokens,
            component_tokens=current_component_tokens,
        )

    return {
        "theme_tokens": current_theme_tokens,
        "motif_tokens": current_motif_tokens,
        "layout_tokens": current_layout_tokens,
        "component_tokens": current_component_tokens,
        "active_overrides": deepcopy(active_overrides),
        "theme_reset": deepcopy(theme_reset),
    }


def _active_overrides(theme_overrides: dict[str, Any], theme_reset: dict[str, Any]) -> dict[str, Any]:
    raw = {
        str(key): value
        for key, value in (theme_overrides or {}).items()
        if value is not None and str(key).strip()
    }
    mode = str((theme_reset or {}).get("mode") or "").strip()
    if mode == "reset_all":
        return {}
    reset_keys = {str(key).strip() for key in (theme_reset or {}).get("keys") or [] if str(key).strip()}
    reset_groups = {str(group).strip() for group in (theme_reset or {}).get("groups") or [] if str(group).strip()}
    if reset_groups:
        for group_name in reset_groups:
            reset_keys.update(_GROUP_TO_KEYS.get(group_name) or set())
    return {key: value for key, value in raw.items() if key not in reset_keys}


def _apply_override(
    *,
    key: str,
    value: Any,
    theme_tokens: dict[str, Any],
    motif_tokens: dict[str, Any],
    layout_tokens: dict[str, Any],
    component_tokens: dict[str, Any],
) -> None:
    if key == "accent_color":
        theme_tokens["accent"] = str(value)
    elif key == "accent_alt_color":
        theme_tokens["accent_alt"] = str(value)
    elif key == "positive_color":
        theme_tokens["positive"] = str(value)
    elif key == "negative_color":
        theme_tokens["negative"] = str(value)
    elif key == "neutral_color":
        theme_tokens["neutral"] = str(value)
    elif key == "series_palette" and isinstance(value, list):
        theme_tokens["series"] = [str(item) for item in value if str(item).strip()]
    elif key == "grid_color":
        theme_tokens["grid"] = str(value)
    elif key == "panel_color":
        theme_tokens["panel"] = str(value)
    elif key == "plot_bg_color":
        theme_tokens["plot_bg"] = str(value)
    elif key == "corner_radius":
        theme_tokens["radius_card"] = _coerce_int(value, theme_tokens.get("radius_card"))
    elif key == "chip_radius":
        theme_tokens["radius_chip"] = _coerce_int(value, theme_tokens.get("radius_chip"))
    elif key == "bar_gap":
        layout_tokens["bar_gap"] = _coerce_float(value, layout_tokens.get("bar_gap", 0.18))
    elif key == "group_gap":
        layout_tokens["group_gap"] = _coerce_float(value, layout_tokens.get("group_gap", 0.12))
    elif key == "panel_padding":
        layout_tokens["panel_padding"] = _coerce_int(value, layout_tokens.get("panel_padding", 24))
    elif key == "rail_width":
        layout_tokens["rail_width"] = _coerce_int(value, layout_tokens.get("rail_width", 220))
    elif key == "stroke_width":
        motif_tokens["primary_stroke_width"] = _coerce_float(value, motif_tokens.get("primary_stroke_width", 4))
    elif key == "outline_width":
        width = _coerce_float(value, motif_tokens.get("patterned_outline_width", 2.2))
        motif_tokens["patterned_outline_width"] = width
        motif_tokens["outline_only_width"] = width
    elif key == "grid_width":
        motif_tokens["guide_stroke_width"] = _coerce_float(value, motif_tokens.get("guide_stroke_width", 1))
    elif key == "axis_width":
        motif_tokens["axis_stroke_width"] = _coerce_float(value, motif_tokens.get("axis_stroke_width", 2))
    elif key == "pattern_mode":
        component_tokens["pattern_mode"] = str(value)
    elif key == "pattern_density":
        _apply_pattern_density(str(value), motif_tokens=motif_tokens)
        component_tokens["pattern_density"] = str(value)
    elif key == "pattern_angle":
        motif_tokens["pattern_angle"] = _coerce_float(value, motif_tokens.get("pattern_angle", 45))
    elif key == "pattern_opacity":
        motif_tokens["pattern_opacity"] = _coerce_float(value, motif_tokens.get("pattern_opacity", 0.2))
    elif key == "pattern_spacing":
        motif_tokens["pattern_spacing"] = _coerce_float(value, motif_tokens.get("pattern_spacing", 10))
    elif key == "title_scale":
        theme_tokens["title_size"] = _scaled(theme_tokens.get("title_size", 28), value)
    elif key == "subtitle_scale":
        theme_tokens["subtitle_size"] = _scaled(theme_tokens.get("subtitle_size", 18), value)
    elif key == "body_scale":
        theme_tokens["body_size"] = _scaled(theme_tokens.get("body_size", 16), value)
    elif key == "tick_scale":
        theme_tokens["tick_size"] = _scaled(theme_tokens.get("tick_size", 14), value)
    elif key == "source_scale":
        theme_tokens["source_size"] = _scaled(theme_tokens.get("source_size", 14), value)
    elif key == "label_weight":
        component_tokens["label_weight"] = _coerce_int(value, component_tokens.get("label_weight", 600))
    elif key == "annotation_fill":
        theme_tokens["annotation_fill"] = str(value)
    elif key == "annotation_stroke":
        theme_tokens["annotation_stroke"] = str(value)
    elif key == "annotation_radius":
        motif_tokens["annotation_radius"] = _coerce_int(value, motif_tokens.get("annotation_radius", 8))
    elif key in {"annotation_rail_width", "rail_width"}:
        layout_tokens["annotation_rail_width"] = _coerce_int(value, layout_tokens.get("annotation_rail_width", 0))
    elif key == "table_header_fill":
        theme_tokens["header_fill"] = str(value)
    elif key == "table_header_weight":
        component_tokens["table_header_weight"] = _coerce_int(value, component_tokens.get("table_header_weight", 700))
    elif key == "table_cell_padding":
        component_tokens["table_cell_padding"] = _coerce_int(value, component_tokens.get("table_cell_padding", 16))
    elif key == "table_row_divider_opacity":
        component_tokens["table_row_divider_opacity"] = _coerce_float(value, component_tokens.get("table_row_divider_opacity", 0.2))
    elif key == "source_mode":
        component_tokens["source_mode"] = str(value)
    elif key == "source_opacity":
        component_tokens["source_opacity"] = _coerce_float(value, component_tokens.get("source_opacity", 0.8))


def _apply_pattern_density(level: str, motif_tokens: dict[str, Any]) -> None:
    base_spacing = _coerce_float(motif_tokens.get("pattern_spacing", 10), 10)
    base_opacity = _coerce_float(motif_tokens.get("pattern_opacity", 0.2), 0.2)
    density = level.strip().lower()
    if density == "low":
        motif_tokens["pattern_spacing"] = round(base_spacing + 3, 2)
        motif_tokens["pattern_opacity"] = round(max(0.08, base_opacity - 0.06), 3)
    elif density == "high":
        motif_tokens["pattern_spacing"] = round(max(4, base_spacing - 2), 2)
        motif_tokens["pattern_opacity"] = round(min(0.7, base_opacity + 0.08), 3)
    else:
        motif_tokens["pattern_spacing"] = round(base_spacing, 2)
        motif_tokens["pattern_opacity"] = round(base_opacity, 3)


def _scaled(base_value: Any, scale: Any) -> int:
    base = _coerce_float(base_value, 16)
    factor = _coerce_float(scale, 1.0)
    return max(10, int(round(base * factor)))


def _coerce_int(value: Any, default: Any) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return int(round(float(default))) if default is not None else 0


def _coerce_float(value: Any, default: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default) if default is not None else 0.0
