from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.dependencies import get_db
from datetime import datetime, timedelta
from app.models import Destination
from fastapi.responses import JSONResponse
from optimization.travel_planner_for_backend import plan_itenerary
from fastapi.exceptions import HTTPException
import requests

router = APIRouter()

@router.get("/")
def get_root():
    return {"message": "Hello World"}

@router.post("/api/optimize")
async def optimize(request: Request):
    request_data = await request.json()
    latitude = request_data.get("latitude")
    longitude = request_data.get("longitude")
    departure = request_data.get("departure")
    people = request_data.get("people")
    budget = request_data.get("budget")
    days = request_data.get("days")
    startDate = request_data.get("startDate")
    startTimes = request_data.get("startTimes")
    area = request_data.get("area")
    
    print(f"緯度：{latitude}")
    print(f"経度：{longitude}")
    print(f"出発地：{departure}")
    print(f"人数：{people}")
    print(f"予算：{budget}")
    print(f"日数：{days}")
    print(f"開始日：{startDate}")
    print(f"開始時間：{startTimes}")
    print(f"観光エリア：{area}")
    
    startDate_iso = datetime.strptime(startDate, "%Y-%m-%d")
    startTimes_iso = datetime.strptime(startTimes, "%H:%M")
    startDate_iso = startDate_iso.replace(hour=startTimes_iso.hour, minute=startTimes_iso.minute)

    startDate_iso_str = startDate_iso.isoformat()

    result_json = plan_itenerary(area, budget, days, people, startDate_iso_str)

    return result_json


@router.get("/destinations/{destination_name}")
def get_destination(destination_name: str, db: Session = Depends(get_db)):
    destination = db.query(Destination).filter(Destination.destination_name == destination_name).first()
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")

    destination_dict = {
        "destination_id": destination.destination_id,
        "destination_name": destination.destination_name,
        "destination_category": destination.destination_category,
        "destination_fare": destination.destination_fare,
        "destination_staytime": destination.destination_staytime,
        "destination_rating": destination.destination_rating,
        "destination_description": destination.destination_description,
        "destination_address": destination.destination_address,
        "destination_latitude": destination.destination_latitude,
        "destination_longitude": destination.destination_longitude,
        "destination_area": destination.destination_area,
    }
    
    return JSONResponse(content=destination_dict)
