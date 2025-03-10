from fastapi import FastAPI
from .routers import router

# FastAPIのインスタンスを作成（アプリケーション全体を管理する）
app = FastAPI()

# routers.pyで作成したルーティングを読み込む
app.include_router(router)
