from fastapi import Depends, HTTPException, status 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from app.models.user import User
from app.database import SessionLocal

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    print(f"[DEBUG] Received Token: {token}")  # Debugging

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"[DEBUG] Decoded JWT Payload: {payload}")  # Debugging

        user_id: str = payload.get("sub")
        if user_id is None:
            print("[DEBUG] JWT payload missing 'sub'")  # Debugging
            raise HTTPException(status_code=401, detail="Invalid JWT token")
    except JWTError as e:
        print(f"[DEBUG] JWT decoding error: {e}")  # Debugging
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    db = SessionLocal()
    try:
        print(f"[DEBUG] Looking for user_id: {user_id} in DB")  # Debugging
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            print(f"[DEBUG] Found user: {user.mobile_number}")  # Debugging
        else:
            print(f"[DEBUG] User not found for id: {user_id}")  # Debugging
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        db.close()
