# Pinterest Reference Analysis

Updated: 2026-04-07

## Goal

Pinterest를 직접 복제 source가 아니라, visual benchmark discovery surface로 활용한다.

이 문서는:

- 어떤 Pinterest 레퍼런스를 볼지
- 거기서 무엇을 추출할지
- `Auto Kairos`와 `ChartAgent`에 어떻게 연결할지

를 정리한다.

## 1. Constraint

Pinterest는 robots 제약이 강해서 pin 본문/이미지를 자동으로 대량 수집하는 데 한계가 있다.

따라서 현재 기준 전략은:

1. Pinterest를 discovery surface로 사용
2. 보드/핀 제목과 관련 검색어를 seed로 삼음
3. 사람이 실제 pin을 확인해 추가 선별
4. 선별 결과를 내부 benchmark로 추상화

즉 Pinterest는 자동 완전 수집 대상이 아니라, 고품질 reference를 찾는 입구로 사용한다.

## 2. Useful boards and pages found

### Editorial / infographic boards

- https://au.pinterest.com/vlatrice/editorial-design/
  - `Editorial design`
  - magazine layout, editorial layout, publication design, data poster 관련 추천이 풍부함
- https://ph.pinterest.com/kpnzlinh/infographic-layouts/
  - `infographic layouts`
  - infographic layout, graphic design inspiration 계열
- https://www.pinterest.com/xyakamoz/information-visualization-design/
  - `Information Visualization Design`
- https://www.pinterest.com/efreber9693/graphic-design/
  - `Graphic Design and Editorial Layout Ideas`

### Specific pin seeds

- https://www.pinterest.com/pin/web-design--488218415826060357/
  - `IdN - Designing Data the Infographics`
- https://www.pinterest.com/pin/642888915539552622/
  - `Visualizing | Information visualization, Data visualization design, Big data visualization`
- https://www.pinterest.com/pin/editorialmagazine-design--1055599892491519/
  - editorial / magazine layout inspiration

### User-provided seed

- https://kr.pinterest.com/pin/806988827629113483#imgViewer

Note:

- 직접 pin fetch는 제한될 수 있으므로, 수동 확인과 함께 써야 한다.

## 3. What Pinterest is especially good for

Pinterest는 아래 레퍼런스를 찾는 데 특히 좋다.

- editorial infographic poster
- magazine spread style data layout
- typography-led information poster
- mixed image + data collage
- chart/table + annotation poster
- quote + image + caption composition
- number-heavy visual hierarchy

즉 `website UI reference`보다

- poster
- spread
- infographic
- print-like layout

쪽이 강하다.

이건 `awesome-design-md`가 잘 못 주는 영역이다.

## 4. Extractable design grammar

Pinterest에서 특히 뽑아야 할 건 다음이다.

### Spatial grammar

- text mass vs image mass 비율
- asymmetry 사용 방식
- spread-style reading flow
- 캔버스 중앙축 유무
- negative space를 어떻게 남기는지

### Typography grammar

- 큰 숫자/짧은 label 조합
- 제목보다 section label이 강한 경우
- serif + sans 혼합
- 세로 타이포/회전 라벨

### Information grammar

- 차트를 poster 구성요소로 다루는 방식
- 표와 차트를 같은 캔버스에서 묶는 방식
- annotation line / note block / caption rail
- 이미지와 데이터의 우선순위 조절

### Surface grammar

- 종이감 / 인쇄감 / 리소그래프 느낌
- bold color block
- outline poster
- monochrome technical poster

## 5. New benchmark families Pinterest can unlock

Pinterest를 보면 기존 `theme_set`만으로 부족한 영역이 보인다.

새로 열리는 후보:

- `poster_editorial`
  - 큰 제목보다 캔버스 구조가 중요
- `data_poster_constructed`
  - 차트 + 타이포 + shape가 한 장 포스터처럼 결합
- `magazine_spread_infographic`
  - 좌우 spread, strong gutter, rich annotations
- `type_led_information`
  - 차트보다 숫자/제목/라벨이 구조를 만드는 방식
- `print_warm_collage`
  - 이미지, 메모, 표, 작은 chart가 섞인 따뜻한 구성

## 6. Direct application to Auto Kairos

Pinterest 레퍼런스는 특히 `creative_scene` 쪽에 도움이 된다.

### Strong-fit scene kinds

- `data`
- `compare`
- `quote_pull`
- `artifact_reveal`
- `items_list`

### New composition ideas

- `poster_stack`
- `spread_gutter`
- `type_led_mass`
- `annotation_constellation`
- `image_data_collage`

### Text role additions worth considering

- `section_kicker`
- `data_caption`
- `footnote_block`
- `poster_stat`
- `spread_label`

## 7. Direct application to ChartAgent

Pinterest 레퍼런스는 `theme_set`보다 아래 두 층에 더 강하게 먹는다.

- `pattern_format_preset`
- `chart family composition preset`

특히 유용한 방향:

- chart를 단독 component가 아니라 poster surface 일부로 보게 함
- 표와 chart를 한 panel에 함께 두는 방식
- source를 작은 footnote block으로 처리
- annotation을 line-callout rather than chip으로 확장

## 8. Recommended search clusters

Pinterest에서 다음 cluster로 계속 찾으면 좋다.

### Chart / infographic

- `infographic layout`
- `information visualization`
- `data visualization poster`
- `designing data infographic`

### Editorial / spread

- `editorial design infographic`
- `magazine spread infographic`
- `publication design data`
- `graphic design editorial layout`

### Typography / poster

- `type poster infographic`
- `experimental type information design`
- `poster layout data`
- `number layout editorial`

## 9. Practical operating rule

Pinterest reference workflow는 이렇게 간다.

1. board/pin title로 discovery
2. 사람이 pin visually 확인
3. 내부 note로 추상화
4. `theme_set`, `creative_scene`, `pattern_format_preset`로 환원
5. production에서는 조합해서 재구성

## 10. Immediate next step

다음엔 아래 중 하나가 맞다.

1. Pinterest 기반 `poster_editorial` theme_set seed 만들기
2. `compare/data/quote`용 Pinterest-inspired composition preset 만들기
3. Pinterest reference만 모아 `creative_scene` 후보 still board 만들기

