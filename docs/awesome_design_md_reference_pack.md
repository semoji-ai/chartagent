# awesome-design-md Reference Pack

Updated: 2026-04-07

Source repo:

- https://github.com/VoltAgent/awesome-design-md

Purpose:

- `awesome-design-md`에서 직접 복제하지 않고
- `ChartAgent`와 `Auto Kairos`가 사용할 수 있는 추상화된 benchmark seed를 만든다

## How to use this pack

- 원본 사이트를 그대로 재현하지 않는다
- 아래 항목은 `theme_set`, `reference_profile`, `creative_scene grammar`의 seed로만 사용한다
- 실제 산출물은 여러 seed를 섞거나 약화시켜 재구성한다

## Theme-set candidate mapping

### 1. `neutral_white`

Reference seeds:

- Vercel
- Apple
- Notion

Useful traits:

- white or near-white canvas
- very restrained border/shadow treatment
- high text clarity with minimal accent use
- precise hierarchy with strong whitespace control

Carry over:

- micro-contrast neutral text
- whisper borders
- sparse annotation
- quiet source note

Avoid copying:

- exact Vercel monochrome shell
- Apple’s full-bleed product hero staging

### 2. `editorial_outline`

Reference seeds:

- Notion
- Claude

Useful traits:

- warm paper-like surfaces
- restrained editorial borders
- softer reading rhythm
- explanation-first hierarchy

Carry over:

- warm off-white panels
- low-contrast section dividers
- calm table headers
- source as quiet footnote or rail

Avoid copying:

- Claude’s exact serif brand voice
- Notion’s exact card composition

### 3. `broadcast_signal`

Reference seeds:

- ClickHouse
- Vercel workflow accents

Useful traits:

- high-contrast panel language
- strong highlight accent
- crisp borders and stronger information urgency
- chart as signal carrier rather than decoration

Carry over:

- dark panel + bright accent
- sharper stroke language
- stronger annotation tags
- rail-based source treatment

Avoid copying:

- ClickHouse’s exact neon identity
- Vercel’s exact workflow colors

### 4. `dashboard_analytical`

Reference seeds:

- Coinbase
- ClickHouse

Useful traits:

- institutional readability
- panelized analytical surfaces
- clear CTA-grade accent separation
- high legibility labels and values

Carry over:

- cool neutral panel system
- stronger grid and axis clarity
- compact analytical tables
- low-noise but readable metadata

Avoid copying:

- exact Coinbase blue dependence
- ClickHouse neon aggression

### 5. `gallery_infographic`

Reference seeds:

- Pinterest
- Claude

Useful traits:

- warmer, more illustrative mood
- generous rounding
- softer surfaces
- image-friendly infographic treatment

Carry over:

- warm accent surfaces
- higher corner radius
- decorative but controlled pattern usage
- friendlier note/annotation voice

Avoid copying:

- Pinterest’s masonry identity
- Claude’s exact illustration language

### 6. `market_technical`

Reference seeds:

- ClickHouse
- Coinbase
- Vercel

Useful traits:

- precision over decoration
- denser guides
- terminal/market seriousness
- compact, high-clarity values

Carry over:

- dense grid logic
- reduced ornament
- compact labels
- strong value emphasis

Avoid copying:

- terminal cosplay for non-technical contexts
- brand-color dominance

## Extractable benchmark fields

These are safe to reuse after abstraction.

- surface tone
- accent role
- border philosophy
- shadow philosophy
- typography hierarchy
- display/body/source contrast
- chart family preference
- table header/body rhythm
- source rail style
- annotation/callout style
- density preference
- radius preference

## Direct applications

### For `ChartAgent`

- convert into `theme_set` seed notes
- convert into `reference_profile` defaults
- compare dashboard previews against these source traits

### For `Auto Kairos`

- borrow section pacing
- borrow text-vs-surface restraint
- borrow source/caption quietness
- borrow contrast strategy for map/data/quote scenes

### For `FontAgent`

- extract role hierarchy only
- do not try to clone proprietary brand typography

## Practical next step

1. turn each of the 6 theme-set candidates into a real `THEME.md`
2. optionally add `source_refs` metadata to each internal `theme_set`
3. use this pack as benchmark only, not production copy source

