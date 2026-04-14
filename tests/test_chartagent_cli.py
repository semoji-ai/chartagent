from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from chartagent import cli


class ChartAgentCliTests(unittest.TestCase):
    def test_run_command_writes_expected_artifacts(self) -> None:
        task_path = Path(__file__).resolve().parent.parent / "examples" / "smoke" / "chart_task.json"
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "run-output"
            stdout = io.StringIO()
            argv = sys.argv[:]
            try:
                sys.argv = [
                    "chartagent",
                    "run",
                    "--task",
                    str(task_path),
                    "--out-dir",
                    str(out_dir),
                ]
                with redirect_stdout(stdout):
                    cli.main()
            finally:
                sys.argv = argv

            payload = json.loads(stdout.getvalue())
            self.assertTrue((out_dir / "chart_task.normalized.json").exists())
            self.assertTrue((out_dir / "dataset.normalized.json").exists())
            self.assertTrue((out_dir / "dataset.normalized.csv").exists())
            self.assertTrue((out_dir / "chart_spec.json").exists())
            self.assertTrue((out_dir / "notes.md").exists())
            self.assertTrue((out_dir / "render.svg").exists())
            self.assertEqual(Path(payload["chart_spec"]).resolve(), (out_dir / "chart_spec.json").resolve())
            self.assertEqual(Path(payload["render_svg"]).resolve(), (out_dir / "render.svg").resolve())

    def test_dashboard_command_writes_dashboard_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "dashboard-output"
            stdout = io.StringIO()
            argv = sys.argv[:]
            try:
                sys.argv = [
                    "chartagent",
                    "dashboard",
                    "--out-dir",
                    str(out_dir),
                ]
                with redirect_stdout(stdout):
                    cli.main()
            finally:
                sys.argv = argv

            payload = json.loads(stdout.getvalue())
            self.assertTrue((out_dir / "index.html").exists())
            self.assertTrue((out_dir / "theme_gallery.html").exists())
            self.assertTrue((out_dir / "dashboard_manifest.json").exists())
            self.assertEqual(Path(payload["dashboard"]).resolve(), (out_dir / "index.html").resolve())
            self.assertEqual(Path(payload["theme_gallery"]).resolve(), (out_dir / "theme_gallery.html").resolve())


if __name__ == "__main__":
    unittest.main()
