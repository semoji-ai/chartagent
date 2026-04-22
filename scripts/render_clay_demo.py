"""Render a clay-style chart gallery and an HTML viewer for visual comparison.

Usage:
    PYTHONPATH=src python3 scripts/render_clay_demo.py [--out-dir tmp/clay_demo]
"""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from chartagent.design.themes import get_theme_tokens
from chartagent.renderers.svg_renderer import render_chart_svg


def build_chart_spec(*, family: str, title: str, subtitle: str, theme_name: str, source_note: str) -> dict:
    return {
        "chart_family": family,
        "title_text": title,
        "subtitle_text": subtitle,
        "source_note_text": source_note,
        "style_spec": {
            "theme_name": theme_name,
            "theme_tokens": get_theme_tokens(theme_name),
            "motif_tokens": {
                "guide_line_count": 4,
                "guide_opacity": 0.35,
                "guide_stroke_width": 1.25,
                "axis_stroke_width": 2,
                "primary_stroke_width": 5,
                "marker_radius": 7,
                "bar_radius": 14,
                "legend_swatch_radius": 6,
            },
            "component_tokens": {},
            "layout_tokens": {},
            "pattern_policy": {"enabled": False},
        },
    }


SAMPLE_BAR_DATASET = {
    "records": [
        {"label": "Organic", "display_label": "Organic", "value": 420, "unit": "pt"},
        {"label": "Creators", "display_label": "Creators", "value": 310, "unit": "pt"},
        {"label": "Email", "display_label": "Email", "value": 260, "unit": "pt"},
        {"label": "Paid", "display_label": "Paid", "value": 180, "unit": "pt"},
        {"label": "Partnerships", "display_label": "Partners", "value": 135, "unit": "pt"},
    ]
}

SAMPLE_DONUT_DATASET = {
    "records": [
        {"label": "Purple", "display_label": "Purple", "value": 42, "unit": "%"},
        {"label": "Peach", "display_label": "Peach", "value": 26, "unit": "%"},
        {"label": "Sage", "display_label": "Sage", "value": 18, "unit": "%"},
        {"label": "Coral", "display_label": "Coral", "value": 14, "unit": "%"},
    ],
    "unit": "%",
}

SAMPLE_LINE_DATASET = {
    "points": [
        {"x": "W1", "y": 12},
        {"x": "W2", "y": 18},
        {"x": "W3", "y": 24},
        {"x": "W4", "y": 21},
        {"x": "W5", "y": 33},
        {"x": "W6", "y": 38},
        {"x": "W7", "y": 44},
        {"x": "W8", "y": 52},
    ],
    "y_label": "active users (k)",
}


def render_gallery(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    panels = [
        {
            "slug": "bar_vertical",
            "caption": "Vertical bar · clay",
            "spec": build_chart_spec(
                family="bar",
                title="Top growth channels",
                subtitle="단위: pt",
                theme_name="clay",
                source_note="Source: demo · clay finish",
            ),
            "dataset": SAMPLE_BAR_DATASET,
        },
        {
            "slug": "bar_vertical_minimal",
            "caption": "Vertical bar · minimal (before)",
            "spec": build_chart_spec(
                family="bar",
                title="Top growth channels",
                subtitle="단위: pt",
                theme_name="minimal",
                source_note="Source: demo · minimal baseline",
            ),
            "dataset": SAMPLE_BAR_DATASET,
        },
        {
            "slug": "bar_horizontal",
            "caption": "Horizontal bar · clay",
            "spec": build_chart_spec(
                family="bar_horizontal",
                title="Channel ranking",
                subtitle="단위: pt",
                theme_name="clay",
                source_note="Source: demo · clay finish",
            ),
            "dataset": SAMPLE_BAR_DATASET,
        },
        {
            "slug": "donut",
            "caption": "Donut · clay",
            "spec": build_chart_spec(
                family="donut",
                title="Palette share",
                subtitle="전체 대비 구성비",
                theme_name="clay",
                source_note="Source: demo · clay finish",
            ),
            "dataset": SAMPLE_DONUT_DATASET,
        },
        {
            "slug": "line",
            "caption": "Line · clay",
            "spec": build_chart_spec(
                family="line",
                title="Active users trend",
                subtitle="최근 8주",
                theme_name="clay",
                source_note="Source: demo · clay finish",
            ),
            "dataset": SAMPLE_LINE_DATASET,
        },
    ]

    for panel in panels:
        svg = render_chart_svg(panel["spec"], panel["dataset"])
        svg_path = out_dir / f"{panel['slug']}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        entries.append({"caption": panel["caption"], "svg_path": svg_path.name})

    html = _build_viewer_html(entries)
    index_path = out_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    manifest = {
        "out_dir": str(out_dir),
        "index": str(index_path),
        "panels": [{"slug": panel["slug"], "file": f"{panel['slug']}.svg"} for panel in panels],
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _build_viewer_html(entries: list[dict]) -> str:
    cards = "\n".join(
        f'<figure><figcaption>{escape(entry["caption"])}</figcaption>'
        f'<img src="{escape(entry["svg_path"])}" alt="{escape(entry["caption"])}" /></figure>'
        for entry in entries
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<title>ChartAgent · clay finish preview</title>
<style>
  :root {{ color-scheme: light; }}
  body {{
    margin: 0;
    padding: 40px;
    background: #eef2ef;
    font-family: 'Pretendard', 'Apple SD Gothic Neo', system-ui, sans-serif;
    color: #1f2a24;
  }}
  h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: -0.02em; }}
  p.lead {{ margin: 0 0 32px; color: #4a5550; }}
  .grid {{
    display: grid;
    gap: 24px;
    grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
  }}
  figure {{
    margin: 0;
    padding: 16px;
    background: #ffffff;
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(15, 27, 22, 0.08);
  }}
  figcaption {{ font-size: 14px; color: #4a5550; margin-bottom: 12px; }}
  img {{ display: block; width: 100%; height: auto; border-radius: 12px; background: transparent; }}
</style>
</head>
<body>
  <h1>Clay finish preview</h1>
  <p class="lead">SVG 필터 + radial gradient 기반 1단계 faux-3D 프로토타입입니다. 기준 대비 비교를 위해 minimal 테마 바 차트도 포함했습니다.</p>
  <div class="grid">
{cards}
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render clay-style chart gallery")
    parser.add_argument("--out-dir", default="tmp/clay_demo", help="Output directory")
    args = parser.parse_args()
    out_dir = Path(args.out_dir).expanduser().resolve()
    manifest = render_gallery(out_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
