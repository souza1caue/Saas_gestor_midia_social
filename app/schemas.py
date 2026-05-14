from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    business_name: str
    instagram_handle: str
    business_segment: str
    business_description: str
    products_services: str | None = None
    main_offer: str | None = None
    target_audience_description: str
    audience_pain_points: str | None = None
    audience_desires: str | None = None
    brand_positioning: str | None = None
    brand_voice: str
    communication_style: str | None = None
    content_goals: str | None = None
    preferred_content_types: str | None = None
    competitors: str | None = None
    visual_references: str | None = None
    words_to_use: str | None = None
    words_to_avoid: str | None = None
    posting_frequency: str | None = None
    location: str | None = None
    website_url: str | None = None
    whatsapp_contact: str | None = None


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    business_name: str
    instagram_handle: str
    business_segment: str
    business_description: str
    target_audience_description: str
    brand_voice: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentCreate(BaseModel):
    content_type: str
    theme: str
    objective: str
    notes: Optional[str] = None


class CalendarCreate(BaseModel):
    days: int
    frequency: str


class CalendarItemRead(BaseModel):
    id: int
    date: date
    content_type: str
    theme: str
    objective: str
    status: str

    class Config:
        from_attributes = True
