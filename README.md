# ChartAgent

`ChartAgent` is a specialist package for:

- `chart_task -> chart_spec`
- dataset normalization and display simplification
- theme-set based static SVG rendering
- dashboard and theme gallery generation

It was split out of `auto_kairos_codex` so other projects can consume it without taking the full video pipeline.

## Current Scope

`ChartAgent` owns:

- chart and table family selection
- dataset normalization
- style resolution
- static SVG rendering
- dashboard review artifacts

`ChartAgent` does not own:

- `scene_specs.json`
- composition orchestration
- font resolution
- image orchestration
- Remotion rendering

## Install

```bash
cd /Users/jleavens_macmini/Projects/chartagent
python3.12 -m pip install -e .
```

## Commands

Run a task:

```bash
chartagent run --task ./examples/smoke/chart_task.json --out-dir ./tmp/chart_run
```

Build the review dashboard:

```bash
chartagent dashboard --out-dir ./examples/chartagent_dashboard
```

Current verified outputs:

- dashboard: [examples/chartagent_dashboard/index.html](/Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard/index.html)
- theme gallery: [examples/chartagent_dashboard/theme_gallery.html](/Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard/theme_gallery.html)
- smoke output: [tmp/smoke/render.svg](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/render.svg)

## Tests

```bash
cd /Users/jleavens_macmini/Projects/chartagent
PYTHONPATH=src python3.12 -m unittest \
  tests.test_chartagent_runner \
  tests.test_chartagent_dashboard
```

## Key Directories

- `src/chartagent/`
- `tests/`
- `docs/`
- `examples/chartagent_dashboard/`

See also:

- [docs/chartagent_repo_split_status_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_split_status_2026-04-08.md)
