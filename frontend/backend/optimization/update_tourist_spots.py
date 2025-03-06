import json
from openai import OpenAI
import time
import re
from dotenv import load_dotenv
import os

load_dotenv(".env.local")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_openai_for_info(spot):
    """
    指定された観光地情報に基づき、description, fare, staytime の情報をJSON形式で取得するためのAPI呼び出し関数
    """
    prompt = (
        f"以下の日本の観光地に関する情報をJSON形式で出力してください。\n"
        f"【入力情報】\n"
        f"観光地名: {spot['name']}\n"
        f"カテゴリ: {spot['category']}\n"
        f"評価: {spot['rating']}\n"
        f"住所: {spot['address']}\n\n"
        f"【出力フォーマット】\n"
        f"{{\"japanese_name\": \"日本語の観光地名\", \"description\": \"観光地の簡単な説明\", \"fare\": 平均費用（円）, \"staytime\": 平均滞在時間（分）}}\n"
        f"観光地の簡単な説明は観光地名を含め日本語で、 2~4行文で常体で書いてください。\n"
        f"回答は厳密にJSON形式で出力してください。"
    )

    try:
        response = client.chat.completions.create(model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=150)
        content = response.choices[0].message.content
        # APIの返答が厳密なJSONでない場合、正規表現でJSON部分を抽出
        try:
            info = json.loads(content)
            return info
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                info = json.loads(json_str)
                return info
            else:
                raise ValueError("有効なJSONが見つかりません")
    except Exception as e:
        print(f"【エラー】 {spot['name']} の情報取得に失敗しました: {e}")
        return {"description": "情報取得に失敗しました", "fare": 0, "staytime": 0}

def main():
    # tourist_spots.json を読み込む
    with open("data/tourist_spots.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)

    # 各都市内の観光地ごとに OpenAI API を呼び出して追加情報を取得する
    for city, spots in data.items():
        for spot in spots:
            print(f"{spot['name']} の情報を取得中...")
            extra_info = call_openai_for_info(spot)
            spot.update(extra_info)
            # API のレート制限対策として1秒待機
            time.sleep(1)

    # 結果を新しい JSON ファイルに出力する
    with open("data/tourist_spots_with_info.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

    print("新しいJSONファイル 'tourist_spots_with_info.json' が作成されました。")

if __name__ == "__main__":
    main()
