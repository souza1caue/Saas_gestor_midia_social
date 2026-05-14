from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine, ensure_sqlite_schema
from app.routers import auth_routes, calendar_routes, content_routes, dashboard_routes


settings = get_settings()
Base.metadata.create_all(bind=engine)
ensure_sqlite_schema()

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(content_routes.router)
app.include_router(calendar_routes.router)
