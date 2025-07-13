# app/models/subscription.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    stripe_subscription_id = Column(String, nullable=False)
    status = Column(String, default="inactive")  # e.g., "active", "inactive"

    user = relationship("User", back_populates="subscription")
