# Reference -> Benchmark -> Production Policy

Updated: 2026-04-07

## Goal

외부 레퍼런스를 그대로 복제하지 않고,

1. 참고용으로 학습하고
2. 내부 benchmark 규칙으로 추상화한 뒤
3. 실제 산출물에서는 재구성해서 활용

하는 운영 원칙을 고정한다.

이 문서는 `ChartAgent`, `Auto Kairos`, `FontAgent` 모두에 적용된다.

## 1. Core Rule

외부 레퍼런스는 `copy source`가 아니라 `benchmark source`로 사용한다.

즉:

- 원본 화면을 그대로 재현하지 않는다
- 브랜드 고유 식별성을 그대로 가져오지 않는다
- 대신 디자인 언어, 공간 문법, 표면 규칙, 위계 규칙을 추출한다

## 2. Allowed Reference Inputs

- public website UI
- 공개된 `DESIGN.md`
- preview html
- 공개된 스타일 토큰
- 방송/유튜브 화면 스틸
- 공개 자료의 차트/표 화면

## 3. What We Extract

### Design language

- 색 역할
- 타이포 위계
- spacing / density
- surface tone
- border / outline / shadow 방식
- roundness / geometry
- pattern / texture

### Spatial grammar

- dominant layer
- negative space strategy
- reading flow
- anchor topology
- text surface
- source / annotation placement

### Structured visual grammar

- 차트 family별 surface language
- 표 헤더/셀 규칙
- source rail 규칙
- annotation/callout 규칙
- quote / map / timeline / compare 장면 문법

## 4. What We Do Not Copy

- 로고
- 브랜드명
- 제품명/서비스명
- 고유 문구
- 화면 전체를 사실상 동일하게 만드는 layout 복제
- trade dress를 직접 식별할 수 있을 정도의 조합

## 5. Required Abstraction Step

레퍼런스를 바로 production에 연결하지 않는다.

반드시 중간 추상화층을 만든다.

Examples:

- `awesome-design-md` -> `theme_set` / `reference_profile`
- 방송 스틸 -> `creative_scene grammar`
- 폰트 사례 -> `font role profile`

즉 원본 브랜드 단어를 떼고,

- `dark broadcast panel`
- `editorial outline`
- `documentary subject frame`
- `source rail with quiet edge continuity`

같은 중립 언어로 바꿔서 저장한다.

## 6. Production Rule

실제 산출물은 반드시 아래 중 하나여야 한다.

- 단일 레퍼런스를 추상화해서 변형한 결과
- 여러 레퍼런스를 혼합해 재구성한 결과
- 내부 benchmark를 기반으로 새로 조합한 결과

즉 “이 사이트/채널 화면을 그대로 만들기”는 금지하고,
“이런 공간 문법과 이런 surface language를 가지는 결과”만 허용한다.

## 7. Agent-specific Application

### ChartAgent

- Reference input:
  - `DESIGN.md`
  - preview html
  - dashboard/chart screenshots
- Internal abstraction:
  - `theme_set`
  - `reference_profile`
  - `theme_artwork_signature`
- Production:
  - chart family별 theme-consistent render

### Auto Kairos

- Reference input:
  - 방송 스틸
  - explainer channel frames
- Internal abstraction:
  - `creative_scene.kind`
  - `creative_scene.composition`
  - spatial grammar tags
- Production:
  - scene payload에 맞는 새 장면 구성

### FontAgent

- Reference input:
  - 브랜드/채널 타이포 사례
- Internal abstraction:
  - `font role profile`
  - `headline/body/subtitle/source` role map
- Production:
  - 프로젝트 목적에 맞는 폰트 조합

## 8. Review Checklist

출력물을 검토할 때 아래를 확인한다.

- 특정 브랜드/채널의 화면을 그대로 베낀 느낌이 나는가
- 로고나 고유 식별 문구가 남아 있는가
- 색/타이포/레이아웃 조합이 지나치게 동일한가
- 추상화된 benchmark 언어로 설명 가능한 결과인가
- 레퍼런스를 참고했지만 자체 목적에 맞게 변형되었는가

## 9. Practical Standard

좋은 활용:

- `Notion`에서 배운 quiet editorial spacing을 일반화해서 새로운 테이블 UI에 적용
- `io` 채널에서 배운 source rail 문법을 새 explainer 장면에 적용
- `broadcast_signal` 테마에서 dark panel + sharp accent만 가져오고, 실제 chart 구조는 새로 설계

나쁜 활용:

- 특정 서비스의 hero, 카드, 버튼, 색 조합을 거의 동일하게 재현
- 특정 채널의 frame을 동일 위치/동일 조합으로 그대로 모사
- 브랜드 고유 UI를 사실상 skin처럼 옮겨오기

## 10. Default Policy

기본 정책은 아래다.

- `reference first`
- `benchmark abstraction mandatory`
- `production reuse only through abstraction`

한 줄로 요약하면:

> 외부 레퍼런스는 학습용으로 보고, 내부 benchmark로 추상화한 다음, 실제 결과물은 그 benchmark를 바탕으로 재구성한다.

