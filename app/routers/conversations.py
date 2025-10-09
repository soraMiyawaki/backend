# app/routers/conversations.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.database import (
    save_conversation,
    get_conversation,
    list_conversations,
    delete_conversation
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

class SaveConversationRequest(BaseModel):
    conversation_id: str
    conversation_tree: Dict[str, Any]
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    conversation_tree: Optional[Dict[str, Any]] = None

def get_user_id_from_header(x_ms_client_principal_name: Optional[str] = Header(None)) -> str:
    """
    Azure Static Web Appsから送られてくるヘッダーからユーザーIDを取得
    開発環境ではダミーユーザーを返す
    """
    if x_ms_client_principal_name:
        return x_ms_client_principal_name

    # 開発環境用のダミーユーザー
    return "dev-user"

@router.post("/save")
async def save_conversation_endpoint(
    request: SaveConversationRequest,
    x_ms_client_principal_name: Optional[str] = Header(None)
):
    """会話を保存"""
    user_id = get_user_id_from_header(x_ms_client_principal_name)

    success = save_conversation(
        conversation_id=request.conversation_id,
        user_id=user_id,
        conversation_tree=request.conversation_tree,
        title=request.title
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to save conversation")

    return {"success": True, "conversation_id": request.conversation_id}

@router.get("/list")
async def list_conversations_endpoint(
    x_ms_client_principal_name: Optional[str] = Header(None)
) -> List[ConversationResponse]:
    """ユーザーの会話一覧を取得"""
    user_id = get_user_id_from_header(x_ms_client_principal_name)
    conversations = list_conversations(user_id)

    return [
        ConversationResponse(
            id=conv["id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"]
        )
        for conv in conversations
    ]

@router.get("/{conversation_id}")
async def get_conversation_endpoint(
    conversation_id: str,
    x_ms_client_principal_name: Optional[str] = Header(None)
) -> ConversationResponse:
    """会話を取得"""
    user_id = get_user_id_from_header(x_ms_client_principal_name)
    conversation = get_conversation(conversation_id, user_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        id=conversation["id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        conversation_tree=conversation["conversation_tree"]
    )

@router.delete("/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str,
    x_ms_client_principal_name: Optional[str] = Header(None)
):
    """会話を削除"""
    user_id = get_user_id_from_header(x_ms_client_principal_name)
    success = delete_conversation(conversation_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"success": True}
