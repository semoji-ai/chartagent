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

            index_html = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("ChartAgent Static Review", index_html)
            self.assertIn("annotated_chart", index_html)
            self.assertIn("metric_wall", index_html)
            self.assertIn("stock_candlestick", index_html)
            self.assertIn("distribution_histogram", index_html)
            self.assertIn(">bar<", index_html)
            self.assertIn('id="family-filter"', index_html)
            self.assertIn('id="theme-set-filter"', index_html)
            self.assertIn('id="warning-only-toggle"', index_html)
            self.assertIn('id="case-search"', index_html)
            self.assertIn('id="visible-case-count"', index_html)
            self.assertIn("No matching cases for the current filter.", index_html)
            self.assertIn('class="panel side-panel"', index_html)
            self.assertIn('class="scroll-window"', index_html)
            self.assertIn('class="panel details-panel"', index_html)
            self.assertIn("Task Input", index_html)
            self.assertIn("theme", index_html)
            self.assertIn("theme_set", index_html)
            self.assertIn("refs", index_html)
            self.assertIn("mode", index_html)
            self.assertIn("layout", index_html)
            self.assertIn("reference", index_html)
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


if __name__ == "__main__":
    unittest.main()
