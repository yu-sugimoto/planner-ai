import json

# 入力ファイルと出力ファイルのパスを指定
input_file = "data/transportation_costs2.json"
output_file = "data/transportation_costs2_with_reverse.json"

# JSON を読み込む
with open(input_file, "r", encoding="utf-8") as f:
    records = json.load(f)

# 既存の組み合わせをセットで管理 (start, end) のタプル
existing_pairs = {(record["start_destination_id"], record["end_destination_id"]) for record in records}

# 逆向きのレコードを追加するためのリスト
new_records = []

for record in records:
    reverse_pair = (record["end_destination_id"], record["start_destination_id"])
    # 逆向きの組み合わせが存在しなければ追加
    if reverse_pair not in existing_pairs:
        # レコードをコピーしてキーを入れ替え
        new_record = {
            "start_destination_id": record["end_destination_id"],
            "end_destination_id": record["start_destination_id"],
            "transportation_fare": record["transportation_fare"],
            "transportation_method": record["transportation_method"],
            "transportation_time": record["transportation_time"],
        }
        new_records.append(new_record)
        existing_pairs.add(reverse_pair)

# もともとのレコードと新規追加したレコードを結合
all_records = records + new_records

# 結果を JSON ファイルに書き出す
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=2, ensure_ascii=False)

print(f"新しいファイルは {output_file} に保存されました。")
