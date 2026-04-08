#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/src"

python3.12 -m chartagent.cli dashboard --out-dir "$ROOT/examples/chartagent_dashboard"
