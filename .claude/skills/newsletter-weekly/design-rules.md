# Newsletter 디자인·HTML 구조 규칙

`report-poll.py`가 id 속성으로 파싱한다. font-size 등 스타일은 자유지만 **id는 필수**.

---

## 섹션 구분: HTML 주석

시작: `<!-- ── {MODULE_ID}: {제목} ── -->`, 종료: `<!-- /{MODULE_ID} -->`

**모듈 순서 (고정):**
1. `MODULE 2` — 편의점 트렌드
2. `MODULE 5B` — 메가트렌드
3. `MODULE 4` — 날씨 (6권역)
4. `MODULE 5A` — 이벤트

---

## ID 매핑 테이블

### HEADER
| id | 추출 내용 |
|---|---|
| `header-title` | 뉴스레터 제목 (예: 4월 3주차 스토어레터) |
| `header-date` | 발행 기간 (예: 4월 15일 (수) — 4월 21일 (화)) |

### 섹션 공통
| id | 추출 내용 |
|---|---|
| `section-title` | 각 MODULE 제목 (예: 이번주 편의점 트렌드) |
| `section-desc` | 각 MODULE 부제/요약 |
| `card` | 카드 컨테이너 `<table>` |

### 트렌드 카드 (MODULE 2, MODULE 5B)
| id | 추출 내용 |
|---|---|
| `card-title` | 상품/트렌드명 |
| `card-body` | 설명 텍스트 |
| `card-badge` | HOT 배지 (span, card-title 내부) |

### 날씨 카드 (MODULE 4)
| id | 추출 내용 |
|---|---|
| `weather-region` | 지역명 (수도권·강원 등) |
| `weather-temp` | 온도 (최저X° / 최고X°) |
| `weather-summary` | 날씨 요약 |
| `weather-tip` | 판매 TIP 본문 |

### 이벤트 카드 (MODULE 5A)
| id | 추출 내용 |
|---|---|
| `event-month` | 월 (MAY·APR 등) |
| `event-day` | 일 (1·5 등) |
| `event-label` | 이벤트명 (법정공휴일 · 근로자의 날 (금)) |
| `event-body` | 상세 설명 |

---

## 편의점 브랜드 표시 (고정 스펙)

카드 **우측 상단**에 브랜드 색상 텍스트. **Pill·박스·border·로고 이미지 전부 금지**.

```html
<td style="vertical-align:middle;text-align:right;white-space:nowrap;padding-left:8px;">
  <span style="color:{BRAND_COLOR};font-weight:700;font-size:13px;letter-spacing:0.04em;">{BRAND_NAME}</span>
</td>
```

| 편의점 | 색상 | 표기 |
|---|---|---|
| **세븐일레븐** | `#EE162E`(7) + `#046A38`(-ELEVEN) **분리** | `<span style="color:#EE162E;">7</span><span style="color:#046A38;">-ELEVEN</span>` |
| **GS25** | `#003B7B` | GS25 |
| **CU** | `#552084` | CU |
| **편의점 공용** | `#787f89` | ALL |

---

## 카드 제목 영역 구조

**2컬럼 테이블** (좌: 제품명+배지, 우: 편의점 브랜드)

```html
<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
  <td style="vertical-align:middle;">
    <div id="card-title">제품명 [HOT 배지]</div>
  </td>
  <td style="vertical-align:middle;text-align:right;white-space:nowrap;padding-left:8px;">
    {브랜드 라벨}
  </td>
</tr></table>
```

---

## 섹션 헤더 구조

**2컬럼** (좌: 섹션 제목·설명, 우: "검색량·SNS 반응 강한 순" 안내 12px 회색)

---

## 인용블록 스타일 (메가트렌드 내 편의점 진입 정보)

```html
<div style="margin-top:8px;padding:8px 12px;background:#f2f2f4;border-radius:6px;font-size:13px;color:#565f6c;line-height:1.7;">
  ↳ <span style="color:{브랜드색};font-weight:700;">{브랜드}</span> 편의점 최초 출시 · {상품명} · {가격}원
</div>
```
- 배경 `#f2f2f4` 연회색만. **stripe·border-left 금지**
- `↳` 화살표로 연관 관계

---

## 이벤트 dot 색상·크기

- 법정공휴일·법정휴일: `#376ae2` (파랑)
- 기념일·데이: `#1ab715` (녹색)
- 시즌·절기: `#fad232` (노랑)

**크기**: `width:8px;height:8px;` **반드시 둘 다 명시** (height 빠지면 안 보임)

---

## 레이아웃 기본

- 카드 간 간격: `<div style="height:8px;font-size:0;line-height:0;">&nbsp;</div>`
- 모듈 간 간격: `<div style="height:24px;font-size:0;line-height:0;">&nbsp;</div>`
- 마지막 카드 뒤에는 spacer 없음
- 카드 높이 = **auto** (고정 X)
- 폰트: 본문 14px / 카드 제목 18px / 섹션 30px / 헤드라인 36px / 서브 12~13px

---

## 피드백 버튼 (필수 스펙)

- 440×64px pill
- `height:64px` + `line-height:64px` **둘 다 명시**
- 22px 흰 글씨, 배경 `#376ae2`

---

## ❌ 절대 금지 (반복 실수 방지)

- **Border-left stripe** (카드·박스·어느 요소든)
- **카드 배경 컬러 박스·stripe** 장식
- **`height:\d+px` 정규식 일괄 제거** — spacer·dot·버튼 전부 망가짐
- **로고 이미지** (브랜드마다 크기 제각각 문제)
- **pill 뱃지** (편의점 표시용으로)
- **HOT/주목/초기 배지 남발** — 현재 버전은 배지 제거 + "검색량·SNS 반응 강한 순" 한 줄 안내로 대체
