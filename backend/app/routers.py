from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.travel_plan import generate_travel_plan
from datetime import date
from app.models import Destination
from fastapi.responses import JSONResponse

# APIRouterインスタンスを作成（ルーティングを管理する）
router = APIRouter()

# ホーム
@router.get("/")
def get_root():
    return {"message": "Hello World"}

# 旅行プランの生成して提案
@router.get("/suggestion")
def get_suggestion(
    start_location: str = Header(...),
    num_people: int = Header(...),
    budget: int = Header(...),
    num_days: int = Header(...),
    start_date: date = Header(...),
    db: Session = Depends(get_db),
):
    plan = generate_travel_plan(db, start_location, num_people, budget, num_days, start_date)
    return JSONResponse(content=plan)

# 観光地の詳細情報を取得
@router.get("/destinations/{destination_id}")
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    destination = db.query(Destination).filter(Destination.destination_id == destination_id).first()
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    return JSONResponse(content=destination.__dict__)