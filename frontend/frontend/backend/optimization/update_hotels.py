import json
import asyncio
import aiohttp
from openai import AsyncOpenAI
import re
from dotenv import load_dotenv
import os
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv(".env.local")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 同時実行数を制限するセマフォ
semaphore = asyncio.Semaphore(20)

async def call_openai_for_info(hotel):
    """
    指定されたホテル情報に基づき、description, fare, staytime の情報をJSON形式で取得するためのAPI呼び出し関数
    """
    prompt = (
        f"以下の日本のホテルに関する情報をJSON形式で出力してください。\n"
        f"【入力情報】\n"
        f"ホテル名: {hotel['name']}\n"
        f"カテゴリ: {hotel['category']}\n"
        f"評価: {hotel['rating']}\n"
        f"住所: {hotel['address']}\n\n"
        f"【出力フォーマット】\n"
        f'{{"japanese_name": "日本語のホテル名", "description": "ホテルの簡単な説明", "fare": 平均宿泊料金（円）, "staytime": 900}}\n'
        f"ホテルの簡単な説明はホテル名を含め日本語で、 2~4行文で常体で書いてください。\n"
        f"回答は厳密にJSON形式で出力してください。"
    )

    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは日本のホテルに詳しい専門家です。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=250,
            )
            content = response.choices[0].message.content
            logger.info(f"【成功】 {hotel['name']} の情報取得に成功しました")
            logger.info(f"【出力】\n {content}")
            # APIの返答が厳密なJSONでない場合、正規表現でJSON部分を抽出
            try:
                info = json.loads(content)
                return info
            except json.JSONDecodeError:
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    info = json.loads(json_str)
                    return info
                else:
                    raise ValueError("有効なJSONが見つかりません")
        except Exception as e:
            print(f"【エラー】 {hotel['name']} の情報取得に失敗しました: {e}")
            return {"description": "情報取得に失敗しました", "fare": 0, "staytime": 900}

async def process_city(city, hotels, pbar):
    tasks = []
    for hotel in hotels:
        task = asyncio.create_task(call_openai_for_info(hotel))
        task.add_done_callback(lambda _: pbar.update())
        tasks.append(task)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 結果をホテル情報にマージ
    for hotel, result in zip(hotels, results):
        if not isinstance(result, Exception):
            hotel.update(result)
    
async def main():
    # hotels.json を読み込む
    with open("data/hotels.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)
        
    already_collected_cities = []
    already_hotels_with_info = {}
    with open("data/hotels_with_info.json", "r", encoding="utf-8") as infile:
        already_hotels_with_info = json.load(infile)

    # 進捗表示用のバーを初期化
    total_hotels = sum(len(hotels) for city, hotels in data.items() 
                    if city not in already_collected_cities)
    
    with tqdm(total=total_hotels, desc="Processing hotels") as pbar:
        # 各都市の処理を並列実行
        tasks = []
        for city, hotels in data.items():
            if city in already_collected_cities:
                print(f"Skipping {city} since it's already collected.")
                continue
            task = asyncio.create_task(process_city(city, hotels, pbar))
            tasks.append(task)
        
        await asyncio.gather(*tasks)

    # すでに取得済みの情報をマージ
    for city, hotels in already_hotels_with_info.items():
        if city in data:
            for hotel in hotels:
                if hotel["name"] not in [h["name"] for h in data[city]]:
                    data[city].append(hotel)
        else:
            data[city] = hotels
            
    # 結果を新しい JSON ファイルに出力する
    with open("data/hotels_with_info2.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

    print("新しいJSONファイル 'hotels_with_info2.json' が作成されました。")

if __name__ == "__main__":
    asyncio.run(main())
