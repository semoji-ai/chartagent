#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/src"

python3.12 -m chartagent.cli run --task "$ROOT/examples/smoke/chart_task.json" --out-dir "$ROOT/tmp/smoke"
