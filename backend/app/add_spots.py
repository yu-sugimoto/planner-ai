# Destination テーブルにデータを追加するためのスクリプト（単独実行ファイル）
# $ poetry run python -m app.add_spots
# 保存成功 → データベースへの保存が完了しました

import json
from app.models.destination import Destination
from app.schemas.destination import DestinationCreate
from app.dependencies import get_db

# DB接続
db_generator = get_db()  # ジェネレータを作成
db = next(db_generator)  # セッションを取得

# jsonファイルの読み込み
with open("optimization/data/combined_with_info.json", "r", encoding="utf-8") as f:
    spots = json.load(f)

# 観光地エリアのリストを取得
cities = list(spots.keys())

# 保存カウントの初期化
add_count = 0
del_count = 0

# jsonファイルの中身を確認
for city in cities:
    for destination_data in spots[city]:
        try:
            # jsonファイルのデータをDestinationモデルに変換（構造が異なるため）
            destination = Destination(
                destination_name=destination_data["japanese_name"],
                destination_category=destination_data["category"],
                destination_fare=destination_data["fare"],
                destination_staytime=destination_data["staytime"],
                destination_rating=destination_data["rating"],
                destination_description=destination_data["description"],
                destination_address=destination_data["address"],
                destination_latitude=destination_data["location"]["lat"],
                destination_longitude=destination_data["location"]["lng"],
                destination_area=city,
            )
            # DestinationモデルをDestinationCreateスキーマに変換
            destination_create = DestinationCreate(**destination.__dict__)
            # DBに追加
            db.add(destination)
            add_count += 1

        except Exception as e:
            print(e)
            del_count += 1

# DBへの保存
try:
    db.commit()
    print(f"データベースへの保存が完了しました。保存件数：{add_count}件, 保存失敗：{del_count}件")
except Exception as e:
    db.rollback()
    print(f"データベースへの保存中にエラーが発生しました: {e}")
finally:
    next(db_generator, None) # ジェネレータを最後まで実行してセッションをクローズ
    print("データベース接続をクローズしました。")