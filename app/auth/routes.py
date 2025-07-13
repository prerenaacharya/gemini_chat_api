from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth.schemas import SendOTPRequest, VerifyOTPRequest, TokenResponse
from app.models.user import User
from app.auth.models import OTP
from app.auth.utils import generate_otp, create_jwt_token
from app.auth.dependencies import get_current_user
from app.auth.schemas import SignupRequest, ResetPasswordRequest, ChangePasswordRequest
from app.auth.utils import hash_password, verify_password
from app.database import Base, engine


router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.mobile_number == data.mobile_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=data.name,
        mobile_number=data.mobile_number,
        password_hash=hash_password(data.password),
        is_verified=True  # since this bypasses OTP for now
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully"}


@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    otp = generate_otp()

    # Save OTP in DB
    otp_entry = OTP(mobile_number=data.mobile_number, otp_code=otp)
    db.add(otp_entry)
    db.commit()

    return {"message": "OTP sent (mocked)", "otp": otp}  # Mocked OTP


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp_entry = db.query(OTP).filter(
        OTP.mobile_number == data.mobile_number,
        OTP.otp_code == data.otp_code
    ).order_by(OTP.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Check if user exists, else create
    user = db.query(User).filter(User.mobile_number == data.mobile_number).first()
    if not user:
        user = User(mobile_number=data.mobile_number, is_verified=True)
        db.add(user)
    else:
        user.is_verified = True # type: ignore

    db.commit()

    token = create_jwt_token({"sub": str(user.id)})
    return {"access_token": token}


@router.post("/forgot-password")
def forgot_password(data: SendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile_number == data.mobile_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    db.add(OTP(mobile_number=data.mobile_number, otp_code=otp))
    db.commit()
    return {"message": "OTP sent (mocked)", "otp": otp}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    otp_entry = db.query(OTP).filter(
        OTP.mobile_number == data.mobile_number,
        OTP.otp_code == data.otp_code
    ).order_by(OTP.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(User).filter(User.mobile_number == data.mobile_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    db.commit()

    return {"message": "Password reset successful"}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "mobile": current_user.mobile_number}
