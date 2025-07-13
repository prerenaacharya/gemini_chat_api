from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import SessionLocal
from app.models.user import User
from app.config import settings
import stripe

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


# -------------------------
# 1. Create Pro Subscription
# -------------------------
@router.post("/subscribe/pro")
def create_checkout_session(current_user: User = Depends(get_current_user)):
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url="http://localhost:8000/payments/test/success",  # Mock URL
            cancel_url="http://localhost:8000/payments/test/cancel",    # Mock URL
            payment_method_types=["card"],
            mode="subscription",
            customer_email=current_user.mobile_number + "@test.local",  # Fake email for sandbox
            line_items=[{
                "price": settings.STRIPE_PRO_PRICE_ID,
                "quantity": 1
            }],
            metadata={"user_id": current_user.id}
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# 2. Stripe Webhook Handler
# -------------------------
@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        print("❌ Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    print("✅ Event received:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("🎯 Session received:", session)

        metadata = session.get("metadata", {})
        print("📦 Metadata:", metadata)

        user_id = metadata.get("user_id")
        print("🆔 user_id:", user_id)

        if user_id:
            db: Session = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if user:
                    print(f"🔁 Updating user {user.id} subscription to Pro")
                    user.subscription_type = "Pro"
                    db.commit()
            finally:
                db.close()

    return {"status": "success"}


# -------------------------
# 3. Get Subscription Status
# -------------------------
@router.get("/subscription/status")
def subscription_status(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "subscription": current_user.subscription_type
    }

@router.get("/test/success")
async def test_success():
    return {"message": "Payment success test route working"}
