from sqlalchemy import Column, Integer, String, Float, Text  # SQLAlchemyのデータ型をインポート
from app.db.base_class import Base # Baseクラスをインポート

# 観光地モデルの定義
class Destination(Base):
    __tablename__ = "destinations"

    destination_id = Column(Integer, primary_key=True, index=True)
    destination_name = Column(String, nullable=False)
    destination_category = Column(String, nullable=False)
    destination_fare = Column(Integer, nullable=False)
    destination_staytime = Column(Integer, nullable=False)
    destination_rating = Column(Float, nullable=False)
    destination_description = Column(Text, nullable=False)
    destination_address = Column(String, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)

    # オブジェクトの表示設定
    def __repr__(self):
        return f"<Destination(id={self.destination_id}, name={self.destination_name}, category={self.destination_category}, address={self.destination_address})>"