from fastapi import FastAPI
from .routers import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# フロントエンドの両方の URL を許可する場合
origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000/destinations/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
