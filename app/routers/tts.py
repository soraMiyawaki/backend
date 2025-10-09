# app/routers/tts.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import os

router = APIRouter(prefix="/api/tts", tags=["tts"])

# VOICEVOX Web API エンドポイント
VOICEVOX_API_BASE = os.getenv("VOICEVOX_API_BASE", "https://deprecatedapis.tts.quest/v2/voicevox")

class TTSRequest(BaseModel):
    text: str
    speaker: int = 1  # 1: ずんだもん（ノーマル）

@router.post("/voicevox")
async def generate_voicevox_audio(request: TTSRequest):
    """
    VOICEVOX Web APIを使って音声を生成
    speaker: 1 = ずんだもん（ノーマル）
    """
    try:
        # テキストが空の場合はエラー
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        # VOICEVOX APIに音声クエリを送信
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 音声クエリを作成
            query_response = await client.post(
                f"{VOICEVOX_API_BASE}/audio_query",
                params={"text": request.text, "speaker": request.speaker}
            )

            if query_response.status_code != 200:
                print(f"[TTS] Audio query failed: {query_response.status_code}")
                raise HTTPException(
                    status_code=query_response.status_code,
                    detail="Failed to create audio query"
                )

            audio_query = query_response.json()

            # 音声合成
            synthesis_response = await client.post(
                f"{VOICEVOX_API_BASE}/synthesis",
                params={"speaker": request.speaker},
                json=audio_query
            )

            if synthesis_response.status_code != 200:
                print(f"[TTS] Synthesis failed: {synthesis_response.status_code}")
                raise HTTPException(
                    status_code=synthesis_response.status_code,
                    detail="Failed to synthesize audio"
                )

            # 音声データを返す
            return Response(
                content=synthesis_response.content,
                media_type="audio/wav",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": "inline"
                }
            )

    except httpx.TimeoutException:
        print("[TTS] Request timeout")
        raise HTTPException(status_code=504, detail="VOICEVOX API timeout")
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/speakers")
async def get_voicevox_speakers():
    """
    利用可能なVOICEVOX話者一覧を取得
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{VOICEVOX_API_BASE}/speakers")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch speakers"
                )

            return response.json()

    except Exception as e:
        print(f"[TTS] Error fetching speakers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
