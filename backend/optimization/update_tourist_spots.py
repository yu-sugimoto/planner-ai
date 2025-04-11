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

async def call_openai_for_info(spot):
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
        f'{{"japanese_name": "日本語の観光地名", "description": "観光地の簡単な説明", "fare": 平均費用（円）, "staytime": 平均滞在時間（分）}}\n'
        f"観光地の簡単な説明は観光地名を含め日本語で、 2~4行文で常体で書いてください。\n"
        f"回答は厳密にJSON形式で出力してください。"
    )

    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini-search-preview-2025-03-11",
                messages=[
                    {"role": "system", "content": "あなたは日本の観光地に詳しい専門家です。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=250,
            )
            content = response.choices[0].message.content
            logger.info(f"【成功】 {spot['name']} の情報取得に成功しました")
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
            print(f"【エラー】 {spot['name']} の情報取得に失敗しました: {e}")
            return {"description": "情報取得に失敗しました", "fare": 0, "staytime": 0}


async def process_city(city, spots, pbar):
    tasks = []
    for spot in spots:
        task = asyncio.create_task(call_openai_for_info(spot))
        task.add_done_callback(lambda _: pbar.update())
        tasks.append(task)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 結果をスポット情報にマージ
    for spot, result in zip(spots, results):
        if not isinstance(result, Exception):
            spot.update(result)
    
async def main():
    # tourist_spots.json を読み込む
    with open("data/tourist_spots.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)
        
    already_collected_cities = ["hakodate", "hiroshima", "kobe"]
    already_tourist_spots_with_info = {}
    with open("data/tourist_spots_with_info.json", "r", encoding="utf-8") as infile:
        already_tourist_spots_with_info = json.load(infile)

    # 進捗表示用のバーを初期化
    total_spots = sum(len(spots) for city, spots in data.items() 
                    if city not in already_collected_cities)
    
    with tqdm(total=total_spots, desc="Processing spots") as pbar:
        # 各都市の処理を並列実行
        tasks = []
        for city, spots in data.items():
            if city in already_collected_cities:
                print(f"Skipping {city} since it's already collected.")
                continue
            task = asyncio.create_task(process_city(city, spots, pbar))
            tasks.append(task)
        
        await asyncio.gather(*tasks)

    # すでに取得済みの情報をマージ
    for city, spots in already_tourist_spots_with_info.items():
        if city in data:
            for spot in spots:
                if spot["name"] not in [s["name"] for s in data[city]]:
                    data[city].append(spot)
        else:
            data[city] = spots
            
    # 結果を新しい JSON ファイルに出力する
    with open("data/tourist_spots_with_info2.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

    print("新しいJSONファイル 'tourist_spots_with_info2.json' が作成されました。")


if __name__ == "__main__":
    asyncio.run(main())
