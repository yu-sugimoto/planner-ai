import os
import json
import requests
import time
import math
from dotenv import load_dotenv

# 環境変数から API キーを読み込む（.env.local に GOOGLE_MAPS_API_KEY を定義してください）
load_dotenv(".env.local")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 定数設定
QUERY_RADIUS = 15000  # 各グリッド検索の半径（15km）
RESULTS_PER_CITY = 100  # 各都市で取得したい施設数
GRID_DIM = 4  # 例：4×4のグリッドで検索（計16クエリ）
STEP_KM = 10  # グリッドの間隔（km）

# API のエンドポイントとヘッダー
BASE_URL = "https://places.googleapis.com/v1/places:searchNearby"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "places.adrFormatAddress,places.businessStatus,places.displayName,"
        "places.googleMapsUri,places.iconMaskBaseUri,places.id,places.location,"
        "places.primaryTypeDisplayName,places.types,places.nationalPhoneNumber,"
        "places.rating,places.regularOpeningHours,places.userRatingCount,"
        "places.websiteUri,places.editorialSummary"
    ),
}


def get_grid_points(center, grid_dim, step_km):
    """
    中心座標(center={'lat': float, 'lng': float})を基準に、
    grid_dim×grid_dim のグリッドの各点の座標をリストで返す。
    1度の緯度は約111km、経度は cos(緯度) に依存するので補正しています。
    """
    step_deg_lat = step_km / 111.0
    step_deg_lng = step_km / (111.0 * math.cos(math.radians(center["lat"])))
    grid_points = []
    offset = (grid_dim - 1) / 2.0
    for i in range(grid_dim):
        for j in range(grid_dim):
            lat = center["lat"] + (i - offset) * step_deg_lat
            lng = center["lng"] + (j - offset) * step_deg_lng
            grid_points.append({"lat": lat, "lng": lng})
    return grid_points


def get_tourist_spots_for_city(city, center):
    """
    指定都市(center)周辺で、各グリッド点を中心とする小さい検索エリアで
    "tourist_attraction" タイプの施設を検索し、重複除去後に最大 RESULTS_PER_CITY 件
    の施設情報（施設名、カテゴリー、rating、住所、緯度・経度）を返す。
    """
    grid_points = get_grid_points(center, GRID_DIM, STEP_KM)
    unique_places = {}
    for point in grid_points:
        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(point["lat"]),
                        "longitude": float(point["lng"]),
                    },
                    "radius": QUERY_RADIUS,
                }
            },
            "includedTypes": ["tourist_attraction"],
            "maxResultCount": 10,
        }
        try:
            response = requests.post(BASE_URL, headers=HEADERS, json=payload)
            data = response.json()
            print(f"API Response for {city} at {point}: {data}")
            if "places" in data:
                for place in data["places"]:
                    pid = place.get("id")
                    if pid and pid not in unique_places:
                        facility = {
                            "name": place.get("displayName", {}).get("text", "不明"),
                            "category": place.get("primaryTypeDisplayName", {}).get(
                                "text", "不明"
                            ),
                            "rating": place.get("rating", "不明"),
                            "address": place.get("adrFormatAddress", "不明"),
                            "location": {
                                "lat": place.get("location", {}).get("latitude", None),
                                "lng": place.get("location", {}).get("longitude", None),
                            },
                        }
                        unique_places[pid] = facility
            # 各クエリ間は軽く待機（API利用制限対策）
            time.sleep(1)
        except Exception as e:
            print(f"API request failed for {city} at {point}: {str(e)}")
            continue
    places_list = list(unique_places.values())
    return places_list[:RESULTS_PER_CITY]


def main():
    # cities.json から各都市のデータを読み込む（例: {"cities": [{"name": "東京", "location": {"lat": 35.6895, "lng": 139.6917}}, ...]}）
    with open("data/cities.json", "r", encoding="utf-8") as f:
        cities_data = json.load(f)

    all_spots = {}
    for city in cities_data["cities"]:
        print(f"Processing {city['name']}...")
        spots = get_tourist_spots_for_city(city["name"], city["location"])
        all_spots[city["name"]] = spots

    # 取得結果を tourist_spots.json に保存
    with open("data/tourist_spots.json", "w", encoding="utf-8") as f:
        json.dump(all_spots, f, ensure_ascii=False, indent=2)
    print("Data collection complete!")


if __name__ == "__main__":
    main()
