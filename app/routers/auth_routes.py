from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_session_token, get_password_hash, get_user_by_email
from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

BRIEFING_FIELDS = [
    "business_name",
    "instagram_handle",
    "business_segment",
    "business_description",
    "products_services",
    "main_offer",
    "target_audience_description",
    "audience_pain_points",
    "audience_desires",
    "brand_positioning",
    "brand_voice",
    "communication_style",
    "content_goals",
    "preferred_content_types",
    "competitors",
    "visual_references",
    "words_to_use",
    "words_to_avoid",
    "posting_frequency",
    "location",
    "website_url",
    "whatsapp_contact",
]

REQUIRED_REGISTER_FIELDS = [
    "name",
    "email",
    "password",
    "business_name",
    "instagram_handle",
    "business_segment",
    "business_description",
    "target_audience_description",
    "brand_voice",
]


def _clean(value) -> str:
    return str(value or "").strip()


def _multi_value(form, key: str) -> str:
    return ", ".join(_clean(value) for value in form.getlist(key) if _clean(value))


def _briefing_data(form) -> dict:
    data = {field: _clean(form.get(field)) for field in BRIEFING_FIELDS}
    data["content_goals"] = _multi_value(form, "content_goals")
    data["preferred_content_types"] = _multi_value(form, "preferred_content_types")
    return data


def _missing_required(form, fields: list[str]) -> list[str]:
    return [field for field in fields if not _clean(form.get(field))]


@router.get("/")
def home():
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "E-mail ou senha invalidos."},
            status_code=400,
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key=get_settings().session_cookie_name,
        value=create_session_token(user.id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {})


@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    missing = _missing_required(form, REQUIRED_REGISTER_FIELDS)
    if missing:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "Preencha todos os campos obrigatorios do briefing.", "form_data": form},
            status_code=400,
        )

    email = _clean(form.get("email")).lower()
    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            request,
            "register.html",
            {"error": "Ja existe uma conta com este e-mail.", "form_data": form},
            status_code=400,
        )

    briefing_data = _briefing_data(form)
    user = User(
        name=_clean(form.get("name")),
        email=email,
        hashed_password=get_password_hash(_clean(form.get("password"))),
        **briefing_data,
        instagram_page_name=briefing_data["business_name"],
        niche=briefing_data["business_segment"],
        target_audience=briefing_data["target_audience_description"][:255],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key=get_settings().session_cookie_name,
        value=create_session_token(user.id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/briefing")
def briefing_page(request: Request, user: User | None = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "briefing.html", {"user": user})


@router.post("/briefing")
async def update_briefing(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    missing = _missing_required(
        form,
        [
            "business_name",
            "instagram_handle",
            "business_segment",
            "business_description",
            "target_audience_description",
            "brand_voice",
        ],
    )
    if missing:
        return templates.TemplateResponse(
            request,
            "briefing.html",
            {"user": user, "error": "Preencha todos os campos obrigatorios do briefing."},
            status_code=400,
        )

    for field, value in _briefing_data(form).items():
        setattr(user, field, value)
    user.instagram_page_name = user.business_name
    user.niche = user.business_segment
    user.target_audience = user.target_audience_description[:255]
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse(
        request,
        "briefing.html",
        {"user": user, "success": "Briefing atualizado com sucesso."},
    )


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(get_settings().session_cookie_name)
    return response
