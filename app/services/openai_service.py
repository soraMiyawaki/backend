# app/services/openai_service.py
import os
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

def _auth_headers() -> Dict[str, str]:
    key = os.getenv("OPENAI_API_KEY")  # 呼び出し毎に取得（import時に固定しない）
    if not key:
        raise RuntimeError("OPENAI_API_KEY が設定されていません（.env を確認）")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

async def complete_once(
    messages: List[Dict[str, Any]],
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> str:
    url = f"{OPENAI_API_BASE.rstrip('/')}/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(url, headers=_auth_headers(), json=payload)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"]

async def stream_completion(
    messages: List[Dict[str, Any]],
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> AsyncGenerator[str, None]:
    """
    OpenAI SSEの 'data: {...}' 行から delta.content を逐次 yield
    """
    url = f"{OPENAI_API_BASE.rstrip('/')}/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, headers=_auth_headers(), json=payload) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line.split(":", 1)[1].strip()  # "data: {..}" -> "{..}"
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                    delta = obj["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
                except Exception:
                    # roleのみ/parse失敗はスキップ
                    continue
