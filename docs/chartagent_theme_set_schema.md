# ChartAgent Theme Set Schema

Updated: 2026-04-07

## Goal

`ChartAgent`의 내부 디자인 시스템은 이미 아래 4층으로 나뉘어 있습니다.

- `theme`
- `reference_profile`
- `style_combo_preset`
- `pattern_format_preset`

하지만 사용자나 다른 에이전트 입장에서는 이 구조가 너무 세분화되어 있습니다.

그래서 외부 계약은 아래처럼 단순화합니다.

- `theme_set`
- `theme_overrides`
- `theme_reset`

즉 사용자 surface는 간단하게 유지하고, 내부에서만 4층 디자인 시스템으로 해석합니다.

## Top-level contract

```json
{
  "theme_set": "broadcast_signal",
  "theme_overrides": {
    "accent_color": "#0F766E",
    "stroke_width": 2.5,
    "corner_radius": 12,
    "pattern_density": "medium"
  },
  "theme_reset": {
    "mode": "reset_keys",
    "keys": ["accent_color"]
  }
}
```

## 1. `theme_set`

`theme_set`은 사용자가 직접 고르는 상위 프리셋입니다.

이 프리셋 하나로 아래가 함께 정해집니다.

- 기본 palette
- chart surface tone
- outline/pattern 기본 규칙
- typography baseline
- annotation 느낌
- table header/body 스타일
- source note 스타일

### Recommended initial `theme_set`

- `neutral_white`
- `editorial_outline`
- `broadcast_signal`
- `dashboard_analytical`
- `gallery_infographic`
- `market_technical`

## 2. `theme_overrides`

`theme_overrides`는 `theme_set` 위에 덮는 미세조정입니다.

원칙:

- 모든 필드는 optional
- override는 원본 theme token을 바꾸지 않음
- override는 항상 현재 `theme_set`의 파생값으로만 동작

### Allowed override groups

- `color`
- `geometry`
- `pattern`
- `stroke`
- `label`
- `annotation`
- `table`
- `source`

### Recommended override keys

#### Color

- `accent_color`
- `accent_alt_color`
- `positive_color`
- `negative_color`
- `neutral_color`
- `series_palette`
- `grid_color`
- `panel_color`
- `plot_bg_color`

#### Geometry

- `corner_radius`
- `chip_radius`
- `bar_gap`
- `group_gap`
- `panel_padding`
- `rail_width`

#### Stroke

- `stroke_width`
- `outline_width`
- `grid_width`
- `axis_width`

#### Pattern

- `pattern_mode`
  - `solid`
  - `outline_only`
  - `outline_plus_hatch`
  - `range_hatch`
- `pattern_density`
  - `low`
  - `medium`
  - `high`
- `pattern_angle`
- `pattern_opacity`
- `pattern_spacing`

#### Label / typography

- `title_scale`
- `subtitle_scale`
- `body_scale`
- `tick_scale`
- `source_scale`
- `label_weight`
- `source_opacity`

#### Annotation

- `annotation_fill`
- `annotation_stroke`
- `annotation_radius`
- `annotation_rail_width`

#### Table

- `table_header_fill`
- `table_header_weight`
- `table_cell_padding`
- `table_row_divider_opacity`

#### Source

- `source_mode`
  - `inline`
  - `bottom_left`
  - `bottom_right`
  - `edge_rail`
- `source_opacity`

## 3. `theme_reset`

override가 계속 쌓이면 테마가 오염되기 때문에 reset이 필수입니다.

### Reset modes

- `reset_all`
  - 현재 `theme_set`의 원본 토큰으로 전체 복구
- `reset_keys`
  - 지정한 key만 복구
- `reset_groups`
  - 지정한 group 전체 복구

### Example: reset all

```json
{
  "theme_set": "editorial_outline",
  "theme_reset": {
    "mode": "reset_all"
  }
}
```

### Example: reset keys

```json
{
  "theme_set": "broadcast_signal",
  "theme_overrides": {
    "accent_color": "#14B8A6",
    "corner_radius": 14
  },
  "theme_reset": {
    "mode": "reset_keys",
    "keys": ["accent_color"]
  }
}
```

### Example: reset groups

```json
{
  "theme_set": "dashboard_analytical",
  "theme_reset": {
    "mode": "reset_groups",
    "groups": ["pattern", "color"]
  }
}
```

### Reset rule

중요:

- reset은 항상 `theme_set` 원본 토큰 기준
- override 결과를 새 기본값으로 삼지 않음
- 내부 4층 시스템도 원본 기준으로 다시 resolve

## 4. Internal mapping

외부 계약은 단순하지만 내부에서는 기존 4층 시스템으로 해석합니다.

### Example mapping

#### `neutral_white`

- `theme` -> `minimal`
- `reference_profile` -> `datawrapper_clean`
- `style_combo_preset` -> `neutral_system`
- `pattern_format_preset` -> disabled or `signal_outline_dashboard`

#### `editorial_outline`

- `theme` -> `editorial`
- `reference_profile` -> `editorial_paper`
- `style_combo_preset` -> `editorial_outline`
- `pattern_format_preset` -> `signal_outline_editorial`

#### `broadcast_signal`

- `theme` -> `broadcast`
- `reference_profile` -> `broadcast_live_panel`
- `style_combo_preset` -> `broadcast_signal`
- `pattern_format_preset` -> `signal_outline_broadcast`

#### `dashboard_analytical`

- `theme` -> `dashboard`
- `reference_profile` -> `dashboard_dense`
- `style_combo_preset` -> `analytical_panel`
- `pattern_format_preset` -> `signal_outline_dashboard`

#### `gallery_infographic`

- `theme` -> `editorial`
- `reference_profile` -> `gallery_wall`
- `style_combo_preset` -> `gallery_infographic`
- `pattern_format_preset` -> `signal_outline_editorial`

#### `market_technical`

- `theme` -> `dashboard`
- `reference_profile` -> `market_terminal`
- `style_combo_preset` -> `market_technical`
- `pattern_format_preset` -> `signal_outline_dashboard`

## 5. Resolution order

해석 순서는 고정해야 합니다.

1. `theme_set`
2. internal mapping to 4-layer system
3. base theme tokens resolve
4. `theme_overrides` apply
5. `theme_reset` apply
6. final render tokens emit

이 순서가 뒤집히면 reset이 깨집니다.

## 6. Why this is better

장점:

- 사용자와 에이전트는 `theme_set`만 알면 됨
- 내부 구현은 기존 4층을 그대로 활용 가능
- family가 달라도 차트군 전체 톤을 유지 가능
- override와 reset이 명확함
- 다른 에이전트와의 계약도 훨씬 단순해짐

## 7. Next implementation step

구현 순서는 이 정도가 적절합니다.

1. `theme_set` registry 추가
2. `theme_set -> 4-layer` resolver 추가
3. `theme_overrides` 허용 키 화이트리스트 추가
4. `theme_reset` 적용기 추가
5. dashboard에서 `theme_set` 선택 + reset UI 추가
