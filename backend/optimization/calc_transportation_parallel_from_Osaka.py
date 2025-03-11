import os
import json
import concurrent.futures
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv(".env.local")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def estimate_transportation(
    start: str, end: str, start_address: str, end_address: str
) -> dict:
    """Estimate transportation cost and time using GPT-4-mini"""
    prompt = f"""
    {start} (住所: {start_address})から{end} (住所: {end_address})までに公共交通機関を利用してかかる合計金額を推定してください。
    あなたは以下の出力をしてください。
    
    # 最終的な出力
    <think>(推定プロセス)</think>
    
    # 最終的な出力
    利用する交通手段:(「徒歩」「バス」「電車」「飛行機」の最もメインで利用するいずれかの手段を出力)
    金額: (最終的に推測した日本円の合計金額, 数字のみ)
    時間:(分換算, 数字のみ)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは日本の交通費と所要時間を推定する専門家です。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=2048,
        )
    except Exception as e:
        print(f"Error estimating transportation from {start} to {end}: {str(e)}")
        return {
            "method": "公共交通機関",
            "fare": 300,  # default value
            "time": 30,  # default value
        }

    # Parse response
    result = {}
    response_text = response.choices[0].message.content

    try:
        for line in response_text.split("\n"):
            if "利用する交通手段:" in line:
                result["method"] = line.split(":")[1].strip()
            elif "金額:" in line:
                fare_str = "".join(c for c in line.split(":")[1].strip() if c.isdigit())
                fare = int(fare_str) if fare_str else 300
                result["fare"] = fare
            elif "時間:" in line:
                time_str = "".join(c for c in line.split(":")[1].strip() if c.isdigit())
                time = int(time_str) if time_str else 30
                result["time"] = min(time, 120)

        # Validate required fields
        if "method" not in result:
            result["method"] = "公共交通機関"
        if "fare" not in result:
            result["fare"] = 17000
        if "time" not in result:
            result["time"] = 180

    except Exception as e:
        print(f"Error parsing response for {start} to {end}: {str(e)}")
        return {"method": "公共交通機関", "fare": 300, "time": 30}

    return result


def process_route(start: dict, end: dict) -> dict:
    """Process a single route and return the result"""
    result = estimate_transportation(
        start["name"], end["name"], start["address"], end["address"]
    )

    return {
        "start_destination_id": start["id"],
        "end_destination_id": end["id"],
        "transportation_fare": result["fare"],
        "transportation_method": result["method"],
        "transportation_time": result["time"],
    }


def main():
    # Load combined data
    with open("data/combined_with_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 抽出する: JSON のルートが辞書の場合、各都市のスポットリストをまとめる
    spots = []
    if isinstance(data, dict):
        for city, city_spots in data.items():
            if isinstance(city_spots, list):
                spots.extend(city_spots)
            else:
                print(f"Warning: {city} のデータがリストではありません。")
    elif isinstance(data, list):
        spots = data
    else:
        raise ValueError("JSONデータの形式が不正です。")

    # Get Osaka station
    osaka_station = {
        "id": "osaka_station",
        "name": "大阪駅",
        "address": "大阪府大阪市北区梅田三丁目1番1号",
    }

    # Initialize results list
    results = []

    # Process routes in parallel with increased workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []

        # Create futures for all routes
        for spot in spots:
            # 型チェック：spot が辞書であることを確認
            if not isinstance(spot, dict):
                print(f"Warning: 辞書型ではないスポットをスキップ: {spot}")
                continue
            futures.append(executor.submit(process_route, osaka_station, spot))

        # Process results with enhanced progress bar
        with tqdm(total=len(futures), desc="Processing routes") as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing route: {str(e)}")
                finally:
                    pbar.update(1)

    # Save results to file
    with open("data/Osaka_to_all_spots.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
