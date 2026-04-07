# SAAI 뉴스레터 자동화 프로젝트

## 목표
트렌드 키워드 입력 + 기상청 날씨 데이터 + 이벤트 파일 + 오피스 상권 매출 데이터를 읽어
편의점 점주 대상 뉴스레터 HTML 파일을 자동 생성한다.

---

## 폴더 구조

```
saai-newsletter/
├── CLAUDE.md                        # 이 파일 (프로젝트 컨텍스트)
├── .env                             # API 키 (공유 금지)
│                                     KMA_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
├── fetch_weather.py                 # 기상청 API 호출 → data/weather.json 생성
├── fetch_naver_trend.py             # 네이버 DataLab 검색 트렌드 API
│                                     --compare 모드: 5개씩 묶어 상대 비교
│                                     기본 모드: 개별 방향성(상승/유지/하락) 판단
├── 가설검증_통합결과.xlsx             # 오피스 상권 매출 가설검증 결과 (155건)
│                                     날씨·이벤트 섹션 판매 TIP 근거로 활용
│
├── guides/
│   ├── voice-tone-guide.md          # 보이스톤·CTA·퍼소나·금지 표현
│   ├── newsletter-trend-sources.md  # 키워드 검색 쿼리 규칙
│   └── newsletter-trade-area.md     # 상권 유형별 특성 (주택가/오피스/대학가/역세권/관광지)
│
├── prompt/
│   └── newsletter-prompt.md         # 뉴스레터 생성 지시문 (섹션별 작성 규칙)
│
├── template/
│   ├── store-letter-template.html   # CSS 클래스 기반 HTML (디자인 원본, 수정 금지)
│   └── store-letter-template-v1.html # v1 백업
│
├── product_fit.py                   # 상품×상권 적합도 분석 (랜딩페이지 백엔드)
│                                     product_analysis.json을 읽어 결과 출력
│
├── data/
│   ├── weather.json                 # 기상청 API 결과 (fetch_weather.py로 자동 생성)
│   ├── trends.json                  # 네이버 트렌드 결과 (fetch_naver_trend.py로 자동 생성)
│   ├── product_analysis.json        # 상품×상권 적합도 (뉴스레터 생성 시 자동 생성)
│   └── events.md                    # 연간 이벤트 캘린더 (수동 관리)
│
└── outputs/
    ├── newsletter-YYYY-MM-DD.html         # CSS 클래스 버전 (브라우저 미리보기용)
    ├── newsletter-YYYY-MM-DD-inline.html  # juice로 인라인 CSS 변환 (중간 산출물)
    └── newsletter-YYYY-MM-DD-stibee.html  # 스티비 발송용 최종본 (인라인 CSS 테이블 레이아웃)
```

---

## 출력 포맷

최종 발송용 출력은 **stibee 포맷**:
- `<table>` 기반 레이아웃 (이메일 클라이언트 호환)
- 모든 CSS를 `style=""` 인라인으로 작성
- CSS 클래스(`class="trend-kw"` 등) 대신 인라인 스타일 직접 지정
- 색상·간격·폰트 값은 `template/store-letter-template.html`의 CSS 변수 참조
- 피드백 버튼에 Google Forms 링크 연결
- 푸터에 "매출 경향은 내부 분석 기반으로, 상권에 따라 다를 수 있어요" 면책 문구 포함

참고: `newsletter-YYYY-MM-DD.html` (CSS 클래스 버전)은 로컬 미리보기용. 실제 발송은 `-stibee.html` 파일.

---

## 섹션 순서 (고정)

| 순서 | 섹션 | 내용 | 데이터 소스 |
|------|------|------|------------|
| 1 | HEADER | Hook 헤드라인 + 날짜 | 자동 |
| 2 | 편의점 트렌드 | 편의점에 있거나 곧 나올 상품 | 웹 검색 + Naver DataLab |
| 3 | 메가트렌드 | 편의점 밖 외부 신호 | 웹 검색 |
| 4 | 권역별 날씨 | 5~6개 권역 날씨 + 판매 TIP | weather.json + xlsx 데이터 |
| 5 | 이벤트/일정 | 한 달 이내 공휴일·데이 | events.md + xlsx 데이터 |
| 6 | 피드백 | 도움 여부 투표 | Google Forms |
| 7 | 푸터 | 발행처 정보 | 고정 |

---

## 실행 프로세스

### 1단계: 키워드 수집
```
뉴스레터 생성해줘
트렌드: 버터떡, 두쫀쿠, 비빔면 제로슈거, ...
```
사용자가 X(트위터) 데이터 테이블을 제공하면:
- 중복 키워드 제거
- RT·Likes 수치 추출 (트렌드 규모 판단 참고)

### 2단계: 키워드 트렌드 확인
각 키워드의 검색 변형을 판단한 뒤 `fetch_naver_trend.py` 실행.
콜론(:)으로 합산 그룹 지정 가능 (예: `"진밀면:오뚜기 진밀면, 두쫀쿠"`).
상세 절차는 `prompt/newsletter-prompt.md`의 "키워드 트렌드 조회 절차" 참조.

**규모** (떡볶이 기준선 비교 — 신상품은 스테디셀러보다 검색량이 적으므로 기준을 낮게 설정):
- 🔥 트렌드: 떡볶이 30% 이상 — 대중 인지 충분
- 📈 주목: 10~29% — 신상품 치고 유의미한 검색량
- 🌱 성장중: 3~9% — 검색 존재 자체가 시그널
- · 니치: 3% 미만 — 네이버에선 아직 안 잡힘 (SNS 선행 가능)

**방향** (자체 스케일 최근 7일 vs 이전 7일):
- 상승(▲): +20% 이상
- 유지(—): ±20% 이내
- 하락(▼): -20% 이하

### 3단계: 키워드 분류 (웹 검색)
각 키워드를 편의점 입점 여부로 분류:
- 편의점 입점/신상 확인 → **편의점 트렌드** (상태값 배지 ▲/—/▼)
- 편의점 입점 없음 → **메가트렌드** (상태값 배지 없음)

유사 키워드는 하나로 묶을 수 있음:
- 예: 세븐일레븐×롯데자이언츠 + SSG랜더스×이마트24 → "KBO 개막 콜라보"

### 4단계: 날씨·이벤트 데이터
- `fetch_weather.py` 실행 → `data/weather.json` 생성
- `data/events.md` 읽어서 한 달 이내 이벤트 확인
- 날씨 뉴스 검색 (꽃샘추위, 황사, 미세먼지, 건조주의보, 이른 더위 등)

### 5단계: 상권 데이터 반영
`가설검증_통합결과.xlsx` 의 오피스 상권 매출 가설검증 결과를 참고하여:
- 날씨 판매 TIP에 데이터 근거 반영 (예: "15°C 넘으면 냉음료가 눈에 띄게 늘어요")
- 이벤트 팁에 공휴일/주말 매출 경향 반영 (예: "공휴일에 방문 고객이 크게 줄지만 1인당 구매 금액은 올라가는 경향이 있어요")
- **주의: 구체적 퍼센트 숫자를 직접 노출하지 않고 자연스럽게 녹여서 표현**

### 6단계: HTML 생성
- 출처 검색 → 공신력 있는 기사 링크 확보 (기사 날짜 함께 표기)
- 모든 가이드 파일 참조하여 HTML 작성
- `outputs/newsletter-YYYY-MM-DD-stibee.html` 생성

### 7단계: 상품 분석 JSON 생성
- `data/product_analysis.json` 생성 (랜딩페이지 데이터)
- `product_fit.py`의 `calc_score()`가 `data/trade_area_patterns.json` 기반으로 점수 산출
- 뉴스레터에는 상권 태그(상위 2개 상권 + 이유)만 노출, 점수는 랜딩 독점

### 8단계: 아카이브 저장
- `data/archive/{YYYY-MM-DD}.json`으로 복사
- `data/archive/index.json` 업데이트
- 이전 주 JSON과 비교하여 메가트렌드 입점 트래킹

---

## 파일별 역할

| 파일 | 역할 | 수정 주체 |
|------|------|----------|
| `voice-tone-guide.md` | 보이스톤·CTA·퍼소나·금지 표현 | 팀 |
| `newsletter-trend-sources.md` | 키워드 검색 쿼리 규칙 | 팀 |
| `newsletter-trade-area.md` | 상권 유형별 특성 | 팀 |
| `newsletter-prompt.md` | 섹션별 생성 규칙·placeholder 매핑 | 팀 |
| `store-letter-template.html` | HTML 디자인 원본 (수정 금지) | 슬기 |
| `fetch_weather.py` | 기상청 API 호출 | 팀 |
| `fetch_naver_trend.py` | 네이버 DataLab API 호출 | 팀 |
| `가설검증_통합결과.xlsx` | 오피스 상권 매출 가설검증 (155건, 7축) | 팀 |
| `events.md` | 연간 이벤트 캘린더 | 팀 |
| `.env` | API 키 (공유·Git 업로드 금지) | 개인 |

---

## 주의사항

- `store-letter-template.html` CSS·SVG 로고·피드백 섹션·푸터 수정 금지
- 트렌드 상태값(▲/—/▼)은 반드시 네이버 DataLab + 웹 검색으로 판단. 추측 금지.
- 편의점 신상 제품명은 검색 확인된 경우에만 기재.
- 출처 링크는 공신력 있는 언론사·공식 보도자료만 사용. 기사 날짜 함께 표기.
- 출처를 못 찾은 키워드도 작성 가능 (출처 링크만 생략).
- 이벤트 요일은 반드시 확인.
- 상권 데이터 수치는 직접 노출 금지 → "경향이 있어요", "눈에 띄게 늘어요" 등 자연어로 표현.
- `.env` 파일 절대 Git에 올리지 말 것.
- `env.env`는 구버전 환경변수 파일 (무시).
