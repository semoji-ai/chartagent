# ChartAgent Repo Split Status

Updated: 2026-04-08

Repo: `/Users/jleavens_macmini/Projects/chartagent`

Related:

- [chartagent_repo_separation_checklist.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_separation_checklist.md)
- [chartagent_repo_target_tree.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_target_tree.md)
- [chartagent_theme_set_schema.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_set_schema.md)
- [chartagent_theme_set_taxonomy.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_set_taxonomy.md)

## Current Status

`ChartAgent`는 이제 monorepo 내부 서브패키지가 아니라,
독립적으로 실행 가능한 specialist repo scaffold를 가진다.

현재 경로:

- source: `/Users/jleavens_macmini/Projects/chartagent/src/chartagent`
- tests: `/Users/jleavens_macmini/Projects/chartagent/tests`
- docs: `/Users/jleavens_macmini/Projects/chartagent/docs`
- examples: `/Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard`

## What Was Completed

- package tree를 `src/chartagent` 기준으로 이관
- import namespace를 `auto_kairos_codex.chartagent`에서 `chartagent`로 변경
- 독립 `pyproject.toml` 추가
- 독립 CLI 추가
  - `chartagent run`
  - `chartagent dashboard`
- docs/theme docs/examples 이관
- smoke task 추가

## Verification

아래는 새 repo에서 직접 검증했다.

### 1. Unit tests

```bash
cd /Users/jleavens_macmini/Projects/chartagent
PYTHONPATH=src python3.12 -m unittest \
  tests.test_chartagent_runner \
  tests.test_chartagent_dashboard
```

Result:

- `38` tests passed

### 2. Dashboard generation

```bash
cd /Users/jleavens_macmini/Projects/chartagent
PYTHONPATH=src python3.12 -m chartagent.cli dashboard \
  --out-dir /Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard
```

Result summary:

- `case_count`: `33`
- `theme_gallery_case_count`: `147`
- dashboard: [index.html](/Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard/index.html)
- gallery: [theme_gallery.html](/Users/jleavens_macmini/Projects/chartagent/examples/chartagent_dashboard/theme_gallery.html)

### 3. Smoke run

```bash
cd /Users/jleavens_macmini/Projects/chartagent
PYTHONPATH=src python3.12 -m chartagent.cli run \
  --task /Users/jleavens_macmini/Projects/chartagent/examples/smoke/chart_task.json \
  --out-dir /Users/jleavens_macmini/Projects/chartagent/tmp/smoke
```

Generated:

- [chart_task.normalized.json](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/chart_task.normalized.json)
- [dataset.normalized.json](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/dataset.normalized.json)
- [dataset.normalized.csv](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/dataset.normalized.csv)
- [chart_spec.json](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/chart_spec.json)
- [render.svg](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/render.svg)
- [notes.md](/Users/jleavens_macmini/Projects/chartagent/tmp/smoke/notes.md)

## What Is Still Pending

분리는 기술적으로 시작된 상태지만, 아래는 아직 후속 작업이다.

- public API freeze
- contract envelope/versioning 명시
- `auto_kairos_codex` consumer adapter
- Claude project consumer adapter
- package publish policy

즉 현재 상태는:

- `repo split scaffold`: done
- `independent execution`: done
- `consumer contract hardening`: pending

## Practical Judgment

지금 시점의 `ChartAgent`는 이미 별도 프로젝트에서 실험하거나
독립 specialist로 협업시키기에 충분하다.

다만 production-level reuse를 위해서는 다음 순서가 맞다.

1. `public API` 고정
2. artifact `contract_version` 정책 추가
3. consumer adapter를 각 프로젝트에서 별도로 붙이기
