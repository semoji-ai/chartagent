# ChartAgent Theme Set Taxonomy

Updated: 2026-04-07

Related:

- [awesome_design_md_reference_pack.md](/Users/jleavens_macmini/Projects/chartagent/docs/awesome_design_md_reference_pack.md)
- [chartagent_theme_set_schema.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_set_schema.md)
- [chartagent_theme_md_template.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_theme_md_template.md)
- Actual theme docs:
  - [neutral_white.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/neutral_white.THEME.md)
  - [editorial_outline.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/editorial_outline.THEME.md)
  - [broadcast_signal.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/broadcast_signal.THEME.md)
  - [dashboard_analytical.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/dashboard_analytical.THEME.md)
  - [poster_editorial.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/poster_editorial.THEME.md)
  - [market_technical.THEME.md](/Users/jleavens_macmini/Projects/chartagent/docs/chartagent_themes/market_technical.THEME.md)

## Goal

`theme_set`을 감각적인 이름 모음이 아니라, 재사용 가능한 taxonomy로 고정한다.

각 `theme_set`는 아래를 가진다.

- design intent
- source references
- visual signature
- recommended chart families
- weak-fit families

## 1. Base theme sets

| Theme set | Intent | Source refs | Signature |
|---|---|---|---|
| `neutral_white` | 가장 조용하고 범용적인 light chart | `vercel`, `apple`, `notion` | white canvas, thin border, minimal accent |
| `editorial_outline` | 설명형, 종이감, 읽기 좋은 chart/table | `notion`, `claude` | warm paper surface, restrained outline |
| `broadcast_signal` | 강한 대비와 신호형 강조가 필요한 영상/방송 스타일 | `clickhouse`, `vercel` | dark panel, sharp accent, rail-like metadata |
| `dashboard_analytical` | 패널형 분석, 기관형 숫자 전달 | `coinbase`, `clickhouse` | cool/neutral panels, strong axis clarity |
| `gallery_infographic` | 따뜻하고 이미지 친화적인 인포그래픽 | `pinterest`, `claude` | warm surface, rounded geometry, friendlier pattern |
| `poster_editorial` | 포스터/매거진 spread 감각의 type-led 차트 | `pinterest`, `notion`, `claude` | type-led hierarchy, warm poster field, editorial contrast |
| `market_technical` | 정밀하고 밀도 높은 기술/시장형 chart | `clickhouse`, `coinbase`, `vercel` | dense guides, compact labels, low ornament |

## 2. Expansion theme sets

| Theme set | Intent | Source refs | Signature |
|---|---|---|---|
| `premium_dark` | 제품/숫자를 떠오르게 하는 고급 dark surface | `apple`, `ferrari`, `lamborghini` | cinematic black, precise highlight |
| `terminal_mono` | 터미널/개발자/분석 콘솔형 | `ollama`, `opencode.ai` | mono-first, grid-heavy, minimal color |
| `ai_gradient_signal` | 생성형 AI/launch 스타일의 미래형 표현 | `cohere`, `minimax`, `runwayml` | gradient accent, luminous panels |
| `enterprise_carbony` | 구조적이고 보수적인 B2B 설계 | `ibm`, `hashicorp` | modular structure, disciplined contrast |
| `friendly_productive` | 교육/설명/업무생산성형 시각 톤 | `notion`, `intercom`, `webflow` | soft hierarchy, calm UI rhythm |
| `social_bold` | 존재감 큰 브랜드/카드형 시각 시스템 | `pinterest`, `spotify`, `airbnb` | warm/accented color blocks, bolder cards |
| `institutional_finance` | 금융/리포트형 신뢰 전달 | `coinbase`, `wise`, `revolut` | blue/neutral trust palette, stable tables |
| `neo_broadcast_dark` | 방송형이지만 더 현대적이고 인터랙티브한 dark system | `vercel`, `clickhouse`, broadcast seeds | signal chips, source rail, dense info panel |

## 3. Chart family fit matrix

Legend:

- `strong`
- `good`
- `okay`
- `weak`

| Theme set | bar | line | donut/pie | comparison_table | fact_table | metric_wall | single_stat | candlestick/histogram |
|---|---|---|---|---|---|---|---|---|
| `neutral_white` | strong | strong | good | strong | strong | good | good | weak |
| `editorial_outline` | good | strong | okay | strong | strong | okay | good | weak |
| `broadcast_signal` | strong | strong | good | strong | okay | strong | strong | okay |
| `dashboard_analytical` | strong | strong | good | strong | strong | strong | strong | good |
| `gallery_infographic` | good | okay | strong | okay | okay | good | good | weak |
| `poster_editorial` | strong | good | okay | good | strong | good | strong | weak |
| `market_technical` | strong | strong | weak | strong | strong | strong | strong | strong |
| `premium_dark` | good | strong | okay | good | okay | strong | strong | okay |
| `terminal_mono` | okay | strong | weak | strong | strong | good | strong | strong |
| `ai_gradient_signal` | good | strong | strong | okay | weak | good | strong | weak |
| `enterprise_carbony` | strong | strong | weak | strong | strong | strong | good | okay |
| `friendly_productive` | good | good | okay | strong | strong | okay | okay | weak |
| `social_bold` | good | okay | strong | weak | weak | okay | good | weak |
| `institutional_finance` | strong | strong | okay | strong | strong | strong | strong | strong |
| `neo_broadcast_dark` | strong | strong | okay | strong | okay | strong | strong | good |

## 4. Theme-set selection guide

### Use `neutral_white` when

- 기본값이 필요할 때
- 보고서/영상/슬라이드 어디에도 무난해야 할 때
- source note를 조용하게 두고 싶을 때

### Use `editorial_outline` when

- 차트보다 읽는 경험이 중요할 때
- 표와 본문이 같이 나오는 컨텍스트일 때
- 종이감, warm neutral, 설명형 주석이 필요할 때

### Use `broadcast_signal` when

- 영상형 긴장감이 필요할 때
- 숫자를 “신호”처럼 보여줘야 할 때
- rail source, tag annotation, dark contrast가 중요할 때

### Use `dashboard_analytical` when

- 비교/지표판/표가 주도할 때
- 공적/기관형 읽기 경험이 필요할 때

### Use `gallery_infographic` when

- 이미지와 함께 노출될 때
- 따뜻하고 친화적인 인포그래픽이 필요할 때

### Use `poster_editorial` when

- 포스터/스프레드 감각이 필요할 때
- 큰 숫자, 짧은 제목, footnote block이 중요할 때
- component보다 composition이 먼저 보여야 할 때

### Use `market_technical` when

- 정확성, 밀도, 기술성이 우선일 때
- decorative surface보다 guide/value legibility가 중요할 때

## 5. Recommended first build order

If implementation bandwidth is limited, build in this order:

1. `neutral_white`
2. `broadcast_signal`
3. `dashboard_analytical`
4. `editorial_outline`
5. `poster_editorial`
6. `market_technical`
7. `gallery_infographic`

Reason:

- 이 6개만으로도 대부분의 `ChartAgent` 사용 상황을 커버한다
- 서로 시각 차이도 충분히 커서 review가 쉽다

## 6. Variant strategy

Each `theme_set` should eventually support a small, explicit variant layer.

Recommended shared variants:

- `base`
- `signal`
- `rounded`
- `quiet`
- `dense`

Examples:

- `neutral_white.quiet`
- `broadcast_signal.signal`
- `dashboard_analytical.dense`
- `gallery_infographic.rounded`

## 7. What not to do

- `theme_set`를 브랜드명과 1:1로 대응시키지 말 것
- `apple_theme`, `notion_theme`처럼 외부 브랜드를 내부 운영 이름으로 직접 쓰지 말 것
- exact color/token 복제를 목표로 하지 말 것

Internal names should remain abstract and reusable.
