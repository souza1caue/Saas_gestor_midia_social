from typing import Optional

from itsdangerous import BadSignature, URLSafeSerializer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_session_token(user_id: int) -> str:
    serializer = URLSafeSerializer(get_settings().secret_key, salt="auth-session")
    return serializer.dumps({"user_id": user_id})


def decode_session_token(token: str) -> Optional[int]:
    serializer = URLSafeSerializer(get_settings().secret_key, salt="auth-session")
    try:
        payload = serializer.loads(token)
    except BadSignature:
        return None
    return payload.get("user_id")
