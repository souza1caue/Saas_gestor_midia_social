from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.brand import get_or_create_brand_user
from app.database import get_db
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    return get_or_create_brand_user(db)


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    return get_or_create_brand_user(db)

