from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import CalendarEvent, ContentCalendar, GeneratedContent, User
from app.services.content_generator import generate_content


router = APIRouter(tags=["content"])
templates = Jinja2Templates(directory="app/templates")


def _ensure_calendar_items_have_content(db: Session, user: User, items: list[ContentCalendar]) -> None:
    pending_items = [item for item in items if not item.generated_content_id]
    if not pending_items:
        return

    recent_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(8)
        .all()
    )
    for item in pending_items:
        notes = (
            f"Conteudo criado automaticamente para o calendario em {item.date.strftime('%d/%m/%Y')}. "
            "Entregue legenda, CTA, hashtags, roteiro completo e direcao visual pronta para producao."
        )
        generated = generate_content(
            user,
            item.content_type,
            item.theme,
            item.objective,
            notes,
            recent_contents=recent_contents,
        )
        content = GeneratedContent(
            user_id=user.id,
            content_type=item.content_type,
            theme=item.theme,
            objective=item.objective,
            **generated,
        )
        db.add(content)
        db.flush()
        item.generated_content_id = content.id
        item.status = "conteudo pronto"
        recent_contents.insert(0, content)
        del recent_contents[8:]
    db.commit()


@router.get("/content/generate")
def generate_content_page(
    request: Request,
    content_type: str = "",
    theme: str = "",
    objective: str = "",
    notes: str = "",
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request,
        "generate_content.html",
        {
            "user": user,
            "content_generation_enabled": bool(get_settings().openai_api_key),
            "prefill_content_type": content_type,
            "prefill_theme": theme,
            "prefill_objective": objective,
            "prefill_notes": notes,
        },
    )


@router.post("/content/generate")
def create_content(
    request: Request,
    content_type: str = Form(...),
    theme: str = Form(...),
    objective: str = Form(...),
    notes: str = Form(""),
    show_date: str = Form(""),
    show_time: str = Form(""),
    show_location: str = Form(""),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    show_notes = []
    if show_date.strip():
        show_notes.append(f"Data do show: {show_date.strip()}")
    if show_time.strip():
        show_notes.append(f"Horario: {show_time.strip()}")
    if show_location.strip():
        show_notes.append(f"Local: {show_location.strip()}")
    enriched_notes = notes
    if show_notes:
        enriched_notes = "\n".join([notes.strip(), *show_notes]).strip()

    recent_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(8)
        .all()
    )
    generated = generate_content(
        user,
        content_type,
        theme,
        objective,
        enriched_notes,
        recent_contents=recent_contents,
    )

    content = GeneratedContent(
        user_id=user.id,
        content_type=content_type,
        theme=theme,
        objective=objective,
        **generated,
    )
    db.add(content)
    db.commit()
    db.refresh(content)

    return templates.TemplateResponse(
        request,
        "generate_content.html",
        {
            "user": user,
            "content": content,
            "content_generation_enabled": bool(get_settings().openai_api_key),
            "success": "Conteudo gerado e salvo no historico.",
        },
    )


@router.post("/content/{content_id}/status")
def update_content_status(
    content_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    allowed_statuses = {"rascunho", "aprovado", "publicado", "arquivado"}
    content = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.id == content_id, GeneratedContent.user_id == user.id)
        .first()
    )
    if content and status in allowed_statuses:
        content.status = status
        db.commit()
    return RedirectResponse(url=f"/content/{content_id}", status_code=303)


@router.post("/content/delete-selected")
def delete_selected_contents(
    content_ids: list[int] = Form([]),
    calendar_item_ids: list[int] = Form([]),
    return_to: str = Form("/content/history"),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    safe_return_to = return_to if return_to in {"/content/history", "/content/future"} else "/content/history"
    if calendar_item_ids:
        calendar_items = (
            db.query(ContentCalendar)
            .filter(ContentCalendar.user_id == user.id, ContentCalendar.id.in_(calendar_item_ids))
            .all()
        )
        linked_content_ids = [item.generated_content_id for item in calendar_items if item.generated_content_id]
        if linked_content_ids:
            db.query(CalendarEvent).filter(
                CalendarEvent.user_id == user.id,
                CalendarEvent.generated_content_id.in_(linked_content_ids),
            ).update(
                {
                    CalendarEvent.generated_content_id: None,
                    CalendarEvent.status: "planejado",
                },
                synchronize_session=False,
            )
            db.query(GeneratedContent).filter(
                GeneratedContent.user_id == user.id,
                GeneratedContent.id.in_(linked_content_ids),
            ).delete(synchronize_session=False)
        for item in calendar_items:
            db.delete(item)
        db.commit()
        return RedirectResponse(url=safe_return_to, status_code=303)

    if not content_ids:
        return RedirectResponse(url=safe_return_to, status_code=303)

    contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id, GeneratedContent.id.in_(content_ids))
        .all()
    )
    safe_ids = [content.id for content in contents]
    if safe_ids:
        if safe_return_to == "/content/future":
            db.query(ContentCalendar).filter(
                ContentCalendar.user_id == user.id,
                ContentCalendar.generated_content_id.in_(safe_ids),
            ).delete(synchronize_session=False)
        else:
            db.query(ContentCalendar).filter(
                ContentCalendar.user_id == user.id,
                ContentCalendar.generated_content_id.in_(safe_ids),
            ).update(
                {
                    ContentCalendar.generated_content_id: None,
                    ContentCalendar.status: "planejado",
                },
                synchronize_session=False,
            )
        db.query(CalendarEvent).filter(
            CalendarEvent.user_id == user.id,
            CalendarEvent.generated_content_id.in_(safe_ids),
        ).update(
            {
                CalendarEvent.generated_content_id: None,
                CalendarEvent.status: "planejado",
            },
            synchronize_session=False,
        )
        for content in contents:
            db.delete(content)
        db.commit()

    return RedirectResponse(url=safe_return_to, status_code=303)


@router.get("/content/history")
def content_history(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    future_content_ids = (
        db.query(ContentCalendar.generated_content_id)
        .filter(
            ContentCalendar.user_id == user.id,
            ContentCalendar.generated_content_id.isnot(None),
            ContentCalendar.date >= date.today(),
        )
        .subquery()
    )
    contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .filter(~GeneratedContent.id.in_(future_content_ids))
        .order_by(GeneratedContent.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(request, "content_history.html", {"user": user, "contents": contents})


@router.get("/content/future")
def future_posts(request: Request, db: Session = Depends(get_db), user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    items = (
        db.query(ContentCalendar)
        .filter(
            ContentCalendar.user_id == user.id,
            ContentCalendar.date >= date.today(),
        )
        .order_by(ContentCalendar.date.asc(), ContentCalendar.created_at.asc())
        .all()
    )
    _ensure_calendar_items_have_content(db, user, items)
    return templates.TemplateResponse(request, "future_posts.html", {"user": user, "items": items})


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
