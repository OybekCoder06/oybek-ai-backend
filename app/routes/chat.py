from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.ai_client import generate_ai_response

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/")
async def chat_endpoint(req: ChatRequest):
    response = await generate_ai_response(req.user_id, req.message)
    return {"reply": response}
