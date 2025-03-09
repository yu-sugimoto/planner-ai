from pydantic import BaseModel
from typing import Optional

# Destinationの基本スキーマを定義
class DestinationBase(BaseModel):
    destination_name: str
    destination_category: str
    destination_fare: int
    destination_staytime: int
    destination_rating: float
    destination_description: str
    destination_address: str
    destination_latitude: float
    destination_longitude: float

# Destinationの作成時のスキーマを定義
class DestinationCreate(DestinationBase):
    pass

# Destinationの更新時のスキーマを定義
class DestinationUpdate(DestinationBase):
    destination_name: Optional[str] = None
    destination_category: Optional[str] = None
    destination_fare: Optional[int] = None
    destination_staytime: Optional[int] = None
    destination_rating: Optional[float] = None
    destination_description: Optional[str] = None
    destination_address: Optional[str] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None

# Destinationの取得時のスキーマを定義
class Destination(DestinationBase):
    destination_id: int

    class Config:
        orm_mode = True