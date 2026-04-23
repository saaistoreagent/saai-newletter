# 스토어레터 주간 뉴스레터 작성 가이드

> 이 문서 하나만 있으면 팀원 누구나 동일한 품질의 뉴스레터를 만들 수 있어요.
> 소요 시간: **약 1시간** (사용자 30분 + Claude 20~40분)

---

## 🏁 처음 1회 세팅

팀에 처음 합류한 사람만 한 번 하면 됩니다.

```bash
# 1. 레포 clone
cd ~/Desktop
git clone https://github.com/saaistoreagent/saai-newletter.git saai-newsletter

# 2. Python 패키지 설치
cd ~/Desktop/saai-newsletter
pip3 install requests python-dotenv openpyxl

# 3. API 키 설정
#    노션 [SAAI 뉴스레터 공용 환경변수] 페이지에서 키 복사
#    → saai-newsletter 폴더에 .env 파일 만들어 아래 내용 저장
#
#    NAVER_CLIENT_ID=xxx
#    NAVER_CLIENT_SECRET=xxx
#    KMA_API_KEY=xxx
```

⚠️ **`.env`는 Git에 올리면 안 됨** (이미 `.gitignore`에 포함됨)

---

## 📋 전체 흐름 한눈에

```
[사용자 수집]               [Claude 자동]              [사용자 마무리]
                                                             
1. Grok 3회 실행  ─┐                                         
2. 인스타 긁기    ─┼─►  3. Claude가 취합·검증·HTML 생성  ─►  4. 리뷰·발송
(30분 내외)          │                  (20~40분)                   (15분)
                     │
(선택) 공식 SNS 포스트 URL
```

---

## STEP 1. Grok에서 X 트렌드 수집 (사용자 · 약 15분)

### 1-1. [Grok](https://grok.com) 접속

### 1-2. 아래 프롬프트에서 **`YYYY-MM-DD` 부분만 교체** 후 붙여넣기
- **시작일**: 발행일 기준 14일 전
- **종료일**: 발행일 전날

### 1-3. 같은 프롬프트로 **3번 반복 실행** (검색 결과 랜덤이라 놓치는 키워드 보완용)

<details>
<summary><b>📋 Grok 프롬프트 전문 (클릭해서 복사)</b></summary>

```
너는 한국 편의점 점주를 위한 실시간 트렌드 신호 탐지 전문 AI야.
반드시 실시간 X(트위터) 검색 도구만 사용해서 답변해야 해.
(x_keyword_search, x_semantic_search, x_thread_fetch, x_user_search 등을 최소 15개 이상 병렬 호출로 적극 활용, 교차 검증 필수)
조사 기간 (절대 위반 금지): 최근 2주 (예: since:2026-04-08 until:2026-04-22)
→ 모든 검색에 since:YYYY-MM-DD until:YYYY-MM-DD (keyword_search) 또는 from_date/to_date (semantic_search) 반드시 적용

필수 3대 조건 (모두 충족해야만 포함, 단 아래 완화 규칙 적용)
1. 참여도 상향: min_retweets:10 이상 또는 min_faves:100 이상
   (초반 신상·급성장 포스트는 min_faves:60까지 완화 가능하나, 퍼짐·긍정성 반드시 검증)
2. 퍼짐 확인 (완화):
   * 서로 다른 계정 3개 이상에서 RT·인용·답글로 확산된 것
   * 또는 단일 인플루언서 계정의 신상 발표 포스트라도 min_faves:300 이상 + 서로 다른 유저 reply/quote 15개 이상 확인된 경우 허용
     (단일 계정·RT 5회 미만은 여전히 무조건 제외)
3. 긍정성 필터 (최우선): 포스트에 아래 키워드 하나 이상 반드시 포함
   '맛있', '기대', '신상', '출시', '사러감', '인증', '추천', '구매', '핫', '미쳤다', '최애', '정식출시', '나온다고', '돌던데', '사야지', '콜라보', '한정', '선출시', '무조건 사먹을', '달려갈', '팬덤', '최애 추가', '대박', '기욤', 'ㅁㅊ'
   부정 표현(맛없, 짜바리, 개새키, 실격, 피함, 후회, 불호, 최악 등)이 주를 이루면 무조건 제외

강제 병렬 검색 키워드 (무조건 실행, 최소 15개 이상)
아래 조합으로 x_keyword_search 최소 10개 + x_semantic_search 최소 5개 병렬 호출 (총 15개 이상):

* (편의점 OR CU OR GS25 OR 세븐일레븐) (콜라보 OR 아이돌 OR 캐릭터) min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (편의점 OR CU OR GS25 OR 세븐일레븐) (신상 OR 디저트 OR 간식) min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (콜라보 OR 한정 OR 선출시) (디저트 OR 빵 OR 과자 OR 음료) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (아이돌 OR 팬덤) (편의점 OR 콜라보) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (편의점 OR CU OR GS25 OR 세븐일레븐) (신상 OR 디저트 OR 간식 OR 콜라보) (맛있 OR 기대 OR 사야지 OR 미쳤다 OR 최애) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD -(맛없 OR 불호 OR 최악)
* (콜라보 OR 아이돌 OR 캐릭터 OR 셰프 OR 인플루언서) (편의점) (후기 OR 인증 OR 구매 OR 기대) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (편의점 OR CU OR GS25 OR 세븐일레븐) (품절 OR 가격 OR 공급 OR 이벤트 OR 스포츠 OR 콘서트 OR 컴백) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (디저트 OR 빵 OR 과자 OR 음료 OR 생활용품) (신상 OR 한정 OR 콜라보) min_retweets:10 OR min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD

추가 병렬 검색 (편의점 이름 없는 신상·디저트·올리브영→편의점 전환 신호 적극 포착)
* (콜라보 OR 신상 OR 한정 OR 선출시) (디저트 OR 빵 OR 과자 OR 음료 OR 스낵) min_faves:60 OR min_retweets:8 since:YYYY-MM-DD until:YYYY-MM-DD
* (디저트 OR 간식) (콜라보 OR 신상 OR 한정) (맛있 OR 기대 OR 미쳤다 OR 사야지 OR 최애 OR 인증) min_faves:60 since:YYYY-MM-DD until:YYYY-MM-DD
* (신상 OR 콜라보 OR 한정) (디저트 OR 빵 OR 과자 OR 음료) (후기 OR 기대 OR 인증 OR 입고 OR 예정 OR 곧) min_faves:100 since:YYYY-MM-DD until:YYYY-MM-DD
* (올리브영 OR 신상) (디저트 OR 간식 OR 콜라보) (편의점 OR CU OR GS25 OR 세븐일레븐 OR 입고) min_faves:80 since:YYYY-MM-DD until:YYYY-MM-DD
* (신상 OR 콜라보) (디저트 OR 간식) (대박 OR 기대 OR 사먹을 OR 미쳤다) min_faves:200 since:YYYY-MM-DD until:YYYY-MM-DD

Semantic Search (반드시 병렬 실행, 5개 이상)
* "편의점 신상 디저트 기대 후기" (from_date:YYYY-MM-DD, to_date:YYYY-MM-DD)
* "편의점 아이돌·캐릭터 콜라보"
* "프리미엄 디저트·변형 스낵 신상"
* "신상 디저트 콜라보 기대감·인증"
* "올리브영 신상 편의점 입고 예정"
* "디저트 간식 신상 기대 후기"

추가 강화 규칙
* 미출시·루머·올리브영 신상 단계라도 고참여·퍼짐·긍정 기대감이 확인되면 "출시 전 핫 트렌드" 또는 "올리브영→편의점 예상"으로 별도 표시하고 적극 포함
* 고참여 포스트 발견 즉시 x_thread_fetch 의무 실행 → 퍼짐·긍정 확산 최종 검증
* 편의점 이름 미등장 포스트도 적극 포함 (식품·디저트·간식·생활용품 카테고리라면 편의점 취급 가능 상품으로 판단)
* 카테고리 균형 유지: 식품·음료·디저트·간식·생활용품을 동등하게 스캔
* 반드시 커버해야 할 유형: 카페·자영업 선행 상품, 기존 상품 폭증, SNS·아이돌·셰프·캐릭터 콜라보, 인플루언서 신상 정보, 해외 유행 유입, 미출시 루머, 공급 이슈·품절, 이벤트(스포츠·콘서트·컴백·계절·공휴일) 등

분석 필수 항목
* 타깃 나이대 추정: 매 키워드마다 "10대 후반~20대 초반 여성 중심", "20~30대 성인"처럼 구체적으로 표기 (작성자 바이오 + 포스트 + 참여 패턴 교차 분석)
* 추천 상권 추정: 매 키워드마다 편의점 6개 상권 중 우선순위 표기 (학교앞 / 관광지 / 오피스 / 유흥가 / 역세권 / 주택가) → 근거 최소 2가지 이상 제시

결과 형식 (절대 변경 금지)
2026년 4월 X(트위터) 편의점 트렌드 신호 보고서
(조사 기간: 2026-04-08 ~ 2026-04-22, 고참여·퍼짐·긍정 확인된 키워드만)

#: 1
키워드: (키워드명)
언급 패턴: 4/XX부터 급증, 3일간 RT XX+·좋아요 XX+ 확산
타깃 나이대: XX대 XX 중심
추천 상권: 학교앞 1순위 / 관광지 2순위 — 근거2가지 이상
실제 X 포스트 URL: https://x.com/...
포스트 내용 요약 + 참여 수: "…(긍정 후기 요약)" RT XX, 좋아요 XX
(미출시·올리브영 신상 키워드는 "출시 전 핫 트렌드" 또는 "올리브영→편의점 예상" 표시 추가)

(찾은 만큼 전부 나열. 최소 15개 이상 확보. URL 없는 키워드는 제외)

편의점 점주님 활용 팁 (상권 유형별로 분리):
(기존 형식 그대로 + 미출시·예상 입고 상품은 "출시 전 재고 선점 추천" 별도 언급)
```

</details>

### 1-4. 3회분 결과 전체 복사해서 메모장·Notion에 임시 저장

---

## STEP 2. 인스타그램 피드 긁기 (사용자 · 약 5분)

### 2-1. 준비
- 본인 계정으로 `instagram.com` **웹** 로그인 (앱 아님)
- 아래 계정들 팔로우되어 있는지 확인 (팔로우 안 돼 있으면 피드에 안 뜸):
  - 편의점 공식: `gs25_official`, `7elevenkorea`, `cu_official`
  - 리뷰: `new__eats`, `omuk.official`, `tastynews`, `minwoo_dessert`
  - 매거진: `eateat.mag`, `knewnew.official`

### 2-2. 개발자 도구 열기
- Mac: `Cmd + Option + I`
- Windows: `F12`
- 상단 **Console** 탭 클릭
- 빨간 경고 뜨면 `allow pasting` 입력 후 엔터 (보안 확인용)

### 2-3. 아래 스크립트 전체 복사 → 콘솔에 붙여넣기 → 엔터

```javascript
(async () => {
  const posts = new Map();
  console.log('🔄 스크롤 시작 (약 50초 소요)...');
  for (let i = 0; i < 25; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 2000));
    document.querySelectorAll('article').forEach(a => {
      const l = a.querySelector('a[href*="/p/"],a[href*="/reel/"]');
      if (l && !posts.has(l.href)) posts.set(l.href, a.innerText);
    });
    console.log(`[${i+1}/25] 수집 ${posts.size}개`);
  }
  const text = Array.from(posts.entries())
    .map(([u,c]) => `--- ${u} ---\n${c}`).join('\n\n');
  window._igFeed = text;
  try {
    await navigator.clipboard.writeText(text);
    console.log(`✅ ${posts.size}개 포스트 클립보드 복사 완료. 채팅에 Cmd+V`);
  } catch (e) {
    console.log(`⚠️ 자동 복사 실패. 아래 명령 입력: copy(window._igFeed)`);
  }
})();
```

### 2-4. 50초 기다리기
- 콘솔에 `[1/25] 수집 X개` 순서로 찍힘
- 끝나면 `✅ N개 포스트 클립보드 복사 완료` 메시지
- 자동 복사 실패 시 → `copy(window._igFeed)` 한 줄 더 실행

### 2-5. 텍스트 저장
Grok 결과와 같은 메모장·Notion에 임시 저장

💡 **Tip**: 더 많은 포스트 원하면 페이지 새로고침 후 한 번 더 실행 (다른 포스트 섞여서 뜸)

---

## STEP 3. Claude에 전달 (사용자 · 약 5분)

### 3-1. 터미널에서 프로젝트 폴더로 이동 + Claude Code 실행

```bash
cd ~/Desktop/saai-newsletter
claude
```

### 3-2. 채팅창에 아래 형식대로 붙여넣기

```
/newsletter-weekly

2026-MM-DD(요일) 발행 스토어레터 시작.

━━━ Grok 결과 1회차 ━━━
(Grok 1회차 결과 전체 붙여넣기)

━━━ Grok 결과 2회차 ━━━
(Grok 2회차 결과 전체 붙여넣기)

━━━ Grok 결과 3회차 ━━━
(Grok 3회차 결과 전체 붙여넣기)

━━━ 인스타 피드 ━━━
(인스타 스크립트 결과 전체 붙여넣기)
```

### 3-3. (선택) 추가 정보 공유
작업 중 SNS에서 직접 본 공식 포스트·기사·사진이 있으면 **URL·캡션 복붙**해서 추가로 보내기.

---

## STEP 4. Claude 자동 처리 (20~40분)

사용자는 Claude 답변 보며 대기. 중간에 **확인 질문** 나올 수 있음:
- "이 SNS 애칭의 정식 상품명이 무엇인가요?"
- "이 트렌드를 메가트렌드로 분류할까요, 편의점 트렌드로 둘까요?"
- "이벤트 중 이 날짜는 범위 밖인데 포함할까요?"

### Claude가 내부적으로 하는 일 (참고용)
1. **취합·중복 제거** — Grok 3회 + IG 통합
2. **편의점 영향 필터** — 콜라보·선행 신호·품절 등 분류
3. **DataLab 조회** — `fetch_naver_trend.py`로 떡볶이 대비 검색량
4. **날씨·이벤트** — `fetch_weather.py` + `data/events.md`
5. **언론 기사 검증** — 카드별 가격·출시일 기사 원문 확인
6. **HTML 생성** — `outputs/newsletter-YYYY-MM-DD-stibee.html`

완료되면 **클립보드에 HTML 자동 복사**됨.

---

## STEP 5. 리뷰·발송 (사용자 · 약 15분)

### 5-1. 파일 열어서 확인
```bash
open outputs/newsletter-YYYY-MM-DD-stibee.html
```
- 브라우저에서 실제 렌더링 확인
- 어색한 문장·오타 있으면 Claude에 **"XX 부분 수정해줘"** 요청

### 5-2. Stibee 업로드
- Stibee 에디터에서 **HTML 편집 모드** → 클립보드 내용 붙여넣기 (Cmd+V)
- 제목: Claude가 추천해준 옵션 중 선택 (또는 직접 작성)
- 미리보기 → 발송

---

## 🚨 자주 발생하는 문제

### Q. Grok에서 검색 결과가 너무 적어요
- 최근 2주 범위 확인 (더 긴 기간 잡으면 잘 안 나옴)
- 프롬프트 수정하지 말고 그대로 3회 실행
- 발행 타이밍이 월요일~화요일이라면 결과 적을 수 있음 (주말 후 포스트 적음)

### Q. 인스타 스크립트 에러 나요
- **로그인 상태 확인** (비로그인이면 피드 로드 안 됨)
- **Cmd+Shift+R로 새로고침** 후 재시도
- **allow pasting** 입력 안 했을 가능성

### Q. Claude가 이상한 출처(루리웹·블로그)를 써요
- "언론사 기사로 교체해줘" 요청
- 기사 못 찾으면 출처 생략하라고 지시

### Q. 카드 개수가 너무 많아요/적어요
- "상위 N개만 남겨줘" 또는 "XX 카드 추가해줘"

---

## 📁 프로젝트 파일 위치

| 파일 | 역할 |
|---|---|
| `PIPELINE.md` | 이 문서 (작성 가이드) |
| `.claude/skills/newsletter-weekly/` | Claude 스킬 본체 |
| `fetch_naver_trend.py` | 네이버 DataLab API 호출 |
| `fetch_weather.py` | 기상청 API 호출 |
| `data/events.md` | 연간 이벤트 캘린더 |
| `가설검증_통합결과.xlsx` | 상권별 매출 경향 데이터 |
| `.env` | **개인 API 키** (Git 제외) |
| `outputs/` | 최종 HTML 저장 경로 |

---

## 🔗 참고 링크
- [네이버 데이터랩 API 신청](https://developers.naver.com/apps/#/register)
- [기상청 공공데이터포털](https://www.data.go.kr/iim/api/selectAPIAcountView.do)
- [떡볶이 지수 배경 설명](https://longblack.co/note/1942)
- [Stibee](https://stibee.com)

---

## ⚠️ 절대 금지 사항 (Claude·사용자 공통)

- 가격·출시일 추측으로 기재 (기사 원문 확인 필수)
- 루리웹·디시·블로그 출처 사용 (언론사 기사만)
- "호불호가 적어요", "10~20대가 찾아요" 주관적 추측
- 발행일 + 한 달 범위 밖 이벤트 포함
- `.env` 파일을 Git에 커밋 (API 키 유출)
