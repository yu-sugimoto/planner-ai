from fastapi import APIRouter, Depends, FastAPI, Request
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.travel_plan import generate_travel_plan
from datetime import date
from app.models import Destination
from fastapi.responses import JSONResponse
from optimization.travel_planner_for_backend import plan_itenerary


# APIRouterインスタンスを作成（ルーティングを管理する）
router = APIRouter()

# ホーム
@router.get("/")
def get_root():
    return {"message": "Hello World"}

# 旅行プランの生成して提案
@router.post("/api/optimize")
async def optimize(request: Request):
    request_data = await request.json()

    latitude = request_data.get("latitude")
    longitude = request_data.get("longitude")
    departure = request_data.get("departure")
    people = request_data.get("people")
    budget = request_data.get("budget")
    days = request_data.get("days")
    startDate = 540
    area = request_data.get("area")

    # パラメータを確認
    print(f"緯度：{latitude}")
    print(f"経度：{longitude}")
    print(f"出発地：{departure}")
    print(f"人数：{people}")
    print(f"予算：{budget}")
    print(f"日数：{days}")
    print(f"開始日：{startDate}")
    print(f"観光エリア：{area}")

    # 旅行プランの生成
    result_json = plan_itenerary(area, budget, days, startDate, people)

    # 例として受け取ったデータをそのまま返す
    return result_json

# 観光地の詳細情報を取得
# @router.get("/destinations/{destination_id}")
# def get_destination(destination_id: int, db: Session = Depends(get_db)):
#     destination = db.query(Destination).filter(Destination.destination_id == destination_id).first()
#     if destination is None:
#         raise HTTPException(status_code=404, detail="Destination not found")
#     return JSONResponse(content=destination.__dict__)