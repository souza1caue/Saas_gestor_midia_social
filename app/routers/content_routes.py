from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import GeneratedContent, User
from app.services.content_generator import generate_content


router = APIRouter(tags=["content"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/content/generate")
def generate_content_page(request: Request, user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "generate_content.html", {"user": user})


@router.post("/content/generate")
def create_content(
    request: Request,
    content_type: str = Form(...),
    theme: str = Form(...),
    objective: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    generated = generate_content(user, content_type, theme, objective, notes)
    content = GeneratedContent(user_id=user.id, content_type=content_type, theme=theme, objective=objective, **generated)
    db.add(content)
    db.commit()
    db.refresh(content)

    return templates.TemplateResponse(
        request,
        "generate_content.html",
        {"user": user, "content": content, "success": "Conteúdo gerado e salvo no histórico."},
    )


@router.get("/content/history")
def content_history(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "content_history.html", {"user": user, "contents": contents})


@router.get("/content/{content_id}")
def content_detail(
    request: Request,
    content_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    content = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.id == content_id, GeneratedContent.user_id == user.id)
        .first()
    )
    if not content:
        return RedirectResponse(url="/content/history", status_code=303)
    return templates.TemplateResponse(
        request,
        "content_history.html",
        {"user": user, "contents": [], "selected_content": content},
    )
