import calendar as calendar_lib
from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import CalendarEvent, ContentCalendar, GeneratedContent, User
from app.services.calendar_generator import generate_calendar, generate_interactive_sequence
from app.services.content_generator import generate_content, generate_content_from_event


router = APIRouter(prefix="/calendar", tags=["calendar"])
templates = Jinja2Templates(directory="app/templates")


def _create_ready_calendar_item(db: Session, user: User, suggestion: dict, recent_contents: list[GeneratedContent]) -> None:
    notes = (
        f"Conteudo criado automaticamente pelo calendario para {suggestion['date'].strftime('%d/%m/%Y')}. "
        f"Status do planejamento: {suggestion['status']}."
    )
    generated = generate_content(
        user,
        suggestion["content_type"],
        suggestion["theme"],
        suggestion["objective"],
        notes,
        recent_contents=recent_contents,
    )
    content = GeneratedContent(
        user_id=user.id,
        content_type=suggestion["content_type"],
        theme=suggestion["theme"],
        objective=suggestion["objective"],
        **generated,
    )
    db.add(content)
    db.flush()
    calendar_item = {**suggestion, "status": "conteudo pronto"}
    db.add(ContentCalendar(user_id=user.id, generated_content_id=content.id, **calendar_item))
    recent_contents.insert(0, content)
    del recent_contents[8:]


def _calendar_context(db: Session, user: User, year: int | None = None, month: int | None = None) -> dict:
    today = date.today()
    year = year or today.year
    month = month or today.month
    first_day = date(year, month, 1)
    _, last_day_number = calendar_lib.monthrange(year, month)
    last_day = date(year, month, last_day_number)

    month_days = calendar_lib.Calendar(firstweekday=6).monthdatescalendar(year, month)
    events = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.user_id == user.id,
            CalendarEvent.event_date >= first_day,
            CalendarEvent.event_date <= last_day,
        )
        .order_by(CalendarEvent.event_date.asc(), CalendarEvent.created_at.asc())
        .all()
    )
    events_by_date: dict[date, list[CalendarEvent]] = {}
    for event in events:
        events_by_date.setdefault(event.event_date, []).append(event)

    items = (
        db.query(ContentCalendar)
        .filter(ContentCalendar.user_id == user.id)
        .order_by(ContentCalendar.date.asc())
        .all()
    )
    items_by_date: dict[date, list[ContentCalendar]] = {}
    for item in items:
        items_by_date.setdefault(item.date, []).append(item)

    previous_month = date(year - 1, 12, 1) if month == 1 else date(year, month - 1, 1)
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    return {
        "items": items,
        "items_by_date": items_by_date,
        "events": events,
        "events_by_date": events_by_date,
        "month_days": month_days,
        "current_month": first_day,
        "previous_month": previous_month,
        "next_month": next_month,
        "today": today,
    }


@router.get("")
def calendar_page(
    request: Request,
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    context = _calendar_context(db, user, year, month)
    return templates.TemplateResponse(request, "calendar.html", {"user": user, **context})


@router.post("")
def create_calendar(
    request: Request,
    days: int = Form(...),
    frequency: str = Form(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    suggestions = generate_calendar(user, days, frequency)
    recent_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(8)
        .all()
    )
    for suggestion in suggestions:
        _create_ready_calendar_item(db, user, suggestion, recent_contents)
    db.commit()

    context = _calendar_context(db, user)
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {"user": user, **context, "success": "Calendario gerado com conteudos prontos."},
    )


@router.post("/interactive-sequence")
def create_interactive_sequence(
    request: Request,
    start_date: str = Form(""),
    theme: str = Form(""),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    parsed_start_date = date.today()
    if start_date.strip():
        parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    suggestions = generate_interactive_sequence(user, parsed_start_date, theme)
    recent_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(8)
        .all()
    )
    for suggestion in suggestions:
        _create_ready_calendar_item(db, user, suggestion, recent_contents)
    db.commit()

    context = _calendar_context(db, user, parsed_start_date.year, parsed_start_date.month)
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {"user": user, **context, "success": "Sequencia interativa criada com conteudos prontos."},
    )


@router.post("/events")
def create_event(
    event_date: str = Form(...),
    event_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    parsed_date = datetime.strptime(event_date, "%Y-%m-%d").date()
    event = CalendarEvent(
        user_id=user.id,
        event_date=parsed_date,
        event_type=event_type,
        title=title.strip(),
        description=description.strip() or None,
        location=location.strip() or None,
    )
    db.add(event)
    db.commit()
    return RedirectResponse(url=f"/calendar?year={parsed_date.year}&month={parsed_date.month}", status_code=303)


@router.post("/events/{event_id}/generate-post")
def generate_event_post(
    event_id: int,
    content_type: str = Form("feed"),
    objective: str = Form("divulgar"),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id).first()
    if not event:
        return RedirectResponse(url="/calendar", status_code=303)

    recent_contents = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.user_id == user.id)
        .order_by(GeneratedContent.created_at.desc())
        .limit(8)
        .all()
    )
    generated = generate_content_from_event(user, event, content_type, objective, recent_contents=recent_contents)
    theme = f"{event.event_type}: {event.title}"
    content = GeneratedContent(
        user_id=user.id,
        content_type=content_type,
        theme=theme,
        objective=objective,
        **generated,
    )
    db.add(content)
    db.flush()
    event.generated_content_id = content.id
    event.status = "post gerado"
    db.commit()
    return RedirectResponse(url=f"/content/{content.id}", status_code=303)
