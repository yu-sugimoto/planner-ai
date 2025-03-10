import os
import json
import requests
import time
import math
from dotenv import load_dotenv

# .env.local から API キーを読み込む
load_dotenv(".env.local")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 定数設定
QUERY_RADIUS = 40000  # 各グリッド検索の半径（15km）
RESULTS_PER_CITY = 3  # 各都市で取得したいホテル数
GRID_DIM = 4  # 例：4×4 のグリッド（計16クエリ）
STEP_KM = 10  # グリッド間の間隔（km）

# API エンドポイントとヘッダー
BASE_URL = "https://places.googleapis.com/v1/places:searchNearby"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "places.adrFormatAddress,places.businessStatus,places.displayName,"
        "places.googleMapsUri,places.iconMaskBaseUri,places.id,places.location,"
        "places.primaryTypeDisplayName,places.types,places.nationalPhoneNumber,"
        "places.rating,places.regularOpeningHours,places.userRatingCount,"
        "places.websiteUri,places.editorialSummary,places.priceLevel"
    ),
}


def get_grid_points(center, grid_dim, step_km):
    """
    指定した中心座標(center={'lat': float, 'lng': float})を基準に、
    grid_dim×grid_dim のグリッドの各点の座標をリストで返す関数。
    1度の緯度は約111km、経度は cos(緯度) によって補正しています。
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


def get_hotels_for_city(city, center):
    """
    指定した都市(center)周辺で、グリッド上の各点を中心とする検索エリア内の
    "lodging" タイプ（ホテル等）の施設を検索し、重複除去後に最大 RESULTS_PER_CITY 件の
    ホテル情報を取得する関数。

    各ホテルの情報は以下の形式で返されます：
      {
        "name": "",                      # 施設名
        "category": "",                  # カテゴリ
        "rating": ,                     # 評価
        "address": "",                   # 住所
        "location": { "lat": , "lng": }, # 緯度・経度
        "ishotel": true,                 # ホテルの場合は true
        "price":                      # 料金情報（priceLevel）を追加
      }
    """
    grid_points = get_grid_points(center, GRID_DIM, STEP_KM)
    unique_hotels = {}
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
            "includedTypes": ["lodging"],
            "maxResultCount": 10,
        }
        try:
            response = requests.post(BASE_URL, headers=HEADERS, json=payload)
            data = response.json()
            print(f"API Response for {city} at {point}: {data}")
            if "places" in data:
                for place in data["places"]:
                    pid = place.get("id")
                    if pid and pid not in unique_hotels:
                        hotel = {
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
                            "ishotel": True,
                            "price": place.get("priceLevel", "不明"),
                        }
                        unique_hotels[pid] = hotel
            # API 利用制限対策のため、各クエリ間は待機
            time.sleep(1)
        except Exception as e:
            print(f"API request failed for {city} at {point}: {str(e)}")
            continue
    hotels_list = list(unique_hotels.values())
    return hotels_list[:RESULTS_PER_CITY]


def main():
    # hakodate, kobe, hiroshima の各都市の中心座標を定義
    cities_data = {
        "cities": [
            {"name": "hakodate", "location": {"lat": 41.7687, "lng": 140.7288}},
            {"name": "kobe", "location": {"lat": 34.6901, "lng": 135.1955}},
            {"name": "hiroshima", "location": {"lat": 34.3853, "lng": 132.4553}},
        ]
    }

    all_hotels = {}
    for city in cities_data["cities"]:
        print(f"Processing {city['name']}...")
        hotels = get_hotels_for_city(city["name"], city["location"])
        all_hotels[city["name"]] = hotels

    # 取得結果を hotels.json に保存
    with open("data/hotels.json", "w", encoding="utf-8") as f:
        json.dump(all_hotels, f, ensure_ascii=False, indent=2)
    print("Hotel data collection complete!")


if __name__ == "__main__":
    main()
