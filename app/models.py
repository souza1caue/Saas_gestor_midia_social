from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    business_name = Column(String(160), nullable=False)
    instagram_handle = Column(String(120), nullable=False)
    business_segment = Column(String(160), nullable=False)
    business_description = Column(Text, nullable=False)
    products_services = Column(Text, nullable=True)
    main_offer = Column(Text, nullable=True)
    target_audience_description = Column(Text, nullable=False)
    audience_pain_points = Column(Text, nullable=True)
    audience_desires = Column(Text, nullable=True)
    brand_positioning = Column(Text, nullable=True)
    brand_voice = Column(String(160), nullable=False)
    communication_style = Column(String(160), nullable=True)
    content_goals = Column(Text, nullable=True)
    preferred_content_types = Column(Text, nullable=True)
    competitors = Column(Text, nullable=True)
    visual_references = Column(Text, nullable=True)
    words_to_use = Column(Text, nullable=True)
    words_to_avoid = Column(Text, nullable=True)
    posting_frequency = Column(String(120), nullable=True)
    location = Column(String(160), nullable=True)
    website_url = Column(String(255), nullable=True)
    whatsapp_contact = Column(String(80), nullable=True)
    instagram_page_name = Column(String(120), nullable=True)
    niche = Column(String(160), nullable=True)
    target_audience = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    contents = relationship("GeneratedContent", back_populates="user", cascade="all, delete-orphan")
    calendars = relationship("ContentCalendar", back_populates="user", cascade="all, delete-orphan")
    events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")


class GeneratedContent(Base):
    __tablename__ = "generated_contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    theme = Column(String(255), nullable=False)
    objective = Column(String(80), nullable=False)
    title = Column(String(255), nullable=False)
    caption = Column(Text, nullable=False)
    call_to_action = Column(String(255), nullable=False)
    hashtags = Column(Text, nullable=False)
    visual_script = Column(Text, nullable=False)
    image_prompt = Column(Text, nullable=False)
    suggested_post_time = Column(String(40), nullable=False)
    status = Column(String(40), default="rascunho", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="contents")


class ContentCalendar(Base):
    __tablename__ = "content_calendars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    theme = Column(String(255), nullable=False)
    objective = Column(String(80), nullable=False)
    status = Column(String(40), default="planejado", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="calendars")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_type = Column(String(80), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    status = Column(String(40), default="planejado", nullable=False)
    generated_content_id = Column(Integer, ForeignKey("generated_contents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="events")
    generated_content = relationship("GeneratedContent")
