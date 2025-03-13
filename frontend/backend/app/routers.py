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

    # Wikipedia API を使った画像取得処理
    API_URL = "https://ja.wikipedia.org/w/api.php"

    def get_image_url(query):
        search_params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'utf8': '',
            'format': 'json'
        }
        response = requests.get(API_URL, params=search_params)
        search_data = response.json()
        
        if 'query' in search_data and 'search' in search_data['query']:
            page_title = search_data['query']['search'][0]['title']
            print(f"Found page: {page_title}")
        else:
            print("No results found.")
            return None

        image_params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'images',
            'format': 'json'
        }
        response = requests.get(API_URL, params=image_params)
        image_data = response.json()

        if 'query' in image_data and 'pages' in image_data['query']:
            page = list(image_data['query']['pages'].values())[0]
            if 'images' in page:
                image_file = page['images'][0]['title']
                print(f"Found image file: {image_file}")
            else:
                print("No images found on the page.")
                return None
        else:
            print("No images found on the page.")
            return None

        image_info_params = {
            'action': 'query',
            'titles': image_file,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'format': 'json'
        }
        response = requests.get(API_URL, params=image_info_params)
        image_info_data = response.json()

        if 'query' in image_info_data and 'pages' in image_info_data['query']:
            page = list(image_info_data['query']['pages'].values())[0]
            if 'imageinfo' in page:
                image_url = page['imageinfo'][0]['url']
                return image_url
            else:
                print("No image URL found.")
                return None
        else:
            print("No image URL found.")
            return None
    
    query = destination.destination_name
    image_url = get_image_url(query)
    if image_url:
        print(f"Image URL: {image_url}")

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
        "image_url": image_url
    }
    
    return JSONResponse(content=destination_dict)
