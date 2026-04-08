# ChartAgent Repo Target Tree

Updated: 2026-04-08

Repo goal:

- `ChartAgent`를 `auto_kairos_codex` 밖으로 분리했을 때의 권장 디렉터리 구조

Related:

- [chartagent_repo_separation_checklist.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_separation_checklist.md)
- [chartagent_repo_split_status_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_split_status_2026-04-08.md)
- [chartagent_handoff_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_handoff_2026-04-08.md)

## Target Repository Shape

```text
chartagent/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── chartagent/
│       ├── __init__.py
│       ├── contracts/
│       │   ├── __init__.py
│       │   ├── chart_task.py
│       │   └── dataset_schema.py
│       ├── design/
│       │   ├── __init__.py
│       │   ├── themes.py
│       │   ├── theme_sets.py
│       │   ├── reference_profiles.py
│       │   ├── style_combos.py
│       │   ├── pattern_formats.py
│       │   ├── style_resolver.py
│       │   └── design_md_reference_pack.json
│       ├── normalizers/
│       │   ├── __init__.py
│       │   └── display_simplifier.py
│       ├── qa/
│       │   ├── __init__.py
│       │   ├── chart_quality.py
│       │   └── design_quality.py
│       ├── renderers/
│       │   ├── __init__.py
│       │   └── svg_renderer.py
│       ├── runners/
│       │   ├── __init__.py
│       │   ├── chartagent_runner.py
│       │   └── dashboard_runner.py
│       ├── selectors/
│       │   ├── __init__.py
│       │   └── chart_family_selector.py
│       └── cli.py
├── tests/
│   ├── test_chartagent_runner.py
│   └── test_chartagent_dashboard.py
├── docs/
│   ├── chartagent_theme_set_schema.md
│   ├── chartagent_theme_set_taxonomy.md
│   ├── chartagent_theme_md_template.md
│   ├── chartagent_themes/
│   │   ├── neutral_white.THEME.md
│   │   ├── editorial_outline.THEME.md
│   │   ├── broadcast_signal.THEME.md
│   │   ├── dashboard_analytical.THEME.md
│   │   ├── market_technical.THEME.md
│   │   └── poster_editorial.THEME.md
│   └── architecture/
│       ├── repo_separation_checklist.md
│       └── contracts_map.md
├── examples/
│   └── chartagent_dashboard/
│       ├── index.html
│       ├── theme_gallery.html
│       ├── dashboard_manifest.json
│       ├── cases/
│       └── theme_gallery_cases/
└── scripts/
    ├── build_dashboard.sh
    └── run_smoke.sh
```

## Package Layout Notes

### `src/chartagent/`

독립 package root다.

여기서 중요한 원칙:

- 더 이상 `auto_kairos_codex` namespace를 쓰지 않는다
- 외부 consumer는 `chartagent.*`만 import한다

### `contracts/`

여기는 분리 후 가장 중요한 폴더다.

최소 소유 계약:

- `chart_task`
- normalized dataset

나중에 추가 가능:

- `chart_result`
- `style_spec`

단, 지금은 기존 코드와 호환되게 incremental하게 가는 것이 맞다.

### `design/`

`ChartAgent`의 경쟁력 핵심이다.

포함해야 하는 것:

- base theme tokens
- `theme_set`
- `reference_profile`
- `style_combo_preset`
- `pattern_format_preset`
- benchmark reference pack

즉 이 폴더는 renderer helper가 아니라
`ChartAgent design system` 그 자체다.

### `renderers/`

초기 분리에서는 `svg_renderer.py`만 가져가면 충분하다.

나중에 확장 가능:

- `png_renderer.py`
- `html_renderer.py`
- `remotion_adapter.py`

하지만 `Remotion`은 core와 분리된 adapter여야 한다.

### `runners/`

여기는 consumer가 실제로 쓰는 high-level entry다.

최소:

- `chartagent_runner.py`
- `dashboard_runner.py`

권장 방향:

- runner는 artifact in/out 중심
- internal implementation detail을 숨기는 facade

### `cli.py`

분리 후 CLI는 repo root command entry가 된다.

권장 subcommands:

- `run`
- `dashboard`
- `validate`
- `gallery`

## Test Layout Notes

초기에는 아래 둘만 있어도 충분하다.

- `test_chartagent_runner.py`
- `test_chartagent_dashboard.py`

이후 추가 권장:

- `test_chartagent_contracts.py`
- `test_chartagent_theme_sets.py`
- `test_chartagent_svg_snapshots.py`

## Docs Layout Notes

`ChartAgent`는 코드만 옮기면 끝나는 타입이 아니다.

꼭 같이 가야 하는 docs:

- theme schema
- taxonomy
- THEME docs
- repo separation / contracts map

즉 docs는 optional 부속물이 아니라
실제 design language contract의 일부다.

## Example Layout Notes

예제는 한 개만 남기지 말고 두 층으로 나누는 게 좋다.

### 1. `examples/chartagent_dashboard/`

실제 review surface

### 2. `examples/smoke/`

작은 JSON task와 output만 담는 smoke examples

초기에는 dashboard 하나만 가져가도 되지만,
장기적으로는 smoke examples도 있으면 외부 consumer 테스트가 쉬워진다.

## What Should Stay Out Of The Repo

초기 split에서는 아래를 넣지 않는 편이 낫다.

- `scene_specs` orchestration logic
- `research_report` pipeline logic
- Remotion production modules
- TTS / subtitle assembly
- image provider integrations
- monorepo-level workspace orchestration

즉 `ChartAgent repo`는:

- chart specialist package
- docs
- tests
- examples

까지만 책임진다.

## Historical Path Mapping

원래 monorepo 경로와 현재 split repo 경로는 대략 이렇게 대응된다.

### Source

- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/contracts`
  -> `chartagent/src/chartagent/contracts`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design`
  -> `chartagent/src/chartagent/design`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/normalizers`
  -> `chartagent/src/chartagent/normalizers`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/qa`
  -> `chartagent/src/chartagent/qa`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/renderers`
  -> `chartagent/src/chartagent/renderers`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/runners`
  -> `chartagent/src/chartagent/runners`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/selectors`
  -> `chartagent/src/chartagent/selectors`

### Tests

- `/Users/jleavens_macmini/Projects/auto_kairos_codex/tests/test_chartagent_runner.py`
  -> `chartagent/tests/test_chartagent_runner.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/tests/test_chartagent_dashboard.py`
  -> `chartagent/tests/test_chartagent_dashboard.py`

### Docs

- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_schema.md`
  -> `chartagent/docs/chartagent_theme_set_schema.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_taxonomy.md`
  -> `chartagent/docs/chartagent_theme_set_taxonomy.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/*`
  -> `chartagent/docs/chartagent_themes/*`

### Examples

- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard`
  -> `chartagent/examples/chartagent_dashboard`

## Recommended First Split Milestone

첫 milestone은 이 정도면 충분하다.

- 새 repo에 package tree 생성
- source code 이동
- imports rewrite
- two core tests green
- dashboard generation green
- docs/theme docs 이동

여기까지 되면,
consumer adapter가 아직 없어도 “독립 specialist repo”로는 충분히 성립한다.

## One-Line Judgment

목표 트리는 복잡하지 않다.

핵심은:

- `src/chartagent`
- `tests`
- `docs`
- `examples`

이 네 축을 self-contained 하게 만드는 것이다.
