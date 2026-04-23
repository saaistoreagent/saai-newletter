---
name: newsletter-weekly
description: SAAI 스토어레터(편의점 점주용 주간 뉴스레터) 작성 전체 파이프라인. 사용자가 Grok X 트렌드 결과·IG 피드 스크립트 결과를 붙여넣으면 취합·DataLab·기사 검증·HTML까지 자동 진행. "스토어레터", "뉴스레터 작성", "편의점 트렌드 뉴스레터" 관련 요청 시 사용.
---

# newsletter-weekly

편의점 점주용 **스토어레터** 주간 파이프라인. 이 스킬 하나로 완결.

## 📁 스킬 내부 파일 구조

```
~/.claude/skills/newsletter-weekly/
├── SKILL.md                ← 이 파일 (전체 프로세스)
├── template.html           ← HTML 템플릿 (구조·예시 카드)
├── design-rules.md         ← HTML id 매핑·디자인 금지 사항
├── quality-rules.md        ← 콘텐츠 품질 기준·톤·금지 표현
├── grok-prompt.md          ← Grok X 검색 프롬프트 원본
└── instagram-script.js     ← IG 피드 긁기 Console 스크립트
```

**Claude는 이 스킬 실행 시 위 모든 파일을 참조할 것.**

## 🚀 사용자 실행 순서

### STEP 1. 사용자가 사전 수행

#### 1-1. Grok에 X 트렌드 검색 프롬프트 3회
- 프롬프트 전문: **`grok-prompt.md`** 참조
- `since:YYYY-MM-DD until:YYYY-MM-DD` 발행일 기준 최근 2주로 교체
- 3회 돌려 검색 풀 최대 커버

#### 1-2. 인스타그램 피드 긁기
- IG 웹 로그인 → DevTools(Cmd+Option+I) → Console → `allow pasting` 입력
- **`instagram-script.js`** 전체 복사 → 붙여넣기 → 엔터
- 50초 후 자동 클립보드 복사됨

#### 1-3. (선택) 사용자가 본 공식 SNS 포스트 URL·캡션 직접 공유

### STEP 2. 사용자가 Claude에 공유

```
/newsletter-weekly

2026-04-29(수) 발행 스토어레터 시작.

[Grok 결과 3회분]
...

[IG 피드 긁기 결과]
...
```

### STEP 3. Claude 자동 실행 (Phase 1~6)

## 🔄 Phase 1. 취합·중복 제거

- Grok 3회분 + IG 피드 통합 → 키워드 중복 제거
- 참여도 정리:
  - **X**: RT·좋아요
  - **IG 릴스** (음악·오리지널 오디오 있음): 첫 숫자 = 조회수 (좋아요 아님)
  - **IG 사진**: 좋아요·댓글 순
- **협찬 광고 태그** 있는 포스트는 자연 바이럴 아님 → 참여도 할인 평가

## 🎯 Phase 2. 편의점 영향 필터

다음 카테고리별로 선별:
- **편의점 미입점 선행 신호** (카페·자영업·홈레시피 중심)
- **편의점 기존 상품 급증** (언급 폭증·품절)
- **콜라보** (아이돌·캐릭터·셰프·인플루언서)
- **해외 유행 유입** (일본·중국·미국)
- **공급·가격·품절 이슈**

## 📊 Phase 3. 네이버 DataLab 조회

```bash
cd /Users/hyeon/Desktop/saai-newsletter
python3 fetch_naver_trend.py "카테고리1, 카테고리2, ..."
```

- **카테고리 키워드만** 조회 (개별 상품명은 검색량 미미)
- 떡볶이 앵커 대비 % + 폭증률 출력
- 배지:
  - HOT (30%+) → 녹색
  - 주목 (10~29%) → 노란색
  - 초기 (3~9%) → 파란색
  - <3% → 배지 없음
- **본문에 "떡볶이 대비" 절대 노출 금지** (내부 기준일 뿐)
- 정렬 안내: 카드 위에 **"검색량·SNS 반응 강한 순"** 한 줄 (우상단 12px 회색)

## 🌤️ Phase 4. 날씨·이벤트

### 날씨
```bash
python3 /Users/hyeon/Desktop/saai-newsletter/fetch_weather.py
```
- 6권역 (수도권·강원·충청권·전라권·경상권·제주) 기온·강수확률·특보 자동 저장
- 권역별 판매 TIP은 **xlsx 가설검증 데이터** + **지역 특색** 혼합. 반복 문장 피하기
- 보충 검색: 당일 미세먼지·황사·특보 뉴스 확인

### 이벤트
- `/Users/hyeon/Desktop/saai-newsletter/data/events.md` 참조
- **발행일 ~ 한 달 이내만** 포함 (31일째 이벤트도 제외)
- 요일·공휴일 날짜 **웹 검색 재검증 필수** (원본 오류 있음)
- 정식 용어:
  - 근로자의 날 = **법정휴일** (준공휴일 아님)
  - 어린이날·설·추석 = 법정공휴일
  - 음력 공휴일(부처님오신날 등) = 매년 양력 다름 → 웹 검색 필수

## 📰 Phase 5. 언론 기사 검증 (★ 필수)

**카드별 제품명·가격·출시일·콜라보 상품 리스트 = 언론사 기사 URL 직접 fetch**.

### 허용 매체
뉴시스·한국경제·머니투데이·뉴스1·전자신문·ZDNet·서울신문·MBC·이코노뉴스·서울파이낸스·이투데이 등

### 금지 출처
- 루리웹·디시·클리앙 등 **커뮤니티**
- Threads·인스타그램·페이스북 등 **SNS**
- Aboda·brunch 등 **개인 블로그**
- X(트위터) 공식 계정 = **언론 기사 없을 때만 최후 수단**

### 원칙
- Grok 요약·GPT 요약·WebSearch 요약 단독으로 신뢰 X → **기사 원문 WebFetch**
- 기사 못 찾으면 본문은 쓰되 **출처 링크 생략** (추측으로 출처 만들지 말 것)
- 출처 형식: `{매체명} — {기사 제목 요약} ({M/D})`

## 🎨 Phase 6. HTML 작성

- **`template.html`** 구조 그대로 복제
- **`design-rules.md`** id 매핑·디자인 스펙 준수
- **`quality-rules.md`** 콘텐츠 품질 기준 준수
- 출력 경로: `/Users/hyeon/Desktop/saai-newsletter/outputs/newsletter-YYYY-MM-DD-stibee.html`
- 완성 후 `pbcopy < outputs/newsletter-*.html`로 **클립보드 복사** (사용자 Stibee 바로 붙여넣기)

## ❌ 절대 금지 (반복 실수 차단)

### 할루시네이션
- Grok·GPT·SNS 요약만 보고 가격·출시일·상품명 단정 — 2026-04-22 세션 "본격 출시 4/29"·"도시락 5,900원"·"우베 라떼" 등 실수 재발 방지
- 검색 요약 문서의 "확인되지 않은 내용" 그대로 기재

### 주관적 판단
- "~찾는 고객이 많아요" (추측)
- "10~20대가 찾아요" (인구통계 추측)
- "특수가 크다/작다" (데이터 없이 단정)
- "호불호 적어요" (주관)
- "수요가 붙어요" (업계 jargon → "늘어나요" 사용)

### 구조·콘텐츠
- 이벤트 상권 구분 남발 ("오피스는 줄고, 주택가는 늘고" 반복)
- 이벤트 본문에 라벨 중복 ("법정공휴일(화요일)이에요"는 이미 라벨에 있음)
- 청탁금지법·근로자의날법 같은 법적 배경 설명
- 발행일 + 한 달 범위 밖 이벤트

### 디자인
- `design-rules.md` "절대 금지" 섹션 참조
- stripe·로고 이미지·컬러 박스·pill 뱃지 금지
- `height:\d+px` 정규식 일괄 제거 금지

## 💡 Claude가 사용자에게 물어봐야 할 것

- **SNS 애칭 → 정식 상품명** 확인 (검색 실패 시)
- **편의점 공식 출시 여부** (Claude가 기사 못 찾아도 사용자가 알 수 있음)
- **카드 개수 제한** (점수순 전부 vs 상위 N개)
- **이벤트 범위 애매한 것** (예: 31일째)
- **Grok 결과 중 제외할 키워드** (스테디셀러 등)

## 🎁 최종 산출물

1. **HTML 파일**: `/Users/hyeon/Desktop/saai-newsletter/outputs/newsletter-YYYY-MM-DD-stibee.html`
2. **클립보드**: HTML 전체 복사 (Stibee 붙여넣기용)
3. **제목 추천**: 오픈율 고려 5~10개 옵션 (이모지 포함 가능)

## 🏢 팀 배포 가이드

다른 팀원이 이 스킬 사용하려면:

```bash
# 1. 스킬 폴더 통째로 복사
cp -r ~/.claude/skills/newsletter-weekly/ ~/target/

# 2. 본인 기기 ~/.claude/skills/ 에 설치
cp -r ~/target/newsletter-weekly ~/.claude/skills/

# 3. 프로젝트 폴더(Desktop/saai-newsletter) 별도 필요
#    - fetch_naver_trend.py, fetch_weather.py
#    - .env (본인 API 키)
#    - data/events.md
#    - 가설검증_통합결과.xlsx
```

**.env는 개별 관리**: NAVER_CLIENT_ID/SECRET, KMA_API_KEY 개인별 발급.

## 📚 프로젝트 종속 파일 (스킬 외부)

이 스킬이 호출하는 프로젝트 폴더:

```
~/Desktop/saai-newsletter/
├── fetch_naver_trend.py           # DataLab API 호출
├── fetch_weather.py               # 기상청 API 호출
├── .env                           # API 키 (개인)
├── data/
│   ├── events.md                  # 연간 이벤트 캘린더
│   ├── weather.json               # 날씨 API 결과
│   └── trends.json                # DataLab API 결과
├── 가설검증_통합결과.xlsx           # 상권별 매출 경향 데이터
└── outputs/                       # 최종 HTML 저장
```
