# SAAI 스토어레터 주간 뉴스레터 스킬

편의점 점주용 주간 뉴스레터(스토어레터) 자동 생성 파이프라인.

---

## 🚀 빠른 사용법

1. Grok에 X 트렌드 프롬프트 3회 실행 (`grok-prompt.md` 전문 사용)
2. IG 피드 DevTools Console에서 `instagram-script.js` 실행
3. Claude 채팅에:

```
/newsletter-weekly

YYYY-MM-DD(요일) 발행 스토어레터 시작.

[Grok 결과 3회분]
...

[IG 피드 긁기 결과]
...
```

4. Claude가 취합·DataLab·기사 검증·HTML 작성까지 자동 진행
5. 출력: `~/Desktop/saai-newsletter/outputs/newsletter-YYYY-MM-DD-stibee.html`
6. 클립보드에 자동 복사 → Stibee에 Cmd+V

---

## 📁 스킬 파일 구성

| 파일 | 역할 |
|---|---|
| `SKILL.md` | 전체 파이프라인 (진입점) |
| `template.html` | HTML 템플릿 (MODULE 2/5B/4/5A + 피드백·푸터) |
| `design-rules.md` | HTML id 매핑·디자인 금지 사항 |
| `quality-rules.md` | 콘텐츠 품질 기준·톤·금지 표현 |
| `grok-prompt.md` | Grok X 검색 프롬프트 원본 |
| `instagram-script.js` | IG 피드 긁기 Console 스크립트 |

---

## 🏢 팀원이 이 스킬 쓰려면

### 1. 스킬 폴더 복사
```bash
# 원본 소유자가 압축
cd ~/.claude/skills
zip -r newsletter-weekly.zip newsletter-weekly/

# 받은 사람이 설치
unzip newsletter-weekly.zip -d ~/.claude/skills/
```

또는 GitHub 레포로 관리:
```bash
# 받는 쪽
git clone https://github.com/<org>/saai-skills.git ~/saai-skills
ln -s ~/saai-skills/newsletter-weekly ~/.claude/skills/newsletter-weekly
```

### 2. 프로젝트 폴더도 별도 설치 필요

스킬만으로는 안 돌아감. 아래 프로젝트 폴더가 **`~/Desktop/saai-newsletter/`에 동일 경로로** 있어야 함:

```
~/Desktop/saai-newsletter/
├── fetch_naver_trend.py           # DataLab API
├── fetch_weather.py               # 기상청 API
├── .env                           # 개별 API 키 ⚠️
├── data/
│   ├── events.md                  # 연간 이벤트 캘린더
│   ├── weather.json               # (자동 생성)
│   └── trends.json                # (자동 생성)
├── 가설검증_통합결과.xlsx
└── outputs/                       # 최종 HTML 저장
```

### 3. `.env` 본인 발급 필수

팀원도 각자 API 키 발급해서 `.env` 만들어야 함:

```bash
NAVER_CLIENT_ID=xxx
NAVER_CLIENT_SECRET=xxx
KMA_API_KEY=xxx
```

- **NAVER DataLab**: https://developers.naver.com/apps/#/register
- **기상청 KMA**: https://www.data.go.kr/iim/api/selectAPIAcountView.do (MidFcstInfoService·WthrWrnInfoService 신청)

**공유 금지**: `.env`는 Git에 올리지 말 것 (`.gitignore` 필수).

---

## 🔗 관련 스킬

- **`newsletter-html-rules`**: 이미 작성된 HTML을 수정만 할 때 사용 (이 스킬은 HTML 룰만 로드). `newsletter-weekly`는 전체 파이프라인이라 HTML 룰까지 포함.

---

## 📝 유지보수

스킬 업데이트 시 `SKILL.md` + 관련 파일만 수정 → 팀원에게 다시 공유.

품질 기준이나 디자인 룰 변경사항은 `quality-rules.md` / `design-rules.md`에만 반영하면 `SKILL.md`에 자동 전파 (파일 참조 구조).
