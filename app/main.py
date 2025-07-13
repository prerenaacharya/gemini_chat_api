from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.chatroom.routes import router as chatroom_router
from app.payments.routes import router as payments_router
from app.auth.models import OTP
from app.models.user import User
from app.chatroom.models import Chatroom, Message  # if applicable
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(chatroom_router, prefix="/chatroom", tags=["Chatroom"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])

