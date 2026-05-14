from datetime import date, timedelta

from app.models import User


CONTENT_TYPES = ["feed", "stories", "carrossel", "reels"]
OBJECTIVES = ["educar", "engajar", "autoridade", "vender", "divulgar"]


def _step_from_frequency(frequency: str) -> int:
    options = {
        "diaria": 1,
        "dia_sim_dia_nao": 2,
        "semanal": 7,
    }
    return options.get(frequency, 1)


def generate_calendar(user: User, days: int, frequency: str) -> list[dict]:
    safe_days = max(1, min(days, 90))
    step = _step_from_frequency(frequency)
    start = date.today()
    items = []
    index = 0

    for offset in range(0, safe_days, step):
        content_date = start + timedelta(days=offset)
        objective = OBJECTIVES[index % len(OBJECTIVES)]
        content_type = CONTENT_TYPES[index % len(CONTENT_TYPES)]
        segment = user.business_segment or user.niche or "seu segmento"
        audience = user.target_audience_description or user.target_audience or "seu publico"
        theme = f"{segment}: ideia {objective} para {audience}"
        items.append(
            {
                "date": content_date,
                "content_type": content_type,
                "theme": theme,
                "objective": objective,
                "status": "planejado",
            }
        )
        index += 1

    return items
