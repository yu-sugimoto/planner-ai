from sqlalchemy.orm import Session
from app.schemas import Destination, Transportation
from typing import List, Dict
import datetime

def generate_travel_plan(
    db: Session,
    start_location: str,
    num_people: int,
    budget: int,
    num_days: int,
    start_date: datetime.date,
) -> Dict:
    
    # 観光地とルートの情報を取得
    destinations = db.query(Destination).all()
    transportations = db.query(Transportation).all()

    # 以下、生成ロジック (予算、日数、出発地などを考慮)
    selected_destinations = []
    selected_routes = []
    total_fare = 0

    # 最適化アルゴリズムなど
    

    # 結果を整形（各観光地情報 / ルート情報に詳細が入っているイメージ）
    plan = {
        "destinations": [dest.__dict__ for dest in selected_destinations],
        "routes": [route.__dict__ for route in selected_routes],
        "total_fare": total_fare,
        "fare_per_person": total_fare / num_people,
    }

    return plan