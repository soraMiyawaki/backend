# app/main.py
import os
from dotenv import load_dotenv, find_dotenv

# ① .env を最初に読み込む（親ディレクトリからの起動でも拾えるように）
load_dotenv(find_dotenv(filename=".env", usecwd=True))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router

app = FastAPI()

# ② CORS 設定（.env の FRONTEND_ORIGIN を利用）
# カンマ区切りで複数のオリジンをサポート
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
origins = [origin.strip() for origin in frontend_origin.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
