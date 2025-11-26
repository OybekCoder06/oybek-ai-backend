from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db
from app.utils.ai_client import generate_ai_response

router = APIRouter()

def get_or_create_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        user = models.User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_user_history(db: Session, user_id: int, limit: int = 10) -> List[models.Message]:
    return (db.query(models.Message)
              .filter(models.Message.user_id == user_id)
              .order_by(models.Message.created_at.desc())
              .limit(limit)
              .all())[::-1]  # reverse: oldest first

@router.post("/", response_model=schemas.ChatResponse)
async def chat_endpoint(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if not req.username or not req.message:
        raise HTTPException(status_code=400, detail="username and message required")

    user = get_or_create_user(db, req.username)

    # Saqlanish — foydalanuvchi xabari
    user_msg = models.Message(
        user_id=user.id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Kontekstni yaratish — oxirgi N xabarlar
    history = get_user_history(db, user.id, limit=10)
    # Build messages list for AI
    messages_for_ai = []
    system_prompt = """You are OybekCoder's friendly and humorous Uzbek AI assistant. 
    Answer warmly, sometimes with mild jokes/memes (non-offensive), keep it helpful and light."""

    messages_for_ai.append({"role": "system", "content": system_prompt})
    for m in history:
        messages_for_ai.append({"role": m.role, "content": m.content})

    # So'rov yuborish
    ai_reply = await generate_ai_response(user.id, messages_for_ai)

    # Javobni saqlash
    bot_msg = models.Message(
        user_id=user.id,
        role="assistant",
        content=ai_reply
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    # DB dan to'liq kontekst (yangi + eski)
    full_history = get_user_history(db, user.id, limit=10)

    # Response
    return schemas.ChatResponse(
        reply=ai_reply,
        context=[schemas.MessageResponse(
            id=m.id, role=m.role, content=m.content
        ) for m in full_history]
    )
