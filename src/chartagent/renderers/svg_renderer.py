from __future__ import annotations

from html import escape
import math
import re
from typing import Any


def render_chart_svg(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    family = str(chart_spec.get("chart_family") or "fact_table")
    if family == "annotated_chart":
        svg = _render_annotated_chart(chart_spec, dataset)
    elif family == "bar":
        svg = _render_bar(chart_spec, dataset)
    elif family == "bar_horizontal":
        svg = _render_bar_horizontal(chart_spec, dataset)
    elif family == "line":
        svg = _render_line(chart_spec, dataset)
    elif family == "distribution_histogram":
        svg = _render_distribution_histogram(chart_spec, dataset)
    elif family == "stock_candlestick":
        svg = _render_stock_candlestick(chart_spec, dataset)
    elif family == "donut":
        svg = _render_donut(chart_spec, dataset)
    elif family == "pie":
        svg = _render_pie(chart_spec, dataset)
    elif family == "radial_gauge":
        svg = _render_radial_gauge(chart_spec, dataset)
    elif family == "semi_donut":
        svg = _render_semi_donut(chart_spec, dataset)
    elif family == "stacked_progress":
        svg = _render_stacked_progress(chart_spec, dataset)
    elif family == "percentage_progress":
        svg = _render_percentage_progress(chart_spec, dataset)
    elif family == "metric_wall":
        svg = _render_metric_wall(chart_spec, dataset)
    elif family == "single_stat":
        svg = _render_single_stat(chart_spec, dataset)
    elif family == "fact_table":
        svg = _render_fact_table(chart_spec, dataset)
    elif family in {"comparison_table", "timeline_table"}:
        svg = _render_table(chart_spec, dataset)
    else:
        svg = _render_fallback(chart_spec)
    return _inline_text_fill_tokens(svg, chart_spec)


def _svg_parts(width: int, height: int, chart_spec: dict[str, Any]) -> list[str]:
    return [
        _svg_open(width, height),
        _style_block(chart_spec),
        _background_rect(width, height, chart_spec),
        '<g class="cg-root">',
        _title_block(chart_spec),
    ]


def _background_rect(width: int, height: int, chart_spec: dict[str, Any]) -> str:
    return f'<rect x="0" y="0" width="{width}" height="{height}" fill="{_theme_token(chart_spec, "bg", "#ffffff")}" />'


def _render_bar_horizontal(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    top = _content_top(chart_spec)
    left = 260
    row_height = 48
    chart_width = 520
    value_x = width - 60
    max_value = max((float(item.get("value") or 0.0) for item in records), default=1.0) or 1.0
    height = top + row_height * len(records) + 80
    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "bar_horizontal")
    parts.append(
        f'<rect x="{left}" y="{top - 20}" width="{chart_width}" height="{row_height * len(records)}" fill="{_theme_token(chart_spec, "plot_bg", "#f8fafc")}" rx="16" />'
    )
    for index, record in enumerate(records):
        y = top + index * row_height
        value = float(record.get("value") or 0.0)
        bar_width = max(12.0, chart_width * (value / max_value)) if value > 0 else 12.0
        label = escape(str(record.get("display_label") or record.get("label") or ""))
        value_text = _format_value(value, str(record.get("unit") or dataset.get("unit") or "").strip())
        bar_fill = _theme_token(chart_spec, "accent", "#2563eb")
        bar_style = {"paint": bar_fill, "stroke": None, "stroke_width": None}
        if index in patterned_indexes:
            bar_style = _series_fill_style(chart_spec, pattern_defs, slot=f"bar-horizontal-{index}", base_color=bar_fill)
        parts.append(f'<text x="{left - 16}" y="{y + 24}" class="label" text-anchor="end">{label}</text>')
        parts.append(
            f'<rect x="{left}" y="{y + 8}" width="{bar_width:.2f}" height="20" rx="10" fill="{bar_style["paint"]}"'
            f'{_svg_optional_stroke(bar_style["stroke"], bar_style["stroke_width"])} />'
        )
        parts.append(f'<text x="{value_x}" y="{y + 24}" class="value" text-anchor="end">{escape(value_text)}</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_bar(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    return _render_bar_core(chart_spec=chart_spec, dataset=dataset, annotated=False)


def _render_line(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    points = dataset.get("points") or []
    width = 960
    height = 560
    frame = _plot_frame(chart_spec, width=width, height=height, default_left=110, default_right=80, default_bottom=80)
    left = frame["plot_left"]
    top = frame["plot_top"]
    chart_width = frame["plot_width"]
    chart_height = frame["plot_height"]
    max_value = max((float(point.get("y") or 0.0) for point in points), default=1.0) or 1.0
    min_value = min((float(point.get("y") or 0.0) for point in points), default=0.0)
    span = max_value - min_value or 1.0
    step_x = chart_width / max(1, len(points) - 1)

    poly_points: list[str] = []
    parts = _svg_parts(width, height, chart_spec)
    parts.extend(_plot_guides(chart_spec, frame))
    parts.append(
        f'<line x1="{left}" y1="{frame["plot_bottom"]}" x2="{frame["plot_right"]}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />'
    )
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    for index, point in enumerate(points):
        x = left + step_x * index
        y_value = float(point.get("y") or 0.0)
        y = top + chart_height - ((y_value - min_value) / span) * chart_height
        poly_points.append(f"{x:.2f},{y:.2f}")
        marker_svg = _marker_svg(chart_spec, x=x, y=y, fill=_theme_token(chart_spec, "accent", "#2563eb"))
        if marker_svg:
            parts.append(marker_svg)
        parts.append(f'<text x="{x:.2f}" y="{frame["plot_bottom"] + 26}" class="tick" text-anchor="middle">{escape(str(point.get("x") or ""))}</text>')
    parts.append(
        f'<polyline fill="none" stroke="{_theme_token(chart_spec, "accent", "#2563eb")}" stroke-width="{_motif_token(chart_spec, "primary_stroke_width", 4)}" points="{" ".join(poly_points)}" stroke-linecap="round" stroke-linejoin="round" />'
    )
    parts.append(f'<text x="{left}" y="{top - 18}" class="axis">{escape(str(dataset.get("y_label") or "y"))}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_single_stat(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    width = 960
    height = 420
    value = float(dataset.get("value") or 0.0)
    value_text = _format_value(value, str(dataset.get("unit") or "").strip())
    label = escape(str(dataset.get("label") or chart_spec.get("title_text") or "Value"))
    theme_set = _theme_set_key(chart_spec)
    panel_x = 60
    panel_y = _content_top(chart_spec) + 10
    panel_width = width - 120
    panel_height = 240
    radius = _theme_token(chart_spec, "radius_card", 20)
    parts = _svg_parts(width, height, chart_spec)
    if theme_set == "broadcast_signal":
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="16" fill="{_theme_token(chart_spec, "panel", "#0c1730")}" />')
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="10" rx="16" fill="{_theme_token(chart_spec, "accent", "#f97316")}" />')
        parts.append(f'<rect x="{panel_x + 24}" y="{panel_y + 24}" width="108" height="28" rx="8" fill="{_theme_token(chart_spec, "header_fill", "#16243f")}" />')
        parts.append(f'<text x="{panel_x + 38}" y="{panel_y + 43}" class="source">LIVE KPI</text>')
        parts.append(f'<text x="{panel_x + 28}" y="{panel_y + 144}" class="stat" font-size="112">{escape(value_text)}</text>')
        parts.append(f'<text x="{panel_x + 28}" y="{panel_y + 188}" class="subtitle">{label}</text>')
        parts.append(f'<line x1="{panel_x + 28}" y1="{panel_y + 202}" x2="{panel_x + 220}" y2="{panel_y + 202}" stroke="{_theme_token(chart_spec, "accent_alt", "#22d3ee")}" stroke-width="4" />')
    elif theme_set == "poster_editorial":
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height + 18}" rx="30" fill="{_theme_token(chart_spec, "panel", "#fff3e5")}" />')
        parts.append(f'<rect x="{panel_x + 24}" y="{panel_y + 26}" width="12" height="{panel_height - 32}" rx="6" fill="{_theme_token(chart_spec, "accent", "#c2410c")}" />')
        parts.append(f'<text x="{panel_x + 56}" y="{panel_y + 52}" class="subtitle">Poster Stat</text>')
        parts.append(f'<text x="{panel_x + 56}" y="{panel_y + 170}" class="stat" font-size="126">{escape(value_text)}</text>')
        parts.append(f'<text x="{panel_x + 56}" y="{panel_y + 214}" class="subtitle">{label}</text>')
        parts.append(f'<text x="{panel_x + 56}" y="{panel_y + 248}" class="source">Type-led highlight block</text>')
    elif theme_set == "market_technical":
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="12" fill="{_theme_token(chart_spec, "panel", "#f9fbfd")}" stroke="{_theme_token(chart_spec, "grid_strong", "#90a3b8")}" stroke-width="2" />')
        parts.append(f'<line x1="{panel_x}" y1="{panel_y + 44}" x2="{panel_x + panel_width}" y2="{panel_y + 44}" stroke="{_theme_token(chart_spec, "grid", "#c4d2de")}" stroke-width="1" stroke-opacity="0.9" />')
        parts.append(f'<text x="{panel_x + 18}" y="{panel_y + 30}" class="source">STAT BLOCK</text>')
        parts.append(f'<text x="{panel_x + 18}" y="{panel_y + 102}" class="subtitle">{label}</text>')
        parts.append(f'<text x="{panel_x + panel_width - 20}" y="{panel_y + 164}" class="stat" font-size="98" text-anchor="end">{escape(value_text)}</text>')
        parts.append(f'<text x="{panel_x + panel_width - 20}" y="{panel_y + 204}" class="source" text-anchor="end">technical readout</text>')
    elif theme_set in {"editorial_outline", "gallery_infographic"}:
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="{28 if theme_set == "gallery_infographic" else 20}" fill="{_theme_token(chart_spec, "panel", "#fff8f0")}" stroke="{_theme_token(chart_spec, "accent", "#b45309")}" stroke-width="2" />')
        parts.append(f'<text x="{panel_x + 28}" y="{panel_y + 48}" class="subtitle">{label}</text>')
        parts.append(f'<text x="{panel_x + 28}" y="{panel_y + 156}" class="stat" font-size="112">{escape(value_text)}</text>')
        parts.append(f'<line x1="{panel_x + 28}" y1="{panel_y + 178}" x2="{panel_x + panel_width - 28}" y2="{panel_y + 178}" stroke="{_theme_token(chart_spec, "accent_alt", "#7c2d12")}" stroke-width="2" stroke-opacity="0.55" />')
        if theme_set == "gallery_infographic":
            parts.append(f'<circle cx="{panel_x + panel_width - 40}" cy="{panel_y + 38}" r="12" fill="{_theme_token(chart_spec, "accent_alt", "#0f766e")}" fill-opacity="0.18" stroke="{_theme_token(chart_spec, "accent_alt", "#0f766e")}" stroke-width="2" />')
    else:
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="{radius}" fill="{_theme_token(chart_spec, "panel", "#ffffff")}" stroke="{_theme_token(chart_spec, "grid", "#cbd5e1")}" stroke-width="1.5" />')
        parts.append(f'<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="8" rx="{radius}" fill="{_theme_token(chart_spec, "accent", "#2563eb")}" fill-opacity="0.88" />')
        parts.append(f'<text x="{panel_x + 26}" y="{panel_y + 48}" class="subtitle">{label}</text>')
        parts.append(f'<text x="{panel_x + 26}" y="{panel_y + 154}" class="stat" font-size="110">{escape(value_text)}</text>')
        parts.append(f'<text x="{panel_x + 26}" y="{panel_y + 198}" class="source">headline summary</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_donut(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    height = 560
    cx = 270
    cy = 285
    radius = 120
    circumference = 2 * 3.141592653589793 * radius
    total = sum(float(record.get("value") or 0.0) for record in records) or 1.0
    colors = _share_palette(chart_spec)
    offset = 0.0
    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "donut")
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{_theme_token(chart_spec, "track", "#e2e8f0")}" stroke-width="40" fill="none" />'
    )
    for index, record in enumerate(records):
        value = float(record.get("value") or 0.0)
        dash = (value / total) * circumference
        segment_stroke = colors[index % len(colors)]
        if index in patterned_indexes:
            segment_stroke = _series_fill_style(
                chart_spec,
                pattern_defs,
                slot=f"donut-{index}",
                base_color=segment_stroke,
                geometry="stroke",
            )["paint"]
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{segment_stroke}" stroke-width="40" fill="none" '
            f'stroke-dasharray="{dash:.2f} {circumference - dash:.2f}" stroke-dashoffset="-{offset:.2f}" transform="rotate(-90 {cx} {cy})" />'
        )
        offset += dash
    dominant = max(records, key=lambda record: float(record.get("value") or 0.0), default={})
    center_value = _format_value(float(dominant.get("value") or 0.0), str(dominant.get("unit") or dataset.get("unit") or "").strip())
    parts.append(f'<text x="{cx}" y="{cy - 8}" class="stat" text-anchor="middle" font-size="48">{escape(center_value)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 26}" class="subtitle" text-anchor="middle">{escape(str(dominant.get("label") or ""))}</text>')
    legend_x = 520
    legend_y = 170
    value_x = width - 80
    swatch_radius = _motif_token(chart_spec, "legend_swatch_radius", 4)
    for index, record in enumerate(records):
        row_center = legend_y + index * 48
        color = colors[index % len(colors)]
        value_text = _format_value(float(record.get("value") or 0.0), str(record.get("unit") or dataset.get("unit") or "").strip())
        text_y = _text_baseline_for_center(row_center, font_size=16)
        swatch_style = {"paint": color, "stroke": None, "stroke_width": None}
        if index in patterned_indexes:
            swatch_style = _series_fill_style(chart_spec, pattern_defs, slot=f"donut-legend-{index}", base_color=color)
        parts.append(
            f'<rect x="{legend_x}" y="{row_center - 9}" width="18" height="18" rx="{swatch_radius}" fill="{swatch_style["paint"]}"'
            f'{_svg_optional_stroke(swatch_style["stroke"], swatch_style["stroke_width"])} />'
        )
        parts.append(
            f'<text x="{legend_x + 28}" y="{text_y}" class="label">{escape(str(record.get("display_label") or record.get("label") or ""))}</text>'
        )
        parts.append(f'<text x="{value_x}" y="{text_y}" class="value" text-anchor="end">{escape(value_text)}</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_pie(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    height = 560
    cx = 280
    cy = 300
    radius = 148
    total = sum(float(record.get("value") or 0.0) for record in records) or 1.0
    colors = _share_palette(chart_spec)
    start_angle = -90.0
    dominant = max(records, key=lambda record: float(record.get("value") or 0.0), default={})

    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "pie")
    for index, record in enumerate(records):
        value = float(record.get("value") or 0.0)
        sweep = (value / total) * 360.0
        end_angle = start_angle + sweep
        slice_fill = colors[index % len(colors)]
        slice_style = {"paint": slice_fill, "stroke": _theme_token(chart_spec, "panel", "#ffffff"), "stroke_width": 3}
        if index in patterned_indexes:
            slice_style = _series_fill_style(chart_spec, pattern_defs, slot=f"pie-{index}", base_color=slice_fill)
            if slice_style["stroke"] is None:
                slice_style["stroke"] = _theme_token(chart_spec, "panel", "#ffffff")
                slice_style["stroke_width"] = 3
        parts.append(
            f'<path d="{_pie_slice_path(cx=cx, cy=cy, radius=radius, start_angle=start_angle, end_angle=end_angle)}" '
            f'fill="{slice_style["paint"]}"{_svg_optional_stroke(slice_style["stroke"], slice_style["stroke_width"])} />'
        )
        start_angle = end_angle
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="52" fill="{_theme_token(chart_spec, "panel", "#ffffff")}" fill-opacity="0.84" stroke="{_theme_token(chart_spec, "track", "#e2e8f0")}" stroke-width="2" />'
    )
    dominant_label = escape(str(dominant.get("label") or ""))
    dominant_value = _format_value(float(dominant.get("value") or 0.0), str(dominant.get("unit") or dataset.get("unit") or "").strip())
    parts.append(f'<text x="{cx}" y="{cy - 4}" class="value" text-anchor="middle" font-size="30">{escape(dominant_value)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 22}" class="source" text-anchor="middle">{dominant_label}</text>')

    legend_x = 560
    legend_y = 156
    value_x = width - 80
    swatch_radius = _motif_token(chart_spec, "legend_swatch_radius", 4)
    for index, record in enumerate(records):
        row_center = legend_y + index * 48
        color = colors[index % len(colors)]
        value_text = _format_value(float(record.get("value") or 0.0), str(record.get("unit") or dataset.get("unit") or "").strip())
        text_y = _text_baseline_for_center(row_center, font_size=16)
        swatch_style = {"paint": color, "stroke": None, "stroke_width": None}
        if index in patterned_indexes:
            swatch_style = _series_fill_style(chart_spec, pattern_defs, slot=f"pie-legend-{index}", base_color=color)
        parts.append(
            f'<rect x="{legend_x}" y="{row_center - 9}" width="18" height="18" rx="{swatch_radius}" fill="{swatch_style["paint"]}"'
            f'{_svg_optional_stroke(swatch_style["stroke"], swatch_style["stroke_width"])} />'
        )
        parts.append(
            f'<text x="{legend_x + 28}" y="{text_y}" class="label">{escape(str(record.get("display_label") or record.get("label") or ""))}</text>'
        )
        parts.append(f'<text x="{value_x}" y="{text_y}" class="value" text-anchor="end">{escape(value_text)}</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_percentage_progress(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    if dataset.get("shape") == "single_value":
        return _render_single_progress(chart_spec, dataset)
    return _render_multi_progress(chart_spec, dataset)


def _render_radial_gauge(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    width = 960
    height = 520
    cx = 290
    cy = 300
    radius = 128
    stroke = 34
    raw_value = float(dataset.get("value") or 0.0)
    progress = max(0.0, min(100.0, raw_value))
    circumference = 2 * math.pi * radius
    dash = circumference * (progress / 100.0)
    value_text = _format_value(raw_value, str(dataset.get("unit") or "").strip())
    label = escape(str(dataset.get("label") or chart_spec.get("title_text") or "Progress"))

    parts = _svg_parts(width, height, chart_spec)
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{_theme_token(chart_spec, "track", "#e2e8f0")}" stroke-width="{stroke}" fill="none" />')
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{_theme_token(chart_spec, "accent", "#2563eb")}" stroke-width="{stroke}" fill="none" '
        f'stroke-dasharray="{dash:.2f} {circumference - dash:.2f}" transform="rotate(-90 {cx} {cy})" stroke-linecap="round" />'
    )
    parts.append(f'<text x="{cx}" y="{cy - 8}" class="stat" text-anchor="middle" font-size="56">{escape(value_text)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 28}" class="subtitle" text-anchor="middle">{label}</text>')
    parts.append(f'<text x="{cx - radius}" y="{cy + radius + 34}" class="source" text-anchor="start">0%</text>')
    parts.append(f'<text x="{cx + radius}" y="{cy + radius + 34}" class="source" text-anchor="end">100%</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_semi_donut(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    width = 960
    height = 500
    cx = 320
    cy = 360
    radius = 170
    stroke = 34
    raw_value = float(dataset.get("value") or 0.0)
    progress = max(0.0, min(100.0, raw_value))
    value_text = _format_value(raw_value, str(dataset.get("unit") or "").strip())
    label = escape(str(dataset.get("label") or chart_spec.get("title_text") or "Progress"))
    arc_path = _arc_path(cx=cx, cy=cy, radius=radius, start_angle=180.0, end_angle=360.0)
    progress_path = _arc_path(cx=cx, cy=cy, radius=radius, start_angle=180.0, end_angle=180.0 + 180.0 * (progress / 100.0))

    parts = _svg_parts(width, height, chart_spec)
    parts.append(f'<path d="{arc_path}" stroke="{_theme_token(chart_spec, "track", "#e2e8f0")}" stroke-width="{stroke}" fill="none" stroke-linecap="round" />')
    parts.append(f'<path d="{progress_path}" stroke="{_theme_token(chart_spec, "accent", "#2563eb")}" stroke-width="{stroke}" fill="none" stroke-linecap="round" />')
    parts.append(f'<text x="{cx}" y="{cy - 32}" class="stat" text-anchor="middle" font-size="54">{escape(value_text)}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 8}" class="subtitle" text-anchor="middle">{label}</text>')
    parts.append(f'<text x="{cx - radius}" y="{cy + 22}" class="source" text-anchor="start">0%</text>')
    parts.append(f'<text x="{cx + radius}" y="{cy + 22}" class="source" text-anchor="end">100%</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_stacked_progress(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    height = 520
    top = _content_top(chart_spec) + 12
    left = 60
    bar_y = top + 28
    bar_width = 840
    bar_height = 42
    colors = _share_palette(chart_spec)
    total = sum(float(record.get("value") or 0.0) for record in records) or 1.0
    legend_y = bar_y + 96
    value_x = width - 80
    swatch_radius = _motif_token(chart_spec, "legend_swatch_radius", 4)

    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "stacked_progress")
    parts.append(f'<rect x="{left}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="21" fill="{_theme_token(chart_spec, "track", "#e2e8f0")}" />')
    cursor = 0.0
    for index, record in enumerate(records):
        value = float(record.get("value") or 0.0)
        segment_width = bar_width * (value / total)
        color = colors[index % len(colors)]
        segment_style = {"paint": color, "stroke": None, "stroke_width": None}
        if index in patterned_indexes:
            segment_style = _series_fill_style(chart_spec, pattern_defs, slot=f"stacked-progress-{index}", base_color=color)
        parts.append(
            f'<rect x="{left + cursor:.2f}" y="{bar_y}" width="{segment_width:.2f}" height="{bar_height}" fill="{segment_style["paint"]}"'
            f'{_svg_optional_stroke(segment_style["stroke"], segment_style["stroke_width"])} rx="21" />'
        )
        cursor += segment_width
    parts.append(f'<text x="{left}" y="{bar_y + 68}" class="source">0%</text>')
    parts.append(f'<text x="{left + bar_width}" y="{bar_y + 68}" class="source" text-anchor="end">100%</text>')
    for index, record in enumerate(records):
        row_center = legend_y + index * 42
        color = colors[index % len(colors)]
        value_text = _format_value(float(record.get("value") or 0.0), str(record.get("unit") or dataset.get("unit") or "").strip())
        text_y = _text_baseline_for_center(row_center, font_size=16)
        swatch_style = {"paint": color, "stroke": None, "stroke_width": None}
        if index in patterned_indexes:
            swatch_style = _series_fill_style(chart_spec, pattern_defs, slot=f"stacked-progress-legend-{index}", base_color=color)
        parts.append(
            f'<rect x="{left}" y="{row_center - 9}" width="18" height="18" rx="{swatch_radius}" fill="{swatch_style["paint"]}"'
            f'{_svg_optional_stroke(swatch_style["stroke"], swatch_style["stroke_width"])} />'
        )
        parts.append(f'<text x="{left + 28}" y="{text_y}" class="label">{escape(str(record.get("display_label") or record.get("label") or ""))}</text>')
        parts.append(f'<text x="{value_x}" y="{text_y}" class="value" text-anchor="end">{escape(value_text)}</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_single_progress(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    width = 960
    height = 360
    top = _content_top(chart_spec)
    label = escape(str(dataset.get("label") or chart_spec.get("title_text") or "Progress"))
    raw_value = float(dataset.get("value") or 0.0)
    progress = max(0.0, min(100.0, raw_value))
    value_text = _format_value(raw_value, str(dataset.get("unit") or "").strip())
    track_x = 60
    track_y = top + 76
    track_width = 840
    track_height = 34
    fill_width = track_width * (progress / 100.0)

    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    parts.append(f'<text x="{track_x}" y="{top + 24}" class="subtitle">{label}</text>')
    parts.append(f'<text x="{width - 60}" y="{top + 24}" class="stat" text-anchor="end" font-size="46">{escape(value_text)}</text>')
    parts.append(f'<rect x="{track_x}" y="{track_y}" width="{track_width}" height="{track_height}" rx="17" fill="{_theme_token(chart_spec, "track", "#e2e8f0")}" />')
    if fill_width > 0:
        progress_style = {"paint": _theme_token(chart_spec, "accent", "#2563eb"), "stroke": None, "stroke_width": None}
        if _pattern_policy(chart_spec).get("enabled"):
            progress_style = _series_fill_style(
                chart_spec,
                pattern_defs,
                slot="single-progress",
                base_color=_theme_token(chart_spec, "accent", "#2563eb"),
            )
        parts.append(
            f'<rect x="{track_x}" y="{track_y}" width="{max(18.0, fill_width):.2f}" height="{track_height}" rx="17" fill="{progress_style["paint"]}"'
            f'{_svg_optional_stroke(progress_style["stroke"], progress_style["stroke_width"])} />'
        )
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(f'<text x="{track_x}" y="{track_y + 60}" class="source">0%</text>')
    parts.append(f'<text x="{track_x + track_width}" y="{track_y + 60}" class="source" text-anchor="end">100%</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_multi_progress(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    top = _content_top(chart_spec) + 12
    left = 60
    label_col_width = 190
    track_x = left + label_col_width
    track_width = 600
    value_x = width - 60
    track_height = 22
    row_height = 76
    height = top + row_height * len(records) + 70

    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "percentage_progress")
    for index, record in enumerate(records):
        y = top + index * row_height
        raw_value = float(record.get("value") or 0.0)
        progress = max(0.0, min(100.0, raw_value))
        value_text = _format_value(raw_value, str(record.get("unit") or dataset.get("unit") or "").strip())
        fill_width = track_width * (progress / 100.0)
        track_y = y + 20
        row_center = track_y + track_height / 2
        text_y = _text_baseline_for_center(row_center, font_size=16)
        parts.append(f'<text x="{left}" y="{text_y}" class="label">{escape(str(record.get("display_label") or record.get("label") or ""))}</text>')
        parts.append(f'<text x="{value_x}" y="{text_y}" class="value" text-anchor="end">{escape(value_text)}</text>')
        parts.append(f'<rect x="{track_x}" y="{track_y}" width="{track_width}" height="{track_height}" rx="11" fill="{_theme_token(chart_spec, "track", "#e2e8f0")}" />')
        if fill_width > 0:
            bar_fill = _theme_token(chart_spec, "accent", "#2563eb")
            bar_style = {"paint": bar_fill, "stroke": None, "stroke_width": None}
            if index in patterned_indexes:
                bar_style = _series_fill_style(chart_spec, pattern_defs, slot=f"percentage-progress-{index}", base_color=bar_fill)
            parts.append(
                f'<rect x="{track_x}" y="{track_y}" width="{max(10.0, fill_width):.2f}" height="{track_height}" rx="11" fill="{bar_style["paint"]}"'
                f'{_svg_optional_stroke(bar_style["stroke"], bar_style["stroke_width"])} />'
            )
        source_y = track_y + track_height + 18
        parts.append(f'<text x="{track_x}" y="{source_y}" class="source">0%</text>')
        parts.append(f'<text x="{track_x + track_width}" y="{source_y}" class="source" text-anchor="end">100%</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_distribution_histogram(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    bins = dataset.get("bins") or []
    width = 960
    height = 560
    frame = _plot_frame(chart_spec, width=width, height=height, default_left=80, default_right=40, default_bottom=90)
    left = frame["plot_left"]
    top = frame["plot_top"]
    chart_width = frame["plot_width"]
    chart_height = frame["plot_height"]
    max_count = max((float(item.get("count") or 0.0) for item in bins), default=1.0) or 1.0
    bar_width = chart_width / max(1, len(bins))

    parts = _svg_parts(width, height, chart_spec)
    parts.extend(_plot_guides(chart_spec, frame))
    parts.append(f'<line x1="{left}" y1="{frame["plot_bottom"]}" x2="{frame["plot_right"]}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    for index, item in enumerate(bins):
        count = float(item.get("count") or 0.0)
        x = left + bar_width * index + 2
        bar_h = (count / max_count) * chart_height
        y = top + chart_height - bar_h
        width_inner = max(8.0, bar_width - 4)
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{width_inner:.2f}" height="{bar_h:.2f}" fill="{_theme_token(chart_spec, "accent_alt", "#0f766e")}" rx="{_motif_token(chart_spec, "bar_radius", 6)}" />')
        parts.append(f'<text x="{x + width_inner / 2:.2f}" y="{frame["plot_bottom"] + 24}" class="tick" text-anchor="middle">{escape(str(item.get("label") or ""))}</text>')
    parts.append(f'<text x="{left}" y="{top - 18}" class="axis">{escape(str(dataset.get("y_label") or "count"))}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_stock_candlestick(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    candles = dataset.get("candles") or []
    width = 960
    height = 560
    frame = _plot_frame(chart_spec, width=width, height=height, default_left=80, default_right=40, default_bottom=90)
    left = frame["plot_left"]
    top = frame["plot_top"]
    chart_width = frame["plot_width"]
    chart_height = frame["plot_height"]
    highest = max((float(item.get("high") or 0.0) for item in candles), default=1.0) or 1.0
    lowest = min((float(item.get("low") or 0.0) for item in candles), default=0.0)
    span = highest - lowest or 1.0
    candle_step = chart_width / max(1, len(candles))
    body_width = max(10.0, min(26.0, candle_step * 0.45))

    parts = _svg_parts(width, height, chart_spec)
    parts.extend(_plot_guides(chart_spec, frame))
    parts.append(f'<line x1="{left}" y1="{frame["plot_bottom"]}" x2="{frame["plot_right"]}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    for index, candle in enumerate(candles):
        x_center = left + candle_step * index + candle_step / 2
        high_y = top + chart_height - ((float(candle.get("high") or 0.0) - lowest) / span) * chart_height
        low_y = top + chart_height - ((float(candle.get("low") or 0.0) - lowest) / span) * chart_height
        open_y = top + chart_height - ((float(candle.get("open") or 0.0) - lowest) / span) * chart_height
        close_y = top + chart_height - ((float(candle.get("close") or 0.0) - lowest) / span) * chart_height
        rise = float(candle.get("close") or 0.0) >= float(candle.get("open") or 0.0)
        color = _theme_token(chart_spec, "positive", "#0f766e") if rise else _theme_token(chart_spec, "negative", "#dc2626")
        body_y = min(open_y, close_y)
        body_h = max(3.0, abs(close_y - open_y))
        parts.append(f'<line x1="{x_center:.2f}" y1="{high_y:.2f}" x2="{x_center:.2f}" y2="{low_y:.2f}" stroke="{color}" stroke-width="{_motif_token(chart_spec, "candlestick_wick_width", 2)}" />')
        parts.append(f'<rect x="{x_center - body_width / 2:.2f}" y="{body_y:.2f}" width="{body_width:.2f}" height="{body_h:.2f}" fill="{color}" rx="3"{_svg_optional_stroke(_theme_token(chart_spec, "bg", "#ffffff"), _motif_token(chart_spec, "candlestick_body_stroke_width", 0))} />')
        parts.append(f'<text x="{x_center:.2f}" y="{frame["plot_bottom"] + 24}" class="tick" text-anchor="middle">{escape(str(candle.get("x") or ""))}</text>')
    parts.append(f'<text x="{left}" y="{top - 18}" class="axis">{escape(str(dataset.get("y_label") or "price"))}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_metric_wall(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    width = 960
    theme_set = _theme_set_key(chart_spec)
    gap_x = 28
    gap_y = 28
    start_x = 60
    start_y = _content_top(chart_spec) + 12
    colors = _card_palette(chart_spec)
    positions: list[dict[str, float]] = []
    if theme_set == "poster_editorial" and records:
        hero_height = 178
        positions.append({"x": start_x, "y": start_y, "width": width - 120, "height": hero_height})
        small_width = (width - 120 - gap_x) / 2
        small_height = 150
        for index in range(1, len(records)):
            row = (index - 1) // 2
            col = (index - 1) % 2
            positions.append(
                {
                    "x": start_x + col * (small_width + gap_x),
                    "y": start_y + hero_height + gap_y + row * (small_height + gap_y),
                    "width": small_width,
                    "height": small_height,
                }
            )
        final_bottom = positions[-1]["y"] + positions[-1]["height"] if positions else start_y
    else:
        if theme_set == "market_technical":
            cols = 3 if len(records) >= 3 else max(1, len(records))
            card_height = 132
            card_width = (width - 120 - gap_x * max(0, cols - 1)) / cols
        else:
            cols = 2 if len(records) > 2 else max(1, len(records))
            card_width = 400
            card_height = 156
        row_count = max(1, (len(records) + cols - 1) // cols)
        for index in range(len(records)):
            row = index // cols
            col = index % cols
            positions.append(
                {
                    "x": start_x + col * (card_width + gap_x),
                    "y": start_y + row * (card_height + gap_y),
                    "width": card_width,
                    "height": card_height,
                }
            )
        final_bottom = start_y + row_count * card_height + max(0, row_count - 1) * gap_y
    height = int(final_bottom + 72)
    parts = _svg_parts(width, height, chart_spec)
    for index, record in enumerate(records):
        position = positions[index]
        x = position["x"]
        y = position["y"]
        card_width = position["width"]
        card_height = position["height"]
        fill = colors[index % len(colors)]
        value_text = _format_value(float(record.get("value") or 0.0), str(record.get("unit") or dataset.get("unit") or "").strip())
        value_font_size = _metric_font_size(value_text)
        label = escape(str(record.get("display_label") or record.get("label") or ""))
        note = escape(str(record.get("note") or ""))
        if theme_set == "broadcast_signal":
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="16" fill="{_theme_token(chart_spec, "panel_alt", "#12203a")}" />')
            parts.append(f'<rect x="{x}" y="{y}" width="8" height="{card_height}" rx="6" fill="{_theme_token(chart_spec, "accent", "#f97316")}" />')
            parts.append(f'<rect x="{x + 20}" y="{y + 18}" width="116" height="24" rx="8" fill="{_theme_token(chart_spec, "header_fill", "#16243f")}" />')
            parts.append(f'<text x="{x + 32}" y="{y + 35}" class="source">SIGNAL KPI</text>')
            parts.append(f'<text x="{x + 20}" y="{y + 66}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{x + 20}" y="{y + 122}" class="stat" font-size="{value_font_size + 4}">{escape(value_text)}</text>')
            parts.append(f'<line x1="{x + 20}" y1="{y + card_height - 18}" x2="{x + card_width - 24}" y2="{y + card_height - 18}" stroke="{_theme_token(chart_spec, "accent_alt", "#22d3ee")}" stroke-width="2" stroke-opacity="0.5" />')
            if note:
                parts.append(f'<text x="{x + 20}" y="{y + card_height - 28}" class="source">{note}</text>')
        elif theme_set == "poster_editorial":
            radius = 30 if index == 0 else 22
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="{radius}" fill="{_theme_token(chart_spec, "panel", "#fff3e5")}" />')
            parts.append(f'<rect x="{x + 24}" y="{y + 22}" width="{12 if index == 0 else 8}" height="{card_height - 42}" rx="6" fill="{_theme_token(chart_spec, "accent", "#c2410c")}" />')
            parts.append(f'<text x="{x + 48}" y="{y + 46}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{x + 48}" y="{y + min(card_height - 42, 128)}" class="stat" font-size="{value_font_size + (22 if index == 0 else 4)}">{escape(value_text)}</text>')
            parts.append(f'<text x="{x + 48}" y="{y + card_height - 20}" class="source">{note or "editorial poster metric"}</text>')
        elif theme_set == "market_technical":
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="12" fill="{_theme_token(chart_spec, "panel", "#f9fbfd")}" stroke="{_theme_token(chart_spec, "grid_strong", "#90a3b8")}" stroke-width="1.5" />')
            parts.append(f'<line x1="{x}" y1="{y + 34}" x2="{x + card_width}" y2="{y + 34}" stroke="{_theme_token(chart_spec, "grid", "#c4d2de")}" stroke-width="1" stroke-opacity="0.9" />')
            parts.append(f'<text x="{x + 14}" y="{y + 23}" class="source">KPI {index + 1:02d}</text>')
            parts.append(f'<text x="{x + 14}" y="{y + 58}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{x + card_width - 14}" y="{y + 104}" class="stat" font-size="{value_font_size - 2}" text-anchor="end">{escape(value_text)}</text>')
        elif theme_set in {"editorial_outline", "gallery_infographic"}:
            radius = 28 if theme_set == "gallery_infographic" else 18
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="{radius}" fill="{_theme_token(chart_spec, "panel", "#fff8f0")}" stroke="{_theme_token(chart_spec, "accent", "#b45309")}" stroke-width="2" />')
            parts.append(f'<text x="{x + 22}" y="{y + 38}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{x + 22}" y="{y + 104}" class="stat" font-size="{value_font_size}">{escape(value_text)}</text>')
            parts.append(f'<line x1="{x + 22}" y1="{y + card_height - 24}" x2="{x + card_width - 22}" y2="{y + card_height - 24}" stroke="{_theme_token(chart_spec, "accent_alt", "#7c2d12")}" stroke-width="2" stroke-opacity="0.35" />')
            if note:
                parts.append(f'<text x="{x + 22}" y="{y + card_height - 32}" class="source">{note}</text>')
            if theme_set == "gallery_infographic":
                parts.append(f'<circle cx="{x + card_width - 28}" cy="{y + 28}" r="10" fill="{_theme_token(chart_spec, "accent_alt", "#0f766e")}" fill-opacity="0.16" stroke="{_theme_token(chart_spec, "accent_alt", "#0f766e")}" stroke-width="2" />')
        else:
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="{card_height}" rx="22" fill="{fill}" />')
            parts.append(f'<rect x="{x}" y="{y}" width="{card_width}" height="8" rx="22" fill="{_theme_token(chart_spec, "accent", "#2563eb")}" fill-opacity="0.88" />')
            parts.append(f'<text x="{x + 22}" y="{y + 36}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{x + 22}" y="{y + 96}" class="stat" font-size="{value_font_size}">{escape(value_text)}</text>')
            if note:
                parts.append(f'<text x="{x + 22}" y="{y + 132}" class="source">{note}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_fact_table(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    headers = dataset.get("headers") or ["항목", "값"]
    rows = dataset.get("rows") or []
    width = 960
    top = _content_top(chart_spec)
    table_x = 60
    table_y = top + 12
    table_width = width - 120
    row_height = 78
    padding = int(_component_token(chart_spec, "table_cell_padding", 16) or 16)
    divider_opacity = float(_component_token(chart_spec, "table_row_divider_opacity", 0.2) or 0.2)
    theme_set = _theme_set_key(chart_spec)
    header_offset = 68 if theme_set == "broadcast_signal" else 54
    container_height = header_offset + row_height * len(rows)
    height = table_y + container_height + 72
    label_header = escape(str(headers[0] if headers else "항목"))
    value_header = escape(str(headers[1] if len(headers) > 1 else "값"))
    parts = _svg_parts(width, height, chart_spec)

    if theme_set == "broadcast_signal":
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{container_height}" rx="20" fill="{_theme_token(chart_spec, "panel", "#0c1730")}" />')
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="12" rx="20" fill="{_theme_token(chart_spec, "accent", "#f97316")}" />')
        parts.append(f'<text x="{table_x + padding}" y="{table_y + 30}" class="source">FACT SHEET</text>')
        header_y = table_y + 52
    elif theme_set == "poster_editorial":
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{container_height}" rx="30" fill="{_theme_token(chart_spec, "panel", "#fff3e5")}" />')
        parts.append(f'<rect x="{table_x + 22}" y="{table_y + 18}" width="10" height="{container_height - 36}" rx="5" fill="{_theme_token(chart_spec, "accent", "#c2410c")}" />')
        header_y = table_y + 36
    elif theme_set == "market_technical":
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{container_height}" rx="12" fill="{_theme_token(chart_spec, "panel", "#f9fbfd")}" stroke="{_theme_token(chart_spec, "grid_strong", "#90a3b8")}" stroke-width="1.5" />')
        header_y = table_y + 36
    elif theme_set in {"editorial_outline", "gallery_infographic"}:
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{container_height}" rx="{28 if theme_set == "gallery_infographic" else 20}" fill="{_theme_token(chart_spec, "panel", "#fff8f0")}" stroke="{_theme_token(chart_spec, "accent", "#b45309")}" stroke-width="2" />')
        header_y = table_y + 36
    else:
        parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{container_height}" rx="20" fill="{_theme_token(chart_spec, "panel", "#ffffff")}" stroke="{_theme_token(chart_spec, "grid", "#cbd5e1")}" stroke-width="1.2" />')
        header_y = table_y + 36

    parts.append(f'<text x="{table_x + padding}" y="{header_y}" class="header">{label_header}</text>')
    parts.append(f'<text x="{table_x + table_width - padding}" y="{header_y}" class="header" text-anchor="end">{value_header}</text>')
    value_x = table_x + table_width - padding
    label_x = table_x + padding
    for row_index, row in enumerate(rows):
        label = escape(str(row[0] if row else ""))
        value = escape(str(row[1] if len(row) > 1 else ""))
        y = table_y + header_offset + row_index * row_height
        if theme_set == "broadcast_signal":
            parts.append(f'<rect x="{table_x + 14}" y="{y + 8}" width="{table_width - 28}" height="{row_height - 12}" rx="14" fill="{_theme_token(chart_spec, "panel_alt", "#12203a")}" />')
            parts.append(f'<rect x="{table_x + 14}" y="{y + 8}" width="6" height="{row_height - 12}" rx="4" fill="{_theme_token(chart_spec, "accent_alt", "#22d3ee")}" />')
            label_y = y + 34
            value_y = y + 50
            parts.append(f'<text x="{label_x + 18}" y="{label_y}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{value_x - 10}" y="{value_y}" class="value" text-anchor="end" font-size="28">{value}</text>')
        elif theme_set == "poster_editorial":
            parts.append(f'<line x1="{table_x + 40}" y1="{y}" x2="{table_x + table_width - 40}" y2="{y}" stroke="{_theme_token(chart_spec, "accent_alt", "#7c3aed")}" stroke-width="1.5" stroke-opacity="0.28" />')
            parts.append(f'<text x="{label_x + 24}" y="{y + 26}" class="source">{label}</text>')
            parts.append(f'<text x="{value_x - 8}" y="{y + 52}" class="stat" text-anchor="end" font-size="34">{value}</text>')
        elif theme_set == "market_technical":
            parts.append(f'<line x1="{table_x}" y1="{y}" x2="{table_x + table_width}" y2="{y}" stroke="{_theme_token(chart_spec, "grid", "#c4d2de")}" stroke-width="1" stroke-opacity="{1 - divider_opacity / 2:.2f}" />')
            parts.append(f'<text x="{label_x}" y="{y + 32}" class="label">{label}</text>')
            parts.append(f'<text x="{value_x}" y="{y + 32}" class="value" text-anchor="end">{value}</text>')
        elif theme_set in {"editorial_outline", "gallery_infographic"}:
            row_radius = 18 if theme_set == "gallery_infographic" else 12
            parts.append(f'<rect x="{table_x + 16}" y="{y + 8}" width="{table_width - 32}" height="{row_height - 16}" rx="{row_radius}" fill="{_theme_token(chart_spec, "panel_alt", "#f2e6d4")}" />')
            parts.append(f'<text x="{label_x + 12}" y="{y + 32}" class="subtitle">{label}</text>')
            parts.append(f'<text x="{value_x - 12}" y="{y + 48}" class="value" text-anchor="end" font-size="28">{value}</text>')
        else:
            fill = _theme_token(chart_spec, "panel", "#ffffff") if row_index % 2 == 0 else _theme_token(chart_spec, "panel_alt", "#f8fafc")
            parts.append(f'<rect x="{table_x + 12}" y="{y + 8}" width="{table_width - 24}" height="{row_height - 14}" rx="14" fill="{fill}" />')
            parts.append(f'<text x="{label_x + 10}" y="{y + 32}" class="label">{label}</text>')
            parts.append(f'<text x="{value_x - 10}" y="{y + 48}" class="value" text-anchor="end" font-size="28">{value}</text>')
        if theme_set not in {"poster_editorial", "broadcast_signal"} and row_index < len(rows) - 1:
            parts.append(
                f'<line x1="{table_x + 18}" y1="{y + row_height}" x2="{table_x + table_width - 18}" y2="{y + row_height}" stroke="{_theme_token(chart_spec, "grid", "#cbd5e1")}" stroke-width="1" stroke-opacity="{divider_opacity}" />'
            )
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_table(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    headers = dataset.get("headers") or []
    rows = dataset.get("rows") or []
    col_count = max(1, len(headers))
    column_alignments = _table_column_alignments(headers, rows)
    width = max(960, 180 * col_count)
    row_height = 40
    top = _content_top(chart_spec)
    height = top + row_height * (len(rows) + 1) + 80
    table_x = 60
    table_y = top + 10
    table_width = width - 120
    col_width = table_width / col_count
    parts = _svg_parts(width, height, chart_spec)
    parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_width}" height="{row_height}" fill="{_theme_token(chart_spec, "header_fill", "#e2e8f0")}" rx="12" />')
    for index, header in enumerate(headers):
        x = table_x + col_width * index
        anchor_x, anchor = _table_text_anchor(x=x, col_width=col_width, alignment=column_alignments[index])
        parts.append(
            f'<text x="{anchor_x:.2f}" y="{_text_baseline_for_center(table_y + row_height / 2, font_size=16)}" class="header"{_svg_text_anchor_attr(anchor)}>{escape(str(header))}</text>'
        )
    for row_index, row in enumerate(rows, start=1):
        y = table_y + row_height * row_index
        fill = _theme_token(chart_spec, "panel", "#ffffff") if row_index % 2 else _theme_token(chart_spec, "panel_alt", "#f8fafc")
        parts.append(f'<rect x="{table_x}" y="{y}" width="{table_width}" height="{row_height}" fill="{fill}" />')
        for col_index in range(col_count):
            cell = row[col_index] if col_index < len(row) else ""
            x = table_x + col_width * col_index
            anchor_x, anchor = _table_text_anchor(x=x, col_width=col_width, alignment=column_alignments[col_index])
            parts.append(
                f'<text x="{anchor_x:.2f}" y="{_text_baseline_for_center(y + row_height / 2, font_size=16)}" class="cell"{_svg_text_anchor_attr(anchor)}>{escape(str(cell))}</text>'
            )
            parts.append(f'<line x1="{x:.2f}" y1="{table_y}" x2="{x:.2f}" y2="{y + row_height}" stroke="{_theme_token(chart_spec, "grid", "#cbd5e1")}" />')
    parts.append(
        f'<line x1="{table_x + table_width:.2f}" y1="{table_y}" x2="{table_x + table_width:.2f}" y2="{table_y + row_height * (len(rows) + 1)}" stroke="{_theme_token(chart_spec, "grid", "#cbd5e1")}" />'
    )
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_fallback(chart_spec: dict[str, Any]) -> str:
    width = 960
    height = 240
    parts = _svg_parts(width, height, chart_spec)
    parts.append(
        f'<text x="60" y="160" class="subtitle">Fallback renderer used for {escape(str(chart_spec.get("chart_family") or "unknown"))}</text>'
    )
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_annotated_chart(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    base_family = str(chart_spec.get("base_chart_family") or "line")
    if base_family == "bar_horizontal":
        return _render_annotated_bar_horizontal(chart_spec, dataset)
    if base_family == "bar":
        return _render_annotated_bar(chart_spec, dataset)
    return _render_annotated_line(chart_spec, dataset)


def _render_bar_core(chart_spec: dict[str, Any], dataset: dict[str, Any], annotated: bool) -> str:
    records = dataset.get("records") or []
    annotations = chart_spec.get("annotations") or []
    annotation = annotations[0] if annotations else {}
    width = 960
    height = 560
    frame = _plot_frame(
        chart_spec,
        width=width,
        height=height,
        default_left=80,
        default_right=40,
        default_bottom=90,
        reserve_annotation_rail=annotated,
    )
    left = frame["plot_left"]
    top = frame["plot_top"]
    chart_width = frame["plot_width"]
    chart_height = frame["plot_height"]
    max_value = max((float(item.get("value") or 0.0) for item in records), default=1.0) or 1.0
    bar_step = chart_width / max(1, len(records))
    bar_width = max(18.0, min(64.0, bar_step * 0.52))
    is_three_d = str(chart_spec.get("chart_variant") or "") == "three_d"

    parts = _svg_parts(width, height, chart_spec)
    pattern_defs: list[str] = []
    patterned_indexes = _pattern_indexes(chart_spec, records, "bar")
    parts.extend(_plot_guides(chart_spec, frame))
    parts.append(f'<line x1="{left}" y1="{frame["plot_bottom"]}" x2="{frame["plot_right"]}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    for index, record in enumerate(records):
        value = float(record.get("value") or 0.0)
        x_center = left + bar_step * index + bar_step / 2
        bar_h = (value / max_value) * chart_height
        x = x_center - bar_width / 2
        y = top + chart_height - bar_h
        label = escape(str(record.get("display_label") or record.get("label") or ""))
        fill = _theme_token(chart_spec, "accent", "#2563eb")
        bar_style = {"paint": fill, "stroke": None, "stroke_width": None}
        if annotated and str(record.get("label") or "") == str(annotation.get("label") or ""):
            fill = _theme_token(chart_spec, "annotation_stroke", "#dc2626")
            bar_style = {"paint": fill, "stroke": None, "stroke_width": None}
        elif index in patterned_indexes:
            bar_style = _series_fill_style(chart_spec, pattern_defs, slot=f"bar-{index}", base_color=fill)
        if is_three_d:
            depth = 10
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_h:.2f}" fill="{bar_style["paint"]}"'
                f'{_svg_optional_stroke(bar_style["stroke"], bar_style["stroke_width"])} rx="4" />'
            )
            parts.append(
                f'<polygon points="{x + bar_width:.2f},{y:.2f} {x + bar_width + depth:.2f},{y - depth:.2f} {x + bar_width + depth:.2f},{y + bar_h - depth:.2f} {x + bar_width:.2f},{y + bar_h:.2f}" fill="{_theme_token(chart_spec, "accent_alt", "#1d4ed8")}" />'
            )
            parts.append(
                f'<polygon points="{x:.2f},{y:.2f} {x + depth:.2f},{y - depth:.2f} {x + bar_width + depth:.2f},{y - depth:.2f} {x + bar_width:.2f},{y:.2f}" fill="{_theme_token(chart_spec, "series", ["#60a5fa"])[0]}" />'
            )
        else:
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_h:.2f}" fill="{bar_style["paint"]}"'
                f'{_svg_optional_stroke(bar_style["stroke"], bar_style["stroke_width"])} rx="{_motif_token(chart_spec, "bar_radius", 6)}" />'
            )
        parts.append(f'<text x="{x_center:.2f}" y="{frame["plot_bottom"] + 24}" class="tick" text-anchor="middle">{label}</text>')
        if annotated and str(record.get("label") or "") == str(annotation.get("label") or ""):
            callout = escape(str(annotation.get("label_text") or annotation.get("label") or "Highlighted bar"))
            callout_width = 184
            callout_height = 36
            callout_x = _annotation_rail_x(chart_spec, frame, callout_width)
            callout_y = _annotation_rail_y(frame, anchor_y=y, callout_height=callout_height)
            line_end_y = callout_y + callout_height / 2
            parts.append(f'<line x1="{x_center:.2f}" y1="{y:.2f}" x2="{callout_x:.2f}" y2="{line_end_y:.2f}" stroke="{_theme_token(chart_spec, "annotation_stroke", "#dc2626")}" stroke-width="2"{_svg_dash_attr(_motif_token(chart_spec, "annotation_connector_dasharray", None))} />')
            parts.append(f'<rect x="{callout_x:.2f}" y="{callout_y:.2f}" width="{callout_width}" height="{callout_height}" rx="{_motif_token(chart_spec, "annotation_radius", 8)}" fill="{_theme_token(chart_spec, "annotation_fill", "#fee2e2")}" />')
            parts.append(f'<text x="{callout_x + 12:.2f}" y="{_text_baseline_for_center(callout_y + callout_height / 2, font_size=14)}" class="source">{callout}</text>')
    if pattern_defs:
        parts.append(_pattern_defs_block(pattern_defs))
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_annotated_line(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    points = dataset.get("points") or []
    annotations = chart_spec.get("annotations") or []
    annotation = annotations[0] if annotations else {}
    width = 960
    height = 560
    frame = _plot_frame(
        chart_spec,
        width=width,
        height=height,
        default_left=110,
        default_right=80,
        default_bottom=80,
        reserve_annotation_rail=True,
    )
    left = frame["plot_left"]
    top = frame["plot_top"]
    chart_width = frame["plot_width"]
    chart_height = frame["plot_height"]
    max_value = max((float(point.get("y") or 0.0) for point in points), default=1.0) or 1.0
    min_value = min((float(point.get("y") or 0.0) for point in points), default=0.0)
    span = max_value - min_value or 1.0
    step_x = chart_width / max(1, len(points) - 1)

    annotation_x = None
    annotation_y = None
    poly_points: list[str] = []
    parts = _svg_parts(width, height, chart_spec)
    parts.extend(_plot_guides(chart_spec, frame))
    parts.append(
        f'<line x1="{left}" y1="{frame["plot_bottom"]}" x2="{frame["plot_right"]}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />'
    )
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{frame["plot_bottom"]}" stroke="{_theme_token(chart_spec, "grid_strong", "#cbd5e1")}" stroke-width="{_motif_token(chart_spec, "axis_stroke_width", 2)}" />')
    for index, point in enumerate(points):
        x = left + step_x * index
        y_value = float(point.get("y") or 0.0)
        y = top + chart_height - ((y_value - min_value) / span) * chart_height
        poly_points.append(f"{x:.2f},{y:.2f}")
        marker_svg = _marker_svg(chart_spec, x=x, y=y, fill=_theme_token(chart_spec, "accent", "#2563eb"))
        if marker_svg:
            parts.append(marker_svg)
        parts.append(f'<text x="{x:.2f}" y="{frame["plot_bottom"] + 26}" class="tick" text-anchor="middle">{escape(str(point.get("x") or ""))}</text>')
        if str(point.get("x") or "") == str(annotation.get("x") or "") and float(point.get("y") or 0.0) == float(annotation.get("y") or 0.0):
            annotation_x = x
            annotation_y = y
    parts.append(
        f'<polyline fill="none" stroke="{_theme_token(chart_spec, "accent", "#2563eb")}" stroke-width="{_motif_token(chart_spec, "primary_stroke_width", 4)}" points="{" ".join(poly_points)}" stroke-linecap="round" stroke-linejoin="round" />'
    )
    if annotation_x is not None and annotation_y is not None:
        label = escape(str(annotation.get("label") or "Key point"))
        callout_width = 192
        callout_height = 36
        callout_x = _annotation_rail_x(chart_spec, frame, callout_width)
        callout_y = _annotation_rail_y(frame, anchor_y=annotation_y, callout_height=callout_height)
        line_end_y = callout_y + callout_height / 2
        parts.append(_marker_svg(chart_spec, x=annotation_x, y=annotation_y, fill=_theme_token(chart_spec, "annotation_stroke", "#dc2626"), highlight=True))
        parts.append(f'<line x1="{annotation_x:.2f}" y1="{annotation_y:.2f}" x2="{callout_x:.2f}" y2="{line_end_y:.2f}" stroke="{_theme_token(chart_spec, "annotation_stroke", "#dc2626")}" stroke-width="2"{_svg_dash_attr(_motif_token(chart_spec, "annotation_connector_dasharray", None))} />')
        parts.append(f'<rect x="{callout_x:.2f}" y="{callout_y:.2f}" width="{callout_width}" height="{callout_height}" rx="{_motif_token(chart_spec, "annotation_radius", 8)}" fill="{_theme_token(chart_spec, "annotation_fill", "#fee2e2")}" />')
        parts.append(f'<text x="{callout_x + 12:.2f}" y="{_text_baseline_for_center(callout_y + callout_height / 2, font_size=14)}" class="source">{label}</text>')
    parts.append(f'<text x="{left}" y="{top - 18}" class="axis">{escape(str(dataset.get("y_label") or "y"))}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_annotated_bar_horizontal(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    records = dataset.get("records") or []
    annotations = chart_spec.get("annotations") or []
    annotation = annotations[0] if annotations else {}
    width = 960
    top = _content_top(chart_spec)
    left = 260
    row_height = 48
    chart_width = 520
    value_x = width - 60
    max_value = max((float(item.get("value") or 0.0) for item in records), default=1.0) or 1.0
    height = top + row_height * len(records) + 100
    parts = _svg_parts(width, height, chart_spec)
    for index, record in enumerate(records):
        y = top + index * row_height
        row_center = y + 18
        value = float(record.get("value") or 0.0)
        bar_width = max(12.0, chart_width * (value / max_value)) if value > 0 else 12.0
        label = escape(str(record.get("display_label") or record.get("label") or ""))
        value_text = _format_value(value, str(record.get("unit") or dataset.get("unit") or "").strip())
        is_annotated = str(record.get("label") or "") == str(annotation.get("label") or "")
        fill = _theme_token(chart_spec, "annotation_stroke", "#dc2626") if is_annotated else _theme_token(chart_spec, "accent", "#2563eb")
        parts.append(f'<text x="{left - 16}" y="{_text_baseline_for_center(row_center, font_size=16)}" class="label" text-anchor="end">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y + 8}" width="{bar_width:.2f}" height="20" rx="10" fill="{fill}" />')
        parts.append(f'<text x="{value_x}" y="{_text_baseline_for_center(row_center, font_size=16)}" class="value" text-anchor="end">{escape(value_text)}</text>')
        if is_annotated:
            callout = escape(str(annotation.get("label_text") or annotation.get("label") or "Top rank"))
            callout_width = 170
            callout_height = 30
            callout_x = min(left + bar_width + 18, width - 210)
            callout_y = y - 20
            if callout_y < top + 8:
                callout_y = min(y + 18, height - 70)
            line_end_y = callout_y + callout_height / 2
            parts.append(f'<line x1="{left + bar_width:.2f}" y1="{y + 18}" x2="{callout_x:.2f}" y2="{line_end_y:.2f}" stroke="{_theme_token(chart_spec, "annotation_stroke", "#dc2626")}" stroke-width="2" />')
            parts.append(f'<rect x="{callout_x:.2f}" y="{callout_y:.2f}" width="{callout_width}" height="{callout_height}" rx="8" fill="{_theme_token(chart_spec, "annotation_fill", "#fee2e2")}" />')
            parts.append(f'<text x="{callout_x + 10:.2f}" y="{_text_baseline_for_center(callout_y + callout_height / 2, font_size=14)}" class="source">{callout}</text>')
    parts.append(_source_note(chart_spec, height - 24))
    parts.append(_svg_close())
    return "".join(parts)


def _render_annotated_bar(chart_spec: dict[str, Any], dataset: dict[str, Any]) -> str:
    return _render_bar_core(chart_spec=chart_spec, dataset=dataset, annotated=True)


def _svg_open(width: int, height: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">'


def _style_block(chart_spec: dict[str, Any]) -> str:
    tokens = _theme_tokens(chart_spec)
    label_weight = _component_token(chart_spec, "label_weight", 500)
    source_weight = 600 if str(_component_token(chart_spec, "source_mode", "bottom_left")) == "edge_rail" else 500
    return (
        "<style>"
        f'.cg-root .title{{font:700 {tokens["title_size"]}px {tokens["font_title"]}; fill:{tokens["text_primary"]}; letter-spacing:-0.03em;}}'
        f'.cg-root .subtitle{{font:500 {tokens["subtitle_size"]}px {tokens["font_body"]}; fill:{tokens["text_secondary"]};}}'
        f'.cg-root .label,.cg-root .axis,.cg-root .header,.cg-root .cell{{font:{label_weight} {tokens["body_size"]}px {tokens["font_body"]}; fill:{tokens["text_secondary"]};}}'
        f'.cg-root .value{{font:700 {tokens["body_size"]}px {tokens["font_body"]}; fill:{tokens["text_primary"]};}}'
        f'.cg-root .header{{font-weight:{_component_token(chart_spec, "table_header_weight", 700)}; fill:{tokens["text_primary"]};}}'
        f'.cg-root .tick{{font:500 {tokens["tick_size"]}px {tokens["font_body"]}; fill:{tokens["text_muted"]};}}'
        f'.cg-root .source{{font:{source_weight} {tokens["source_size"]}px {tokens["font_body"]}; fill:{tokens["text_muted"]}; letter-spacing:0.01em;}}'
        f'.cg-root .stat{{font:800 {tokens["stat_size"]}px {tokens["font_title"]}; fill:{tokens["text_primary"]}; letter-spacing:-0.04em;}}'
        "</style>"
    )


def _svg_close() -> str:
    return "</g></svg>"


def _inline_text_fill_tokens(svg: str, chart_spec: dict[str, Any]) -> str:
    fill_by_class = {
        "title": _theme_token(chart_spec, "text_primary", "#0f172a"),
        "subtitle": _theme_token(chart_spec, "text_secondary", "#475569"),
        "label": _theme_token(chart_spec, "text_secondary", "#334155"),
        "axis": _theme_token(chart_spec, "text_secondary", "#334155"),
        "header": _theme_token(chart_spec, "text_primary", "#0f172a"),
        "cell": _theme_token(chart_spec, "text_secondary", "#334155"),
        "value": _theme_token(chart_spec, "text_primary", "#0f172a"),
        "tick": _theme_token(chart_spec, "text_muted", "#64748b"),
        "source": _theme_token(chart_spec, "text_muted", "#64748b"),
        "stat": _theme_token(chart_spec, "text_primary", "#0f172a"),
    }
    for class_name, fill in fill_by_class.items():
        svg = re.sub(
            rf'(<text\b[^>]*class="{class_name}"(?![^>]*\sfill=)[^>]*)>',
            rf'\1 fill="{fill}" style="fill:{fill} !important;">',
            svg,
        )
    return svg


def _title_block(chart_spec: dict[str, Any]) -> str:
    title = escape(str(chart_spec.get("title_text") or "Chart"))
    subtitle = escape(str(chart_spec.get("subtitle_text") or ""))
    metrics = _title_metrics(chart_spec)
    parts = [f'<text x="60" y="{metrics["title_y"]}" class="title">{title}</text>']
    if subtitle:
        parts.append(f'<text x="60" y="{metrics["subtitle_y"]}" class="subtitle">{subtitle}</text>')
    return "".join(parts)


def _source_note(chart_spec: dict[str, Any], y: int, *, width: int = 960) -> str:
    note = escape(str(chart_spec.get("source_note_text") or "Source note pending"))
    source_mode = str(_component_token(chart_spec, "source_mode", "bottom_left") or "bottom_left")
    source_opacity = float(_component_token(chart_spec, "source_opacity", 0.82) or 0.82)
    rail_color = _theme_token(chart_spec, "grid_strong", "#94a3b8")
    if source_mode == "bottom_right":
        return f'<text x="{width - 60}" y="{y}" class="source" text-anchor="end" opacity="{source_opacity}">{note}</text>'
    if source_mode == "edge_rail":
        rail_x = width - 26
        rail_top = max(112, y - 92)
        return (
            f'<line x1="{rail_x}" y1="{rail_top}" x2="{rail_x}" y2="{y + 6}" stroke="{rail_color}" stroke-width="2" stroke-opacity="{source_opacity}" />'
            f'<text x="{rail_x - 14}" y="{y}" class="source" text-anchor="end" opacity="{source_opacity}">{note}</text>'
        )
    return f'<text x="60" y="{y}" class="source" opacity="{source_opacity}">{note}</text>'


def _format_value(value: float, unit: str) -> str:
    text = f"{int(value)}" if value.is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{text}{unit}" if unit else text


def _title_metrics(chart_spec: dict[str, Any]) -> dict[str, int]:
    has_subtitle = bool(str(chart_spec.get("subtitle_text") or "").strip())
    layout_tokens = (chart_spec.get("style_spec") or {}).get("layout_tokens") or {}
    return {
        "title_y": int(layout_tokens.get("title_y") or 52),
        "subtitle_y": int(layout_tokens.get("subtitle_y") or 82),
        "content_top": int(
            layout_tokens.get("content_top_with_subtitle" if has_subtitle else "content_top_without_subtitle")
            or (126 if has_subtitle else 108)
        ),
    }


def _content_top(chart_spec: dict[str, Any]) -> int:
    return int(_title_metrics(chart_spec)["content_top"])


def _layout_tokens(chart_spec: dict[str, Any]) -> dict[str, Any]:
    style_spec = chart_spec.get("style_spec") or {}
    layout_tokens = style_spec.get("layout_tokens")
    if isinstance(layout_tokens, dict):
        return layout_tokens
    return {}


def _component_tokens(chart_spec: dict[str, Any]) -> dict[str, Any]:
    style_spec = chart_spec.get("style_spec") or {}
    component_tokens = style_spec.get("component_tokens")
    if isinstance(component_tokens, dict):
        return component_tokens
    return {}


def _component_token(chart_spec: dict[str, Any], key: str, default: Any) -> Any:
    return _component_tokens(chart_spec).get(key, default)


def _plot_frame(
    chart_spec: dict[str, Any],
    *,
    width: int,
    height: int,
    default_left: int,
    default_right: int,
    default_bottom: int,
    reserve_annotation_rail: bool = False,
) -> dict[str, int]:
    tokens = _layout_tokens(chart_spec)
    plot_left = int(tokens.get("plot_left") or default_left)
    right_margin = int(tokens.get("plot_right") or default_right)
    bottom_margin = int(tokens.get("plot_bottom") or default_bottom)
    annotation_rail_width = int(tokens.get("annotation_rail_width") or 0) if reserve_annotation_rail else 0
    plot_top = _content_top(chart_spec)
    plot_right = width - right_margin - annotation_rail_width
    plot_bottom = height - bottom_margin
    return {
        "plot_left": plot_left,
        "plot_top": plot_top,
        "plot_right": plot_right,
        "plot_bottom": plot_bottom,
        "plot_width": plot_right - plot_left,
        "plot_height": plot_bottom - plot_top,
        "right_margin": right_margin,
        "annotation_rail_width": annotation_rail_width,
        "annotation_rail_gap": int(tokens.get("annotation_rail_gap") or 24),
        "width": width,
        "height": height,
    }


def _annotation_rail_x(chart_spec: dict[str, Any], frame: dict[str, int], callout_width: int) -> float:
    rail_start = frame["plot_right"] + frame["annotation_rail_gap"]
    rail_end = frame["width"] - frame["right_margin"]
    return float(min(rail_start, rail_end - callout_width))


def _annotation_rail_y(frame: dict[str, int], *, anchor_y: float, callout_height: int) -> float:
    min_y = frame["plot_top"] + 8
    max_y = frame["plot_bottom"] - callout_height - 12
    return float(max(min_y, min(anchor_y - callout_height / 2, max_y)))


def _text_baseline_for_center(center_y: float, *, font_size: int) -> int:
    return int(round(center_y + font_size * 0.34))


def _motif_tokens(chart_spec: dict[str, Any]) -> dict[str, Any]:
    style_spec = chart_spec.get("style_spec") or {}
    motif_tokens = style_spec.get("motif_tokens")
    if isinstance(motif_tokens, dict):
        return motif_tokens
    return {}


def _motif_token(chart_spec: dict[str, Any], key: str, default: Any) -> Any:
    return _motif_tokens(chart_spec).get(key, default)


def _svg_dash_attr(dasharray: Any) -> str:
    if not dasharray:
        return ""
    return f' stroke-dasharray="{escape(str(dasharray))}"'


def _svg_optional_stroke(stroke: str, stroke_width: Any) -> str:
    if not stroke_width:
        return ""
    return f' stroke="{stroke}" stroke-width="{stroke_width}"'


def _plot_guides(chart_spec: dict[str, Any], frame: dict[str, int]) -> list[str]:
    guide_count = int(_motif_token(chart_spec, "guide_line_count", 0) or 0)
    if guide_count <= 0:
        return []
    step = frame["plot_height"] / (guide_count + 1)
    dasharray = _motif_token(chart_spec, "guide_dasharray", None)
    opacity = _motif_token(chart_spec, "guide_opacity", 0.4)
    stroke_width = _motif_token(chart_spec, "guide_stroke_width", 1)
    guide_stroke = _theme_token(chart_spec, "grid", "#cbd5e1")
    lines: list[str] = []
    for index in range(1, guide_count + 1):
        y = frame["plot_top"] + step * index
        lines.append(
            f'<line x1="{frame["plot_left"]}" y1="{y:.2f}" x2="{frame["plot_right"]}" y2="{y:.2f}" stroke="{guide_stroke}" stroke-width="{stroke_width}" stroke-opacity="{opacity}"{_svg_dash_attr(dasharray)} />'
        )
    return lines


def _marker_svg(chart_spec: dict[str, Any], *, x: float, y: float, fill: str, highlight: bool = False) -> str:
    marker_style = str(_motif_token(chart_spec, "marker_style", "dot") or "dot")
    radius = float(_motif_token(chart_spec, "marker_radius", 5) or 5)
    if highlight:
        return (
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius + 3:.0f}" fill="{_theme_token(chart_spec, "bg", "#ffffff")}" stroke="{fill}" stroke-width="3" />'
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{max(3.0, radius - 1):.0f}" fill="{fill}" />'
        )
    if marker_style == "none":
        return ""
    if marker_style == "ring":
        return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.0f}" fill="{_theme_token(chart_spec, "bg", "#ffffff")}" stroke="{fill}" stroke-width="2" />'
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.0f}" fill="{fill}" />'


def _pattern_policy(chart_spec: dict[str, Any]) -> dict[str, Any]:
    style_spec = chart_spec.get("style_spec") or {}
    policy = style_spec.get("pattern_policy")
    if isinstance(policy, dict):
        return policy
    return {}


def _fill_treatment(chart_spec: dict[str, Any]) -> str:
    return str(_pattern_policy(chart_spec).get("fill_treatment") or "solid")


def _pattern_format_scope(chart_spec: dict[str, Any]) -> str:
    style_spec = chart_spec.get("style_spec") or {}
    return str(style_spec.get("pattern_format_scope") or "")


def _style_spec_value(chart_spec: dict[str, Any], key: str, default: str = "") -> str:
    style_spec = chart_spec.get("style_spec") or {}
    return str(style_spec.get(key) or default)


def _note_has_pattern_signal(note: Any) -> bool:
    text = str(note or "").strip().lower()
    if not text:
        return False
    return any(
        keyword in text
        for keyword in (
            "forecast",
            "projected",
            "projection",
            "estimate",
            "estimated",
            "preliminary",
            "provisional",
            "incomplete",
            "confidence",
            "interval",
            "range",
            "band",
            "잠정",
            "예상",
            "전망",
            "추정",
            "미완",
            "범위",
            "구간",
            "신뢰구간",
            "밴드",
        )
    )


def _pattern_indexes(chart_spec: dict[str, Any], records: list[dict[str, Any]], chart_family: str) -> set[int]:
    policy = _pattern_policy(chart_spec)
    if not policy.get("enabled") or not records:
        return set()
    if (
        str(policy.get("pattern_kind") or "") == "dot_sparse"
        and str(policy.get("reason") or "") in {"accessibility", "explicit_dot"}
        and chart_family in {"donut", "pie"}
    ):
        return set(range(len(records)))
    if _pattern_format_scope(chart_spec) == "chart_wide" and chart_family in {"bar", "bar_horizontal", "stacked_progress", "percentage_progress"}:
        return set(range(len(records)))
    tagged = {index for index, record in enumerate(records) if _note_has_pattern_signal(record.get("note"))}
    mode = str(policy.get("target_mode") or "none")
    if mode == "tagged_only":
        return _limit_pattern_indexes(tagged, chart_family)
    if mode == "tagged_or_secondary":
        if tagged:
            return _limit_pattern_indexes(tagged, chart_family)
        return _limit_pattern_indexes(_secondary_pattern_indexes(len(records)), chart_family)
    if mode == "alternating":
        return _limit_pattern_indexes({index for index in range(1, len(records), 2)}, chart_family)
    return set()


def _secondary_pattern_indexes(record_count: int) -> set[int]:
    if record_count <= 1:
        return {0}
    if record_count == 2:
        return {1}
    return {index for index in range(1, record_count, 2)}


def _limit_pattern_indexes(indexes: set[int], chart_family: str) -> set[int]:
    if not indexes:
        return set()
    ordered = sorted(indexes)
    if chart_family in {"donut", "pie"}:
        return set(ordered[:2])
    return set(ordered[: max(1, min(3, len(ordered)))])


def _append_pattern_def(
    chart_spec: dict[str, Any],
    pattern_defs: list[str],
    *,
    pattern_id: str,
    base_color: str,
    pattern_kind: str,
    fill_treatment: str,
) -> None:
    spacing = float(_motif_token(chart_spec, "pattern_spacing", 10) or 10)
    stroke_width = float(_motif_token(chart_spec, "pattern_stroke_width", 1.2) or 1.2)
    opacity = float(_motif_token(chart_spec, "pattern_opacity", 0.22) or 0.22)
    background_color = _theme_token(chart_spec, "bg", "#ffffff")
    stripe_color = background_color
    tile_size = spacing
    if pattern_kind == "dot_sparse":
        tile_size = _dot_pattern_tile_size(chart_spec, spacing=spacing)
    width = f"{tile_size:.2f}"
    pattern_parts = [f'<pattern id="{pattern_id}" patternUnits="userSpaceOnUse" width="{width}" height="{width}">']
    if fill_treatment == "pattern_overlay":
        pattern_parts.append(f'<rect x="0" y="0" width="{width}" height="{width}" fill="{base_color}" />')
    elif fill_treatment == "transparent_range_hatch":
        stripe_color = base_color
        opacity = max(opacity + 0.28, 0.48)
        pattern_parts.append(
            f'<rect x="0" y="0" width="{width}" height="{width}" fill="{base_color}" fill-opacity="0.12" />'
        )
    elif fill_treatment == "outline_plus_hatch":
        stripe_color = base_color
        opacity = max(opacity + 0.34, 0.56)
    else:
        stripe_color = base_color
        opacity = max(opacity + 0.18, 0.4)
    if pattern_kind == "dot_sparse":
        pattern_parts.extend(
            _dot_pattern_elements(
                chart_spec,
                tile_size=tile_size,
                stroke_width=stroke_width,
                dot_color=stripe_color,
                opacity=opacity,
            )
        )
    elif pattern_kind == "crosshatch_light":
        pattern_parts.append(
            f'<path d="M {-spacing / 2:.2f} {spacing / 2:.2f} L {spacing / 2:.2f} {-spacing / 2:.2f} M 0 {spacing:.2f} L {spacing:.2f} 0 M {-spacing / 2:.2f} {spacing / 2:.2f} L {spacing / 2:.2f} {spacing * 1.5:.2f} M 0 0 L {spacing:.2f} {spacing:.2f}" stroke="{stripe_color}" stroke-width="{stroke_width}" stroke-opacity="{opacity}" />'
        )
    elif pattern_kind == "vertical_stripe":
        pattern_parts.append(
            f'<path d="M {spacing / 3:.2f} 0 L {spacing / 3:.2f} {spacing:.2f} M {spacing * 0.75:.2f} 0 L {spacing * 0.75:.2f} {spacing:.2f}" stroke="{stripe_color}" stroke-width="{stroke_width}" stroke-opacity="{opacity}" />'
        )
    elif pattern_kind == "wide_diagonal":
        pattern_parts.append(
            f'<path d="M {-spacing:.2f} {spacing * 0.65:.2f} L {spacing * 0.65:.2f} {-spacing:.2f} M {-spacing * 0.15:.2f} {spacing * 1.15:.2f} L {spacing * 1.15:.2f} {-spacing * 0.15:.2f}" stroke="{stripe_color}" stroke-width="{stroke_width}" stroke-opacity="{opacity}" />'
        )
    else:
        pattern_parts.append(
            f'<path d="M {-spacing / 2:.2f} {spacing / 2:.2f} L {spacing / 2:.2f} {-spacing / 2:.2f} M 0 {spacing:.2f} L {spacing:.2f} 0 M {spacing / 2:.2f} {spacing * 1.5:.2f} L {spacing * 1.5:.2f} {spacing / 2:.2f}" stroke="{stripe_color}" stroke-width="{stroke_width}" stroke-opacity="{opacity}" />'
        )
    pattern_parts.append("</pattern>")
    pattern_defs.append("".join(pattern_parts))


def _dot_pattern_elements(
    chart_spec: dict[str, Any],
    *,
    tile_size: float,
    stroke_width: float,
    dot_color: str,
    opacity: float,
) -> list[str]:
    variant = _dot_pattern_variant(chart_spec)
    base_radius = _dot_pattern_base_radius(chart_spec, tile_size=tile_size, stroke_width=stroke_width)
    dot_specs: list[tuple[float, float, float, float]]
    if variant == "signal_grid":
        dot_specs = [
            (0.24, 0.24, 0.92, 0.88),
            (0.76, 0.24, 1.18, 1.0),
            (0.24, 0.76, 1.18, 1.0),
            (0.76, 0.76, 0.92, 0.88),
        ]
    elif variant == "poster_polka":
        dot_specs = [
            (0.22, 0.22, 1.72, 0.96),
            (0.76, 0.22, 0.88, 0.62),
            (0.68, 0.72, 1.34, 0.84),
            (0.12, 0.82, 0.62, 0.44),
        ]
    elif variant == "halftone_cluster":
        dot_specs = [
            (0.18, 0.22, 0.72, 0.42),
            (0.42, 0.26, 1.24, 0.72),
            (0.70, 0.34, 1.92, 1.0),
            (0.58, 0.66, 1.08, 0.62),
            (0.24, 0.78, 0.54, 0.34),
        ]
    elif variant == "perforation_grid":
        dot_specs = [
            (0.18, 0.18, 0.78, 0.68),
            (0.50, 0.18, 1.24, 0.96),
            (0.82, 0.18, 0.78, 0.68),
            (0.18, 0.50, 1.24, 0.96),
            (0.50, 0.50, 0.92, 0.82),
            (0.82, 0.50, 1.24, 0.96),
            (0.18, 0.82, 0.78, 0.68),
            (0.50, 0.82, 1.24, 0.96),
            (0.82, 0.82, 0.78, 0.68),
        ]
    else:
        dot_specs = [
            (0.26, 0.24, 1.34, 0.94),
            (0.74, 0.54, 0.94, 0.72),
            (0.18, 0.80, 0.68, 0.52),
            (0.84, 0.84, 0.58, 0.44),
        ]
    return [
        (
            f'<circle cx="{tile_size * x:.2f}" cy="{tile_size * y:.2f}" '
            f'r="{base_radius * scale:.2f}" fill="{dot_color}" fill-opacity="{min(1.0, opacity * alpha):.3f}" />'
        )
        for x, y, scale, alpha in dot_specs
    ]


def _dot_pattern_tile_size(chart_spec: dict[str, Any], *, spacing: float) -> float:
    variant = _dot_pattern_variant(chart_spec)
    if variant == "poster_polka":
        return max(24.0, spacing * 2.6)
    if variant == "halftone_cluster":
        return max(20.0, spacing * 2.2)
    if variant == "signal_grid":
        return max(14.0, spacing * 1.55)
    if variant == "perforation_grid":
        return max(16.0, spacing * 1.8)
    return max(18.0, spacing * 2.0)


def _dot_pattern_base_radius(chart_spec: dict[str, Any], *, tile_size: float, stroke_width: float) -> float:
    variant = _dot_pattern_variant(chart_spec)
    if variant == "poster_polka":
        return max(2.8, stroke_width * 2.0, tile_size * 0.18)
    if variant == "halftone_cluster":
        return max(2.2, stroke_width * 1.7, tile_size * 0.16)
    if variant == "signal_grid":
        return max(1.7, stroke_width * 1.3, tile_size * 0.11)
    if variant == "perforation_grid":
        return max(1.9, stroke_width * 1.45, tile_size * 0.12)
    return max(2.0, stroke_width * 1.55, tile_size * 0.13)


def _dot_pattern_variant(chart_spec: dict[str, Any]) -> str:
    theme_set = _style_spec_value(chart_spec, "theme_set")
    combo = _style_spec_value(chart_spec, "style_combo_preset")
    theme_name = _style_spec_value(chart_spec, "theme_name")
    if combo == "broadcast_signal" or theme_name == "broadcast":
        return "signal_grid"
    if combo == "poster_editorial" or theme_set == "poster_editorial":
        return "poster_polka"
    if combo == "gallery_infographic" or theme_set == "gallery_infographic":
        # Pinterest-style references favored halftone clusters over a uniform dot lattice.
        return "halftone_cluster"
    if combo in {"analytical_panel", "market_technical"} or theme_name == "dashboard":
        return "perforation_grid"
    return "offset_triplet"


def _pattern_fill(chart_spec: dict[str, Any], pattern_defs: list[str], *, slot: str, base_color: str) -> str:
    policy = _pattern_policy(chart_spec)
    kind = str(policy.get("pattern_kind") or _motif_token(chart_spec, "pattern_kind_default", "diagonal_hatch") or "diagonal_hatch")
    treatment = _fill_treatment(chart_spec)
    pattern_id = f"cg-pattern-{slot}"
    _append_pattern_def(
        chart_spec,
        pattern_defs,
        pattern_id=pattern_id,
        base_color=base_color,
        pattern_kind=kind,
        fill_treatment=treatment,
    )
    return f"url(#{pattern_id})"


def _series_fill_style(
    chart_spec: dict[str, Any],
    pattern_defs: list[str],
    *,
    slot: str,
    base_color: str,
    geometry: str = "fill",
) -> dict[str, Any]:
    treatment = _fill_treatment(chart_spec)
    if geometry == "stroke":
        if treatment == "pattern_overlay":
            return {"paint": _pattern_fill(chart_spec, pattern_defs, slot=slot, base_color=base_color), "stroke": None, "stroke_width": None}
        return {"paint": base_color, "stroke": None, "stroke_width": None}
    if treatment == "outline_only":
        return {"paint": "none", "stroke": base_color, "stroke_width": _motif_token(chart_spec, "outline_only_width", 2.4)}
    if treatment == "outline_plus_hatch":
        return {
            "paint": _pattern_fill(chart_spec, pattern_defs, slot=slot, base_color=base_color),
            "stroke": base_color,
            "stroke_width": _motif_token(chart_spec, "patterned_outline_width", 2.2),
        }
    if treatment == "transparent_range_hatch":
        return {
            "paint": _pattern_fill(chart_spec, pattern_defs, slot=slot, base_color=base_color),
            "stroke": base_color,
            "stroke_width": _motif_token(chart_spec, "range_outline_width", 1.7),
        }
    if treatment == "pattern_overlay":
        return {"paint": _pattern_fill(chart_spec, pattern_defs, slot=slot, base_color=base_color), "stroke": None, "stroke_width": None}
    return {"paint": base_color, "stroke": None, "stroke_width": None}


def _pattern_defs_block(pattern_defs: list[str]) -> str:
    if not pattern_defs:
        return ""
    return "<defs>" + "".join(pattern_defs) + "</defs>"


def _metric_font_size(value_text: str) -> int:
    length = len(value_text)
    if length >= 12:
        return 28
    if length >= 9:
        return 34
    if length >= 7:
        return 38
    return 42


def _share_palette(chart_spec: dict[str, Any]) -> list[str]:
    palette = _theme_token(chart_spec, "series", [])
    if isinstance(palette, list) and palette:
        return [str(item) for item in palette]
    return ["#2563eb", "#0f766e", "#dc2626", "#d97706", "#7c3aed", "#0891b2"]


def _card_palette(chart_spec: dict[str, Any]) -> list[str]:
    palette = _theme_token(chart_spec, "card_fills", [])
    if isinstance(palette, list) and palette:
        return [str(item) for item in palette]
    return ["#eff6ff", "#ecfeff", "#fef3c7", "#f5f3ff"]


def _theme_set_key(chart_spec: dict[str, Any]) -> str:
    style_spec = chart_spec.get("style_spec") or {}
    return str(style_spec.get("theme_set") or "")


def _theme_tokens(chart_spec: dict[str, Any]) -> dict[str, Any]:
    style_spec = chart_spec.get("style_spec") or {}
    tokens = style_spec.get("theme_tokens")
    if isinstance(tokens, dict):
        return tokens
    return {}


def _theme_token(chart_spec: dict[str, Any], key: str, default: Any) -> Any:
    tokens = _theme_tokens(chart_spec)
    return tokens.get(key, default)


def _pie_slice_path(cx: float, cy: float, radius: float, start_angle: float, end_angle: float) -> str:
    start_x = cx + radius * math.cos(math.radians(start_angle))
    start_y = cy + radius * math.sin(math.radians(start_angle))
    end_x = cx + radius * math.cos(math.radians(end_angle))
    end_y = cy + radius * math.sin(math.radians(end_angle))
    large_arc = 1 if end_angle - start_angle > 180 else 0
    return (
        f"M {cx:.2f} {cy:.2f} "
        f"L {start_x:.2f} {start_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f} "
        f"Z"
    )


def _arc_path(cx: float, cy: float, radius: float, start_angle: float, end_angle: float) -> str:
    start_x = cx + radius * math.cos(math.radians(start_angle))
    start_y = cy + radius * math.sin(math.radians(start_angle))
    end_x = cx + radius * math.cos(math.radians(end_angle))
    end_y = cy + radius * math.sin(math.radians(end_angle))
    large_arc = 1 if abs(end_angle - start_angle) > 180 else 0
    sweep_flag = 1 if end_angle >= start_angle else 0
    return (
        f"M {start_x:.2f} {start_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc} {sweep_flag} {end_x:.2f} {end_y:.2f}"
    )


def _column_is_numeric(rows: list[list[Any]], column_index: int) -> bool:
    values = [
        str(row[column_index]).strip()
        for row in rows
        if column_index < len(row) and str(row[column_index]).strip()
    ]
    return bool(values) and all(_is_numericish(value) for value in values)


def _is_numericish(text: str) -> bool:
    normalized = re.sub(r"[\s,]+", "", text.strip())
    if not normalized or normalized in {"-", "—", "–", "N/A", "NA", "n/a"}:
        return False
    if _is_temporalish(text):
        return False
    if re.fullmatch(r"\((.+)\)", normalized):
        inner = normalized[1:-1]
        return _is_numericish(inner)
    numeric_patterns = (
        r"(?:[A-Za-z가-힣$€¥₩]{1,8})?[<>~]?[+-]?\d+(?:\.\d+)?(?:[%]|x|X|배|bp|bps|pp|개|건|명|곳|회|원|달러|엔|유로|조|억|만|천|kg|g|t|m|km|ms|s|분|시간|일|주|개월|년|yr|yrs|k|m|b|bn|mn|mm)?",
        r"(?:[A-Za-z가-힣$€¥₩]{1,8})?[<>~]?[+-]?\d+(?:\.\d+)?/(?:주|월|년|day|week|month|year)",
    )
    return any(re.fullmatch(pattern, normalized) for pattern in numeric_patterns)


def _table_column_alignments(headers: list[Any], rows: list[list[Any]]) -> list[str]:
    col_count = max(1, len(headers))
    alignments: list[str] = []
    for index in range(col_count):
        header = str(headers[index]) if index < len(headers) else ""
        values = [
            str(row[index]).strip()
            for row in rows
            if index < len(row) and str(row[index]).strip()
        ]
        if _column_is_temporal(header, values):
            alignments.append("center")
            continue
        if _column_is_numeric(rows, index):
            alignments.append("right")
            continue
        alignments.append("left")
    return alignments


def _column_is_temporal(header: str, values: list[str]) -> bool:
    normalized_header = re.sub(r"\s+", "", header.strip().lower())
    if normalized_header in {"월", "month"}:
        return True
    if any(
        keyword in normalized_header
        for keyword in ("연도", "년도", "분기", "quarter", "일자", "날짜", "시점", "기간", "연월", "date")
    ):
        return True
    return bool(values) and all(_is_temporalish(value) for value in values)


def _is_temporalish(text: str) -> bool:
    normalized = text.strip()
    temporal_patterns = (
        r"(?:19|20)\d{2}",
        r"(?:19|20)\d{2}[./-](?:0?[1-9]|1[0-2])",
        r"(?:19|20)\d{2}[./-](?:0?[1-9]|1[0-2])[./-](?:0?[1-9]|[12]\d|3[01])",
        r"(?:0?[1-9]|1[0-2])[./-](?:0?[1-9]|[12]\d|3[01])",
        r"(?:19|20)\d{2}년(?:\s*\d{1,2}월)?",
        r"(?:\d{2}|\d{4})년\s*[1-4]분기",
        r"[Qq][1-4]",
        r"(?:19|20)?\d{2}\s*[Qq][1-4]",
        r"[Qq][1-4]\s*(?:19|20)?\d{2}",
        r"[1-4][Qq]\s*(?:19|20)?\d{2}",
        r"FY\s*(?:19|20)?\d{2}(?:[EF])?",
        r"(?:19|20)?\d{2}[EF]",
        r"H[12]\s*(?:19|20)?\d{2}",
        r"[1-4]분기",
        r"(?:0?[1-9]|1[0-2])월",
        r"(?:0?[1-9]|[12]\d|3[01])일",
    )
    return any(re.fullmatch(pattern, normalized) for pattern in temporal_patterns)


def _table_text_anchor(x: float, col_width: float, alignment: str) -> tuple[float, str]:
    if alignment == "right":
        return x + col_width - 14, "end"
    if alignment == "center":
        return x + col_width / 2, "middle"
    return x + 14, "start"


def _svg_text_anchor_attr(anchor: str) -> str:
    if anchor == "start":
        return ""
    return f' text-anchor="{anchor}"'
