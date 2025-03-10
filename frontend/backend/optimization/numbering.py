import json


# JSONファイルの読み込み
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# JSONデータにIDを付与
def add_unique_ids(data):
    counter = 1
    for city, spots in data.items():
        for spot in spots:
            spot["id"] = counter
            counter += 1
    return data


# JSONファイルの保存
def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# メイン処理
file_path = "data/tourist_spots_with_info.json"
data = load_json(file_path)
data_with_ids = add_unique_ids(data)
save_json(data_with_ids, file_path)

print("IDの付与が完了しました。")
