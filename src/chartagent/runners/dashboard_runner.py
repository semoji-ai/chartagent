from __future__ import annotations

import json
import re
from collections import Counter
from html import escape
from pathlib import Path
import shutil
from typing import Any

from chartagent.design.theme_sets import get_theme_set_spec
from chartagent.runners.chartagent_runner import build_chart_artifacts


def write_chartagent_dashboard(
    output_dir: Path,
    sample_tasks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir).expanduser().resolve()
    cases_dir = output_dir / "cases"
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir.mkdir(parents=True, exist_ok=True)

    tasks = list(sample_tasks or _default_sample_tasks())
    if sample_tasks is None:
        tasks = _compact_dashboard_tasks(tasks)
    rendered_cases: list[dict[str, Any]] = []
    family_counter: Counter[str] = Counter()
    theme_set_counter: Counter[str] = Counter()
    warning_count = 0

    for index, task in enumerate(tasks, start=1):
        slug = _slugify(str(task.get("task_id") or f"case-{index}"))
        case_dir = cases_dir / slug
        case_dir.mkdir(parents=True, exist_ok=True)
        task_path = case_dir / "chart_task.json"
        task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")

        result = build_chart_artifacts(task)
        _write_case_artifacts(case_dir=case_dir, result=result)

        chart_family = str(result.chart_spec.get("chart_family") or "invalid")
        family_counter[chart_family] += 1
        style_spec = result.chart_spec.get("style_spec") or {}
        theme_set_counter[str(style_spec.get("theme_set") or "unspecified")] += 1
        warnings = result.chart_spec.get("warnings") or []
        warning_count += len(warnings)
        rendered_cases.append(
            {
                "slug": slug,
                "title": str(result.chart_spec.get("title_text") or task.get("question") or task.get("task_id") or slug),
                "task": task,
                "result": result,
                "warnings": warnings,
                "case_dir": case_dir,
            }
        )

    theme_gallery_data = _build_theme_gallery_sections(output_dir=output_dir)
    index_html = _build_dashboard_html(
        cases=rendered_cases,
        family_counter=family_counter,
        theme_set_counter=theme_set_counter,
        warning_count=warning_count,
        theme_sections=theme_gallery_data["sections"],
        theme_gallery_variants=theme_gallery_data["variants"],
    )
    index_path = output_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")

    gallery_html = _build_theme_gallery_html(theme_gallery_data["sections"])
    gallery_path = output_dir / "theme_gallery.html"
    gallery_path.write_text(gallery_html, encoding="utf-8")

    manifest = {
        "dashboard": str(index_path),
        "theme_gallery": str(gallery_path),
        "case_count": len(rendered_cases),
        "families": dict(family_counter),
        "theme_sets": dict(theme_set_counter),
        "warning_count": warning_count,
        "cases_dir": str(cases_dir),
        "theme_gallery_case_count": theme_gallery_data["case_count"],
        "theme_gallery_themes": theme_gallery_data["themes"],
        "theme_gallery_variants": theme_gallery_data["variants"],
    }
    (output_dir / "dashboard_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def _write_case_artifacts(case_dir: Path, result: Any) -> None:
    (case_dir / "chart_task.normalized.json").write_text(
        json.dumps(result.chart_task, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "dataset.normalized.json").write_text(
        json.dumps(result.dataset_normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "chart_spec.json").write_text(
        json.dumps(result.chart_spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "notes.md").write_text(result.notes_md, encoding="utf-8")
    if result.render_svg:
        (case_dir / "render.svg").write_text(result.render_svg, encoding="utf-8")


def _build_theme_gallery_sections(output_dir: Path) -> dict[str, Any]:
    gallery_dir = output_dir / "theme_gallery_cases"
    theme_docs_dir = output_dir / "theme_docs"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    theme_docs_dir.mkdir(parents=True, exist_ok=True)

    rendered_sections: list[dict[str, Any]] = []
    case_count = 0
    for theme_set in _theme_gallery_theme_sets():
        theme_spec = get_theme_set_spec(theme_set)
        theme_doc_source = _theme_doc_source_path(theme_set)
        theme_doc_relpath = None
        if theme_doc_source.exists():
            theme_doc_target = theme_docs_dir / theme_doc_source.name
            shutil.copyfile(theme_doc_source, theme_doc_target)
            theme_doc_relpath = f"theme_docs/{theme_doc_target.name}"
        section_variants: list[dict[str, Any]] = []
        for variant in _theme_gallery_variants():
            variant_cases: list[dict[str, Any]] = []
            for task in _theme_gallery_sample_tasks(theme_set, variant):
                slug = _slugify(str(task.get("task_id") or f"{theme_set}-case"))
                case_dir = gallery_dir / slug
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "chart_task.json").write_text(
                    json.dumps(task, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                result = build_chart_artifacts(task)
                _write_case_artifacts(case_dir=case_dir, result=result)
                variant_cases.append(
                    {
                        "slug": slug,
                        "task": task,
                        "case_dir": case_dir,
                        "result": result,
                        "variant_key": str(variant["key"]),
                        "variant_label": str(variant["label"]),
                    }
                )
                case_count += 1
            section_variants.append({"variant": variant, "cases": variant_cases})
        rendered_sections.append(
            {
                "theme_set": theme_set,
                "theme_spec": theme_spec,
                "theme_doc_relpath": theme_doc_relpath,
                "variants": section_variants,
            }
        )

    return {
        "sections": rendered_sections,
        "case_count": case_count,
        "themes": [section["theme_set"] for section in rendered_sections],
        "variants": [str(variant["key"]) for variant in _theme_gallery_variants()],
    }


def _compact_dashboard_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    for task in tasks:
        task_id = str(task.get("task_id") or "").strip()
        if task_id.startswith("theme-set-study-"):
            continue
        dedupe_key = task_id or json.dumps(task, ensure_ascii=False, sort_keys=True)
        if dedupe_key in seen_task_ids:
            continue
        seen_task_ids.add(dedupe_key)
        compact.append(task)
    return compact


def _build_dashboard_html(
    cases: list[dict[str, Any]],
    family_counter: Counter[str],
    theme_set_counter: Counter[str],
    warning_count: int,
    theme_sections: list[dict[str, Any]],
    theme_gallery_variants: list[str],
) -> str:
    family_options = "".join(
        f'<option value="{escape(family)}">{escape(family)} ({count})</option>'
        for family, count in sorted(family_counter.items())
    )
    family_chips = "".join(
        f'<span class="summary-chip"><strong>{escape(family)}</strong><span>{count}</span></span>'
        for family, count in sorted(family_counter.items())
    )
    theme_set_options = "".join(
        f'<option value="{escape(theme_set)}">{escape(theme_set)} ({count})</option>'
        for theme_set, count in sorted(theme_set_counter.items())
    )
    theme_set_chips = "".join(
        f'<span class="summary-chip"><strong>{escape(theme_set)}</strong><span>{count}</span></span>'
        for theme_set, count in sorted(theme_set_counter.items())
    )
    case_cards = "".join(_build_case_card(case) for case in cases)
    theme_lab_sections = "".join(
        _build_theme_gallery_section(section, show_variant_controls=False)
        for section in theme_sections
    )
    theme_lab_theme_options = "".join(
        f'<option value="{escape(str(section["theme_set"]))}">{escape(str(section["theme_spec"].get("label") or section["theme_set"]))}</option>'
        for section in theme_sections
    )
    theme_lab_families = sorted(
        {
            str(case["result"].chart_spec.get("chart_family") or "invalid")
            for section in theme_sections
            for item in section["variants"]
            for case in item["cases"]
        }
    )
    theme_lab_family_options = "".join(
        f'<option value="{escape(family)}">{escape(family)}</option>'
        for family in theme_lab_families
    )
    theme_lab_variant_buttons = "".join(
        f'<button class="variant-button" type="button" data-global-variant="{escape(variant)}">{escape(variant)}</button>'
        for variant in theme_gallery_variants
    )
    default_variant = theme_gallery_variants[0] if theme_gallery_variants else "base"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ChartAgent Dashboard</title>
  <style>
    :root {{
      --bg: #f6f3ec;
      --panel: rgba(255,255,255,0.86);
      --panel-strong: rgba(255,255,255,0.96);
      --ink: #18212f;
      --muted: #5d6778;
      --line: rgba(24,33,47,0.12);
      --accent: #0f766e;
      --accent-2: #b45309;
      --warning: #b91c1c;
      --shadow: 0 18px 50px rgba(24,33,47,0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15,118,110,0.12), transparent 28%),
        radial-gradient(circle at top right, rgba(180,83,9,0.10), transparent 24%),
        linear-gradient(180deg, #fbfaf7 0%, var(--bg) 100%);
      font-family: "Space Grotesk", "Pretendard", "Apple SD Gothic Neo", sans-serif;
    }}
    .page {{
      width: min(1420px, calc(100vw - 32px));
      margin: 24px auto 48px;
    }}
    .hero {{
      display: grid;
      gap: 16px;
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.78));
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 3vw, 3.5rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }}
    .lede {{
      max-width: 880px;
      margin: 0;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.65;
    }}
    .summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }}
    .hero-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .hero-link {{
      display: inline-flex;
      align-items: center;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.92);
      color: var(--accent);
      text-decoration: none;
      font-size: 14px;
      font-weight: 800;
    }}
    .lab-shell,
    .audit-shell {{
      display: grid;
      gap: 16px;
      margin-top: 24px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 26px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    .section-header {{
      display: grid;
      gap: 8px;
    }}
    .section-title {{
      margin: 0;
      font-size: clamp(1.5rem, 2vw, 2.3rem);
      line-height: 1;
      letter-spacing: -0.03em;
    }}
    .section-copy {{
      margin: 0;
      max-width: 920px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
    }}
    .lab-toolbar {{
      display: grid;
      grid-template-columns: minmax(0, 220px) minmax(0, 220px) minmax(0, 1fr) auto auto;
      gap: 12px;
      align-items: end;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(255,255,255,0.82);
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(0, 220px) minmax(0, 1fr) auto auto;
      gap: 12px;
      align-items: center;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(255,255,255,0.8);
    }}
    .control {{
      display: grid;
      gap: 6px;
      min-width: 0;
    }}
    .control label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .control select,
    .control input[type="search"] {{
      width: 100%;
      min-width: 0;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.96);
      color: var(--ink);
      font: 500 15px/1.2 "Space Grotesk", "Pretendard", "Apple SD Gothic Neo", sans-serif;
    }}
    .variant-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .variant-button {{
      display: inline-flex;
      align-items: center;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.96);
      color: var(--ink);
      font-size: 13px;
      font-weight: 800;
      cursor: pointer;
    }}
    .variant-button.active {{
      background: #18212f;
      color: #ffffff;
      border-color: #18212f;
    }}
    .toggle {{
      display: inline-flex;
      gap: 10px;
      align-items: center;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.96);
      font-size: 14px;
      font-weight: 700;
    }}
    .visible-count {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #ecfeff;
      color: #155e75;
      font-size: 14px;
      font-weight: 800;
    }}
    .summary-chip {{
      display: inline-flex;
      gap: 10px;
      align-items: center;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--panel-strong);
      font-size: 14px;
    }}
    .theme-lab {{
      display: grid;
      gap: 18px;
    }}
    .theme-section {{
      display: grid;
      gap: 14px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 24px;
      background: rgba(255,255,255,0.9);
    }}
    .theme-section[hidden] {{
      display: none;
    }}
    .theme-header {{
      display: grid;
      gap: 10px;
    }}
    .theme-topline {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
    }}
    .theme-title {{
      margin: 0;
      font-size: 1.35rem;
      line-height: 1.05;
    }}
    .theme-meta,
    .signature-list,
    .chart-notes,
    .footer-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .signature,
    .chart-note {{
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,0.94);
      border: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .theme-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .chart-card {{
      display: grid;
      gap: 12px;
      min-width: 0;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background:
        radial-gradient(circle at top left, rgba(37,99,235,0.04), transparent 24%),
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.94));
    }}
    .chart-card[hidden] {{
      display: none;
    }}
    .chart-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: baseline;
      justify-content: space-between;
    }}
    .chart-title {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.2;
    }}
    .family-pill {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: #ecfeff;
      color: #155e75;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .cases {{
      display: grid;
      gap: 24px;
    }}
    .case {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 26px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    .case-main {{
      display: grid;
      gap: 16px;
      min-width: 0;
    }}
    .case-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
    }}
    .case-title {{
      margin: 0;
      font-size: 1.45rem;
      line-height: 1.15;
    }}
    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .badge.warning {{
      background: #fee2e2;
      color: var(--warning);
    }}
    .badge.base {{
      background: #ecfeff;
      color: #155e75;
    }}
    .badge.theme {{
      background: #fef3c7;
      color: #92400e;
    }}
    .badge.mode {{
      background: #ede9fe;
      color: #6d28d9;
    }}
    .badge.layout {{
      background: #dcfce7;
      color: #166534;
    }}
    .badge.reference {{
      background: #fce7f3;
      color: #9d174d;
    }}
    .badge.combo {{
      background: #ede9fe;
      color: #5b21b6;
    }}
    .badge.pattern {{
      background: #ecfccb;
      color: #3f6212;
    }}
    .badge.theme-set {{
      background: #ede9fe;
      color: #6d28d9;
    }}
    .viz-frame {{
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background:
        radial-gradient(circle at top left, rgba(37,99,235,0.05), transparent 32%),
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.92));
      overflow: auto;
      min-height: 360px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
    }}
    .viz-frame svg {{
      display: block;
      width: 100%;
      height: auto;
      min-width: 320px;
    }}
    .meta-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .meta-pill {{
      display: inline-flex;
      gap: 8px;
      align-items: center;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.88);
      font-size: 13px;
      font-weight: 700;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .panel {{
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--panel-strong);
    }}
    .panel h3 {{
      margin: 0 0 8px;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent-2);
    }}
    .list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.5;
      font-size: 14px;
    }}
    .code {{
      margin: 0;
      padding: 14px;
      border-radius: 18px;
      background: #141923;
      color: #f8fafc;
      overflow: auto;
      font: 12px/1.5 "SFMono-Regular", "JetBrains Mono", monospace;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .details-panel {{
      padding: 0;
      overflow: hidden;
    }}
    .details-panel summary {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      cursor: pointer;
      list-style: none;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent-2);
    }}
    .details-panel summary::-webkit-details-marker {{
      display: none;
    }}
    .details-panel .details-body {{
      padding: 0 14px 14px;
    }}
    .details-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .footer-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .footer-links a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
    }}
    .empty-state {{
      display: none;
      padding: 24px;
      border: 1px dashed var(--line);
      border-radius: 22px;
      background: rgba(255,255,255,0.74);
      color: var(--muted);
      text-align: center;
      font-size: 15px;
      font-weight: 600;
    }}
    .empty-state.active {{
      display: block;
    }}
    @media (max-width: 1100px) {{
      .theme-grid,
      .details-grid {{
        grid-template-columns: 1fr;
      }}
      .lab-toolbar {{
        grid-template-columns: 1fr 1fr;
      }}
      .toolbar {{
        grid-template-columns: 1fr 1fr;
      }}
    }}
    @media (max-width: 720px) {{
      .page {{ width: min(100vw - 18px, 100%); margin: 10px auto 36px; }}
      .hero, .case {{ padding: 14px; border-radius: 20px; }}
      .grid, .theme-grid, .details-grid {{ grid-template-columns: 1fr; }}
      .lab-toolbar,
      .toolbar {{ grid-template-columns: 1fr; }}
      .viz-frame {{ min-height: 320px; padding: 14px; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">ChartAgent Style Lab</div>
      <h1>theme_set과 variant를 먼저 바꾸고 chart family별 결과를 바로 비교</h1>
      <p class="lede">
        메인 화면은 style lab이다. theme_set, variant, chart family를 먼저 고르고 바로 SVG surface language를 비교한다.
        static audit는 아래에 압축해서 두고, raw task/spec/dataset은 필요할 때만 펼쳐 확인한다.
      </p>
      <div class="summary">
        <span class="summary-chip"><strong>lab themes</strong><span>{len(theme_sections)}</span></span>
        <span class="summary-chip"><strong>lab families</strong><span>{len(theme_lab_families)}</span></span>
        <span class="summary-chip"><strong>audit cases</strong><span>{len(cases)}</span></span>
        <span class="summary-chip"><strong>warnings</strong><span>{warning_count}</span></span>
        {family_chips}
        {theme_set_chips}
      </div>
      <div class="hero-links">
        <a class="hero-link" href="./theme_gallery.html">Open dedicated theme gallery</a>
      </div>
    </section>
    <section class="lab-shell">
      <header class="section-header">
        <h2 class="section-title">Theme Lab</h2>
        <p class="section-copy">
          같은 theme_set이 bar, line, share, comparison table, metric wall, single stat, fact table까지 얼마나 일관되게 유지되는지 본다.
          여기서는 variant를 전역으로 바꿔 surface language를 빠르게 비교한다.
        </p>
      </header>
      <div class="lab-toolbar">
        <div class="control">
          <label for="lab-theme-filter">Theme Set</label>
          <select id="lab-theme-filter">
            <option value="all">all theme sets</option>
            {theme_lab_theme_options}
          </select>
        </div>
        <div class="control">
          <label for="lab-family-filter">Chart Family</label>
          <select id="lab-family-filter">
            <option value="all">all families</option>
            {theme_lab_family_options}
          </select>
        </div>
        <div class="control">
          <label>Variant</label>
          <div class="variant-controls">
            {theme_lab_variant_buttons}
          </div>
        </div>
        <div class="visible-count">
          <span>themes</span>
          <span id="lab-visible-theme-count">{len(theme_sections)}</span>
        </div>
        <div class="visible-count">
          <span>previews</span>
          <span id="lab-visible-card-count">{len(theme_sections) * max(len(theme_lab_families), 1)}</span>
        </div>
      </div>
      <div class="theme-lab">
        {theme_lab_sections}
      </div>
      <div id="lab-empty-state" class="empty-state">No matching theme previews for the current style lab filter.</div>
    </section>
    <section class="audit-shell">
      <header class="section-header">
        <h2 class="section-title">Static Audit</h2>
        <p class="section-copy">
          representative tasks에서 family 선택, warning, annotation, raw artifacts를 빠르게 점검한다.
          중복 theme study case는 메인 audit에서 제외했다.
        </p>
      </header>
      <div class="toolbar">
        <div class="control">
          <label for="family-filter">Family</label>
          <select id="family-filter">
            <option value="all">all families</option>
            {family_options}
          </select>
        </div>
        <div class="control">
          <label for="theme-set-filter">Theme Set</label>
          <select id="theme-set-filter">
            <option value="all">all theme sets</option>
            {theme_set_options}
          </select>
        </div>
        <div class="control">
          <label for="case-search">Search</label>
          <input id="case-search" type="search" placeholder="title, family, warning, annotation..." />
        </div>
        <label class="toggle" for="warning-only-toggle">
          <input id="warning-only-toggle" type="checkbox" />
          warning only
        </label>
        <div class="visible-count">
          <span>visible</span>
          <span id="visible-case-count">{len(cases)}</span>
        </div>
      </div>
      <section class="cases">
        {case_cards}
      </section>
      <div id="empty-state" class="empty-state">No matching cases for the current filter.</div>
    </section>
  </main>
  <script>
    (() => {{
      const params = new URLSearchParams(window.location.search);
      const labThemeFilter = document.getElementById("lab-theme-filter");
      const labFamilyFilter = document.getElementById("lab-family-filter");
      const labVisibleThemeCount = document.getElementById("lab-visible-theme-count");
      const labVisibleCardCount = document.getElementById("lab-visible-card-count");
      const labEmptyState = document.getElementById("lab-empty-state");
      const labSections = Array.from(document.querySelectorAll(".theme-section"));
      const globalVariantButtons = Array.from(document.querySelectorAll("[data-global-variant]"));
      let activeVariant = params.get("variant") || "{escape(default_variant)}";

      const applyLabFilters = () => {{
        const themeValue = labThemeFilter.value;
        const familyValue = labFamilyFilter.value;
        let visibleThemes = 0;
        let visibleCards = 0;
        labSections.forEach((section) => {{
          const themeSet = section.dataset.themeSet || "";
          const matchesTheme = themeValue === "all" || themeSet === themeValue;
          let sectionVisibleCards = 0;
          Array.from(section.querySelectorAll(".chart-card")).forEach((card) => {{
            const matchesVariant = (card.dataset.variant || "base") === activeVariant;
            const matchesFamily = familyValue === "all" || (card.dataset.family || "") === familyValue;
            const show = matchesTheme && matchesVariant && matchesFamily;
            card.hidden = !show;
            if (show) {{
              sectionVisibleCards += 1;
            }}
          }});
          section.hidden = sectionVisibleCards == 0;
          if (!section.hidden) {{
            visibleThemes += 1;
          }}
          visibleCards += sectionVisibleCards;
        }});
        labVisibleThemeCount.textContent = String(visibleThemes);
        labVisibleCardCount.textContent = String(visibleCards);
        labEmptyState.classList.toggle("active", visibleCards === 0);
      }};

      const setGlobalVariant = (variant) => {{
        activeVariant = variant;
        globalVariantButtons.forEach((button) => {{
          button.classList.toggle("active", button.dataset.globalVariant === variant);
        }});
        applyLabFilters();
      }};

      if (params.has("theme")) {{
        labThemeFilter.value = params.get("theme") || "all";
      }}
      if (params.has("lab_family")) {{
        labFamilyFilter.value = params.get("lab_family") || "all";
      }}
      labThemeFilter.addEventListener("change", applyLabFilters);
      labFamilyFilter.addEventListener("change", applyLabFilters);
      globalVariantButtons.forEach((button) => {{
        button.addEventListener("click", () => setGlobalVariant(button.dataset.globalVariant || "{escape(default_variant)}"));
      }});
      setGlobalVariant(activeVariant);

      const familyFilter = document.getElementById("family-filter");
      const themeSetFilter = document.getElementById("theme-set-filter");
      const warningOnlyToggle = document.getElementById("warning-only-toggle");
      const caseSearch = document.getElementById("case-search");
      const cards = Array.from(document.querySelectorAll(".case"));
      const visibleCaseCount = document.getElementById("visible-case-count");
      const emptyState = document.getElementById("empty-state");

      if (params.has("family")) {{
        familyFilter.value = params.get("family") || "all";
      }}
      if (params.has("theme_set")) {{
        themeSetFilter.value = params.get("theme_set") || "all";
      }}
      if (params.has("warning_only")) {{
        warningOnlyToggle.checked = params.get("warning_only") === "true";
      }}
      if (params.has("search")) {{
        caseSearch.value = params.get("search") || "";
      }}

      const applyFilters = () => {{
        const familyValue = familyFilter.value;
        const themeSetValue = themeSetFilter.value;
        const warningOnly = warningOnlyToggle.checked;
        const searchValue = caseSearch.value.trim().toLowerCase();
        let visible = 0;

        cards.forEach((card) => {{
          const family = card.dataset.family || "";
          const themeSet = card.dataset.themeSet || "";
          const hasWarnings = card.dataset.hasWarnings === "true";
          const searchText = (card.dataset.search || "").toLowerCase();
          const matchesFamily = familyValue === "all" || family === familyValue;
          const matchesThemeSet = themeSetValue === "all" || themeSet === themeSetValue;
          const matchesWarning = !warningOnly || hasWarnings;
          const matchesSearch = !searchValue || searchText.includes(searchValue);
          const show = matchesFamily && matchesThemeSet && matchesWarning && matchesSearch;
          card.hidden = !show;
          if (show) visible += 1;
        }});

        visibleCaseCount.textContent = String(visible);
        emptyState.classList.toggle("active", visible === 0);
      }};

      familyFilter.addEventListener("change", applyFilters);
      themeSetFilter.addEventListener("change", applyFilters);
      warningOnlyToggle.addEventListener("change", applyFilters);
      caseSearch.addEventListener("input", applyFilters);
      applyFilters();
    }})();
  </script>
</body>
</html>
"""


def _build_theme_gallery_html(sections: list[dict[str, Any]]) -> str:
    nav_links = "".join(
        f'<a class="nav-chip" href="#theme-{escape(str(section["theme_set"]).replace("_", "-"))}">{escape(str(section["theme_spec"].get("label") or section["theme_set"]))}</a>'
        for section in sections
    )
    section_html = "".join(_build_theme_gallery_section(section) for section in sections)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ChartAgent Theme Gallery</title>
  <style>
    :root {{
      --bg: #f5f2eb;
      --panel: rgba(255,255,255,0.92);
      --line: rgba(15,23,42,0.10);
      --ink: #18212f;
      --muted: #5d6778;
      --accent: #0f766e;
      --shadow: 0 20px 60px rgba(24,33,47,0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15,118,110,0.10), transparent 24%),
        radial-gradient(circle at top right, rgba(180,83,9,0.08), transparent 24%),
        linear-gradient(180deg, #fbfaf7 0%, var(--bg) 100%);
      font-family: "Space Grotesk", "Pretendard", "Apple SD Gothic Neo", sans-serif;
    }}
    .page {{
      width: min(1520px, calc(100vw - 32px));
      margin: 24px auto 60px;
      display: grid;
      gap: 22px;
    }}
    .hero {{
      display: grid;
      gap: 16px;
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.82));
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2rem, 3vw, 3.6rem);
      line-height: 0.94;
      letter-spacing: -0.04em;
    }}
    .lede {{
      margin: 0;
      max-width: 980px;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.7;
    }}
    .nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .nav-chip {{
      display: inline-flex;
      align-items: center;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.92);
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }}
    .theme-section {{
      display: grid;
      gap: 16px;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    .theme-header {{
      display: grid;
      gap: 10px;
    }}
    .theme-topline {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
    }}
    .theme-title {{
      margin: 0;
      font-size: clamp(1.4rem, 2vw, 2.2rem);
      line-height: 1.02;
    }}
    .theme-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .meta-pill {{
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      font-size: 12px;
      font-weight: 700;
    }}
    .theme-description {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
    }}
    .variant-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .variant-button {{
      display: inline-flex;
      align-items: center;
      padding: 9px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.96);
      color: var(--ink);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }}
    .variant-button.active {{
      background: #18212f;
      color: #ffffff;
      border-color: #18212f;
    }}
    .variant-button.reset {{
      color: #155e75;
      background: #ecfeff;
    }}
    .signature-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .signature {{
      display: inline-flex;
      align-items: center;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.92);
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }}
    .theme-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .chart-card {{
      display: grid;
      gap: 12px;
      min-width: 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background:
        radial-gradient(circle at top left, rgba(37,99,235,0.04), transparent 26%),
        linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.94));
    }}
    .chart-card[hidden] {{
      display: none;
    }}
    .chart-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: baseline;
      justify-content: space-between;
    }}
    .chart-title {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.2;
    }}
    .family-pill {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: #ecfeff;
      color: #155e75;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .viz-frame {{
      min-height: 380px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,0.96);
      overflow: auto;
    }}
    .viz-frame svg {{
      display: block;
      width: 100%;
      min-width: 300px;
      height: auto;
    }}
    .chart-notes {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .chart-note {{
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      background: #f8fafc;
      border: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    @media (max-width: 960px) {{
      .theme-grid {{ grid-template-columns: 1fr; }}
      .page {{ width: min(100vw - 20px, 100%); }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">ChartAgent Theme Gallery</div>
      <h1>한 페이지에서 theme_set별 차트 surface language를 비교</h1>
      <p class="lede">
        같은 theme_set 아래에서 bar, line, donut, comparison table, metric wall, single stat, fact table을 함께 보여준다.
        즉 한 테마가 chart family를 바꿔도 얼마나 일관된 색, 굵기, 라운드니스, 패턴, source 처리 방식을 유지하는지 바로 확인할 수 있다.
      </p>
      <nav class="nav">{nav_links}</nav>
    </section>
    {section_html}
  </main>
  <script>
    (() => {{
      const params = new URLSearchParams(window.location.search);
      const initialVariant = params.get('variant') || 'base';
      const sections = Array.from(document.querySelectorAll('.theme-section'));
      sections.forEach((section) => {{
        const buttons = Array.from(section.querySelectorAll('[data-variant-button]'));
        const cards = Array.from(section.querySelectorAll('.chart-card[data-variant]'));
        const setVariant = (variant) => {{
          buttons.forEach((button) => {{
            button.classList.toggle('active', button.dataset.variantButton === variant && !button.dataset.resetTarget);
          }});
          cards.forEach((card) => {{
            card.hidden = card.dataset.variant !== variant;
          }});
        }};
        buttons.forEach((button) => {{
          button.addEventListener('click', () => {{
            setVariant(button.dataset.resetTarget || button.dataset.variantButton || 'base');
          }});
        }});
        const allowedVariants = new Set(cards.map((card) => card.dataset.variant || 'base'));
        setVariant(allowedVariants.has(initialVariant) ? initialVariant : 'base');
      }});
    }})();
  </script>
</body>
</html>
"""


def _build_theme_gallery_section(section: dict[str, Any], *, show_variant_controls: bool = True) -> str:
    theme_set = str(section["theme_set"])
    theme_spec = section["theme_spec"]
    theme_doc_relpath = section.get("theme_doc_relpath")
    variants = section["variants"]
    label = str(theme_spec.get("label") or theme_set)
    description = str(theme_spec.get("description") or "")
    theme_name = str(theme_spec.get("theme_name") or "unknown")
    combo = str(theme_spec.get("style_combo_preset") or "unknown")
    pattern = str(theme_spec.get("pattern_format_preset") or "unknown")
    source_refs = list(theme_spec.get("source_refs") or [])
    signatures = "".join(
        f'<span class="signature">{escape(str(item))}</span>'
        for item in (theme_spec.get("artwork_signature") or [])
    )
    source_ref_pills = "".join(f'<span class="signature">ref {escape(str(item))}</span>' for item in source_refs)
    doc_link = (
        f'<a class="doc-link" href="{escape(str(theme_doc_relpath))}" target="_blank" rel="noreferrer">Open THEME.md</a>'
        if theme_doc_relpath
        else ""
    )
    variant_controls = ""
    if show_variant_controls:
        variant_controls = "".join(
            f'<button class="variant-button" type="button" data-variant-button="{escape(str(item["variant"]["key"]))}">{escape(str(item["variant"]["label"]))}</button>'
            for item in variants
        )
        variant_controls += '<button class="variant-button reset" type="button" data-variant-button="base" data-reset-target="base">Reset to Theme</button>'
    cards = "".join(_build_theme_gallery_card(case) for item in variants for case in item["cases"])
    return f"""
    <section class="theme-section" id="theme-{escape(theme_set.replace('_', '-'))}" data-theme-set="{escape(theme_set)}">
      <header class="theme-header">
        <div class="theme-topline">
          <h2 class="theme-title">{escape(label)}</h2>
          <div class="theme-meta">
            <span class="meta-pill">theme_set {escape(theme_set)}</span>
            <span class="meta-pill">theme {escape(theme_name)}</span>
            <span class="meta-pill">combo {escape(combo)}</span>
            <span class="meta-pill">pattern {escape(pattern)}</span>
            <span class="meta-pill">refs {escape(", ".join(source_refs) or "n/a")}</span>
          </div>
        </div>
        <p class="theme-description">{escape(description)}</p>
        {doc_link}
        {'<div class="variant-controls">' + variant_controls + '</div>' if variant_controls else ''}
        <div class="signature-list">{signatures}{source_ref_pills}</div>
      </header>
      <div class="theme-grid">{cards}</div>
    </section>
    """


def _build_theme_gallery_card(case: dict[str, Any]) -> str:
    result = case["result"]
    chart_spec = result.chart_spec or {}
    family = str(chart_spec.get("chart_family") or "invalid")
    title = str(chart_spec.get("title_text") or case["task"].get("question") or case["slug"])
    why = chart_spec.get("why") or []
    annotations = chart_spec.get("annotations") or []
    note_bits = [
        f"annotations {len(annotations)}",
        f"warnings {len(chart_spec.get('warnings') or [])}",
    ]
    if why:
        note_bits.append(str(why[0]))
    notes = "".join(f'<span class="chart-note">{escape(bit)}</span>' for bit in note_bits)
    search_text = " ".join(
        [
            title,
            family,
            str(case["variant_label"]),
            str(case["task"].get("question") or ""),
            str(case["task"].get("theme_set") or ""),
            " ".join(str(item) for item in why[:2]),
        ]
    ).strip().lower()
    return f"""
    <article class="chart-card" data-variant="{escape(str(case['variant_key']))}" data-family="{escape(family)}" data-search="{escape(search_text)}">
      <div class="chart-header">
        <h3 class="chart-title">{escape(title)} <span style="color:#64748b;font-weight:600;">· {escape(str(case['variant_label']))}</span></h3>
        <span class="family-pill">{escape(family)}</span>
      </div>
      <div class="viz-frame">{result.render_svg or '<div>No SVG output</div>'}</div>
      <div class="chart-notes">{notes}</div>
    </article>
    """


def _build_case_card(case: dict[str, Any]) -> str:
    result = case["result"]
    chart_spec = result.chart_spec
    style_spec = chart_spec.get("style_spec") or {}
    warnings = case["warnings"]
    issue_list = result.issues or []
    why_items = "".join(f"<li>{escape(str(item))}</li>" for item in (chart_spec.get("why") or []))
    warning_items = "".join(f"<li>{escape(str(item))}</li>" for item in warnings) or "<li>none</li>"
    issue_items = "".join(
        f"<li>{escape(str(item.get('level', 'info')))}: {escape(str(item.get('message', '')))}</li>"
        for item in issue_list
    ) or "<li>none</li>"
    badges = [
        f'<span class="badge">{escape(str(chart_spec.get("chart_family") or "invalid"))}</span>',
    ]
    base_family = chart_spec.get("base_chart_family")
    if base_family:
        badges.append(f'<span class="badge base">base {escape(str(base_family))}</span>')
    if style_spec.get("theme_name"):
        badges.append(f'<span class="badge theme">theme {escape(str(style_spec.get("theme_name")))}</span>')
    if style_spec.get("theme_set"):
        badges.append(f'<span class="badge theme-set">theme_set {escape(str(style_spec.get("theme_set")))}</span>')
    if style_spec.get("visual_mode"):
        badges.append(f'<span class="badge mode">mode {escape(str(style_spec.get("visual_mode")))}</span>')
    if style_spec.get("layout_preset"):
        badges.append(f'<span class="badge layout">layout {escape(str(style_spec.get("layout_preset")))}</span>')
    if style_spec.get("reference_profile"):
        badges.append(f'<span class="badge reference">reference {escape(str(style_spec.get("reference_profile")))}</span>')
    if style_spec.get("style_combo_preset"):
        badges.append(f'<span class="badge combo">combo {escape(str(style_spec.get("style_combo_preset")))}</span>')
    if style_spec.get("pattern_format_preset"):
        badges.append(f'<span class="badge pattern">pattern {escape(str(style_spec.get("pattern_format_preset")))}</span>')
    if warnings:
        badges.append(f'<span class="badge warning">{len(warnings)} warning{"s" if len(warnings) != 1 else ""}</span>')

    task_json = json.dumps(case["task"], ensure_ascii=False, indent=2)
    spec_json = json.dumps(chart_spec, ensure_ascii=False, indent=2)
    dataset_json = json.dumps(result.dataset_normalized, ensure_ascii=False, indent=2)
    svg_markup = result.render_svg or "<div>No SVG output</div>"
    slug = case["slug"]
    normalized_shape = str(result.dataset_normalized.get("shape") or "unknown")
    annotation_count = len(chart_spec.get("annotations") or [])
    theme_set = str(style_spec.get("theme_set") or "unspecified")
    theme_name = str(style_spec.get("theme_name") or "unknown")
    visual_mode = str(style_spec.get("visual_mode") or "unknown")
    density = str(style_spec.get("density") or "unknown")
    layout_preset = str(style_spec.get("layout_preset") or "unknown")
    reference_profile = str(style_spec.get("reference_profile") or "unknown")
    style_combo_preset = str(style_spec.get("style_combo_preset") or "unknown")
    pattern_format_preset = str(style_spec.get("pattern_format_preset") or "none")
    artwork_signature = ", ".join(str(item) for item in (style_spec.get("theme_artwork_signature") or []))
    theme_source_refs = ", ".join(str(item) for item in (style_spec.get("theme_source_refs") or []))
    search_text = " ".join(
        [
            str(case["title"]),
            str(chart_spec.get("chart_family") or ""),
            str(chart_spec.get("base_chart_family") or ""),
            theme_set,
            theme_name,
            visual_mode,
            density,
            layout_preset,
            reference_profile,
            style_combo_preset,
            pattern_format_preset,
            artwork_signature,
            theme_source_refs,
            " ".join(str(item) for item in (chart_spec.get("why") or [])),
            " ".join(str(item) for item in warnings),
            " ".join(str(item.get("message") or "") for item in issue_list if isinstance(item, dict)),
        ]
    ).strip().lower()
    return f"""
    <article class="case" id="{escape(slug)}" data-family="{escape(str(chart_spec.get("chart_family") or "invalid"))}" data-theme="{escape(theme_name)}" data-theme-set="{escape(theme_set)}" data-has-warnings="{str(bool(warnings)).lower()}" data-search="{escape(search_text)}">
      <div class="case-main">
        <div class="case-header">
          <h2 class="case-title">{escape(case["title"])}</h2>
          <div class="badges">{''.join(badges)}</div>
        </div>
        <div class="meta-strip">
          <span class="meta-pill">shape <strong>{escape(normalized_shape)}</strong></span>
          <span class="meta-pill">theme_set <strong>{escape(theme_set)}</strong></span>
          <span class="meta-pill">theme <strong>{escape(theme_name)}</strong></span>
          <span class="meta-pill">layout <strong>{escape(layout_preset)}</strong></span>
          <span class="meta-pill">density <strong>{escape(density)}</strong></span>
          <span class="meta-pill">reference <strong>{escape(reference_profile)}</strong></span>
          <span class="meta-pill">combo <strong>{escape(style_combo_preset)}</strong></span>
          <span class="meta-pill">pattern <strong>{escape(pattern_format_preset)}</strong></span>
          <span class="meta-pill">artwork <strong>{escape(artwork_signature or 'n/a')}</strong></span>
          <span class="meta-pill">refs <strong>{escape(theme_source_refs or 'n/a')}</strong></span>
          <span class="meta-pill">annotations <strong>{annotation_count}</strong></span>
          <span class="meta-pill">warnings <strong>{len(warnings)}</strong></span>
        </div>
        <div class="viz-frame">{svg_markup}</div>
        <div class="grid">
          <section class="panel">
            <h3>Why</h3>
            <ul class="list">{why_items or '<li>none</li>'}</ul>
          </section>
          <section class="panel">
            <h3>Warnings</h3>
            <ul class="list">{warning_items}</ul>
          </section>
          <section class="panel">
            <h3>Issues</h3>
            <ul class="list">{issue_items}</ul>
          </section>
          <section class="panel">
            <h3>Artifacts</h3>
            <div class="footer-links">
              <a href="./cases/{escape(slug)}/chart_task.json">task</a>
              <a href="./cases/{escape(slug)}/chart_task.normalized.json">task.normalized</a>
              <a href="./cases/{escape(slug)}/dataset.normalized.json">dataset</a>
              <a href="./cases/{escape(slug)}/chart_spec.json">chart_spec</a>
              <a href="./cases/{escape(slug)}/render.svg">render.svg</a>
              <a href="./cases/{escape(slug)}/notes.md">notes</a>
            </div>
          </section>
        </div>
        <details class="panel details-panel">
          <summary>Raw Artifacts <span>expand</span></summary>
          <div class="details-body">
            <div class="details-grid">
              <section class="panel">
                <h3>Task Input</h3>
                <pre class="code">{escape(task_json)}</pre>
              </section>
              <section class="panel">
                <h3>Chart Spec</h3>
                <pre class="code">{escape(spec_json)}</pre>
              </section>
              <section class="panel">
                <h3>Dataset</h3>
                <pre class="code">{escape(dataset_json)}</pre>
              </section>
            </div>
          </div>
        </details>
      </div>
    </article>
    """


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "case"


def _default_sample_tasks() -> list[dict[str, Any]]:
    return [
        {
            "task_id": "theme-set-study-neutral-white",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "neutral_white",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "theme-set-study-editorial-outline",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "editorial_outline",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "theme-set-study-broadcast-signal",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "broadcast_signal",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "theme-set-study-dashboard-analytical",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "dashboard_analytical",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "theme-set-study-gallery-infographic",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "gallery_infographic",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "theme-set-study-market-technical",
            "goal": "show ranking",
            "question": "다음 분기 성장을 주도할 채널은?",
            "theme_set": "market_technical",
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme set study", "Forecast planning model"],
        },
        {
            "task_id": "ranking-bar-horizontal",
            "goal": "show ranking",
            "question": "어떤 카테고리가 가장 큰가?",
            "dataset": {
                "title": "시장 점유 점수",
                "unit": "점",
                "items": [
                    {"label": "대한민국", "value": 42},
                    {"label": "일본", "value": 28},
                    {"label": "대만", "value": 17},
                ],
            },
            "source_hints": ["Internal benchmark"],
        },
        {
            "task_id": "vertical-bar",
            "goal": "show ranking",
            "question": "짧은 레이블은 세로 막대로 비교하라",
            "dataset": {
                "title": "제품 판매량",
                "unit": "만",
                "items": [
                    {"label": "A", "value": 18},
                    {"label": "B", "value": 14},
                    {"label": "C", "value": 9},
                    {"label": "D", "value": 6},
                ],
            },
            "source_hints": ["Sales snapshot"],
        },
        {
            "task_id": "three-d-bar",
            "goal": "입체 막대 그래프로 비교하라",
            "question": "입체 막대 스타일로 제품군을 비교하라",
            "dataset": {
                "title": "제품군 비교",
                "unit": "점",
                "items": [
                    {"label": "A", "value": 16},
                    {"label": "B", "value": 12},
                    {"label": "C", "value": 10},
                ],
            },
            "source_hints": ["Creative direction memo"],
        },
        {
            "task_id": "forecast-pattern-bar",
            "goal": "show ranking with projection marker",
            "question": "예상치가 포함된 막대를 비교하라",
            "dataset": {
                "title": "채널별 신규 유입",
                "unit": "만",
                "items": [
                    {"label": "Organic", "value": 18},
                    {"label": "Paid", "value": 14},
                    {"label": "Partner", "value": 11, "note": "Projected 2026 pipeline"},
                ],
            },
            "source_hints": ["Growth planning memo"],
        },
        {
            "task_id": "outline-hatch-bar",
            "goal": "show forecast as outline hatch",
            "question": "속을 채우지 않고 테두리와 빗금으로 예상치를 표시하라",
            "dataset": {
                "title": "채널별 예상 유입",
                "unit": "만",
                "items": [
                    {"label": "Organic", "value": 18},
                    {"label": "Paid", "value": 14},
                    {"label": "Partner", "value": 11, "note": "Projected 2026 pipeline"},
                ],
            },
            "source_hints": ["Forecast visual test"],
        },
        {
            "task_id": "outline-only-bar",
            "goal": "show preliminary estimate",
            "question": "속을 채우지 않은 테두리 막대로 잠정치를 보여라",
            "dataset": {
                "title": "채널별 잠정 유입",
                "unit": "만",
                "items": [
                    {"label": "Organic", "value": 18},
                    {"label": "Paid", "value": 14},
                    {"label": "Partner", "value": 11, "note": "Preliminary channel total"},
                ],
            },
            "source_hints": ["Draft planning sheet"],
        },
        {
            "task_id": "range-hatch-progress",
            "goal": "show range estimate",
            "question": "투명 범위 해치로 구간 추정을 누적 프로그레스로 보여라",
            "dataset": {
                "title": "전환 구성 범위",
                "items": [
                    {"label": "Baseline", "value": 44, "unit": "%"},
                    {"label": "Upside", "value": 31, "unit": "%", "note": "Confidence range"},
                    {"label": "Stretch", "value": 25, "unit": "%"},
                ],
            },
            "source_hints": ["Planning envelope"],
        },
        {
            "task_id": "editorial-outline-combo-bar",
            "goal": "show outline editorial treatment",
            "question": "에디토리얼 아웃라인 스타일로 테두리와 빗금 막대를 보여라",
            "dataset": {
                "title": "세그먼트 확장 시나리오",
                "unit": "만",
                "items": [
                    {"label": "Core", "value": 21},
                    {"label": "Growth", "value": 16},
                    {"label": "Edge", "value": 9, "note": "Projected scenario"},
                ],
            },
            "source_hints": ["Magazine layout test"],
        },
        {
            "task_id": "broadcast-signal-combo-bar",
            "goal": "show breaking signal chart",
            "question": "속보형 시그널 그래픽처럼 예상치를 강하게 표시하라",
            "dataset": {
                "title": "속보형 유입 시그널",
                "unit": "만",
                "items": [
                    {"label": "Core", "value": 21},
                    {"label": "Growth", "value": 16},
                    {"label": "Edge", "value": 9, "note": "Projected scenario"},
                ],
            },
            "source_hints": ["Breaking desk"],
        },
        {
            "task_id": "gallery-infographic-combo-bar",
            "goal": "show gallery infographic bar",
            "question": "갤러리 인포그래픽 스타일로 줄무늬 막대를 보여라",
            "dataset": {
                "title": "전시형 확장 시나리오",
                "unit": "만",
                "items": [
                    {"label": "Core", "value": 21},
                    {"label": "Growth", "value": 16},
                    {"label": "Edge", "value": 9, "note": "Projected scenario"},
                ],
            },
            "source_hints": ["Exhibition poster test"],
        },
        {
            "task_id": "time-series-line",
            "goal": "show trend",
            "question": "매출이 어떻게 변했는가?",
            "dataset": {
                "title": "연도별 매출",
                "unit": "억",
                "x_label": "연도",
                "y_label": "매출",
                "points": [
                    {"x": "2021", "y": 12},
                    {"x": "2022", "y": 18},
                    {"x": "2023", "y": 27},
                ],
            },
            "source_hints": ["Annual report"],
        },
        {
            "task_id": "broadcast-line",
            "goal": "news trend recap",
            "question": "속보 그래픽처럼 실시간 추세를 보여라",
            "dataset": {
                "title": "실시간 지표",
                "unit": "%",
                "x_label": "시점",
                "y_label": "변화율",
                "points": [
                    {"x": "09:00", "y": 14},
                    {"x": "10:00", "y": 17},
                    {"x": "11:00", "y": 12},
                    {"x": "12:00", "y": 19},
                ],
            },
            "source_hints": ["Live desk"],
        },
        {
            "task_id": "share-donut",
            "goal": "show composition",
            "question": "점유 비중은 어떻게 나뉘는가?",
            "dataset": {
                "title": "점유율",
                "items": [
                    {"label": "A", "value": 46, "unit": "%"},
                    {"label": "B", "value": 34, "unit": "%"},
                    {"label": "C", "value": 20, "unit": "%"},
                ],
            },
            "source_hints": ["Market summary"],
        },
        {
            "task_id": "share-pie",
            "goal": "show composition with pie chart",
            "question": "파이 차트로 유입 비중을 보여라",
            "dataset": {
                "title": "유입 비중",
                "items": [
                    {"label": "Organic", "value": 52, "unit": "%"},
                    {"label": "Paid", "value": 28, "unit": "%"},
                    {"label": "Partner", "value": 20, "unit": "%"},
                ],
            },
            "source_hints": ["Channel report"],
        },
        {
            "task_id": "percentage-progress",
            "goal": "show progress",
            "question": "트랙별 진행률을 프로그레스 바로 비교하라",
            "dataset": {
                "title": "프로젝트 진행률",
                "items": [
                    {"label": "기획", "value": 92, "unit": "%"},
                    {"label": "개발", "value": 68, "unit": "%"},
                    {"label": "QA", "value": 41, "unit": "%"},
                ],
            },
            "source_hints": ["Project board"],
        },
        {
            "task_id": "radial-gauge",
            "goal": "show circular gauge",
            "question": "원형 게이지로 목표 달성률을 보여라",
            "dataset": {
                "title": "목표 달성률",
                "label": "OKR 달성률",
                "value": 74,
                "unit": "%",
            },
            "source_hints": ["Strategy tracker"],
        },
        {
            "task_id": "semi-donut-gauge",
            "goal": "show half gauge",
            "question": "반원 게이지로 이행률을 보여라",
            "dataset": {
                "title": "이행률",
                "label": "로드맵 이행률",
                "value": 61,
                "unit": "%",
            },
            "source_hints": ["Roadmap tracker"],
        },
        {
            "task_id": "stacked-progress",
            "goal": "show stacked progress share",
            "question": "누적 프로그레스 바로 구성 비중을 보여라",
            "dataset": {
                "title": "채널 구성",
                "items": [
                    {"label": "Organic", "value": 52, "unit": "%"},
                    {"label": "Paid", "value": 28, "unit": "%"},
                    {"label": "Partner", "value": 20, "unit": "%"},
                ],
            },
            "source_hints": ["Channel report"],
        },
        {
            "task_id": "distribution-histogram",
            "goal": "show distribution",
            "question": "점수 분포를 구간별로 보여라",
            "dataset": {
                "title": "시험 점수 분포",
                "shape": "distribution_bins",
                "x_label": "점수 구간",
                "y_label": "응답 수",
                "bins": [
                    {"start": 0, "end": 10, "count": 2},
                    {"start": 10, "end": 20, "count": 5},
                    {"start": 20, "end": 30, "count": 11},
                    {"start": 30, "end": 40, "count": 18},
                    {"start": 40, "end": 50, "count": 14},
                ],
            },
            "source_hints": ["Distribution sample"],
        },
        {
            "task_id": "stock-candlestick",
            "goal": "show stock movement",
            "question": "주가 움직임을 시가고가저가종가로 보이라",
            "dataset": {
                "title": "주가 흐름",
                "shape": "ohlc_series",
                "x_label": "날짜",
                "y_label": "가격",
                "candles": [
                    {"x": "04-01", "open": 101, "high": 110, "low": 98, "close": 108},
                    {"x": "04-02", "open": 108, "high": 112, "low": 103, "close": 105},
                    {"x": "04-03", "open": 105, "high": 118, "low": 104, "close": 116},
                    {"x": "04-04", "open": 116, "high": 120, "low": 111, "close": 113},
                ],
            },
            "source_hints": ["Market sample"],
        },
        {
            "task_id": "metric-wall-kpi",
            "goal": "headline kpi summary",
            "question": "핵심 KPI 요약",
            "dataset": {
                "title": "핵심 KPI",
                "items": [
                    {"label": "매출", "value": 128, "unit": "억"},
                    {"label": "영업이익", "value": 19, "unit": "억"},
                    {"label": "가입자", "value": 320, "unit": "만"},
                ],
            },
            "source_hints": ["Quarterly summary"],
        },
        {
            "task_id": "comparison-table",
            "goal": "compare features",
            "question": "세 옵션은 무엇이 다른가?",
            "dataset": {
                "title": "플랜 비교",
                "headers": ["플랜", "월 요금", "저장 용량"],
                "rows": [
                    ["Basic", "9,900", "100GB"],
                    ["Pro", "19,900", "1TB"],
                    ["Enterprise", "49,900", "무제한"],
                ],
            },
            "source_hints": ["Pricing page"],
        },
        {
            "task_id": "fact-table",
            "goal": "fact lookup",
            "dataset": {
                "title": "핵심 정보",
                "headers": ["항목", "값"],
                "rows": [
                    ["설립", "2019"],
                    ["직원 수", "42명"],
                ],
            },
            "source_hints": ["Company profile"],
        },
        {
            "task_id": "timeline-table",
            "goal": "compare milestones",
            "dataset": {
                "title": "주요 연혁",
                "headers": ["연도", "사건", "영향"],
                "rows": [
                    ["2021", "출시", "초기 진입"],
                    ["2022", "확장", "사용자 증가"],
                    ["2023", "흑자 전환", "수익성 개선"],
                ],
            },
            "source_hints": ["Company timeline"],
        },
        {
            "task_id": "annotated-line-peak",
            "goal": "show trend with peak callout",
            "question": "정점 구간을 강조하라",
            "dataset": {
                "title": "연도별 매출",
                "unit": "억",
                "x_label": "연도",
                "y_label": "매출",
                "points": [
                    {"x": "2021", "y": 12},
                    {"x": "2022", "y": 30},
                    {"x": "2023", "y": 19},
                ],
            },
            "source_hints": ["Annual report"],
        },
        {
            "task_id": "annotated-bar-focus",
            "goal": "show ranking",
            "dataset": {
                "items": [
                    {"label": "A", "value": 10, "unit": "점"},
                    {"label": "B", "value": 8, "unit": "점"},
                    {"label": "C", "value": 4, "unit": "점"},
                ]
            },
            "constraints": {
                "annotations": [{"target": "bar", "match_label": "B", "label": "중점 비교"}],
            },
            "source_hints": ["Synthetic"],
        },
        {
            "task_id": "warning-case",
            "goal": "show ranking",
            "dataset": {
                "items": [
                    {"label": "아주아주긴카테고리이름테스트A", "value": 10, "unit": "%"},
                    {"label": "아주아주긴카테고리이름테스트B", "value": 8, "unit": "건"},
                ]
            },
            "constraints": {
                "annotations": [{"target": "slice"}],
            },
        },
    ]


def _theme_gallery_theme_sets() -> list[str]:
    return [
        "neutral_white",
        "editorial_outline",
        "broadcast_signal",
        "dashboard_analytical",
        "gallery_infographic",
        "poster_editorial",
        "market_technical",
    ]


def _theme_doc_source_path(theme_set: str) -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "docs" / "chartagent_themes" / f"{theme_set}.THEME.md"


def _theme_gallery_variants() -> list[dict[str, Any]]:
    return [
        {
            "key": "base",
            "label": "Theme Default",
            "theme_overrides": {},
            "theme_reset": {},
        },
        {
            "key": "signal",
            "label": "Pattern Boost",
            "theme_overrides": {
                "accent_color": "#fb923c",
                "accent_alt_color": "#67e8f9",
                "panel_color": "#0f1a31",
                "plot_bg_color": "#0b1426",
                "pattern_density": "high",
                "stroke_width": 6.0,
                "outline_width": 3.2,
                "source_mode": "edge_rail",
                "source_opacity": 0.92,
                "label_weight": 720,
            },
            "theme_reset": {},
        },
        {
            "key": "rounded",
            "label": "Soft Round",
            "theme_overrides": {
                "accent_color": "#8b5cf6",
                "accent_alt_color": "#14b8a6",
                "panel_color": "#f7efe5",
                "plot_bg_color": "#f4eadb",
                "corner_radius": 34,
                "chip_radius": 22,
                "bar_gap": 0.24,
                "table_cell_padding": 22,
                "source_mode": "bottom_left",
                "source_opacity": 0.84,
                "pattern_density": "low",
                "title_scale": 1.06,
            },
            "theme_reset": {},
        },
    ]


def _theme_gallery_sample_tasks(theme_set: str, variant: dict[str, Any]) -> list[dict[str, Any]]:
    variant_key = str(variant.get("key") or "base")
    theme_overrides = dict(variant.get("theme_overrides") or {})
    theme_reset = dict(variant.get("theme_reset") or {})
    return [
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-ranking",
            "goal": "show ranking",
            "question": "어떤 채널이 다음 분기 성장을 주도할까?",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "성장 채널 전망 점수",
                "unit": "pt",
                "items": [
                    {"label": "Organic SEO", "value": 420},
                    {"label": "Influencers", "value": 270, "note": "forecast"},
                    {"label": "Newsletters", "value": 180},
                    {"label": "Enterprise", "value": 130, "note": "forecast"},
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Forecast planning model"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-trend",
            "goal": "show trend",
            "question": "수익 흐름은 어떻게 변했는가?",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "연도별 ARR",
                "unit": "억",
                "x_label": "연도",
                "y_label": "ARR",
                "points": [
                    {"x": "2021", "y": 12},
                    {"x": "2022", "y": 19},
                    {"x": "2023", "y": 31},
                    {"x": "2024", "y": 46},
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Revenue trend model"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-share",
            "goal": "show composition",
            "question": "유입 비중은 어떻게 나뉘는가?",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "유입 비중",
                "items": [
                    {"label": "Organic", "value": 46, "unit": "%"},
                    {"label": "Paid", "value": 28, "unit": "%"},
                    {"label": "Partner", "value": 16, "unit": "%"},
                    {"label": "Newsletter", "value": 10, "unit": "%"},
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Acquisition mix model"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-comparison",
            "goal": "compare features",
            "question": "세 플랜은 무엇이 다른가?",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "플랜 비교",
                "headers": ["플랜", "월 요금", "AI 크레딧", "협업 좌석"],
                "rows": [
                    ["Starter", "9,900", "50", "1"],
                    ["Pro", "24,900", "250", "5"],
                    ["Scale", "59,000", "Unlimited", "20"],
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Pricing comparison"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-metric-wall",
            "goal": "headline kpi summary",
            "question": "핵심 KPI를 카드 벽으로 요약하라",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "핵심 KPI",
                "items": [
                    {"label": "ARR", "value": 128, "unit": "억"},
                    {"label": "Gross Margin", "value": 71, "unit": "%"},
                    {"label": "Active Seats", "value": 320, "unit": "만"},
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Executive KPI wall"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-single-stat",
            "goal": "headline single stat",
            "question": "하나의 핵심 숫자를 크게 강조하라",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "이번 분기 핵심 수치",
                "label": "분기 ARR",
                "value": 38,
                "unit": "억",
            },
            "source_hints": ["Theme gallery benchmark", "Hero stat treatment"],
        },
        {
            "task_id": f"theme-gallery-{theme_set}-{variant_key}-fact-table",
            "goal": "fact lookup",
            "question": "핵심 사실을 빠르게 읽게 하라",
            "theme_set": theme_set,
            "theme_overrides": theme_overrides,
            "theme_reset": theme_reset,
            "dataset": {
                "title": "프로덕트 팩트",
                "headers": ["항목", "값"],
                "rows": [
                    ["출시", "2021"],
                    ["고객사", "2,400+"],
                    ["시장", "B2B SaaS"],
                ],
            },
            "source_hints": ["Theme gallery benchmark", "Fact lookup sheet"],
        },
    ]
