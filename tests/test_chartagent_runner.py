from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from chartagent.runners.chartagent_runner import (
    build_chart_artifacts,
    write_chart_outputs,
)


class ChartAgentRunnerTests(unittest.TestCase):
    def test_build_chart_artifacts_selects_bar_horizontal_for_label_value_list(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "ranking-test",
                "goal": "show ranking",
                "question": "어떤 카테고리가 가장 큰가?",
                "preferred_output": ["chart_spec", "svg"],
                "dataset": {
                    "title": "시장 점유율",
                    "unit": "점",
                    "items": [
                        {"label": "대한민국 내수 시장 전체", "value": 42},
                        {"label": "일본 수출 채널 확장", "value": 28},
                        {"label": "대만 온라인 판매 전환", "value": 17},
                    ],
                },
                "source_hints": ["Internal benchmark"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "label_value_list")
        self.assertEqual(result.chart_spec["chart_family"], "bar_horizontal")
        self.assertIn("대한민국", result.render_svg)
        self.assertIn('class="value" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">42점</text>', result.render_svg)

    def test_build_chart_artifacts_selects_line_for_time_series(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "trend-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "time_series")
        self.assertEqual(result.chart_spec["chart_family"], "line")
        self.assertIn("polyline", result.render_svg)

    def test_build_chart_artifacts_selects_comparison_table_for_rows_and_columns(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "table-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "comparison_table")
        self.assertEqual(result.chart_spec["style_spec"]["layout_preset"], "comparison_sheet")
        self.assertIn("플랜", result.render_svg)
        self.assertIn('class="header" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">월 요금</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="end" fill="#0f4c5c" style="fill:#0f4c5c !important;">9,900</text>', result.render_svg)

    def test_build_chart_artifacts_selects_fact_table_for_two_column_lookup(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "facts-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "fact_table")

    def test_build_chart_artifacts_selects_donut_for_share_breakdown(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "share-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "share_breakdown")
        self.assertEqual(result.chart_spec["chart_family"], "donut")
        self.assertTrue(any(item["target"] == "dominant_slice" for item in result.chart_spec["annotations"]))
        self.assertIn("stroke-dasharray", result.render_svg)
        self.assertIn('class="value" text-anchor="end" fill="#1f1a17" style="fill:#1f1a17 !important;">46%</text>', result.render_svg)

    def test_build_chart_artifacts_selects_pie_when_requested(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "pie-test",
                "goal": "show composition with pie chart",
                "question": "파이 차트로 비중을 보여라",
                "dataset": {
                    "title": "채널 비중",
                    "items": [
                        {"label": "Organic", "value": 52, "unit": "%"},
                        {"label": "Paid", "value": 28, "unit": "%"},
                        {"label": "Partner", "value": 20, "unit": "%"},
                    ],
                },
                "source_hints": ["Channel report"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "pie")
        self.assertIn("<path d=\"M", result.render_svg)
        self.assertIn('class="value" text-anchor="end" fill="#1f1a17" style="fill:#1f1a17 !important;">52%</text>', result.render_svg)

    def test_build_chart_artifacts_selects_percentage_progress_for_single_percent(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "progress-single-test",
                "goal": "show progress",
                "question": "달성률을 프로그레스 바로 보여라",
                "dataset": {
                    "title": "목표 달성률",
                    "label": "출시 준비",
                    "value": 68,
                    "unit": "%",
                },
                "source_hints": ["Execution tracker"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "percentage_progress")
        self.assertIn(">68%</text>", result.render_svg)
        self.assertIn(">100%</text>", result.render_svg)

    def test_build_chart_artifacts_selects_percentage_progress_for_multi_percent_records(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "progress-multi-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "percentage_progress")
        self.assertEqual(result.dataset_normalized["shape"], "label_value_list")
        self.assertIn(">기획</text>", result.render_svg)
        self.assertIn('class="value" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">92%</text>', result.render_svg)

    def test_build_chart_artifacts_selects_radial_gauge_when_requested(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "radial-gauge-test",
                "goal": "show circular gauge",
                "question": "원형 게이지로 목표 달성률을 보여라",
                "dataset": {
                    "title": "목표 달성률",
                    "label": "OKR 달성률",
                    "value": 74,
                    "unit": "%",
                },
                "source_hints": ["Strategy tracker"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "radial_gauge")
        self.assertIn('stroke-dasharray="', result.render_svg)
        self.assertIn(">74%</text>", result.render_svg)

    def test_build_chart_artifacts_selects_semi_donut_when_requested(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "semi-donut-test",
                "goal": "show half gauge",
                "question": "반원 게이지로 이행률을 보여라",
                "dataset": {
                    "title": "이행률",
                    "label": "로드맵 이행률",
                    "value": 61,
                    "unit": "%",
                },
                "source_hints": ["Roadmap tracker"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "semi_donut")
        self.assertIn('<path d="M', result.render_svg)
        self.assertIn(">61%</text>", result.render_svg)

    def test_build_chart_artifacts_selects_stacked_progress_for_share_breakdown_when_requested(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "stacked-progress-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "share_breakdown")
        self.assertEqual(result.chart_spec["chart_family"], "stacked_progress")
        self.assertIn('class="value" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">52%</text>', result.render_svg)
        self.assertIn('>100%</text>', result.render_svg)

    def test_build_chart_artifacts_selects_vertical_bar_for_short_labels(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "vertical-bar-test",
                "goal": "show ranking",
                "dataset": {
                    "title": "판매량",
                    "unit": "만",
                    "items": [
                        {"label": "A", "value": 18},
                        {"label": "B", "value": 14},
                        {"label": "C", "value": 9},
                        {"label": "D", "value": 6},
                    ],
                },
                "source_hints": ["Sales snapshot"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "bar")
        self.assertEqual(result.chart_spec["chart_variant"], "vertical")

    def test_build_chart_artifacts_applies_pattern_fill_only_to_forecast_marked_bar(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "forecast-pattern-bar-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "bar")
        self.assertTrue(result.chart_spec["style_spec"]["pattern_policy"]["enabled"])
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["reason"], "forecast")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["fill_treatment"], "outline_plus_hatch")
        self.assertEqual(result.chart_spec["style_spec"]["style_combo_preset"], "neutral_system")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_dashboard")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_scope"], "chart_wide")
        self.assertIn('<pattern id="cg-pattern-bar-0"', result.render_svg)
        self.assertIn('<pattern id="cg-pattern-bar-1"', result.render_svg)
        self.assertIn('<pattern id="cg-pattern-bar-2"', result.render_svg)
        self.assertIn('fill="url(#cg-pattern-bar-0)"', result.render_svg)
        self.assertIn('fill="url(#cg-pattern-bar-1)"', result.render_svg)
        self.assertIn('fill="url(#cg-pattern-bar-2)"', result.render_svg)
        self.assertGreaterEqual(result.render_svg.count('stroke="#2563eb" stroke-width="2.2"'), 3)

    def test_build_chart_artifacts_applies_outline_only_fill_treatment_for_preliminary_bar(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "outline-only-bar-test",
                "goal": "show preliminary comparison",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "bar")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["reason"], "incomplete")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["fill_treatment"], "outline_only")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_editorial")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_scope"], "chart_wide")
        self.assertNotIn('<pattern id="cg-pattern-bar-2"', result.render_svg)
        self.assertGreaterEqual(result.render_svg.count('fill="none" stroke="#b45309" stroke-width="2.25"'), 3)

    def test_build_chart_artifacts_applies_transparent_range_hatch_for_range_progress(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "range-progress-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "stacked_progress")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["reason"], "range")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_policy"]["fill_treatment"], "transparent_range_hatch")
        self.assertEqual(result.chart_spec["style_spec"]["style_combo_preset"], "analytical_panel")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_dashboard")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_scope"], "chart_wide")
        self.assertIn('<pattern id="cg-pattern-stacked-progress-0"', result.render_svg)
        self.assertIn('<pattern id="cg-pattern-stacked-progress-1"', result.render_svg)
        self.assertIn('<pattern id="cg-pattern-stacked-progress-2"', result.render_svg)
        self.assertIn('fill-opacity="0.12"', result.render_svg)
        self.assertIn('stroke="#0284c7" stroke-width="1.45"', result.render_svg)
        self.assertIn('stroke="#0f766e" stroke-width="1.45"', result.render_svg)
        self.assertIn('stroke="#2563eb" stroke-width="1.45"', result.render_svg)

    def test_build_chart_artifacts_selects_three_d_bar_variant_when_requested(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "three-d-bar-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "bar")
        self.assertEqual(result.chart_spec["chart_variant"], "three_d")
        self.assertIn("<polygon", result.render_svg)

    def test_build_chart_artifacts_selects_editorial_outline_style_combo(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "editorial-outline-combo-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["style_spec"]["style_combo_preset"], "editorial_outline")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_editorial")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["pattern_kind_default"], "diagonal_hatch")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["guide_dasharray"], "4 6")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["pattern_spacing"], 16)
        self.assertIn('stroke-width="2.45"', result.render_svg)

    def test_build_chart_artifacts_selects_broadcast_signal_style_combo(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "broadcast-signal-combo-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["style_spec"]["style_combo_preset"], "broadcast_signal")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_broadcast")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["guide_dasharray"], "8 6")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["pattern_spacing"], 8)
        self.assertIn('stroke-width="2.75"', result.render_svg)

    def test_build_chart_artifacts_selects_gallery_infographic_style_combo(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "gallery-infographic-combo-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["style_spec"]["style_combo_preset"], "gallery_infographic")
        self.assertEqual(result.chart_spec["style_spec"]["pattern_format_preset"], "signal_outline_editorial")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["pattern_kind_default"], "diagonal_hatch")
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["bar_radius"], 14)
        self.assertEqual(result.chart_spec["style_spec"]["motif_tokens"]["pattern_spacing"], 10)
        self.assertIn('stroke-width="2.45"', result.render_svg)

    def test_build_chart_artifacts_selects_metric_wall_for_kpi_summary(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "metric-wall-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "metric_wall")
        self.assertEqual(result.chart_spec["style_spec"]["theme_name"], "dashboard")
        self.assertEqual(result.chart_spec["style_spec"]["layout_preset"], "hero_panel")
        self.assertEqual(len(result.chart_spec["annotations"]), 3)
        self.assertIn("매출", result.render_svg)
        self.assertIn('<rect x="60" y="122" width="400" height="156"', result.render_svg)
        self.assertIn('class="subtitle" fill="#0f4c5c" style="fill:#0f4c5c !important;">가입자</text>', result.render_svg)

    def test_build_chart_artifacts_uses_poster_hero_metric_wall_layout(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "poster-metric-wall-test",
                "goal": "headline kpi summary",
                "question": "포스터형 KPI 벽으로 핵심 숫자를 보여라",
                "theme_set": "poster_editorial",
                "dataset": {
                    "title": "포스터 KPI",
                    "items": [
                        {"label": "ARR", "value": 128, "unit": "억"},
                        {"label": "Gross Margin", "value": 71, "unit": "%"},
                        {"label": "Active Seats", "value": 320, "unit": "만"},
                    ],
                },
                "source_hints": ["Poster editorial benchmark"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "metric_wall")
        self.assertEqual(result.chart_spec["style_spec"]["theme_set"], "poster_editorial")
        self.assertEqual(result.chart_spec["style_spec"]["theme_source_refs"], ["pinterest", "notion", "claude"])
        self.assertIn('<rect x="60" y="122" width="840" height="178" rx="30"', result.render_svg)
        self.assertIn(">Active Seats</text>", result.render_svg)
        self.assertIn(">editorial poster metric</text>", result.render_svg)

    def test_build_chart_artifacts_uses_broadcast_signal_surface_for_single_stat(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "broadcast-single-stat-test",
                "goal": "headline single stat",
                "question": "방송형 시그널 패널로 핵심 숫자를 보여라",
                "theme_set": "broadcast_signal",
                "dataset": {
                    "title": "핵심 수치",
                    "label": "실시간 ARR",
                    "value": 38,
                    "unit": "억",
                },
                "source_hints": ["Broadcast benchmark"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "single_stat")
        self.assertEqual(result.chart_spec["style_spec"]["theme_set"], "broadcast_signal")
        self.assertIn(">LIVE KPI</text>", result.render_svg)
        self.assertIn('fill="#0c1730"', result.render_svg)
        self.assertIn('stroke="#22d3ee" stroke-width="4"', result.render_svg)

    def test_build_chart_artifacts_uses_broadcast_fact_table_surface(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "broadcast-fact-table-test",
                "goal": "fact lookup",
                "question": "속보형 팩트시트처럼 핵심 사실을 보여라",
                "theme_set": "broadcast_signal",
                "dataset": {
                    "title": "핵심 사실",
                    "headers": ["항목", "값"],
                    "rows": [
                        ["출시", "2021"],
                        ["고객사", "2,400+"],
                    ],
                },
                "source_hints": ["Broadcast benchmark"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "fact_table")
        self.assertEqual(result.chart_spec["style_spec"]["theme_set"], "broadcast_signal")
        self.assertIn(">FACT SHEET</text>", result.render_svg)
        self.assertIn('width="6" height="66" rx="4" fill="#22d3ee"', result.render_svg)

    def test_build_chart_artifacts_applies_broadcast_theme_tokens_to_svg(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "broadcast-line-test",
                "goal": "news trend recap",
                "question": "속보 그래픽처럼 추세를 보여라",
                "dataset": {
                    "title": "실시간 지표",
                    "unit": "%",
                    "x_label": "시점",
                    "y_label": "변화율",
                    "points": [
                        {"x": "09:00", "y": 14},
                        {"x": "10:00", "y": 17},
                        {"x": "11:00", "y": 12},
                    ],
                },
                "source_hints": ["Live desk"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["style_spec"]["theme_name"], "broadcast")
        self.assertEqual(result.chart_spec["style_spec"]["visual_mode"], "broadcast")
        self.assertEqual(result.chart_spec["style_spec"]["layout_preset"], "flash_panel")
        self.assertEqual(result.chart_spec["style_spec"]["reference_profile"], "bloomberg_flash")
        self.assertIn('fill="#07101c"', result.render_svg)
        self.assertIn('<text x="60" y="56" class="title" fill="#f8fafc" style="fill:#f8fafc !important;">', result.render_svg)
        self.assertIn('stroke-dasharray="8 6"', result.render_svg)

    def test_build_chart_artifacts_warns_when_legend_layout_is_crowded(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "legend-crowding-test",
                "goal": "show composition",
                "question": "긴 레이블이 있는 구성 비중을 보여라",
                "dataset": {
                    "title": "긴 구성 라벨",
                    "items": [
                        {"label": "매우긴세그먼트이름A", "value": 20, "unit": "%"},
                        {"label": "매우긴세그먼트이름B", "value": 18, "unit": "%"},
                        {"label": "매우긴세그먼트이름C", "value": 16, "unit": "%"},
                        {"label": "매우긴세그먼트이름D", "value": 14, "unit": "%"},
                        {"label": "매우긴세그먼트이름E", "value": 17, "unit": "%"},
                        {"label": "매우긴세그먼트이름F", "value": 15, "unit": "%"},
                    ],
                },
                "source_hints": ["Segment memo"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "donut")
        self.assertEqual(result.chart_spec["style_spec"]["legend_placement"], "right_rail")
        self.assertIn("Legend labels are long enough to crowd the current legend layout.", result.chart_spec["warnings"])

    def test_build_chart_artifacts_selects_timeline_table_for_time_rows(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "timeline-table-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "timeline_table")
        self.assertIn('class="header" text-anchor="middle" fill="#0f172a" style="fill:#0f172a !important;">연도</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="middle" fill="#0f4c5c" style="fill:#0f4c5c !important;">2021</text>', result.render_svg)

    def test_build_chart_artifacts_aligns_temporal_and_financial_columns_distinctly(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "financial-table-test",
                "goal": "compare periods and financial deltas",
                "dataset": {
                    "title": "분기 실적 요약",
                    "headers": ["기간", "매출", "YoY", "Valuation"],
                    "rows": [
                        ["2024 Q1", "KRW 9,900", "+12%", "1.2x"],
                        ["FY2025", "USD 12,500", "-3.5%", "0.9x"],
                    ],
                },
                "source_hints": ["Finance memo"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "comparison_table")
        self.assertIn('class="header" text-anchor="middle" fill="#0f172a" style="fill:#0f172a !important;">기간</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="middle" fill="#0f4c5c" style="fill:#0f4c5c !important;">2024 Q1</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="middle" fill="#0f4c5c" style="fill:#0f4c5c !important;">FY2025</text>', result.render_svg)
        self.assertIn('class="header" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">매출</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="end" fill="#0f4c5c" style="fill:#0f4c5c !important;">KRW 9,900</text>', result.render_svg)
        self.assertIn('class="header" text-anchor="end" fill="#0f172a" style="fill:#0f172a !important;">YoY</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="end" fill="#0f4c5c" style="fill:#0f4c5c !important;">+12%</text>', result.render_svg)
        self.assertIn('class="cell" text-anchor="end" fill="#0f4c5c" style="fill:#0f4c5c !important;">1.2x</text>', result.render_svg)

    def test_build_chart_artifacts_selects_distribution_histogram_for_bins(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "histogram-test",
                "goal": "show distribution",
                "dataset": {
                    "shape": "distribution_bins",
                    "title": "시험 점수 분포",
                    "bins": [
                        {"start": 0, "end": 10, "count": 2},
                        {"start": 10, "end": 20, "count": 5},
                        {"start": 20, "end": 30, "count": 11},
                    ],
                },
                "source_hints": ["Distribution sample"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "distribution_bins")
        self.assertEqual(result.chart_spec["chart_family"], "distribution_histogram")
        self.assertIn("fill=\"#0f766e\"", result.render_svg)

    def test_build_chart_artifacts_selects_stock_candlestick_for_ohlc_series(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "stock-test",
                "goal": "show stock movement",
                "dataset": {
                    "shape": "ohlc_series",
                    "title": "주가 흐름",
                    "candles": [
                        {"x": "04-01", "open": 101, "high": 110, "low": 98, "close": 108},
                        {"x": "04-02", "open": 108, "high": 112, "low": 103, "close": 105},
                    ],
                },
                "source_hints": ["Market sample"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.dataset_normalized["shape"], "ohlc_series")
        self.assertEqual(result.chart_spec["chart_family"], "stock_candlestick")
        self.assertEqual(result.chart_spec["style_spec"]["reference_profile"], "tradingview_terminal")
        self.assertIn("04-01", result.render_svg)
        self.assertIn('stroke-dasharray="3 5"', result.render_svg)

    def test_build_chart_artifacts_simplifies_long_rankings_for_display(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "simplify-test",
                "goal": "show ranking",
                "dataset": {
                    "items": [
                        {"label": "아주아주긴카테고리이름테스트01", "value": 100, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트02", "value": 95, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트03", "value": 90, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트04", "value": 85, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트05", "value": 80, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트06", "value": 75, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트07", "value": 70, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트08", "value": 65, "unit": "점"},
                        {"label": "아주아주긴카테고리이름테스트09", "value": 60, "unit": "점"},
                    ]
                },
                "source_hints": ["Synthetic"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(len(result.dataset_normalized["records"]), 8)
        self.assertTrue(result.dataset_normalized["simplification"]["label_shortening_applied"])
        self.assertTrue(any(issue["message"].startswith("Trimmed") for issue in result.issues))
        self.assertTrue(all("display_label" in record for record in result.dataset_normalized["records"]))

    def test_build_chart_artifacts_collapses_share_tail_into_other(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "share-collapse-test",
                "goal": "show composition",
                "dataset": {
                    "items": [
                        {"label": "A", "value": 40, "unit": "%"},
                        {"label": "B", "value": 18, "unit": "%"},
                        {"label": "C", "value": 12, "unit": "%"},
                        {"label": "D", "value": 10, "unit": "%"},
                        {"label": "E", "value": 8, "unit": "%"},
                        {"label": "F", "value": 5, "unit": "%"},
                        {"label": "G", "value": 4, "unit": "%"},
                        {"label": "H", "value": 2, "unit": "%"},
                        {"label": "I", "value": 1, "unit": "%"},
                    ]
                },
                "source_hints": ["Synthetic"],
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "donut")
        self.assertEqual(result.dataset_normalized["records"][-1]["label"], "기타")

    def test_build_chart_artifacts_selects_annotated_line_when_callout_is_needed(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "annotated-line-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "annotated_chart")
        self.assertEqual(result.chart_spec["base_chart_family"], "line")
        self.assertTrue(any(item["target"] in {"point", "latest_point"} for item in result.chart_spec["annotations"]))
        self.assertIn("Peak: 2022", result.render_svg)
        annotation_color = result.chart_spec["style_spec"]["theme_tokens"]["annotation_stroke"]
        self.assertIn(f'stroke="{annotation_color}" stroke-width="3"', result.render_svg)
        self.assertIn('<line x1="385.00" y1="126.00" x2="684.00" y2="152.00"', result.render_svg)
        self.assertIn('<rect x="684.00" y="134.00" width="192" height="36"', result.render_svg)

    def test_build_chart_artifacts_selects_annotated_bar_when_explicit_annotation_is_present(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "annotated-bar-test",
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
            }
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.chart_spec["chart_family"], "annotated_chart")
        self.assertEqual(result.chart_spec["base_chart_family"], "bar")
        self.assertIn("중점 비교", result.render_svg)

    def test_build_chart_artifacts_emits_quality_warnings(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "warning-test",
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
            }
        )

        self.assertTrue(result.valid)
        warnings = result.chart_spec["warnings"]
        self.assertTrue(any("Source note is missing" in warning for warning in warnings))
        self.assertTrue(any("Mixed units" in warning for warning in warnings))
        self.assertTrue(any("overflow" in warning for warning in warnings))
        self.assertTrue(any("Unsupported annotation target" in warning for warning in warnings))

    def test_build_chart_artifacts_applies_explicit_theme_set(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "theme-set-test",
                "goal": "show ranking",
                "theme_set": "broadcast_signal",
                "dataset": {
                    "items": [
                        {"label": "A", "value": 10, "unit": "점"},
                        {"label": "B", "value": 8, "unit": "점"},
                    ]
                },
                "source_hints": ["Synthetic"],
            }
        )

        self.assertTrue(result.valid)
        style_spec = result.chart_spec["style_spec"]
        self.assertEqual(style_spec["theme_set"], "broadcast_signal")
        self.assertEqual(style_spec["theme_name"], "broadcast")
        self.assertEqual(style_spec["reference_profile"], "bloomberg_flash")
        self.assertEqual(style_spec["style_combo_preset"], "broadcast_signal")
        self.assertIn("high-contrast dark panel", style_spec["theme_artwork_signature"])

    def test_build_chart_artifacts_applies_theme_overrides_and_reset(self) -> None:
        result = build_chart_artifacts(
            {
                "task_id": "theme-override-test",
                "goal": "show ranking",
                "theme_set": "neutral_white",
                "theme_overrides": {
                    "accent_color": "#14B8A6",
                    "corner_radius": 14,
                    "pattern_density": "high",
                    "title_scale": 1.25,
                },
                "theme_reset": {
                    "mode": "reset_keys",
                    "keys": ["accent_color"],
                },
                "dataset": {
                    "items": [
                        {"label": "A", "value": 10, "unit": "점"},
                        {"label": "B", "value": 8, "unit": "점"},
                    ]
                },
                "source_hints": ["Synthetic"],
            }
        )

        self.assertTrue(result.valid)
        style_spec = result.chart_spec["style_spec"]
        self.assertEqual(style_spec["theme_set"], "neutral_white")
        self.assertEqual(style_spec["theme_tokens"]["accent"], "#2563eb")
        self.assertEqual(style_spec["theme_tokens"]["radius_card"], 14)
        self.assertEqual(style_spec["theme_tokens"]["title_size"], 35)
        self.assertEqual(style_spec["motif_tokens"]["pattern_spacing"], 8.0)
        self.assertEqual(style_spec["theme_overrides"]["corner_radius"], 14)
        self.assertNotIn("accent_color", style_spec["theme_overrides"])

    def test_write_chart_outputs_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            task_path = workspace / "chart_task.json"
            out_dir = workspace / "chartagent_out"
            task_path.write_text(
                json.dumps(
                    {
                        "task_id": "write-test",
                        "goal": "show ranking",
                        "question": "무엇이 가장 큰가?",
                        "dataset": {
                            "items": [
                                {"label": "A", "value": 10},
                                {"label": "B", "value": 8},
                            ]
                        },
                        "source_hints": ["Synthetic"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            outputs = write_chart_outputs(task_path, out_dir)

            self.assertTrue((out_dir / "chart_spec.json").exists())
            self.assertTrue((out_dir / "dataset.normalized.json").exists())
            self.assertTrue((out_dir / "dataset.normalized.csv").exists())
            self.assertTrue((out_dir / "render.svg").exists())
            self.assertTrue((out_dir / "notes.md").exists())
            self.assertIn("render_svg", outputs)


if __name__ == "__main__":
    unittest.main()
