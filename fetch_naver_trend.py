"""
네이버 데이터랩 검색어 트렌드 → data/trends.json 저장

사용법:
  # 개별 호출 (방향 판단용, 기본)
  python3 fetch_naver_trend.py "두쫀쿠,버터떡,종량제봉투"

  # 비교 호출 (규모 비교용, --compare 플래그)
  python3 fetch_naver_trend.py --compare "두쫀쿠,버터떡,종량제봉투,진밀면,하리보"

  # 키워드 파일에서 읽기
  python3 fetch_naver_trend.py
  python3 fetch_naver_trend.py --compare
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
API_URL = "https://openapi.naver.com/v1/datalab/search"

HEADERS = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
    "Content-Type": "application/json",
}


def fetch_trend(keyword_groups, start_date, end_date):
    """네이버 데이터랩 API 호출"""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": keyword_groups,
    }

    res = requests.post(API_URL, headers=HEADERS, json=body, timeout=10)
    res.raise_for_status()
    return res.json().get("results", [])


def judge_direction(data_points):
    """최근 7일 vs 이전 7일 평균 비교로 방향 판단"""
    if len(data_points) < 14:
        recent = data_points[-7:] if len(data_points) >= 7 else data_points
        earlier = data_points[:-7] if len(data_points) > 7 else data_points[:len(data_points)//2]
    else:
        recent = data_points[-7:]
        earlier = data_points[-14:-7]

    recent_avg = sum(d["ratio"] for d in recent) / len(recent) if recent else 0
    earlier_avg = sum(d["ratio"] for d in earlier) / len(earlier) if earlier else 0

    if earlier_avg == 0:
        return "상승" if recent_avg > 0 else "유지", recent_avg, earlier_avg

    change = (recent_avg - earlier_avg) / earlier_avg * 100

    if change >= 20:
        return "상승", recent_avg, earlier_avg
    elif change <= -20:
        return "하락", recent_avg, earlier_avg
    else:
        return "유지", recent_avg, earlier_avg


def run_individual(keywords):
    """개별 호출 — 각 키워드 자체 스케일(peak=100)로 방향 판단"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"[개별 모드] 조회 기간: {start_date} ~ {end_date}")
    print(f"키워드 {len(keywords)}개 → API {len(keywords)}회 호출\n")

    all_results = []

    for kw in keywords:
        try:
            groups = [{"groupName": kw, "keywords": [kw]}]
            results = fetch_trend(groups, start_date, end_date)
            r = results[0] if results else None

            if not r:
                print(f"  ? {kw}: 데이터 없음")
                all_results.append({
                    "keyword": kw, "direction": "확인불가",
                    "badge": "? 확인불가",
                    "recent_7d_avg": 0, "earlier_7d_avg": 0, "data": [],
                })
                continue

            data_points = r.get("data", [])
            direction, recent_avg, earlier_avg = judge_direction(data_points)
            badge = {"상승": "▲", "하락": "▼", "유지": "—"}[direction]
            print(f"  {badge} {kw}: {direction} (최근7일 {recent_avg:.1f} / 이전7일 {earlier_avg:.1f})")

            all_results.append({
                "keyword": kw,
                "direction": direction,
                "badge": f"{badge} {direction}",
                "recent_7d_avg": round(recent_avg, 2),
                "earlier_7d_avg": round(earlier_avg, 2),
                "data": data_points,
            })
        except Exception as e:
            print(f"  ❌ {kw}: {e}")
            all_results.append({
                "keyword": kw, "direction": "확인불가",
                "badge": "? 확인불가",
                "recent_7d_avg": 0, "earlier_7d_avg": 0, "data": [],
                "error": str(e),
            })

    return all_results, start_date, end_date


def run_compare(keywords):
    """비교 호출 — 5개씩 묶어서 같은 스케일로 규모 비교"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"[비교 모드] 조회 기간: {start_date} ~ {end_date}")
    print(f"키워드 {len(keywords)}개 → API {(len(keywords) + 4) // 5}회 호출 (5개씩)\n")

    all_results = []

    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        print(f"  --- 비교 그룹 {i//5 + 1}: {', '.join(batch)} ---")

        try:
            groups = [{"groupName": kw, "keywords": [kw]} for kw in batch]
            results = fetch_trend(groups, start_date, end_date)

            for r in results:
                kw = r["title"]
                data_points = r.get("data", [])
                direction, recent_avg, earlier_avg = judge_direction(data_points)
                badge = {"상승": "▲", "하락": "▼", "유지": "—"}[direction]
                print(f"  {badge} {kw}: {direction} (최근7일 {recent_avg:.1f} / 이전7일 {earlier_avg:.1f})")

                all_results.append({
                    "keyword": kw,
                    "direction": direction,
                    "badge": f"{badge} {direction}",
                    "recent_7d_avg": round(recent_avg, 2),
                    "earlier_7d_avg": round(earlier_avg, 2),
                    "compare_group": i // 5 + 1,
                    "data": data_points,
                })
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            for kw in batch:
                all_results.append({
                    "keyword": kw, "direction": "확인불가",
                    "badge": "? 확인불가",
                    "recent_7d_avg": 0, "earlier_7d_avg": 0, "data": [],
                    "error": str(e),
                })

    return all_results, start_date, end_date


def save_results(all_results, start_date, end_date, mode):
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mode": mode,
        "period": {"start": start_date, "end": end_date},
        "keywords": all_results,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/trends.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ data/trends.json 저장 완료 ({len(all_results)}개 키워드)")
    return output


if __name__ == "__main__":
    compare_mode = "--compare" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--compare"]

    if args:
        kws = [k.strip() for k in args[0].split(",") if k.strip()]
    elif os.path.exists("data/keywords.txt"):
        with open("data/keywords.txt", "r", encoding="utf-8") as f:
            kws = [line.strip() for line in f if line.strip()]
    else:
        print("사용법:")
        print("  python3 fetch_naver_trend.py \"키워드1,키워드2,키워드3\"")
        print("  python3 fetch_naver_trend.py --compare \"키워드1,키워드2,키워드3\"")
        sys.exit(1)

    if compare_mode:
        results, s, e = run_compare(kws)
        save_results(results, s, e, "compare")
    else:
        results, s, e = run_individual(kws)
        save_results(results, s, e, "individual")
