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
        content = await complete_once(
            [m.dict() for m in req.messages],
            req.temperature,
            req.max_tokens,
        )
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def gen():
        async for chunk in stream_completion(
            [m.dict() for m in req.messages],
            req.temperature,
            req.max_tokens,
        ):
            # そのままテキストを流す
            yield chunk
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")
