from app.database import Base, engine
from app.models.user import User
from app.auth.models import OTP

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
