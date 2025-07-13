# app/chatroom/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.database import SessionLocal
from app.chatroom.models import Chatroom, Message
from app.chatroom.schemas import ChatroomCreate, MessageCreate
from app.chatroom.gemini import call_gemini_api
from app.chatroom.utils import stream_gemini_response_with_db
import json
import os

import redis
from rq import Queue

router = APIRouter()

# Redis queue setup
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")  # fallback for local
redis_conn = redis.Redis.from_url(redis_url)
queue = Queue(connection=redis_conn)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_chatroom(
    data: ChatroomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chatroom = Chatroom(name=data.name, user_id=current_user.id)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return {"id": chatroom.id, "name": chatroom.name}


@router.get("/")
def list_chatrooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"chatrooms:{current_user.id}"
    cached = redis_conn.get(cache_key)

    if cached:
        return json.loads(cached)

    # If not cached, fetch from DB
    chatrooms = db.query(Chatroom).filter(Chatroom.user_id == current_user.id).all()
    result = [{"id": c.id, "name": c.name} for c in chatrooms]

    # Cache the result for 10 minutes (600 seconds)
    redis_conn.setex(cache_key, 600, json.dumps(result))

    return result


@router.get("/{chatroom_id}")
def get_chatroom(
    chatroom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()

    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")

    messages = db.query(Message).filter(
        Message.chatroom_id == chatroom_id
    ).order_by(Message.timestamp).all()

    return {
        "id": chatroom.id,
        "name": chatroom.name,
        "messages": [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp}
            for m in messages
        ]
    }


@router.post("/{chatroom_id}/message")
def send_message(
    chatroom_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()

    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")

    # Save user message
    user_msg = Message(
        chatroom_id=chatroom_id,
        sender="user",
        content=data.content
    )
    db.add(user_msg)
    db.commit()

    # Enqueue Gemini API task
    job = queue.enqueue(call_gemini_api, data.content)

    # Save temporary AI message (to be updated later)
    ai_msg = Message(
        chatroom_id=chatroom_id,
        sender="ai",
        content="(processing...)"
    )
    db.add(ai_msg)
    db.commit()

    return stream_gemini_response_with_db(data.content, db, chatroom_id)