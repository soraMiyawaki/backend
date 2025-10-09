# app/main.py
import os
from dotenv import load_dotenv, find_dotenv

# ① .env を最初に読み込む（親ディレクトリからの起動でも拾えるように）
load_dotenv(find_dotenv(filename=".env", usecwd=True))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router
from app.routers.attendance import router as attendance_router

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
app.include_router(attendance_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/auth/roles")
async def get_user_roles(request: Request):
    """
    Azure Static Web Apps認証用のロール割り当てAPI
    許可されたGitHubユーザーのみ'authenticated'ロールを付与
    """
    # 許可するGitHubユーザー名のリスト（環境変数で管理）
    allowed_users_str = os.getenv("ALLOWED_GITHUB_USERS", "")
    allowed_users = [user.strip() for user in allowed_users_str.split(",") if user.strip()]

    # Azure SWAから送られてくるヘッダーからユーザー情報を取得
    user_id = request.headers.get("x-ms-client-principal-id")
    user_name = request.headers.get("x-ms-client-principal-name")

    # デバッグログ
    print(f"[AUTH] Headers: {dict(request.headers)}")
    print(f"[AUTH] User ID: {user_id}, User Name: {user_name}")
    print(f"[AUTH] Allowed users: {allowed_users}")

    # 許可リストが空の場合は全員許可
    if not allowed_users:
        print("[AUTH] No allowlist - granting authenticated role")
        return {"roles": ["authenticated"]}

    # ユーザー名が許可リストに含まれているかチェック
    if user_name and user_name in allowed_users:
        print(f"[AUTH] User {user_name} is in allowlist - granting authenticated role")
        return {"roles": ["authenticated"]}

    # 許可されていないユーザーは匿名扱い
    print(f"[AUTH] User {user_name} NOT in allowlist - denying access")
    return {"roles": ["anonymous"]}
