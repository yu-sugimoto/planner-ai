import sys
import json
import time
import random
from typing import Dict, Any
from datetime import datetime, timedelta

DATA_DIRECTORY = "data"


def load_data():
    with open(f"{DATA_DIRECTORY}/combined_with_info.json", "r", encoding="utf-8") as f:
        tourist_data = json.load(f)
    with open(f"{DATA_DIRECTORY}/transportation_costs.json", "r", encoding="utf-8") as f:
        transportation_data = json.load(f)
    with open(f"{DATA_DIRECTORY}/Osaka_to_all_spots.json", "r", encoding="utf-8") as f:
        osaka_transportation_data = json.load(f)
    return tourist_data, transportation_data, osaka_transportation_data


def build_transportation_lookup(transportation_data, valid_ids):
    trans_lookup = {}
    for record in transportation_data:
        start = record.get("start_destination_id")
        end = record.get("end_destination_id")
        if start in valid_ids and end in valid_ids:
            trans_lookup[(start, end)] = record
    return trans_lookup


def extract_osaka_records(osaka_transportation_data):
    """
    Osaka_to_all_spots.json のデータ形式がリストの場合はそのまま、
    辞書の場合は値（リスト）をすべて結合して返す。
    """
    if isinstance(osaka_transportation_data, dict):
        records = []
        for key, value in osaka_transportation_data.items():
            if isinstance(value, list):
                records.extend(value)
            else:
                records.append(value)
        return records
    return osaka_transportation_data


def build_osaka_transportation_lookup(osaka_transportation_data, valid_ids):
    osaka_lookup = {}
    records = extract_osaka_records(osaka_transportation_data)
    for record in records:
        start = record.get("start_destination_id")
        end = record.get("end_destination_id")
        try:
            start = int(start)
            end = int(end)
        except:
            continue
        if start == 0 and end in valid_ids:
            osaka_lookup[(start, end)] = record
    return osaka_lookup


def build_osaka_return_lookup(osaka_transportation_data, valid_ids):
    """
    大阪への帰り用の移動情報を作成する。元データは大阪→観光地の情報なので、キーを反転して (観光地, 0) とする。
    """
    osaka_return = {}
    # 簡易的な実装（データがリストの場合を想定）
    records = extract_osaka_records(osaka_transportation_data)
    for record in records:
        start = record.get("start_destination_id")
        end = record.get("end_destination_id")
        try:
            start = int(start)
            end = int(end)
        except:
            continue
        if start == 0 and end in valid_ids:
            osaka_return[(end, 0)] = record
    return osaka_return


def get_min_hotel_travel_time(from_id: int, trans_lookup: Dict, dest_by_id: Dict[int, Any], visited: set) -> int:
    """
    指定の施設（from_id）から、未訪問のホテル（ishotel:true）への最小移動時間を返す。
    移動情報がない場合は大きな値（例:1000000）を返す。
    """
    min_time = 1000000
    for dest in dest_by_id.values():
        if dest.get("ishotel") and dest["id"] not in visited:
            key = (from_id, dest["id"])
            if key in trans_lookup:
                travel_time = trans_lookup[key].get(
                    "transportation_time", 1000000)
                if travel_time < min_time:
                    min_time = travel_time
    return min_time


def select_hotel_candidate(
    current_dest: int,
    current_time: int,
    osaka_lookup: Dict,
    trans_lookup: Dict,
    dest_by_id: Dict[int, Any],
    visited: set,
    remaining_budget: int,
    sightseeing_end_time: int,
    day_total_time: int,
) -> Dict:
    """
    現在地から未訪問のホテル候補の中から、ホテル到着時刻が指定ウィンドウ内（[sightseeing_end_time, day_total_time]）になるものを選ぶ。
    複数候補があれば移動費用が最小のものを返す。
    """
    candidate = None
    for dest in dest_by_id.values():
        if not dest.get("ishotel"):
            continue
        if dest["id"] in visited:
            continue
        if current_dest == 0:
            key = (0, dest["id"])
            lookup = osaka_lookup
        else:
            key = (current_dest, dest["id"])
            lookup = trans_lookup
        if key not in lookup:
            continue
        travel = lookup[key]
        travel_time = travel.get("transportation_time", 1000000)
        travel_cost = travel.get("transportation_fare", 1000000)
        departure_offset = current_time
        arrival_offset = current_time + travel_time
        if arrival_offset < sightseeing_end_time or arrival_offset > day_total_time:
            continue
        total_cost = travel_cost + (dest.get("fare") or 0)
        if total_cost > remaining_budget:
            continue
        candidate_info = {
            "destination_id": dest["id"],
            "departure_offset": departure_offset,
            "travel_cost": travel_cost,
            "visit_cost": dest.get("fare") or 0,
            "travel_time": travel_time,
            "visit_time": 0,  # ホテルの場合、滞在時間は必要に応じて固定値に変更可
            "arrival_offset": arrival_offset,
            "total_cost": total_cost,
            "transportation_method": travel.get("transportation_method"),
        }
        if candidate is None:
            candidate = candidate_info
        else:
            # ランダム要素を追加：40%の確率で新しい候補を採用
            if random.random() < 0.4:
                candidate = candidate_info
            else:
                if candidate_info["travel_cost"] < candidate["travel_cost"]:
                    candidate = candidate_info
    return candidate


def select_return_trip(
    current_dest: int,
    current_time: int,
    osaka_return_lookup: Dict,
    remaining_budget: int,
    day_total_time: int,
) -> Dict:
    """
    最終日、現在地から大阪（ID:0）への帰りの移動候補を選ぶ。
    """
    key = (current_dest, 0)
    if key not in osaka_return_lookup:
        return None
    record = osaka_return_lookup[key]
    travel_time = record.get("transportation_time", 1000000)
    travel_cost = record.get("transportation_fare", 1000000)
    departure_offset = current_time
    arrival_offset = current_time + travel_time
    if travel_cost > remaining_budget:
        return None
    return {
        "destination_id": 0,  # 大阪駅のID
        "departure_offset": departure_offset,
        "travel_cost": travel_cost,
        "visit_cost": 0,
        "travel_time": travel_time,
        "visit_time": 0,
        "arrival_offset": arrival_offset,
        "total_cost": travel_cost,
        "transportation_method": record.get("transportation_method"),
    }


def evaluate_plan(itinerary_json: str, budget: int, days: int) -> float:
    """
    旅行プランを評価する関数。

    評価値 = (spots × 50) + (予算 - 総費用) / 人数
    旅行プランは、{"route": [stop, ...]} の形式の JSON 文字列を想定。
    各 stop は "total_cost" を持つものとする。
    total_cost / budget が 1.0 に近いほど高評価となる。

    Args:
        itinerary_json (str): 旅行プランの JSON 文字列
        budget (int): 予算
        people (int): 人数

    Returns:
        float: 評価値
    """
    try:
        itinerary = json.loads(itinerary_json)
    except Exception as e:
        print(f"Error parsing itinerary JSON: {e}")
        return -9999.0

    route = itinerary.get("route", [])
    total_cost = sum(spot.get("total_cost", 0) for spot in route)
    # print(f"len(route): {len(route)}, total_cost: {total_cost} budget: {budget}")
    score = len(route) * 10 + (total_cost / budget) * 100
    return score


def plan_itenerary(city: str, budget: int, days: int, people: int, start_datetime_str: str) -> json:
    """
    departure_time: チェックアウト時刻（分換算、例:10:00→600）
    ホテルのチェックインは18:00～20:00（1080～1200分）に合わせるため、相対時間として利用可能時間は:
      day_total_time = 1400 - departure_time  （例: departure_time=600 → 800分）
      sightseeing_end_time = 1080 - departure_time  （例: departure_time=600 → 480分）
    start_datetime_str: シミュレーション開始の絶対時刻（ISO形式）

    """
    departure_time = datetime.fromisoformat(
        start_datetime_str).hour * 60 + datetime.fromisoformat(start_datetime_str).minute
    # 利用可能な相対時間（分）
    day_total_time = 1400 - departure_time
    sightseeing_end_time = 1080 - departure_time

    best_itinerary = None
    best_score = -1000000


    tourist_data, transportation_data, osaka_transportation_data = load_data()
    if city not in tourist_data:
        raise ValueError(f"{city} のデータが見つかりません。")
    # 2秒で最も高い評価値を持つプランを出力
    start = time.perf_counter()
    destinations = tourist_data[city]
    dest_by_id = {dest["id"]: dest for dest in destinations}
    valid_ids = set(dest_by_id.keys())
    trans_lookup = build_transportation_lookup(
        transportation_data, valid_ids)
    osaka_lookup = build_osaka_transportation_lookup(
        osaka_transportation_data, valid_ids)
    osaka_return_lookup = build_osaka_return_lookup(
        osaka_transportation_data, valid_ids)

    counter = 0

    while time.perf_counter() - start < 1.5:
        # 毎回異なるプランを生成するため、観光地の順番をランダムにシャッフル
        #print(f"counter: {counter}")
        #counter += 1
        
        random.shuffle(destinations)

        # 大阪駅の情報（ID:0）を定義
        osaka_station = {
            "id": 0,
            "name": "大阪駅",
            "location": {"lat": 34.702485, "lng": 135.495951},
            "fare": 0,
            "staytime": 0,
            "ishotel": False
        }

        itinerary = []  # 各日のプラン（リストのリスト）
        remaining_budget = budget
        visited = set()  # 観光施設（ホテル以外）は一度訪れたら除外

        # 各日ごとにシミュレーション（※複数日対応の場合、各日のオフセットを後で加算）
        for day in range(days):
            day_plan = []
            current_time = 0  # その日の相対経過時間（分）
            current_dest = 0  # 初日は大阪（ID:0）から出発
            # 観光施設（ホテル以外）の訪問を追加
            while True:
                candidate = None
                for dest in destinations:
                    if dest.get("ishotel"):
                        continue
                    if dest["id"] in visited:
                        continue
                    if current_dest == 0:
                        key = (0, dest["id"])
                        lookup = osaka_lookup
                    else:
                        key = (current_dest, dest["id"])
                        lookup = trans_lookup
                    if key not in lookup:
                        continue
                    travel = lookup[key]
                    travel_time = travel.get("transportation_time", 1000000)
                    travel_cost = travel.get("transportation_fare", 1000000)
                    departure_offset = current_time
                    arrival_offset = current_time + travel_time
                    if arrival_offset >= sightseeing_end_time:
                        continue
                    visit_time = dest.get("staytime") or 0
                    total_time = travel_time + visit_time
                    min_hotel_time = get_min_hotel_travel_time(
                        dest["id"], trans_lookup, dest_by_id, visited)
                    if current_time + total_time + min_hotel_time > day_total_time:
                        continue
                    total_cost = (
                        travel_cost + (dest.get("fare") or 0)) * people
                    if total_cost > remaining_budget:
                        continue
                    candidate_info = {
                        "destination_id": dest["id"],
                        "departure_offset": current_time,
                        "travel_cost": travel_cost,
                        "visit_cost": dest.get("fare") or 0,
                        "travel_time": travel_time,
                        "visit_time": visit_time,
                        "arrival_offset": arrival_offset,
                        "total_cost": total_cost,
                        "transportation_method": travel.get("transportation_method"),
                    }
                    if candidate is None:
                        candidate = candidate_info
                    else:
                        # ランダム要素を追加：50%の確率で新しい候補を採用
                        if random.random() < 0.5:
                            candidate = candidate_info
                        else:
                            if candidate_info["travel_cost"] < candidate["travel_cost"]:
                                candidate = candidate_info
                            elif candidate_info["travel_cost"] == candidate["travel_cost"]:
                                if candidate_info["visit_cost"] > candidate["visit_cost"]:
                                    candidate = candidate_info
                if candidate is None:
                    break
                day_plan.append(candidate)
                visited.add(candidate["destination_id"])
                current_time = candidate["arrival_offset"] + \
                    candidate["visit_time"]
                remaining_budget -= candidate["total_cost"]
                current_dest = candidate["destination_id"]

            # 最終日の場合は大阪への帰りを追加
            if day == days - 1:
                return_candidate = select_return_trip(
                    current_dest, current_time, osaka_return_lookup, remaining_budget, day_total_time)
                if return_candidate is not None:
                    day_plan.append(return_candidate)
                    remaining_budget -= return_candidate["total_cost"]
                    current_time = return_candidate["arrival_offset"]
                    current_dest = 0
            else:
                # それ以外の日はホテルへのチェックインを追加
                hotel_candidate = select_hotel_candidate(
                    current_dest, current_time, osaka_lookup, trans_lookup, dest_by_id, visited, remaining_budget, sightseeing_end_time, day_total_time)
                if hotel_candidate is not None:
                    day_plan.append(hotel_candidate)
                    visited.add(hotel_candidate["destination_id"])
                    current_time = hotel_candidate["arrival_offset"]
                    remaining_budget -= (
                        hotel_candidate["travel_cost"] + hotel_candidate["visit_cost"]) * people
                    current_dest = hotel_candidate["destination_id"]
            itinerary.append(day_plan)
            # もし観光施設（ホテル以外）すべて訪問済みなら終了
            nonhotel_ids = {d["id"]
                            for d in destinations if not d.get("ishotel")}
            if visited.intersection(nonhotel_ids) == nonhotel_ids:
                break

        # 最終目的地が大阪駅（0）でない場合は空のルートを返す
        if len(itinerary) == 0 or len(itinerary[-1]) == 0 or itinerary[-1][-1]["destination_id"] != 0:
            return json.dumps({"route": []}, ensure_ascii=False)

        # 各日のプランを平坦化し、各日ごとのオフセット（1440分＝1日）を加算
        flat_route = []
        for day_index, day_plan in enumerate(itinerary):
            day_offset = day_index * 1440
            for stop in day_plan:
                stop["departure_offset"] += day_offset
                stop["arrival_offset"] += day_offset
                flat_route.append(stop)

        # ベースの開始日時（ISO形式）から各停留所の出発・到着時刻を算出
        base_dt = datetime.fromisoformat(start_datetime_str)
        # 各停留所の出力形式に変換（lat, lng, name, total_cost, transportation_method, departure_time, arrival_time, stay_duration_minutes）
        # 目的地情報は、id==0 の場合は osaka_station、それ以外は dest_by_id から取得
        dest_mapping = {**dest_by_id, 0: osaka_station}
        route_output = []
        for stop in flat_route:
            dest_id = stop["destination_id"]
            dest_info = dest_mapping.get(dest_id, {})
            output_stop = {
                "lat": dest_info.get("location", {}).get("lat", 0),
                "lng": dest_info.get("location", {}).get("lng", 0),
                "name": dest_info.get("japanese_name", dest_info.get("name", "不明")),
                "total_cost": stop["total_cost"],
                "transportation_method": stop["transportation_method"],
                "departure_time": (base_dt + timedelta(minutes=stop["departure_offset"])).isoformat(),
                "arrival_time": (base_dt + timedelta(minutes=stop["arrival_offset"])).isoformat(),
                "stay_duration_minutes": stop["visit_time"],
            }
            route_output.append(output_stop)
        final_output = {"route": route_output}

        # 評価値を算出
        score = evaluate_plan(json.dumps(
            final_output, ensure_ascii=False), budget, people)
        if score > best_score:
            # print(f"New best score: {score}")

            best_score = score
            best_itinerary = final_output

    return json.dumps(best_itinerary, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 例: python3 get_optimal_travel.py kobe 5000 1 2 "2025-03-11T15:00:00+09:00"
    import sys
    if len(sys.argv) != 6:
        print("Usage: python get_optimal_travel.py <city> <budget> <days>  <people> <start_datetime>")
        sys.exit(1)
    city = sys.argv[1]
    budget = int(sys.argv[2])
    days = int(sys.argv[3])
    people = int(sys.argv[4])
    start_datetime_str = sys.argv[5]    # 例: "2025-03-11T15:00:00+09:00"
    # print(f"detime: {departure_time}")
    result = plan_itenerary(city, budget, days, people, start_datetime_str)
    print(result)
    print(f"score: {evaluate_plan(result, budget, people)}")
