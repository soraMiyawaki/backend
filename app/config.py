from typing import Literal, List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM プロバイダ（未設定やキー無しの時は echo で応答）
    provider: Literal["openai", "echo"] = Field(default="echo", env="PROVIDER")

    # OpenAI 設定（.env は大文字キーでOK）
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    model: str = Field(default="gpt-4o-mini", env="MODEL")

    # CORS 許可オリジン
    allowed_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

    debug: bool = Field(default=True, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
