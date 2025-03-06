import requests
import time

# ★ 個人のAPIキーを設定（セキュリティ上、環境変数で管理するのが望ましい）
API_KEY = "AIzaSyCxCsvApGX_3ZuDCShfljJSwBP0MHp8SEE"
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.adrFormatAddress,places.businessStatus,places.displayName,places.googleMapsUri,places.iconMaskBaseUri,places.id,places.location,places.primaryTypeDisplayName,places.types,places.nationalPhoneNumber,places.rating,places.regularOpeningHours,places.userRatingCount,places.websiteUri,places.editorialSummary",
}

# Google Places API エンドポイント
BASE_URL = "https://places.googleapis.com/v1/places:searchNearby"

# 函館の中心座標
LOCATION_LAT = "41.7686"
LOCATION_LON = "140.7288"
RADIUS = 10000  # 10km以内
TYPE = "tourist_attraction"


def fetch_places():
    """函館の観光地を100件取得（評価3以上 & 評価数が多い順）"""
    places = []
    next_page_token = None
    try:
        while len(places) < 10:
            print("Len of places: ", len(places))
            params = {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": LOCATION_LAT, "longitude": LOCATION_LON},
                        "radius": RADIUS,
                    }
                },
                "includedTypes": [TYPE],
                "maxResultCount": 10,
            }
            if next_page_token:
                params["pagetoken"] = next_page_token
                time.sleep(2)  # Googleの仕様上、次のリクエストは数秒待つ必要がある

            response = requests.post(BASE_URL, headers=headers, json=params)

            data = response.json()
            print(data)

            if "results" in data:
                places.extend(data["results"])

            # 次のページがある場合は取得
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
    except Exception as e:
        print(f"エラーが発生しました: {e}")

    return places[:10]  # 最大100件


def filter_and_sort_places(places):
    """評価が3以上のものを評価数順に並べ替えて取得"""
    filtered_places = [p for p in places if p.get("rating", 0) >= 3]

    # 評価数（user_ratings_total）が多い順にソート
    sorted_places = sorted(
        filtered_places, key=lambda x: x.get("user_ratings_total", 0), reverse=True
    )

    return sorted_places[:10]  # 100件取得


def extract_info(places):
    """必要な情報を抽出"""
    results = []
    for place in places:
        info = {
            "名前": place.get("name"),
            "場所": place.get("geometry", {}).get("location"),
            "評価": place.get("rating", "不明"),
            "評価数": place.get("user_ratings_total", "不明"),
            "金額": place.get("price_level", "不明"),  # 金額情報
            "住所": place.get("vicinity", "不明"),  # 近隣情報
        }
        results.append(info)
    return results


# 観光地データ取得
all_places = fetch_places()
filtered_sorted_places = filter_and_sort_places(all_places)
tourist_spots = extract_info(filtered_sorted_places)
# 結果を表示
for spot in tourist_spots:
    print(spot)
