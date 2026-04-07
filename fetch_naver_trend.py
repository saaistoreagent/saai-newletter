"""
네이버 데이터랩 검색어 트렌드 → data/trends.json 저장

사용법:
  # 기본 호출 (떡볶이 기준선 비교 + 방향 판단)
  python3 fetch_naver_trend.py "두쫀쿠,버터떡,종량제봉투"

  # 비교 호출 (규모 비교용, --compare 플래그)
  python3 fetch_naver_trend.py --compare "두쫀쿠,버터떡,종량제봉투,진밀면,하리보"

  # 기준 키워드 변경 (기본값: 떡볶이)
  python3 fetch_naver_trend.py --baseline "라면" "두쫀쿠,버터떡"

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
BASELINE_KEYWORD = "떡볶이"  # 꾸준한 수요 키워드 — 규모 비교 기준선

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


def judge_scale(keyword_avg, baseline_avg):
    """기준 키워드(떡볶이) 대비 검색 규모 판단

    편의점 신상/트렌드 상품은 떡볶이 같은 스테디셀러보다 검색량이 훨씬 적다.
    떡볶이의 30%만 되어도 대중 인지가 충분한 수준.
    """
    if baseline_avg == 0:
        return "확인불가", 0

    ratio = keyword_avg / baseline_avg * 100  # 떡볶이 = 100% 기준

    if ratio >= 30:
        return "트렌드", round(ratio, 1)
    elif ratio >= 10:
        return "주목", round(ratio, 1)
    elif ratio >= 3:
        return "성장중", round(ratio, 1)
    else:
        return "니치", round(ratio, 1)

SCALE_ICONS = {"트렌드": "🔥", "주목": "📈", "성장중": "🌱", "니치": "·", "확인불가": "?"}


def run_individual(keyword_groups, baseline=None):
    """기준선 비교 — 떡볶이와 같은 스케일에서 비교 + 자체 방향 판단

    keyword_groups: [{"name": "진밀면", "keywords": ["진밀면", "오뚜기 진밀면"]}, ...]
    """
    baseline = baseline or BASELINE_KEYWORD
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # 기준 키워드가 입력 목록에 있으면 제외
    keyword_groups = [g for g in keyword_groups if g["name"] != baseline]

    names = [g["name"] for g in keyword_groups]
    api_calls_batches = (len(keyword_groups) + 3) // 4
    api_calls_direction = len(keyword_groups)
    total_calls = api_calls_batches + api_calls_direction

    print(f"[기준선 비교 모드] 기준: {baseline}")
    print(f"조회 기간: {start_date} ~ {end_date}")
    print(f"키워드 {len(keyword_groups)}개 → API {total_calls}회 호출 (비교 {api_calls_batches} + 방향 {api_calls_direction})")

    # 그룹 키워드 표시
    for g in keyword_groups:
        if len(g["keywords"]) > 1:
            print(f"  📦 {g['name']} ← 합산: {', '.join(g['keywords'])}")
    print()

    # --- Step 1: 떡볶이와 함께 비교해서 규모 판단 ---
    scale_map = {}  # name → (scale_label, ratio)

    for i in range(0, len(keyword_groups), 4):
        batch = keyword_groups[i:i+4]
        batch_names = [g["name"] for g in batch]
        print(f"  --- 규모 비교 그룹 {i//4 + 1}: {baseline} vs {', '.join(batch_names)} ---")

        try:
            groups = [{"groupName": baseline, "keywords": [baseline]}]
            groups += [{"groupName": g["name"], "keywords": g["keywords"]} for g in batch]
            results = fetch_trend(groups, start_date, end_date)

            # 기준 키워드 평균 추출
            baseline_data = next((r for r in results if r["title"] == baseline), None)
            baseline_avg = 0
            if baseline_data and baseline_data.get("data"):
                bp = baseline_data["data"][-7:] if len(baseline_data["data"]) >= 7 else baseline_data["data"]
                baseline_avg = sum(d["ratio"] for d in bp) / len(bp) if bp else 0

            print(f"    {baseline} 최근7일 평균: {baseline_avg:.1f}")

            for r in results:
                name = r["title"]
                if name == baseline:
                    continue
                data_points = r.get("data", [])
                recent = data_points[-7:] if len(data_points) >= 7 else data_points
                kw_avg = sum(d["ratio"] for d in recent) / len(recent) if recent else 0
                scale, ratio = judge_scale(kw_avg, baseline_avg)
                scale_map[name] = (scale, ratio)
                icon = SCALE_ICONS[scale]
                print(f"    {icon} {name}: {scale} ({ratio:.1f}% vs {baseline})")

        except Exception as e:
            print(f"  ❌ 규모 비교 오류: {e}")
            for g in batch:
                scale_map[g["name"]] = ("확인불가", 0)

    # --- Step 2: 개별 그룹 호출로 방향 판단 (자체 스케일) ---
    print(f"\n  --- 방향 판단 (개별 호출) ---")
    all_results = []

    for g in keyword_groups:
        name = g["name"]
        try:
            groups = [{"groupName": name, "keywords": g["keywords"]}]
            results = fetch_trend(groups, start_date, end_date)
            r = results[0] if results else None

            if not r:
                scale, ratio = scale_map.get(name, ("확인불가", 0))
                print(f"  ? {name}: 데이터 없음")
                all_results.append({
                    "keyword": name, "search_terms": g["keywords"],
                    "direction": "확인불가",
                    "badge": "? 확인불가",
                    "scale": scale, "baseline_ratio": ratio,
                    "baseline": baseline,
                    "recent_7d_avg": 0, "earlier_7d_avg": 0, "data": [],
                })
                continue

            data_points = r.get("data", [])
            direction, recent_avg, earlier_avg = judge_direction(data_points)
            scale, ratio = scale_map.get(name, ("확인불가", 0))

            dir_badge = {"상승": "▲", "하락": "▼", "유지": "—"}[direction]
            scale_icon = SCALE_ICONS[scale]
            group_note = f" (합산: {', '.join(g['keywords'])})" if len(g["keywords"]) > 1 else ""
            print(f"  {scale_icon}{dir_badge} {name}: {scale}({ratio:.0f}%) {direction} (최근7일 {recent_avg:.1f} / 이전7일 {earlier_avg:.1f}){group_note}")

            all_results.append({
                "keyword": name,
                "search_terms": g["keywords"],
                "direction": direction,
                "badge": f"{dir_badge} {direction}",
                "scale": scale,
                "baseline_ratio": ratio,
                "baseline": baseline,
                "recent_7d_avg": round(recent_avg, 2),
                "earlier_7d_avg": round(earlier_avg, 2),
                "data": data_points,
            })
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            scale, ratio = scale_map.get(name, ("확인불가", 0))
            all_results.append({
                "keyword": name, "search_terms": g["keywords"],
                "direction": "확인불가",
                "badge": "? 확인불가",
                "scale": scale, "baseline_ratio": ratio,
                "baseline": baseline,
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


def parse_keyword_input(raw):
    """키워드 입력 파싱. 콜론(:)으로 묶인 것은 하나의 그룹으로 합산 조회.

    예: "진밀면:오뚜기 진밀면, 두쫀쿠, 왕뚜껑 국물라볶이"
    → [
        {"name": "진밀면", "keywords": ["진밀면", "오뚜기 진밀면"]},
        {"name": "두쫀쿠", "keywords": ["두쫀쿠"]},
        {"name": "왕뚜껑 국물라볶이", "keywords": ["왕뚜껑 국물라볶이"]},
      ]
    """
    groups = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = [p.strip() for p in item.split(":") if p.strip()]
        groups.append({
            "name": parts[0],  # 첫 번째가 대표명
            "keywords": parts,
        })
    return groups


if __name__ == "__main__":
    compare_mode = "--compare" in sys.argv
    baseline_kw = None

    # --baseline 파싱
    argv_clean = []
    skip_next = False
    for i, a in enumerate(sys.argv[1:]):
        if skip_next:
            skip_next = False
            continue
        if a == "--baseline" and i + 1 < len(sys.argv) - 1:
            baseline_kw = sys.argv[i + 2]
            skip_next = True
            continue
        if a in ("--compare",):
            continue
        argv_clean.append(a)

    if argv_clean:
        raw_input = argv_clean[0]
    elif os.path.exists("data/keywords.txt"):
        with open("data/keywords.txt", "r", encoding="utf-8") as f:
            raw_input = ",".join(line.strip() for line in f if line.strip())
    else:
        print("사용법:")
        print('  python3 fetch_naver_trend.py "키워드1,키워드2,키워드3"')
        print('  python3 fetch_naver_trend.py "진밀면:오뚜기 진밀면, 두쫀쿠"  # 콜론=합산')
        print('  python3 fetch_naver_trend.py --compare "키워드1,키워드2,키워드3"')
        print('  python3 fetch_naver_trend.py --baseline "라면" "키워드1,키워드2"')
        sys.exit(1)

    keyword_groups = parse_keyword_input(raw_input)

    if compare_mode:
        # compare 모드는 기존처럼 단순 키워드 리스트
        kws = [g["name"] for g in keyword_groups]
        results, s, e = run_compare(kws)
        save_results(results, s, e, "compare")
    else:
        results, s, e = run_individual(keyword_groups, baseline=baseline_kw)
        save_results(results, s, e, "baseline")
