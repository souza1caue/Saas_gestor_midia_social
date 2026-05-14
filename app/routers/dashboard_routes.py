from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import GeneratedContent, User


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    total_posts = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == user.id,
        GeneratedContent.content_type.in_(["feed", "carrossel", "reels"]),
    ).count()
    total_stories = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == user.id,
        GeneratedContent.content_type == "stories",
    ).count()
    latest_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "total_posts": total_posts,
            "total_stories": total_stories,
            "latest_contents": latest_contents,
        },
    )
