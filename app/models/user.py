from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
from app.models.subscription import Subscription  # 👈 Add this


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    subscription_type = Column(String, default="Basic")  # Basic or Pro
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)  # Store hashed password

    chatrooms = relationship("Chatroom", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete")

