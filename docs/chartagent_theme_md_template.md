# ChartAgent THEME.md Template

Updated: 2026-04-07

이 문서는 `ChartAgent`의 `theme_set` 하나를 에이전트가 읽기 좋은 md 계약으로 설명하기 위한 템플릿이다.
목표는 token 나열이 아니라, 차트 전반의 surface language를 에이전트가 이해하게 만드는 것이다.

---

# [Theme Label]

## 1. Theme Identity

- Theme id: `theme_set_id`
- Short label: `Human Readable Label`
- One-line summary: `이 테마가 주는 전체 인상`
- Artwork signature: `예: dark broadcast panel with sharp signal accents`
- Best-fit contexts:
  - `영상 인포그래픽`
  - `대시보드`
  - `기사 삽입 차트`
- Avoid when:
  - `예: 가벼운 교육용 삽화형 차트에는 부적합`

## 2. Visual Theme & Atmosphere

- Mood:
  - `정제됨 / 공격적 / 기술적 / 다큐멘터리 / 에디토리얼`
- Density:
  - `sparse / balanced / dense`
- Contrast strategy:
  - `high contrast dark panel`
- Surface language:
  - `평면 패널인지, 깊이감이 있는지, 종이 같은지`
- Motion expectation:
  - `정적 / 미세 강조 / 방송형 강한 하이라이트`

## 3. Color Roles

- Background:
  - `#HEX`
- Panel:
  - `#HEX`
- Plot background:
  - `#HEX`
- Primary accent:
  - `#HEX`
- Secondary accent:
  - `#HEX`
- Positive:
  - `#HEX`
- Negative:
  - `#HEX`
- Neutral:
  - `#HEX`
- Grid / divider:
  - `#HEX`
- Source note:
  - `#HEX`

### Color usage rules

- `강조 색은 한 chart 안에서 최대 1~2개까지만 강하게 사용`
- `중립 색은 축, divider, 표의 보조 셀에 사용`
- `positive/negative는 수익/감소 같은 명시적 의미가 있을 때만 사용`

## 4. Typography Rules

- Title role:
  - family: `폰트명`
  - weight: `예: 700`
  - tone: `headline / editorial / dashboard`
- Label role:
  - family: `폰트명`
  - weight: `예: 600`
- Value role:
  - family: `폰트명`
  - weight: `예: 700`
- Source role:
  - family: `폰트명`
  - weight: `예: 500`

### Text hierarchy rules

- `title > value > label > source`
- `title은 짧게, label은 기능적으로`
- `source note는 읽히되 시선 주도권을 가져가면 안 됨`

## 5. Geometry & Shape

- Corner radius:
  - `예: 6 / 14 / 28`
- Bar style:
  - `square / soft / pill`
- Chip style:
  - `sharp / round`
- Outline width:
  - `예: 1.5 / 3`
- Stroke width:
  - `예: 2 / 4 / 6`
- Gap language:
  - `tight / balanced / airy`

### Geometry rules

- `라운드니스는 카드와 칩에서만 강하게 적용할지`
- `차트 막대까지 pill로 갈지`
- `표 셀은 각지게 둘지`

## 6. Pattern & Texture

- Pattern mode:
  - `solid / outline_only / outline_plus_hatch / range_hatch`
- Pattern density:
  - `low / medium / high`
- Pattern spacing:
  - `예: 8 / 12 / 16`
- Pattern opacity:
  - `예: 0.12 / 0.24 / 0.4`
- Texture purpose:
  - `장식인지, 구분을 위한 도구인지`

### Pattern rules

- `패턴은 값 전달을 해치지 않는 범위에서만 사용`
- `같은 panel 안에서 2종 이상의 hatch를 남발하지 않음`

## 7. Chart Family Defaults

### bar / bar_horizontal

- Preferred surface:
  - `예: panel`
- Axis treatment:
  - `light grid`
- Label placement:
  - `inside / outside / left rail`
- Best use:
  - `랭킹 / 비교`

### line

- Preferred line style:
  - `thin precise / thick expressive`
- Point marker:
  - `none / dot / pill`
- Best use:
  - `시계열 / 추세`

### donut / pie

- Ring thickness:
  - `thin / medium / thick`
- Center treatment:
  - `empty / total value / short label`
- Best use:
  - `share / composition`

### comparison_table / fact_table

- Header style:
  - `filled / outlined / plain`
- Row divider:
  - `subtle / strong`
- Table density:
  - `tight / balanced / airy`

## 8. Annotation, Source, and Caption Rules

- Annotation style:
  - `chip / inline label / side note / callout rail`
- Source style:
  - `bottom_left / bottom_right / edge_rail / inline`
- Source tone:
  - `quiet / editorial / technical`
- Caption rule:
  - `짧고 기능적으로`

## 9. Recommended Override Ranges

- `stroke_width`: `min ~ max`
- `corner_radius`: `min ~ max`
- `pattern_density`: `allowed values`
- `source_mode`: `allowed values`
- `label_weight`: `min ~ max`

## 10. Reset Expectations

- `reset_all` returns this theme to its original identity.
- `reset_groups` should preserve the rest of the theme.
- `reset_keys` should only roll back the named tokens.

## 11. Do

- `예: 방송형 테마라면 source rail을 적극 활용`
- `예: 데이터 밀도가 높아도 hierarchy는 명확하게 유지`

## 12. Don't

- `예: 강조 색을 3개 이상 섞지 말 것`
- `예: 패턴을 모든 시리즈에 동시에 쓰지 말 것`

## 13. Agent Prompt Guide

- Good prompt:
  - `Use this theme for a high-contrast broadcast explainer chart with strong signal accents and right-edge source rail.`
- Good prompt:
  - `Keep the same theme identity but soften corners and lower pattern density.`
- Bad prompt:
  - `Make it prettier.`

