"""
기상청 중기예보 + 기상특보 → data/weather.json 저장
실행: KMA_API_KEY=키값 python3 fetch_weather.py
"""

import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KMA_API_KEY")
BASE_URL = "https://apis.data.go.kr/1360000"

REGION_CODES = {
    "수도권":  "11B00000",
    "강원":    "11D10000",
    "충청권":  "11C20000",
    "전라권":  "11F20000",
    "경상권":  "11H20000",
    "제주":    "11G00000",
}

TEMP_CODES = {
    "수도권":  "11B10101",  # 서울
    "강원":    "11D10101",  # 춘천
    "충청권":  "11C20401",  # 대전
    "전라권":  "11F20501",  # 광주
    "경상권":  "11H20201",  # 부산
    "제주":    "11G00201",  # 제주
}


def get_base_time():
    now = datetime.now()
    if now.hour < 6:
        base = now - timedelta(days=1)
        return base.strftime("%Y%m%d"), "1800"
    elif now.hour < 18:
        return now.strftime("%Y%m%d"), "0600"
    else:
        return now.strftime("%Y%m%d"), "1800"


def safe_get(url, params):
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    body = res.json().get("response", {}).get("body", {})
    if not body or not isinstance(body, dict):
        return {}
    items = body.get("items", {})
    if not items or not isinstance(items, dict):
        return {}
    item_list = items.get("item", [])
    return item_list[0] if item_list else {}


def fetch_land(reg_code, tmfc):
    return safe_get(f"{BASE_URL}/MidFcstInfoService/getMidLandFcst", {
        "serviceKey": API_KEY, "numOfRows": 1, "pageNo": 1,
        "dataType": "JSON", "regId": reg_code, "tmFc": tmfc,
    })


def fetch_temp(reg_code, tmfc):
    return safe_get(f"{BASE_URL}/MidFcstInfoService/getMidTa", {
        "serviceKey": API_KEY, "numOfRows": 1, "pageNo": 1,
        "dataType": "JSON", "regId": reg_code, "tmFc": tmfc,
    })


def fetch_warnings():
    try:
        res = requests.get(f"{BASE_URL}/WthrWrnInfoService/getWthrWrnList", params={
            "serviceKey": API_KEY, "numOfRows": 100, "pageNo": 1, "dataType": "JSON",
        }, timeout=10)
        res.raise_for_status()
        body = res.json().get("response", {}).get("body", {})
        if not body or not isinstance(body, dict):
            return []
        items = body.get("items", {})
        if not items or not isinstance(items, dict):
            return []
        all_items = items.get("item", [])
        # 해제 특보 제외 — 발효 중인 특보만 반환
        active = [w for w in all_items if "해제" not in w.get("title", "")]
        print(f"기상특보 전체 {len(all_items)}건 / 발효 중 {len(active)}건")
        return active
    except Exception:
        return []


def parse_condition(wf_str):
    mapping = {
        "맑음":           ("☀️",  "맑음"),
        "구름많고 비":    ("🌧",  "구름많고 비"),
        "구름많고 눈":    ("🌨",  "구름많고 눈"),
        "구름많고 비/눈": ("🌧",  "비/눈"),
        "구름많음":       ("⛅",  "구름 많음"),
        "흐리고 비":      ("🌧",  "비 예보"),
        "흐리고 눈":      ("🌨",  "눈 예보"),
        "흐리고 비/눈":   ("🌧",  "비/눈"),
        "흐림":           ("🌥",  "흐림"),
    }
    for key, val in mapping.items():
        if key in wf_str:
            return val
    return ("🌥", wf_str)


def check_warnings(region_name, warnings):
    keywords = {
        "수도권":  ["서울", "인천", "경기"],
        "강원":    ["강원"],
        "충청권":  ["충청", "대전", "세종"],
        "전라권":  ["전라", "광주"],
        "경상권":  ["경상", "부산", "대구", "울산"],
        "제주":    ["제주"],
    }.get(region_name, [])

    specials = []
    for w in warnings:
        field = w.get("areaName", "") + w.get("title", "")
        if any(k in field for k in keywords):
            for wtype in ["황사", "강풍", "대설", "폭설", "폭염", "한파", "호우", "태풍", "건조"]:
                if wtype in w.get("title", ""):
                    specials.append(wtype)
    return specials or None


def build_weather_json():
    base_date, base_time = get_base_time()
    tmfc = base_date + base_time

    base_dt = datetime.strptime(base_date, "%Y%m%d")
    start_dt = base_dt + timedelta(days=3)
    end_dt   = base_dt + timedelta(days=7)

    print(f"발표 기준: {base_date} {base_time}")
    print(f"예보 기간: {start_dt.strftime('%m/%d')} ~ {end_dt.strftime('%m/%d')}")

    warnings = fetch_warnings()
    print(f"기상특보 {len(warnings)}건 조회됨")

    result = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "base_time": f"{base_date} {base_time}",
        "period": {
            "start": start_dt.strftime("%Y-%m-%d"),
            "end":   end_dt.strftime("%Y-%m-%d"),
        },
        "regions": {}
    }

    for region_name, land_code in REGION_CODES.items():
        try:
            land = fetch_land(land_code, tmfc)
            temp = fetch_temp(TEMP_CODES[region_name], tmfc)

            # 4일 후 오전 기준 (API 최소 제공일이 4일 후부터)
            wf_str = land.get("wf4Am") or land.get("wf4") or "정보없음"
            icon, desc = parse_condition(wf_str)

            max_temp = temp.get("taMax4")
            min_temp = temp.get("taMin4")

            specials = check_warnings(region_name, warnings)
            if specials:
                if "황사" in specials:   icon = "🌫";  desc = f"{desc} · 황사"
                elif "대설" in specials: icon = "🌨";  desc = f"{desc} · 대설특보"
                elif "강풍" in specials: icon = "🌬️"; desc = f"{desc} · 강풍특보"
                elif "폭염" in specials: desc = f"{desc} · 폭염특보"
                elif "한파" in specials: desc = f"{desc} · 한파특보"
                elif "건조" in specials: desc = f"{desc} · 건조주의보"

            result["regions"][region_name] = {
                "max_temp": max_temp,
                "min_temp": min_temp,
                "condition": desc,
                "icon": icon,
                "rain_prob_am": land.get("rnSt4Am"),
                "rain_prob_pm": land.get("rnSt4Pm"),
                "specials": specials,
            }
            print(f"  ✅ {region_name}: {desc} 최고{max_temp}°/최저{min_temp}°")

        except Exception as e:
            print(f"  ❌ {region_name} 오류: {e}")
            result["regions"][region_name] = {
                "max_temp": None, "min_temp": None,
                "condition": "정보없음", "icon": "🌥", "specials": None,
            }

    os.makedirs("data", exist_ok=True)
    with open("data/weather.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n✅ data/weather.json 저장 완료")


if __name__ == "__main__":
    build_weather_json()
