from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


settings = get_settings()

if settings.database_url.startswith("sqlite:///./data/"):
    Path("data").mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


USER_BRIEFING_COLUMNS = {
    "business_name": "VARCHAR(160) NOT NULL DEFAULT ''",
    "instagram_handle": "VARCHAR(120) NOT NULL DEFAULT ''",
    "business_segment": "VARCHAR(160) NOT NULL DEFAULT ''",
    "business_description": "TEXT NOT NULL DEFAULT ''",
    "products_services": "TEXT",
    "main_offer": "TEXT",
    "target_audience_description": "TEXT NOT NULL DEFAULT ''",
    "audience_pain_points": "TEXT",
    "audience_desires": "TEXT",
    "brand_positioning": "TEXT",
    "brand_voice": "VARCHAR(160) NOT NULL DEFAULT ''",
    "communication_style": "VARCHAR(160)",
    "content_goals": "TEXT",
    "preferred_content_types": "TEXT",
    "competitors": "TEXT",
    "visual_references": "TEXT",
    "words_to_use": "TEXT",
    "words_to_avoid": "TEXT",
    "posting_frequency": "VARCHAR(120)",
    "location": "VARCHAR(160)",
    "website_url": "VARCHAR(255)",
    "whatsapp_contact": "VARCHAR(80)",
    "instagram_page_name": "VARCHAR(120)",
    "niche": "VARCHAR(160)",
    "target_audience": "VARCHAR(255)",
}


def ensure_sqlite_schema():
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = USER_BRIEFING_COLUMNS.keys() - existing_columns
    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name in missing_columns:
            column_type = USER_BRIEFING_COLUMNS[column_name]
            connection.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
