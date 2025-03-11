import sys
import json
from typing import Dict, Any


DATA_DIRECTORY = "optimization/data"


def load_data():
    with open(f"{DATA_DIRECTORY}/combined_with_info.json", "r", encoding="utf-8") as f:
        tourist_data = json.load(f)
    with open(
        f"{DATA_DIRECTORY}/transportation_costs.json", "r", encoding="utf-8"
    ) as f:
        transportation_data = json.load(f)
    with open(f"{DATA_DIRECTORY}/Osaka_to_all_spots.json", "r", encoding="utf-8") as f:
        osaka_transportation_data = json.load(f)
    return tourist_data, transportation_data, osaka_transportation_data


def build_transportation_lookup(transportation_data, valid_ids):
    trans_lookup = {}
    # print(f"len(transportation_data): {len(transportation_data)}")
    # print(f"valid_ids: {valid_ids}")
    for record in transportation_data:
        start = record.get("start_destination_id")
        end = record.get("end_destination_id")
        if start in valid_ids and end in valid_ids:
            trans_lookup[(start, end)] = record
    # print(f"len(translookup): {len(trans_lookup)}")
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
    # print(f"records{records}")
    for record in records:
        start = record.get("start_destination_id")  # or record.get("startId")
        end = record.get("end_destination_id")  # or record.get("endId")
        # print(f"end: {end}")
        try:
            start = int(start)
            end = int(end)
        except:
            # print(f"invalid {start}, {end}")
            continue

        if start == 0 and end in valid_ids:
            osaka_lookup[(start, end)] = record
    return osaka_lookup


def build_osaka_return_lookup(osaka_transportation_data, valid_ids):
    osaka_return = {}
    records = extract_osaka_records(osaka_transportation_data)
    for record in records:
        start = record.get("start_destination_id") or record.get("startId")
        end = record.get("end_destination_id") or record.get("endId")
        try:
            start = int(start)
            end = int(end)
        except:
            continue
        if start == 0 and end in valid_ids:
            # 逆方向のキーを作成： (end, 0)
            osaka_return[(end, 0)] = record
    return osaka_return


def build_osaka_return_lookup(osaka_transportation_data, valid_ids):
    """
    大阪への帰り用の移動情報を作成する。元データは大阪→観光地の情報なので、キーを反転して (観光地, 0) とする。
    """
    osaka_return = {}
    for record in osaka_transportation_data:
        start = record.get("start_destination_id")
        end = record.get("end_destination_id")
        if start == 0 and end in valid_ids:
            # 逆方向のレコードとする。ここでは同じ数値を採用
            osaka_return[(end, 0)] = record
    return osaka_return


def get_min_hotel_travel_time(
    from_id: int, trans_lookup: Dict, dest_by_id: Dict[int, Any], visited: set
) -> int:
    """
    指定の施設（from_id）から、未訪問のホテル（ishotel:true）への最小移動時間を返す。
    移動情報がない場合は大きな値（例:1000000）を返す。
    """
    min_time = 1000000
    for dest in dest_by_id.values():
        if dest.get("ishotel") and dest["id"] not in visited:
            key = (from_id, dest["id"])
            # print(f"key: {key}")
            if key in trans_lookup:
                travel_time = trans_lookup[key].get("transportation_time", 1000000)
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
    現在地から未訪問のホテル候補の中から、ホテル到着時刻が
    [18:00～20:00]（相対時間で [1080 - departure_time, 1200 - departure_time]）になるものを選ぶ。
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
        arrival_time = current_time + travel_time
        # ホテル到着は指定ウィンドウ内である必要がある
        if arrival_time < sightseeing_end_time or arrival_time > day_total_time:
            continue
        total_cost = travel_cost + (dest.get("fare") or 0)
        if total_cost > remaining_budget:
            continue
        if candidate is None or travel_cost < candidate["travel_cost"]:
            candidate = {
                "destination_id": dest["id"],
                "visit_cost": dest.get("fare") or 0,  # ホテル宿泊費
                "travel_cost": travel_cost,
                "travel_time": travel_time,
                "total_cost": total_cost,
                "arrival_time": arrival_time,
                "transportation_method": travel.get("transportation_method"),
            }
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
    Osaka_to_all_spots.json の逆方向のレコードを利用する。
    """
    key = (current_dest, 0)
    if key not in osaka_return_lookup:
        return None
    record = osaka_return_lookup[key]
    travel_time = record.get("transportation_time", 1000000)
    travel_cost = record.get("transportation_fare", 1000000)
    arrival_time = current_time + travel_time
    if travel_cost > remaining_budget:
        # print(
        #    f"return cost{travel_cost} is over the remaining budget{remaining_budget}"
        # )
        return None
    return {
        "destination_id": 0,  # Osaka の ID は 0
        "visit_cost": 0,
        "travel_cost": travel_cost,
        "travel_time": travel_time,
        "total_cost": travel_cost,
        "arrival_time": arrival_time,
        "transportation_method": record.get("transportation_method"),
    }


def plan_itinerary(
    city: str, budget: int, days: int, departure_time: int, people: int
) -> json:
    """
    departure_time: チェックアウト時刻（分換算、例：10:00 -> 600）
    ホテルのチェックインは18:00～20:00（1080～1200分）に合わせるため、
    相対時間として利用可能時間は:
    day_total_time = 1200 - departure_time
    sightseeing_end_time = 1080 - departure_time
    ※最終日はホテルにチェックインせず、大阪へ帰る
    """
    # 利用可能時間を動的に設定
    day_total_time = 1400 - departure_time  # 例: departure_time=600 → 600分（10時間）
    sightseeing_end_time = (
        1080 - departure_time
    )  # 例: departure_time=600 → 480分（8時間）

    tourist_data, transportation_data, osaka_transportation_data = load_data()
    if city not in tourist_data:
        raise ValueError(f"{city} のデータが見つかりません。")
    destinations = tourist_data[city]
    dest_by_id = {dest["id"]: dest for dest in destinations}
    # print(f"dest_by_id: {dest_by_id}") 全部
    valid_ids = set(dest_by_id.keys())
    # print(f"valid_ids: {valid_ids}") 指定した都市の観光地のidの集合
    trans_lookup = build_transportation_lookup(transportation_data, valid_ids)
    # print(f"len(trans_lookup): {len(trans_lookup)}")
    osaka_lookup = build_osaka_transportation_lookup(
        osaka_transportation_data, valid_ids
    )
    osaka_return_lookup = build_osaka_return_lookup(
        osaka_transportation_data, valid_ids
    )
    # print(trans_lookup)
    # print(osaka_lookup)
    itinerary = []
    remaining_budget = budget
    visited = set()  # 観光施設（ホテル以外）は一度訪れたら除外
    current_dest = 0  # 初日は大阪（ID:0）から出発

    for day in range(days):
        day_plan = []
        current_time = 0  # その日の経過時間（相対値）
        # まず、可能な限り観光施設（ホテル以外）を追加する
        while True:
            candidate = None
            for dest in destinations:
                if dest.get("ishotel"):
                    continue
                if current_dest == 0:
                    key = (0, dest["id"])
                    lookup = osaka_lookup
                else:
                    key = (current_dest, dest["id"])
                    lookup = trans_lookup
                if dest["id"] in visited:
                    continue
                if key not in lookup:
                    continue
                travel = lookup[key]
                travel_time = travel.get("transportation_time", 1000000)
                travel_cost = travel.get("transportation_fare", 1000000)
                arrival_time = current_time + travel_time
                # print(f"arrival_time: {arrival_time}    sightseeing_end_time: {sightseeing_end_time}")
                if arrival_time >= sightseeing_end_time:
                    continue
                visit_time = dest.get("staytime") or 0
                total_time = travel_time + visit_time
                min_hotel_time = get_min_hotel_travel_time(
                    dest["id"], trans_lookup, dest_by_id, visited
                )
                # print(f"min_hotel_time: {min_hotel_time}")
                # print(f"Day {day+1}: {dest['name']} ({dest['id']})")
                if current_time + total_time + min_hotel_time > day_total_time:
                    continue
                total_cost = travel_cost + (dest.get("fare") or 0)
                total_cost *= people
                if total_cost > remaining_budget:
                    continue
                candidate_info = {
                    "destination_id": dest["id"],
                    "visit_cost": dest.get("fare") or 0,
                    "travel_cost": travel_cost,
                    "visit_time": visit_time,
                    "travel_time": travel_time,
                    "total_cost": total_cost,
                    "arrival_time": arrival_time,
                    "transportation_method": travel.get("transportation_method"),
                }
                # 基準は移動費用が最小、同じなら訪問費用が大きい方
                if candidate is None:
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
            current_time += candidate["travel_time"] + candidate["visit_time"]
            remaining_budget -= candidate["total_cost"]
            current_dest = candidate["destination_id"]

        # 最終日の場合、ホテルではなく大阪へ帰る
        if day == days - 1:
            return_candidate = select_return_trip(
                current_dest,
                current_time,
                osaka_return_lookup,
                remaining_budget,
                day_total_time,
            )
            if return_candidate is None:
                pass
                # print(f"Day {day + 1}: 大阪への帰りが見つかりませんでした。")
            else:
                day_plan.append(return_candidate)
                # 帰宅後の更新は必要に応じて
                current_time = return_candidate["arrival_time"]
                remaining_budget -= return_candidate["travel_cost"] * people
                current_dest = 0
        else:
            # その日の締めとしてホテルにチェックイン
            hotel_candidate = select_hotel_candidate(
                current_dest,
                current_time,
                osaka_lookup,
                trans_lookup,
                dest_by_id,
                visited,
                remaining_budget,
                sightseeing_end_time,
                day_total_time,
            )
            if hotel_candidate is None:
                pass
                # print(f"Day {day + 1}: ホテル候補が見つかりませんでした。")
            else:
                day_plan.append(hotel_candidate)
                visited.add(hotel_candidate["destination_id"])
                current_time = hotel_candidate["arrival_time"]
                remaining_budget -= (
                    hotel_candidate["travel_cost"] + hotel_candidate["visit_cost"]
                ) * people
                current_dest = hotel_candidate["destination_id"]
        itinerary.append(day_plan)
        nonhotel_destinations = [d for d in destinations if not d.get("ishotel")]
        if len(visited.intersection({d["id"] for d in nonhotel_destinations})) == len(
            nonhotel_destinations
        ):
            break

    json_itinerary = json.dumps(itinerary, indent=2, ensure_ascii=False)
    return json_itinerary