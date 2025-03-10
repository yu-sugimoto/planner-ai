import json
import os


def add_ishotel_flag(data, is_hotel_flag):
    """
    data の各施設に ishotel キーを追加する（すでに存在する場合は上書き）
    """
    for region, spots in data.items():
        for spot in spots:
            spot["ishotel"] = is_hotel_flag
    return data


def merge_data(tourist_data, hotel_data):
    """
    各地域ごとに、tourist_data と hotel_data をマージし、存在しない地域はそのまま採用する。
    """
    merged = {}
    # すべての地域キー（tourist と hotel 両方）を取得
    all_regions = set(tourist_data.keys()) | set(hotel_data.keys())
    for region in all_regions:
        spots = tourist_data.get(region, [])
        hotels = hotel_data.get(region, [])
        merged[region] = spots + hotels
    return merged


def assign_global_ids(merged_data):
    """
    merged_data 内のすべての施設に対して、全体で一意な連番の id を1から付与する
    """
    counter = 1
    for region in merged_data:
        for spot in merged_data[region]:
            spot["id"] = counter
            counter += 1
    return merged_data


def main():
    # JSONファイルのパス（適宜変更してください）
    tourist_file = os.path.join("data", "tourist_spots_with_info.json")
    hotels_file = os.path.join("data", "hotels_with_info.json")
    output_file = os.path.join("data", "combined_with_info.json")

    # ファイル読み込み
    with open(tourist_file, "r", encoding="utf-8") as infile:
        tourist_data = json.load(infile)
    with open(hotels_file, "r", encoding="utf-8") as infile:
        hotel_data = json.load(infile)

    # tourist_spots の各施設に ishotel: false を追加（または上書き）
    tourist_data = add_ishotel_flag(tourist_data, False)
    # hotel_data はそのままで ishotel: true が設定されている前提

    # 両データを各地域ごとにマージ
    merged_data = merge_data(tourist_data, hotel_data)

    # 全体で一意の連番 id を付与
    merged_data = assign_global_ids(merged_data)

    # 結果を新たなJSONファイルに出力
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(merged_data, outfile, ensure_ascii=False, indent=2)

    print(f"結果は {output_file} に保存されました。")


if __name__ == "__main__":
    main()
