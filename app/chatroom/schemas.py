from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatroomCreate(BaseModel):
    name: str

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    sender: str
    content: str
    timestamp: datetime

class ChatroomDetail(BaseModel):
    id: int
    name: str
    messages: List[MessageOut]

