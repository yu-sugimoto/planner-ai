import os
import json
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
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
                result["method"] = line.split(":", 1)[1].strip()
            elif "金額:" in line:
                # Extract only numeric characters
                fare_str = "".join(
                    c for c in line.split(":", 1)[1].strip() if c.isdigit()
                )
                fare = int(fare_str) if fare_str else 300
                result["fare"] = fare
            elif "時間:" in line:
                # Extract only numeric characters
                time_str = "".join(
                    c for c in line.split(":", 1)[1].strip() if c.isdigit()
                )
                time_val = int(time_str) if time_str else 30
                result["time"] = min(time_val, 120)

        # Validate required fields
        if "method" not in result:
            result["method"] = "公共交通機関"
        if "fare" not in result:
            result["fare"] = 1000
        if "time" not in result:
            result["time"] = 30

    except Exception as e:
        print(f"Error parsing response for {start} to {end}: {str(e)}")
        return {"method": "公共交通機関", "fare": 300, "time": 30}

    return result


def process_combination(start: Dict, end: Dict) -> Dict:
    """Process a single combination of start and end destinations"""
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
    # Load input data
    with open("data/combined_with_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    output_file = "data/transportation_costs.json"

    # Load existing results if file exists
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
        except Exception as e:
            print(f"Error reading {output_file}: {str(e)}")
            existing_results = []
    else:
        existing_results = []

    # Create a set of already processed pairs (start_id, end_id)
    processed_pairs = set()
    for record in existing_results:
        processed_pairs.add(
            (record["start_destination_id"], record["end_destination_id"])
        )

    # Generate all combinations from each city and filter out already processed pairs
    # また、両方ともがホテルの場合はペアを無視する
    combinations = []
    for city, spots in data.items():
        for start, end in itertools.permutations(spots, 2):
            # 両施設ともホテルの場合はスキップ
            if start.get("ishotel") and end.get("ishotel"):
                continue
            pair_key = (start["id"], end["id"])
            if pair_key in processed_pairs:
                continue
            combinations.append((start, end))

    print(f"New combinations to process: {len(combinations)}")

    # Process combinations in parallel
    new_results = []
    with ThreadPoolExecutor(max_workers=80) as executor:
        futures = [
            executor.submit(process_combination, start, end)
            for start, end in combinations
        ]
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing combinations"
        ):
            try:
                result = future.result()
                new_results.append(result)
            except Exception as e:
                print(f"Error processing combination: {str(e)}")

    # Merge existing and new results and sort
    combined_results = existing_results + new_results
    combined_results.sort(
        key=lambda x: (x["start_destination_id"], x["end_destination_id"])
    )

    # Write combined results to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)

    print(f"Processing complete! Updated results saved in {output_file}")


if __name__ == "__main__":
    main()
