# Composition 3-Layer Architecture

Updated: 2026-04-07

See also:

- [auto_kairos_codex_handoff_2026-04-07.md](/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/auto_kairos_codex_handoff_2026-04-07.md)
- [chartagent_plan.md](/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_plan.md)
- [scene_specs_contract.md](/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/scene_specs_contract.md)
- [reference_benchmark_production_policy.md](/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/reference_benchmark_production_policy.md)

## 목적

이 문서는 `ChartAgent / CompositionCore / CompositionAgent` 3층 구조를 정의한다.

핵심 목표는 두 가지다.

- `DesignAgent` 실패를 반복하지 않는다.
- 앞으로 `ChartAgent`, `ImageSearchAgent`, `ImageGenAgent`, `SlideAgent`, `FontAgent` 같은 specialist들이 서로 협업할 수 있게 한다.

## 왜 `DesignAgent`는 실패에 가까웠는가

문제는 감각이 아니라 구조였다.

### 1. 두 번째 semantic contract가 생겼다

`scene_specs.json` 외부에서 다시:

- 장면 의미
- layout 의미
- text 의미
- communication goal

을 만들기 시작했다.

그 결과:

- provenance가 흐려졌고
- 어떤 판단이 어디서 왔는지 추적이 어려워졌고
- override가 누적되었다.

### 2. planner와 renderer가 같은 언어를 쓰지 못했다

상위 단계는 의미를 말하고 있었는데,
하위 단계는 다시 layout preset 언어로 덮었다.

이로 인해:

- scene contract는 얇아졌지만
- renderer에서 다시 장면 의미를 재구성하는 문제가 생겼다.

### 3. specialist가 아니라 vague generalist가 되었다

`DesignAgent`는:

- 차트 전문가도 아니고
- 이미지 전문가도 아니고
- 타이포 전문가도 아니고
- 캔버스 orchestration 전문가도 아니었다.

결과적으로 모든 걸 조금씩 하다가
어느 한 축도 충분히 깊어지지 못했다.

### 4. 실험 경로가 기본 생산 경로를 오염시켰다

실험적인 layout override가
production path까지 들어오면서
기본 파이프라인의 안정성이 떨어졌다.

## 핵심 원칙

### 1. semantic source는 여전히 `scene_specs.json` 하나다

`Auto Kairos` production path에서는:

- 의미는 `scene_specs.json`
- 파생물은 `design_spec.fontagent.json`, `remotion_manifest.json`, `assembly_report.json`

이다.

다른 에이전트가 붙더라도
새 semantic source를 만들면 안 된다.

### 2. specialist는 좁고 깊어야 한다

에이전트는 “모든 걸 다 설계하는 큰 두뇌”가 아니라,
좁은 문제를 매우 잘 푸는 specialist여야 한다.

### 3. composition은 공통 엔진이어야지, 처음부터 큰 에이전트가 되면 안 된다

캔버스 공간 문법은 필요하다.
하지만 그걸 바로 `CompositionAgent`로 만들면 다시 `DesignAgent`처럼 부풀 위험이 있다.

그래서 먼저:

- `CompositionCore`

를 만들고,
나중에 정말 필요할 때만:

- `CompositionAgent`

를 올린다.

## 3층 구조

### Layer 1. Specialist Agents

좁은 도메인 문제를 푸는 레이어다.

예:

- `ChartAgent`
- `FontAgent`
- `ImageSearchAgent`
- `ImageGenAgent`
- `SlideAgent`

#### 역할

- 자신의 도메인에서 가장 적합한 artifact를 만든다.
- semantics를 다시 만들지 않는다.
- 입력이 충분하지 않으면 필요한 결손을 명확히 드러낸다.

#### 예시

`ChartAgent`

- 입력: 질문, 데이터, 제약, theme
- 출력: `chart_spec`, dataset, SVG/PNG, source note

`FontAgent`

- 입력: 텍스트 역할, 언어, 분위기, 사용맥락
- 출력: font roles, fallback, sizing guidance

`ImageSearchAgent`

- 입력: 이미지 의도, factual constraints, style constraints
- 출력: candidate assets, metadata, source/license note

### Layer 2. CompositionCore

이 레이어는 에이전트가 아니다.
공통 계약과 계산 로직이다.

#### 목적

서로 다른 specialist output을
동일한 canvas language로 번역한다.

#### 책임

- canvas grammar
- visual mass distribution
- reading flow
- negative space allocation
- text/item zoning
- image reserve and treatment
- group and depth grammar

#### 이 레이어가 가져야 할 것

- deterministic rules
- token/schema
- preset library
- benchmark-derived defaults

#### 이 레이어가 하면 안 되는 것

- 장면의 새 의미 만들기
- arbitrary override 누적
- 특정 specialist 역할 침범

예:

- `CompositionCore`는 `chart_spec`을 받아
  chart가 화면에서 얼마나 큰 질량을 가져야 하는지 계산할 수 있다.
- 하지만 어떤 chart family가 적절한지 결정하는 건 `ChartAgent`가 한다.

### Layer 3. CompositionAgent

이 레이어는 나중에 필요할 때만 둔다.

#### 목적

여러 specialist를 동시에 조율해야 하는 복합 작업에서,
누가 무엇을 먼저 만들고 어떻게 합칠지 계획하는 상위 orchestration 레이어다.

#### 적합한 상황

- 차트 + 이미지 + 타이포 + 맵 + source rail이 동시에 필요한 장면
- 슬라이드 deck 전체를 일관된 composition grammar로 묶어야 하는 작업
- 하나의 scene/frame에서 여러 specialist output이 충돌하는 상황

#### 부적합한 상황

- 데이터만 보고 차트 하나 그리는 작업
- 단순 이미지 후보 검색
- 단순 font recommendation

즉 `CompositionAgent`는 default가 아니라 advanced orchestration layer다.

## 각 레이어의 입력과 출력

### Specialist Agent

입력:

- own-domain task
- constraints
- reference benchmark

출력:

- own-domain artifact
- notes / assumptions
- composition-relevant metadata

### CompositionCore

입력:

- `scene_specs.json`
- specialist artifacts
- benchmark presets

출력:

- composition tokens
- element zoning
- placement heuristics
- reserve / density / surface grammar

### CompositionAgent

입력:

- scene goal
- available specialist tools
- composition policy

출력:

- collaboration plan
- specialist subtask requests
- merged composition plan

## `Auto Kairos`에 적용하면 어떻게 되나

### 현재 production path

현재 기본 경로는:

- Stage 1
- Stage 2
- Stage 3
- `FontAgent`

이다.

여기서 의미는 `scene_specs.json` 하나다.

### 앞으로 specialist를 붙이는 방법

`scene_specs.json` 안의 `creative_scene`를 보고:

- chart 필요 -> `ChartAgent`
- 지도 필요 -> future `MapAgent` or map renderer
- 이미지 asset 필요 -> `ImageSearchAgent`
- illustration 필요 -> `ImageGenAgent`
- typography role 필요 -> `FontAgent`

를 호출할 수 있다.

하지만 이 호출은 모두:

- `scene_specs.json`
- `creative_scene.kind`
- `creative_scene.payload`

를 출발점으로 해야 한다.

### CompositionCore가 하는 일

specialist output을 받아:

- 어떤 요소가 dominant layer인지
- 어떤 요소가 supporting layer인지
- source rail을 어디에 둘지
- 텍스트를 chip으로 둘지 footnote로 둘지
- 이미지 veil/blur/desaturate를 얼마나 줄지

같은 캔버스 문법을 계산한다.

## 계약 예시

### `scene_specs.json`

semantic source:

- `creative_scene.kind`
- `creative_scene.payload`
- `creative_scene.elements`
- `creative_scene.composition`

### `ChartAgent` output

specialist output:

- `chart_spec.json`
- `dataset.json`
- `render.svg`
- `notes.md`

### `CompositionCore` output

render-prep tokens:

- `element_layout.json`
- `canvas_tokens.json`
- `surface_treatment.json`

### `remotion_manifest.json`

render payload:

- scene media paths
- chart/image asset paths
- subtitles
- composition tokens already flattened for renderer

## 무엇을 어디까지 공통화할 것인가

### 공통화해야 하는 것

- zone vocabulary
- reserve vocabulary
- density vocabulary
- source/caption roles
- image treatment vocabulary
- depth/group grammar

### 공통화하면 안 되는 것

- specialist 의사결정 자체
- semantic meaning
- raw renderer-only hacks

예:

- `source_rail`, `annotation_float`, `center_gutter` 같은 단어는 공통 vocabulary여야 한다.
- 하지만 `bar_horizontal`과 `donut` 중 무엇을 고르는지는 `ChartAgent`가 해야 한다.

## 실패를 반복하지 않기 위한 금지 규칙

### 금지 1. `CompositionAgent`가 두 번째 semantic planner가 되지 않게 한다

`CompositionAgent`가:

- 장면 의미를 다시 정의하거나
- story intent를 바꾸거나
- scene contract를 수정하면

다시 `DesignAgent` 실패를 반복한다.

### 금지 2. override accumulation을 허용하지 않는다

`composition override`
`layout override`
`render override`
가 층층이 쌓이면 실패한다.

변형은:

- benchmark-derived preset
- explicit variant

정도로 제한해야 한다.

### 금지 3. production path를 실험 경로로 오염시키지 않는다

새 specialist나 orchestration은:

- opt-in
- sidecar
- adapter

형태로 붙여야 한다.

기본 production path를 깨면 안 된다.

## 개발 순서

### Phase 1. `ChartAgent`를 specialist로 완성

- chart/table family 판단
- dataset normalization
- theme_set
- source/annotation
- dashboard review

### Phase 2. `CompositionCore` 계약 추출

- zone vocab
- reserve vocab
- image treatment vocab
- text/item canvas grammar

### Phase 3. `Auto Kairos` adapter

- `scene_specs.json` -> specialist task
- specialist output -> composition tokens
- composition tokens -> manifest

### Phase 4. `CompositionAgent`는 필요할 때만 추가

조건:

- specialist가 2개 이상 얽힌 장면이 반복적으로 등장
- composition conflict resolution이 실제 문제로 커짐
- 단순 adapter 수준으로 해결되지 않음

## 현재 권장 결론

지금 당장은:

- `ChartAgent`를 `CompositionAgent`로 키우지 않는다.
- `ChartAgent`는 specialist로 유지한다.
- `CompositionCore`를 먼저 만든다.
- `CompositionAgent`는 나중에 orchestration이 정말 필요할 때 추가한다.

한 줄 요약:

> `DesignAgent`의 실패를 되풀이하지 않으려면, 큰 generalist 하나로 몰지 말고, specialist + shared composition core + optional orchestration으로 가야 한다.
