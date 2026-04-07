#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상품 x 상권 적합도 분석 (데이터 기반)

서울시 열린데이터광장 편의점 추정매출 708개 상권 실데이터에서
상권 유형별 연령/성별/시간대/요일 패턴을 추출하여 점수 산출.

사용법:
  python3 product_fit.py                      # 이번주 상품 목록
  python3 product_fit.py "두쫀쿠" "대학가"     # 특정 상권
  python3 product_fit.py "두쫀쿠"             # 전체 상권 비교
"""
import sys, json, os

BASE = os.path.dirname(__file__)
PATTERN_PATH = os.path.join(BASE, "data", "trade_area_patterns.json")
PRODUCT_PATH = os.path.join(BASE, "data", "product_analysis.json")
AREAS = ["오피스", "주택가", "대학가", "역세권", "관광지", "유흥가"]

# ── 1. 상권 패턴 로드 (실데이터) ──

def load_patterns():
    with open(PATTERN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PATTERNS = load_patterns()

# ── 2. 상품 속성 → 상권 매칭 점수 계산 ──

def calc_score(product, area, profile=None):
    """
    실데이터 기반 점수 계산.

    1. 상품의 타겟 연령 × 상권의 해당 연령 매출 비중
    2. 상품의 타겟 성별 × 상권의 해당 성별 매출 비중
    3. 상품의 소비 시간대 × 상권의 해당 시간대 매출 비중
    4. 바이럴/품절 보정
    5. 매장 고객층 매칭 보정 (profile 있을 때)
    """
    pat = PATTERNS.get(area)
    if not pat:
        return 50  # 데이터 없으면 중립

    score = 0
    weight_total = 0

    # --- (1) 연령 매칭 (가중치 40) ---
    age_target = product.get("target_age", "전연령")
    if age_target == "전연령":
        age_score = 50  # 중립
    else:
        # "2030" → 20대 + 30대 비중 합산
        age_score = 0
        matched = 0
        age_map = {"10": "age_10", "20": "age_20", "30": "age_30",
                   "40": "age_40", "50": "age_50", "60": "age_60"}
        for code, key in age_map.items():
            if code in age_target:
                age_score += pat[key]
                matched += 1
        if matched > 0:
            # 해당 연령 합산 비중을 점수로 변환 (0~100)
            # 전체 평균이 ~20%일 때, 37%면 높은 거
            age_score = min(100, age_score * 2)  # 비중% × 2 = 점수
        else:
            age_score = 50
    score += age_score * 40
    weight_total += 40

    # --- (2) 성별 매칭 (가중치 20) ---
    gender_target = product.get("target_gender", "전체")
    if gender_target == "전체":
        gender_score = 50
    elif gender_target == "여성":
        gender_score = min(100, pat["female"] * 2)
    elif gender_target == "남성":
        gender_score = min(100, pat["male"] * 2)
    else:
        gender_score = 50
    score += gender_score * 20
    weight_total += 20

    # --- (3) 시간대 매칭 (가중치 20) ---
    category = product.get("category", "")
    # 카테고리별 피크 시간대 매핑
    tz_map = {
        "도시락/간편식": ["tz_11_14", "tz_06_11"],      # 점심 + 아침
        "음료/커피": ["tz_06_11", "tz_11_14", "tz_14_17"],  # 아침~오후
        "스낵/과자": ["tz_14_17", "tz_17_21"],           # 오후~저녁
        "주류": ["tz_17_21", "tz_21_24"],                # 저녁~심야
        "라면/즉석조리": ["tz_17_21", "tz_21_24"],       # 저녁~심야
        "아이스크림": ["tz_14_17", "tz_17_21"],          # 오후~저녁
        "빵/디저트": ["tz_11_14", "tz_14_17"],           # 점심~오후
        "디저트": ["tz_11_14", "tz_14_17"],
        "콜라보/한정판": ["tz_14_17", "tz_17_21"],       # 오후~저녁
        "생활용품": ["tz_17_21", "tz_21_24"],            # 저녁~심야
    }
    tz_keys = tz_map.get(category, ["tz_14_17", "tz_17_21"])
    tz_pct = sum(pat[k] for k in tz_keys)
    tz_score = min(100, tz_pct * 2)
    score += tz_score * 20
    weight_total += 20

    # --- (4) 주중/주말 (가중치 10) ---
    # 관광지/대학가는 주말 비중 높으면 시즌 상품에 유리
    wk_score = 50
    if category in ["콜라보/한정판", "아이스크림"]:
        wk_score = min(100, pat["weekend"] * 3)
    elif category in ["도시락/간편식", "음료/커피"]:
        wk_score = min(100, pat["weekday"] * 1.2)
    score += wk_score * 10
    weight_total += 10

    # --- (5) 바이럴/품절 보정 (가중치 10) ---
    viral = product.get("viral", "low")
    viral_score = {"high": 80, "medium": 50, "low": 30}.get(viral, 50)
    # 대학가/관광지는 바이럴에 더 민감 (20대 비중 반영)
    if viral == "high" and pat["age_20"] > 25:
        viral_score = 95
    score += viral_score * 10
    weight_total += 10

    base = round(score / weight_total)

    # --- (6) 매장 고객층 보정 ---
    if profile:
        boost = 0
        # 연령 매칭
        my_ages = profile.get("customers", [])
        if age_target != "전연령" and my_ages:
            age_hit = False
            for c in my_ages:
                decade = c.replace("대", "").replace("+", "")
                if decade in age_target:
                    age_hit = True
            boost += 3 if age_hit else -3

        # 성별 매칭
        my_gender = profile.get("gender", "비슷")
        if gender_target != "전체" and my_gender != "비슷":
            if (gender_target == "여성" and my_gender == "여성 위주") or \
               (gender_target == "남성" and my_gender == "남성 위주"):
                boost += 2
            else:
                boost -= 2
        base = max(0, min(100, base + boost))

    return base


# ── 3. JSON 기반 출력 (product_analysis.json 있을 때) ──

def load_products():
    if not os.path.exists(PRODUCT_PATH):
        return {}
    with open(PRODUCT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["keyword"]: p for p in data.get("products", [])}

def find_product(products, query):
    q = query.lower()
    for name, p in products.items():
        if q in name.lower() or name.lower() in q:
            return p
    return None

# ── 4. 출력 ──

def icon(sc):
    if sc >= 80: return "\U0001f7e2"
    if sc >= 60: return "\U0001f7e1"
    if sc >= 40: return "\U0001f7e0"
    return "\U0001f534"

def grade(sc):
    if sc >= 80: return "강력 추천", "적극 발주하세요"
    if sc >= 60: return "추천", "소량 입점 후 반응 보세요"
    if sc >= 40: return "보통", "기존 재고 소진 위주로 운영하세요"
    return "비추천", "이 상권에선 수요가 적어요"

def show_single(p, area):
    sc = calc_score(p, area)
    g, act = grade(sc)
    pat = PATTERNS[area]

    print()
    print("=" * 55)
    print(f"  \U0001f3ea \"{p['keyword']}\" x {area}  [{sc}점 {icon(sc)} {g}]")
    print("=" * 55)
    print(f"  카테고리 : {p.get('category','?')}")
    if p.get('store'):
        print(f"  판매처   : {p['store']}{' (단독)' if p.get('store_exclusive') else ''}")
    if p.get('price'):
        print(f"  가격     : {p['price']:,}원")
    print(f"  타겟     : {p.get('target_age','?')} {p.get('target_gender','?')}")
    print(f"  화제성   : {p.get('viral','?')} | 트렌드: {p.get('trend','?')}")
    print()

    # 점수 근거
    print(f"  [점수 근거 - {area} 상권 실데이터]")
    at = p.get('target_age', '전연령')
    if at != '전연령':
        age_keys = {"10":"age_10","20":"age_20","30":"age_30","40":"age_40","50":"age_50","60":"age_60"}
        matched_ages = [(k,v) for k,v in age_keys.items() if k in at]
        age_pct = sum(pat[v] for _,v in matched_ages)
        print(f"    타겟 연령({at}) 매출 비중: {age_pct:.1f}%")

    gt = p.get('target_gender', '전체')
    if gt == '여성':
        print(f"    여성 매출 비중: {pat['female']:.1f}%")
    elif gt == '남성':
        print(f"    남성 매출 비중: {pat['male']:.1f}%")

    print(f"    주중/주말: {pat['weekday']:.1f}% / {pat['weekend']:.1f}%")
    print()

    # 액션
    if p.get('action', {}).get(area):
        print(f"  \U0001f4a1 {p['action'][area]}")
    else:
        print(f"  \U0001f4a1 {act}")
    if p.get('warning'):
        print(f"  \u26a0\ufe0f  {p['warning']}")
    print()

    # 상권별 비교
    print(f"  \U0001f4c8 상권별 비교")
    scores = {a: calc_score(p, a) for a in AREAS}
    for a, s in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bar = "\u2588" * (s // 5)
        mark = " \u25c0" if a == area else ""
        print(f"     {a:5s} {s:3d}점 {bar}{mark}")
    print()


def show_all(p):
    print()
    print("=" * 55)
    print(f"  \U0001f3ea \"{p['keyword']}\" - 전체 상권")
    print("=" * 55)
    print(f"  {p.get('category','?')} | {p.get('store','?')}{' (단독)' if p.get('store_exclusive') else ''}")
    if p.get('warning'):
        print(f"  \u26a0\ufe0f  {p['warning']}")
    print()
    scores = {a: calc_score(p, a) for a in AREAS}
    for a, s in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        g, act = grade(s)
        bar = "\u2588" * (s // 5)
        print(f"  {icon(s)} {a:5s} {s:3d}점 {bar}")
        if p.get('action', {}).get(a):
            print(f"          \u2192 {p['action'][a]}")
        print()


def show_list(products):
    if not products:
        print("product_analysis.json이 없어요. 뉴스레터 먼저 생성하세요.")
        return
    with open(PRODUCT_PATH, "r", encoding="utf-8") as f:
        week = json.load(f).get("week", "?")
    print()
    print(f"  \U0001f4c5 {week} 상품 분석 ({len(products)}개)")
    print("=" * 55)
    for name, p in products.items():
        scores = {a: calc_score(p, a) for a in AREAS}
        best_a = max(scores, key=scores.get)
        best_s = scores[best_a]
        store = f"[{p['store']}]" if p.get('store') else ""
        print(f"  {icon(best_s)} {name} {store}")
        print(f"     최적: {best_a} ({best_s}점) | {p.get('viral','?')} 화제성")
    print()


if __name__ == "__main__":
    products = load_products()

    if len(sys.argv) < 2:
        show_list(products)
        sys.exit(0)

    kw = sys.argv[1]
    area = sys.argv[2] if len(sys.argv) >= 3 else None

    if area and area not in AREAS:
        print(f"지원 상권: {', '.join(AREAS)}")
        sys.exit(1)

    p = find_product(products, kw)
    if not p:
        print(f"'{kw}' 상품을 찾을 수 없어요. product_analysis.json을 확인하세요.")
        sys.exit(1)

    if area:
        show_single(p, area)
    else:
        show_all(p)
