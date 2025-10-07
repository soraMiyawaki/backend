from typing import Literal, List
from pydantic import BaseModel

Role = Literal["system", "user", "assistant"]

class ChatMessage(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float | None = 0.7
    max_tokens: int | None = 512

class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
