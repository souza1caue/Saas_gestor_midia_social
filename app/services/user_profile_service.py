from app.models import User


def build_user_context(user: User) -> dict:
    return {
        "business_name": user.business_name,
        "instagram_handle": user.instagram_handle,
        "business_segment": user.business_segment,
        "target_audience_description": user.target_audience_description,
        "brand_voice": user.brand_voice,
        "communication_style": user.communication_style,
    }
