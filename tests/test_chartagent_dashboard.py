from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from chartagent.runners.dashboard_runner import (
    write_chartagent_dashboard,
)


class ChartAgentDashboardTests(unittest.TestCase):
    def test_write_chartagent_dashboard_writes_index_and_case_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "dashboard"
            manifest = write_chartagent_dashboard(out_dir)

            self.assertTrue((out_dir / "index.html").exists())
            self.assertTrue((out_dir / "theme_gallery.html").exists())
            self.assertTrue((out_dir / "dashboard_manifest.json").exists())
            self.assertGreaterEqual(manifest["case_count"], 12)
            self.assertEqual(manifest["theme_gallery_case_count"], 147)
            self.assertIn("broadcast_signal", manifest["theme_gallery_themes"])
            self.assertIn("poster_editorial", manifest["theme_gallery_themes"])
            self.assertEqual(manifest["theme_gallery_variants"], ["base", "signal", "rounded"])
            self.assertEqual(manifest["dashboard_reference_case_count"], 189)
            self.assertEqual(manifest["dashboard_pattern_options"], ["fill", "hatch", "dot"])

            index_html = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("<h1>ChartAgent</h1>", index_html)
            self.assertIn("Reference Grid", index_html)
            self.assertIn("Browse Raw Bundles", index_html)
            self.assertIn("Selected Theme", index_html)
            self.assertIn("Chart Detail", index_html)
            self.assertIn("dashboard_manifest.json", index_html)
            self.assertNotIn("ChartAgent Reference Workspace", index_html)
            self.assertNotIn("reference families", index_html)
            self.assertNotIn("audit bundles", index_html)
            self.assertIn("metric_wall", index_html)
            self.assertIn("fact_table", index_html)
            self.assertIn("single_stat", index_html)
            self.assertIn("bar_horizontal", index_html)
            self.assertIn(">bar<", index_html)
            self.assertIn("stacked_progress", index_html)
            self.assertIn('id="reference-theme-select"', index_html)
            self.assertIn('id="reference-family-filter"', index_html)
            self.assertIn('id="reference-pattern-filter"', index_html)
            self.assertIn('id="reference-visible-count"', index_html)
            self.assertIn('id="reference-grid"', index_html)
            self.assertIn('id="reference-detail-modal"', index_html)
            self.assertIn('id="reference-detail-panel"', index_html)
            self.assertIn('id="reference-modal-close"', index_html)
            self.assertNotIn('data-variant="signal"', index_html)
            self.assertIn("No matching reference charts for the current theme, family, and pattern selection.", index_html)
            self.assertIn('data-reference-card', index_html)
            self.assertIn('data-pattern-option="fill"', index_html)
            self.assertIn('data-pattern-option="hatch"', index_html)
            self.assertIn('data-pattern-option="dot"', index_html)
            self.assertIn('role="dialog"', index_html)
            self.assertIn('data-theme-summary="broadcast_signal"', index_html)
            self.assertIn("Pattern Treatment", index_html)
            self.assertIn(">Fill<", index_html)
            self.assertIn(">Hatch<", index_html)
            self.assertIn(">Dot<", index_html)
            self.assertIn("Why This Form", index_html)
            self.assertIn("Theme Signals", index_html)
            self.assertIn("Artifacts", index_html)
            self.assertIn("theme", index_html)
            self.assertIn("theme_set", index_html)
            self.assertIn("refs", index_html)
            self.assertIn("combo", index_html)
            self.assertIn("pattern", index_html)
            self.assertIn("editorial_outline", index_html)
            self.assertIn("broadcast_signal", index_html)

            gallery_html = (out_dir / "theme_gallery.html").read_text(encoding="utf-8")
            self.assertIn("ChartAgent Theme Gallery", gallery_html)
            self.assertIn("theme-neutral-white", gallery_html)
            self.assertIn("theme-broadcast-signal", gallery_html)
            self.assertIn("theme-poster-editorial", gallery_html)
            self.assertIn("Organic SEO", gallery_html)
            self.assertIn("line", gallery_html)
            self.assertIn("comparison_table", gallery_html)
            self.assertIn("metric_wall", gallery_html)
            self.assertIn("single_stat", gallery_html)
            self.assertIn("fact_table", gallery_html)
            self.assertIn("Pattern Boost", gallery_html)
            self.assertIn("Soft Round", gallery_html)
            self.assertIn("Reset to Theme", gallery_html)
            self.assertIn('data-variant="signal"', gallery_html)

            case_dir = out_dir / "cases" / "annotated-line-peak"
            self.assertTrue((case_dir / "chart_task.json").exists())
            self.assertTrue((case_dir / "chart_spec.json").exists())
            self.assertTrue((case_dir / "dataset.normalized.json").exists())
            self.assertTrue((case_dir / "render.svg").exists())

            gallery_case_dir = out_dir / "theme_gallery_cases" / "theme-gallery-broadcast_signal-base-trend"
            self.assertTrue((gallery_case_dir / "chart_task.json").exists())
            self.assertTrue((gallery_case_dir / "chart_spec.json").exists())
            self.assertTrue((gallery_case_dir / "dataset.normalized.json").exists())
            self.assertTrue((gallery_case_dir / "render.svg").exists())

            reference_case_dir = out_dir / "dashboard_reference_cases" / "dashboard-reference-neutral_white-base-fill-vertical-bar"
            self.assertTrue((reference_case_dir / "chart_task.json").exists())
            self.assertTrue((reference_case_dir / "chart_spec.json").exists())
            self.assertTrue((reference_case_dir / "dataset.normalized.json").exists())
            self.assertTrue((reference_case_dir / "render.svg").exists())


if __name__ == "__main__":
    unittest.main()
