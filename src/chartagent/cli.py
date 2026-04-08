from __future__ import annotations

import argparse
import json
from pathlib import Path

from chartagent.runners.chartagent_runner import write_chart_outputs
from chartagent.runners.dashboard_runner import write_chartagent_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chartagent", description="ChartAgent specialist CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Normalize a chart_task JSON and write chart artifacts",
    )
    run_parser.add_argument("--task", required=True, help="Path to chart_task.json")
    run_parser.add_argument("--out-dir", required=True, help="Output directory for chart artifacts")

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Generate the static ChartAgent dashboard and theme gallery",
    )
    dashboard_parser.add_argument("--out-dir", required=True, help="Output directory for dashboard artifacts")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        outputs = write_chart_outputs(
            chart_task_path=Path(args.task).expanduser().resolve(),
            output_dir=Path(args.out_dir).expanduser().resolve(),
        )
        print(json.dumps(outputs, ensure_ascii=False, indent=2))
        return

    if args.command == "dashboard":
        outputs = write_chartagent_dashboard(
            output_dir=Path(args.out_dir).expanduser().resolve(),
        )
        print(json.dumps(outputs, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
