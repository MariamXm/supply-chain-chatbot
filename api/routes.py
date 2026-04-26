from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.product_service import fetch_product_data
from services.context_builder import build_context
from services.llm_service import get_llm_reply

router = APIRouter()


# Request / Response models
class Message(BaseModel):
    role: str       
    content: str


class ChatRequest(BaseModel):
    container_id: str                             # containerID from QR code 
    message: str                                # customer's question
    conversation_history: List[Message] = []   # prior turns this session


class ChatResponse(BaseModel):
    reply: str


# chat endpoint 
@router.post("/chatbot/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    # 1. fetch product data from api
    try:
        records = await fetch_product_data(request.container_id)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch data for container '{request.container_id}': {str(e)}"
        )

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No records found for container '{request.container_id}'"
        )

    # 2. convert JSON to readable text
    context = build_context(records)

    # 3. call groq
    try:
        reply = await get_llm_reply(
            context=context,
            conversation_history=request.conversation_history,
            user_message=request.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM error: {str(e)}"
        )

    # 4. return response 
    return ChatResponse(reply=reply)