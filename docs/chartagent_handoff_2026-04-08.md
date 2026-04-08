# ChartAgent Handoff

Note:

- 이 문서는 split 직전 monorepo 기준 handoff snapshot이다.
- 현재 독립 repo 상태는 [chartagent_repo_split_status_2026-04-08.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_repo_split_status_2026-04-08.md)를 본다.

Date: 2026-04-08
Repo: `/Users/jleavens_macmini/Projects/auto_kairos_codex`

## 현재 상태 요약

`ChartAgent`는 이미 단순 아이디어 단계가 아니라,

- `chart_task -> chart_spec -> SVG render`
- `theme_set`
- dashboard review
- theme gallery

까지 올라와 있다.

현재 핵심 방향은:

1. `ChartAgent`는 독립 specialist로 유지
2. `theme_set + theme_overrides + theme_reset`를 사용자 surface로 제공
3. 내부적으로는 기존 4층 스타일 시스템을 계속 사용
   - `theme`
   - `reference_profile`
   - `style_combo_preset`
   - `pattern_format_preset`
4. `THEME.md` 문서층을 추가해서 에이전트가 theme의 design language를 읽을 수 있게 함

## 핵심 코드 경로

### Core
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/contracts/chart_task.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/runners/chartagent_runner.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/renderers/svg_renderer.py`

### Design / theme
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/theme_sets.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/style_resolver.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/reference_profiles.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/style_combos.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/pattern_formats.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/design_md_reference_pack.json`

### Dashboard
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/runners/dashboard_runner.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/index.html`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/theme_gallery.html`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/dashboard_manifest.json`

### Tests
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/tests/test_chartagent_runner.py`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/tests/test_chartagent_dashboard.py`

## 현재 지원 family

문서와 구현 기준으로 이미 들어가 있거나 다뤄지는 family:

- `bar`
- `bar_horizontal`
- `line`
- `annotated_chart`
- `donut`
- `pie`
- `metric_wall`
- `single_stat`
- `percentage_progress`
- `stacked_progress`
- `radial_gauge`
- `distribution_histogram`
- `stock_candlestick`
- `comparison_table`
- `fact_table`
- `timeline_table`

## Theme set 구조

사용자 surface:
- `theme_set`
- `theme_overrides`
- `theme_reset`

내부 구현:
- 기존 4층 시스템을 해석해서 실제 token으로 내림

스키마/설명 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_schema.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_taxonomy.md`

reset 원칙:
- 항상 `theme_set` 원본 토큰 기준으로 재계산
- override 결과를 새 기본값으로 삼지 않음

## 현재 theme set

기본/활성:
- `neutral_white`
- `editorial_outline`
- `broadcast_signal`
- `dashboard_analytical`
- `gallery_infographic`
- `market_technical`
- `poster_editorial`

확장 후보 taxonomy 문서에 정리됨:
- `premium_dark`
- `terminal_mono`
- `ai_gradient_signal`
- `enterprise_carbony`
- `friendly_productive`
- `social_bold`
- `institutional_finance`
- `neo_broadcast_dark`

taxonomy 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_taxonomy.md`

## THEME.md 문서층

실제 작성된 테마 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/neutral_white.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/editorial_outline.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/broadcast_signal.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/dashboard_analytical.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/market_technical.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/poster_editorial.THEME.md`

템플릿 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_md_template.md`

의도:
- 코드 토큰과 별개로
- 에이전트가 읽는 design language 계약층 제공

## 레퍼런스 벤치마크

### awesome-design-md

참고 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/awesome_design_md_reference_pack.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/auto_kairos_codex/chartagent/design/design_md_reference_pack.json`

활용 원칙:
- 직접 복제 금지
- benchmark seed로만 사용
- theme_set / surface grammar / spacing / typography logic 추상화

### Pinterest

참고 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/pinterest_reference_analysis_2026-04-07.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/pinterest_composition_preset_seeds.md`

현재 직접 반영된 것:
- `poster_editorial` theme set

중요:
- Pinterest 영향은 아직 대부분 `ChartAgent theme` 쪽이 강함
- `Auto Kairos CreativeScene`까지 픽셀 레벨로 강하게 번역된 건 아직 아님

## Dashboard / Gallery 상태

대시보드:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/index.html`

테마 갤러리:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/theme_gallery.html`

특징:
- theme별로 한 섹션에 여러 chart family를 묶어 보여줌
- `Open THEME.md` 링크가 붙어 있음
- `theme_set`에 따른 artwork signature를 카드에서 확인 가능

현재 갤러리에서 확인하기 좋은 구성:
- `bar_horizontal`
- `line`
- `donut`
- `comparison_table`

## 최근 합의

### 1. ChartAgent는 CompositionAgent가 아니다

- `ChartAgent`는 데이터 specialist
- 차트/표 family 선택
- dataset 정리
- annotation/source 처리

`CompositionCore`는 별도 공통 계약으로 보고,
나중에 필요하면 그 위에 `CompositionAgent`를 얹는 구조가 맞다.

관련 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/composition_3_layer_architecture.md`

### 2. theme_set이 사용자 surface

사용자는
- `theme_set`
- `theme_overrides`
- `theme_reset`

만 직접 다루고,
내부 4층 스타일 시스템은 감춰둔다.

### 3. 복제보다 benchmark

외부 디자인은 copy source가 아니라 benchmark source로 사용한다.

관련 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/reference_benchmark_production_policy.md`

## 현재 품질 상태

좋은 점:
- 테마셋 구조는 꽤 잘 잡혔다
- `broadcast_signal`, `dashboard_analytical`, `poster_editorial`은 시각 차이가 실제로 보인다
- `THEME.md`와 gallery가 연결되어 있어서 에이전트/사람 둘 다 읽기 좋다

아직 약한 점:
- 모든 family에서 theme 차이가 충분히 강하지는 않다
- `bar_horizontal` 쪽은 비교가 잘 보이지만
  - `metric_wall`
  - `single_stat`
  - `table`
  쪽은 더 밀어야 한다
- override/reset은 schema는 있지만 dashboard에서 직접 조작하는 UI는 아직 약하다

## 바로 다음에 하면 좋은 일

### 1. Dashboard에 override/reset UI 붙이기

목표:
- theme 선택 후
  - `accent_color`
  - `stroke_width`
  - `corner_radius`
  - `pattern_density`
  - `label_scale`
  정도를 바꾸고
- `reset_key / reset_group / reset_all`을 바로 확인 가능하게 만들기

관련 문서:
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_schema.md`

### 2. theme 차이를 더 강하게 만드는 family 확장

우선순위:
- `metric_wall`
- `single_stat`
- `fact_table`

이유:
- theme별 차이가 표면 언어에서 더 강하게 드러남

### 3. THEME.md를 더 채우기

우선 후보:
- `gallery_infographic.THEME.md`
- 이후
  - `premium_dark`
  - `institutional_finance`
  - `terminal_mono`

### 4. theme set provenance 메타데이터 강화

현재도 source refs는 문서에 있지만,
추가로 실제 output `style_spec`에도 더 분명히 남기면 좋음:
- `theme_set`
- `theme_set_label`
- `theme_set_description`
- `theme_artwork_signature`
- `source_refs`

## 검증 명령

기본 테스트:

```bash
cd /Users/jleavens_macmini/Projects/auto_kairos_codex
python3.12 -m unittest \
  tests.test_chartagent_runner \
  tests.test_chartagent_dashboard
```

최근 기준:
- `35개` 통과

## 바로 열어볼 파일

1. 갤러리 HTML
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/examples/chartagent_dashboard/theme_gallery.html`

2. 대표 theme 문서
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/poster_editorial.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/broadcast_signal.THEME.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_themes/dashboard_analytical.THEME.md`

3. schema / taxonomy
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_schema.md`
- `/Users/jleavens_macmini/Projects/auto_kairos_codex/docs/chartagent_theme_set_taxonomy.md`

## 한 줄 판단

`ChartAgent`는 지금

- 차트를 그리는 엔진
- theme set 기반 디자인 시스템
- benchmark 기반 테마 확장 구조

까지는 잘 올라왔고,

다음 단계는

- override/reset UX
- family별 theme 차이 강화
- `THEME.md`/gallery/source refs를 더 촘촘히 연결하는 것

이다.
