# ChartAgent Repo Separation Checklist

Updated: 2026-04-08

Repo: `/Users/jleavens_macmini/Projects/chartagent`

Related:

- [chartagent_repo_split_status_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_split_status_2026-04-08.md)
- [chartagent_handoff_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_handoff_2026-04-08.md)
- [chartagent_theme_set_schema.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_set_schema.md)
- [chartagent_theme_set_taxonomy.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_set_taxonomy.md)
- [composition_3_layer_architecture.md](/Users/jleavens_macmini/Projects/chartagent/docs/composition_3_layer_architecture.md)

## Goal

`ChartAgent`를 `auto_kairos_codex` 내부 서브패키지에서,
다른 프로젝트가 재사용 가능한 독립 git repo로 분리할 때 필요한 체크리스트를 정리한다.

이 문서는 아직:

- Claude project adapter
- `auto_kairos_codex` consumer adapter
- package publish policy

까지 확정하지 않는다.

우선은 분리 가능한 경계와 준비 순서만 고정한다.

## Current State

현재 독립 repo의 `ChartAgent` source는 아래 경로에 있다.

- `/Users/jleavens_macmini/Projects/chartagent/src/chartagent`

실질적 외부 결합점은 적다.

- package CLI
- tests
- docs / examples

즉 내부 구현은 거의 자기완결적이고,
분리의 핵심 리스크는 코드 이동보다:

- import namespace 변경
- public API 고정
- contract versioning
- docs/examples/tests 이관

에 있다.

현재 split 진행 상태:

- new repo scaffold 완료
- package import namespace를 `chartagent.*`로 전환 완료
- 독립 CLI 추가 완료
- 테스트 38개 green
- dashboard generation green
- smoke run green
- contract versioning과 consumer adapter는 후속 단계

## Non-Goals

이번 분리 준비 단계에서 하지 않는 것:

- 새로운 semantic source 추가
- `ChartAgent`가 `scene_specs.json` ownership을 가지게 만드는 것
- `FontAgent`, `ResearchAgent`, `WriteAgent`와 직접 코드 결합
- Remotion adapter 포함

## Separation Principle

분리 후에도 `ChartAgent`는 여전히 specialist여야 한다.

- 입력: `chart_task`
- 출력: `chart_spec`, normalized dataset, static render, notes
- 책임: 차트/표 family 선택, dataset normalization, style resolution, static rendering
- 비책임: scene semantics 생성, font choice, image orchestration, final composition

## Checklist

### 1. Package Boundary Freeze

- `ChartAgent` source root를 독립 package root로 고정한다.
- 새 import namespace를 결정한다.
  - 권장: `chartagent.*`
- monorepo 내부 import인 `auto_kairos_codex.chartagent.*`를 점진적으로 제거할 계획을 세운다.

Done when:

- 외부 consumer가 `chartagent` package만 import해도 runner가 동작한다.

### 2. Public API Freeze

분리 전 public surface를 먼저 확정한다.

권장 최소 surface:

- `build_chart_artifacts(task: dict) -> ChartArtifactsResult`
- `write_chart_outputs(task: dict, out_dir: Path) -> dict`
- `write_chartagent_dashboard(out_dir: Path, sample_tasks: list | None = None) -> dict`

분리 전 반드시 결정할 것:

- 어떤 함수가 supported API인지
- 어떤 모듈이 internal-only인지
- 어떤 결과 객체가 stable contract인지

Done when:

- consumer가 내부 renderer/selectors에 직접 의존하지 않아도 된다.

### 3. Contract Versioning

아래 artifact는 분리 전에 버전 정책을 가져야 한다.

- `chart_task`
- `dataset.normalized`
- `chart_spec`
- `style_spec`
- dashboard manifest

최소 공통 필드:

- `contract_name`
- `contract_version`
- `producer`
- `created_at`
- `status`
- `warnings`
- `provenance`

Done when:

- 다른 프로젝트가 repo 버전이 아니라 artifact version을 기준으로 호환성을 판단할 수 있다.

### 4. CLI Decoupling

현재 CLI entry는 `auto_kairos_codex.cli`에 묶여 있다.

분리 후 최소 CLI:

- `chartagent run --task ... --out-dir ...`
- `chartagent dashboard --out-dir ...`

가능하면 나중에 추가:

- `chartagent validate --task ...`
- `chartagent gallery --out-dir ...`

Done when:

- 독립 repo만 checkout해도 chart task 실행과 dashboard 생성이 가능하다.

### 5. Package Metadata

독립 repo에 필요한 기본 메타데이터:

- own `pyproject.toml`
- package name
- python version floor
- runtime dependencies
- optional dev dependencies
- scripts / entry points

권장 초기 runtime dependency는 최소화한다.

현재 `ChartAgent` 관점에서 사실상 필요한 건:

- python stdlib 중심
- 필요하면 `pydantic`만 선택적 도입

Done when:

- package install이 `auto_kairos_codex` 전체 dependency 없이 가능하다.

### 6. Docs Migration

함께 이동해야 할 문서층:

- `chartagent_theme_set_schema.md`
- `chartagent_theme_set_taxonomy.md`
- `chartagent_themes/*.THEME.md`
- 필요 시 `chartagent_theme_md_template.md`

이유:

- `ChartAgent`의 차별점은 단순 renderer가 아니라
  `theme_set + THEME.md + gallery` 구조이기 때문

Done when:

- 새 repo만 봐도 theme language와 contract를 이해할 수 있다.

### 7. Test Migration

함께 이동해야 할 테스트:

- `tests/test_chartagent_runner.py`
- `tests/test_chartagent_dashboard.py`

추가 권장:

- contract snapshot tests
- theme-set regression tests
- render smoke tests

Done when:

- 새 repo CI에서 ChartAgent 테스트가 독립적으로 돈다.

### 8. Example Migration

함께 이동해야 할 예제:

- `examples/chartagent_dashboard/`

권장:

- gallery output은 committed sample로 둘지, generated artifact로 둘지 정책 결정
- 최소 representative sample은 repo에 남긴다

Done when:

- 외부 consumer가 package install 없이도 결과물을 빠르게 확인할 수 있다.

### 9. Import Rewrite Plan

현재 내부 import는 대부분:

- `from auto_kairos_codex.chartagent...`

형태다.

분리 시 해야 할 일:

- package root를 `src/chartagent/`로 옮기기
- 내부 import를 `chartagent...` 기준으로 rewrite

Done when:

- package import가 monorepo root name에 의존하지 않는다.

### 10. Release Readiness Gate

아래가 모두 충족되기 전에는 repo split을 “완료”로 보지 않는다.

- tests green
- CLI green
- dashboard generation green
- docs moved
- public API frozen
- artifact contracts versioned

현재 상태:

- tests green: yes
- CLI green: yes
- dashboard generation green: yes
- docs moved: mostly yes
- public API frozen: partial
- artifact contracts versioned: pending

## Recommended Split Order

### Phase 1. Monorepo Freeze

- public API 정리
- contract version field 추가
- docs/checklist 확정

### Phase 2. New Repo Scaffold

- new repo 생성
- `src/chartagent` 구조 생성
- `pyproject.toml` 작성

### Phase 3. Code Lift

- package code 이동
- import rewrite
- tests 이동
- examples 이동

### Phase 4. Verification

- runner test
- dashboard test
- CLI smoke
- gallery generation

### Phase 5. Consumer Re-attachment

- `auto_kairos_codex`는 consumer로 붙임
- Claude project도 consumer로 붙임
- adapter는 이 단계에서 별도 작업

현재 판단:

- Phase 1-4는 실질적으로 완료
- 지금 남은 핵심은 Phase 5를 서두르는 것이 아니라
  public API와 contract version policy를 먼저 고정하는 것이다

## Immediate Questions To Resolve Before Actual Split

### 1. Package name

후보:

- `chartagent`
- `auto-kairos-chartagent`

권장:

- repo name은 `chartagent`
- package name도 가능하면 `chartagent`

### 2. Artifact ownership

분리 후에도 `ChartAgent`는 아래만 소유한다.

- `chart_task`
- `chart_spec`
- normalized dataset
- static render
- notes

소유하지 않는 것:

- `scene_specs.json`
- `design_spec.json`
- `typography_spec.json`
- `remotion_manifest.json`

### 3. Theme docs location

권장:

- theme docs는 package 안이 아니라 repo `docs/` 아래에 유지
- gallery는 docs/examples와 연결

## Minimum Acceptance For “Ready To Split”

아래가 되면 실제 repo 분리를 진행해도 된다.

- `ChartAgent` package 내부가 monorepo 명에 의미적으로 묶여 있지 않다
- import surface가 안정적이다
- contract version policy가 있다
- docs / tests / examples가 독립 repo에서 self-contained 하다
- `auto_kairos_codex` 외 다른 consumer가 붙어도 개념적으로 무리가 없다

## One-Line Judgment

현재 `ChartAgent`는 아직 monorepo 안에 있지만,
구조적으로는 이미 “분리 준비 단계 후반”에 와 있다.

실제 분리의 핵심은 코드 이동이 아니라:

- public API freeze
- contract versioning
- docs/tests/examples self-containment

이다.
