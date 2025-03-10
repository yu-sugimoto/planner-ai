import os
import json
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv('.env.local')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def estimate_transportation(start: str, end: str, start_address: str, end_address: str) -> dict:
    """Estimate transportation cost and time using GPT-4-mini"""
    prompt = f'''
    {start} (住所: {start_address})から{end} (住所: {end_address})までに公共交通機関を利用してかかる合計金額を推定してください。
    あなたは以下の出力をしてください。
    
    # 最終的な出力
    <think>(推定プロセス)</think>
    
    # 最終的な出力
    利用する交通手段:(「徒歩」「バス」「電車」「飛行機」の最もメインで利用するいずれかの手段を出力)
    金額: (最終的に推測した日本円の合計金額, 数字のみ)
    時間:(分換算, 数字のみ)
    '''
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "あなたは日本の交通費と所要時間を推定する専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=2048,
        )
    except Exception as e:
        print(f"Error estimating transportation from {start} to {end}: {str(e)}")
        return {
            'method': '公共交通機関',
            'fare': 300,  # default value
            'time': 30    # default value
        }
    
    # Parse response
    result = {}
    response_text = response.choices[0].message.content
    
    try:
        for line in response_text.split('\n'):
            if '利用する交通手段:' in line:
                result['method'] = line.split(':')[1].strip()
            elif '金額:' in line:
                # Extract only numeric characters
                fare_str = ''.join(c for c in line.split(':')[1].strip() if c.isdigit())
                fare = int(fare_str) if fare_str else 300
                # Set maximum fare to 10000 yen
                result['fare'] =  fare
            elif '時間:' in line:
                # Extract only numeric characters
                time_str = ''.join(c for c in line.split(':')[1].strip() if c.isdigit())
                time = int(time_str) if time_str else 30
                # Set maximum time to 120 minutes
                result['time'] = min(time, 120)
        
        # Validate required fields
        if 'method' not in result:
            result['method'] = '公共交通機関'
        if 'fare' not in result:
            result['fare'] = 1000
        if 'time' not in result:
            result['time'] = 30
            
    except Exception as e:
        print(f"Error parsing response for {start} to {end}: {str(e)}")
        return {
            'method': '公共交通機関',
            'fare': 300,
            'time': 30
        }
    
    return result

def process_combination(start: Dict, end: Dict) -> Dict:
    """Process a single combination of start and end destinations"""
    result = estimate_transportation(start['name'], end['name'], start['address'], end['address'])
    return {
        'start_destination_id': start['id'],
        'end_destination_id': end['id'],
        'transportation_fare': result['fare'],
        'transportation_method': result['method'],
        'transportation_time': result['time']
    }

def main():
    # Load input data
    with open('data/tourist_spots_with_info.json', 'r') as f:
        data = json.load(f)
    
    # Generate all combinations
    combinations = []
    for city, spots in data.items():
        combinations.extend(itertools.permutations(spots, 2))
    
    # Initialize output file
    output_file = 'data/transportation_costs.json'
    with open(output_file, 'w') as f:
        f.write('[\n')
    
    # Process combinations in parallel
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [
            executor.submit(process_combination, start, end)
            for start, end in combinations
        ]
        
        # Show progress bar and write results incrementally
        first = True
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing combinations"):
            try:
                result = future.result()
                with open(output_file, 'a') as f:
                    if not first:
                        f.write(',\n')
                    json.dump(result, f, indent=2, ensure_ascii=False)
                    first = False
                results.append(result)
            except Exception as e:
                print(f"Error processing combination: {str(e)}")
    
    # Sort results by start_destination_id and end_destination_id
    results.sort(key=lambda x: (x['start_destination_id'], x['end_destination_id']))
    
    # Finalize output file
    with open(output_file, 'a') as f:
        f.write('\n]')

if __name__ == '__main__':
    main()
