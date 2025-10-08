from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from app.services.openai_service import complete_once, stream_completion

router = APIRouter(prefix="/api", tags=["chat"])

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.3
    max_tokens: int = 512

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = await complete_once(
            [m.dict() for m in req.messages],
            req.temperature,
            req.max_tokens,
        )
        # result is dict with 'content' and optionally 'reasoning', 'reasoning_tokens'
        return result
    except RuntimeError as e:
        # APIキー未設定など
        if "API key" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # その他のエラー（OpenAI APIエラー含む）
        raise HTTPException(status_code=500, detail=f"Upstream error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def gen():
        try:
            async for chunk in stream_completion(
                [m.dict() for m in req.messages],
                req.temperature,
                req.max_tokens,
            ):
                yield chunk
        except RuntimeError as e:
            if "API key" in str(e):
                yield f"ERROR: {str(e)}"
            else:
                yield f"ERROR: {str(e)}"
        except Exception as e:
            yield f"ERROR: Upstream error: {str(e)}"

    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")
