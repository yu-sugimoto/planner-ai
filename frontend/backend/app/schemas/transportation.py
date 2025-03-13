from pydantic import BaseModel
from typing import Optional

# Transportationの基本スキーマを定義
class TransportationBase(BaseModel):
    start_destination_id: int
    end_destination_id: int
    transportation_fare: int
    transportation_method: str
    transportation_time: str

# Transportationの作成時のスキーマを定義
class TransportationCreate(TransportationBase):
    pass

# Transportationの更新時のスキーマを定義
class TransportationUpdate(TransportationBase):
    start_destination_id: Optional[int] = None
    end_destination_id: Optional[int] = None
    transportation_fare: Optional[int] = None
    transportation_method: Optional[str] = None
    transportation_time: Optional[str] = None

# Transportationの取得時のスキーマを定義
class Transportation(TransportationBase):
    transportation_id: int

    class Config:
        orm_mode = True