from sqlalchemy import Column, Integer, String, ForeignKey # SQLAlchemyのデータ型をインポート
from sqlalchemy.orm import relationship # リレーションシップを定義するためにインポート
from app.db.base_class import Base # Baseクラスをインポート

# 交通手段モデルの定義
class Transportation(Base):
    __tablename__ = "transportations"

    transportation_id = Column(Integer, primary_key=True, index=True)
    start_destination_id = Column(Integer, ForeignKey("destinations.destination_id"), nullable=False)
    end_destination_id = Column(Integer, ForeignKey("destinations.destination_id"), nullable=False)
    transportation_fare = Column(Integer, nullable=False)
    transportation_method = Column(String, nullable=False)
    transportation_time = Column(String, nullable=False)

    start_destination = relationship("Destination", foreign_keys=[start_destination_id])
    end_destination = relationship("Destination", foreign_keys=[end_destination_id])

    # オブジェクトの表示設定
    def __repr__(self):
        return f"<Transportation(id={self.transportation_id}, fare={self.transportation_fare}, method={self.transportation_method}, time={self.transportation_time})>"