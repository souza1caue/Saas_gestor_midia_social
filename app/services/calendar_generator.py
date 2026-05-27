from datetime import date, timedelta

from app.models import User


CONTENT_TYPES = ["feed", "stories", "carrossel", "reels"]
OBJECTIVES = ["engajar", "divulgar", "educar", "autoridade", "vender", "interagir"]

STRATEGIC_SLOTS = {
    0: {
        "content_type": "reels",
        "objective": "autoridade",
        "theme": "Bastidor rapido da semana com gancho musical forte",
    },
    1: {
        "content_type": "carrossel",
        "objective": "educar",
        "theme": "Conteudo salvavel: curiosidade sobre moda de viola e musica caipira",
    },
    2: {
        "content_type": "stories",
        "objective": "interagir",
        "theme": "Story com enquete para escolher repertorio, lembranca ou proxima moda",
    },
    3: {
        "content_type": "reels",
        "objective": "engajar",
        "theme": "Trecho musical curto com pergunta emocional para comentarios",
    },
    4: {
        "content_type": "feed",
        "objective": "divulgar",
        "theme": "Agenda e contratacao com prova social e CTA claro",
    },
    5: {
        "content_type": "stories",
        "objective": "interagir",
        "theme": "Caixinha de perguntas, pedidos de musica e repost de respostas",
    },
    6: {
        "content_type": "reels",
        "objective": "engajar",
        "theme": "Melhor momento do show ou ensaio em formato compartilhavel",
    },
}

FREQUENCY_WEEKDAYS = {
    "diaria": [0, 1, 2, 3, 4, 5, 6],
    "dia_sim_dia_nao": [1, 3, 5, 6],
    "semanal": [4],
    "3x_semana": [2, 4, 6],
}


def _step_from_frequency(frequency: str) -> int:
    options = {
        "diaria": 1,
        "dia_sim_dia_nao": 2,
        "semanal": 7,
    }
    return options.get(frequency, 1)


def _allowed_weekdays(frequency: str) -> list[int]:
    return FREQUENCY_WEEKDAYS.get(frequency, FREQUENCY_WEEKDAYS["diaria"])


def _next_allowed_date(current: date, allowed_weekdays: list[int]) -> date:
    day = current
    while day.weekday() not in allowed_weekdays:
        day += timedelta(days=1)
    return day


def _theme_for_slot(user: User, slot: dict, index: int) -> str:
    brand = user.business_name or "marca"
    segment = user.business_segment or user.niche or "musica regional"
    audience = user.target_audience_description or user.target_audience or "publico"
    pillars = user.content_pillars or "tradicao, repertorio, bastidores, shows e relacionamento com o publico"
    repertoire = user.repertoire or "modas de viola e classicos sertanejos"
    base_theme = slot["theme"]
    variations = [
        f"{base_theme} para aproximar {brand} de {audience}; incluir CTA de comentario ou compartilhamento",
        f"{segment}: {base_theme} usando pilares como {pillars}; pensar em retencao e salvamento",
        f"{base_theme} conectado ao repertorio: {repertoire}; prever follow-up nos stories no dia seguinte",
    ]
    return variations[index % len(variations)][:255]


def generate_calendar(user: User, days: int, frequency: str) -> list[dict]:
    safe_days = max(1, min(days, 90))
    step = _step_from_frequency(frequency)
    start = date.today()
    items = []
    index = 0
    allowed_weekdays = _allowed_weekdays(frequency)
    current_date = _next_allowed_date(start, allowed_weekdays)

    while (current_date - start).days < safe_days:
        slot = STRATEGIC_SLOTS[current_date.weekday()]
        objective = slot["objective"]
        content_type = slot["content_type"]
        theme = _theme_for_slot(user, slot, index)
        items.append(
            {
                "date": current_date,
                "content_type": content_type,
                "theme": theme,
                "objective": objective,
                "status": "planejado",
            }
        )
        index += 1
        next_date = current_date + timedelta(days=step)
        current_date = _next_allowed_date(next_date, allowed_weekdays)

    return items


def generate_interactive_sequence(user: User, start_date: date, theme: str) -> list[dict]:
    brand = user.business_name or "marca"
    repertoire = user.repertoire or "modas de viola, repertorio raiz e bastidores"
    clean_theme = theme.strip() or "Escolha do publico para o proximo conteudo"
    follow_up_date = start_date + timedelta(days=1)

    return [
        {
            "date": start_date,
            "content_type": "feed",
            "theme": (
                f"{clean_theme}: post principal para abrir conversa com o publico de {brand}"
            )[:255],
            "objective": "engajar",
            "status": "sequencia: post principal",
        },
        {
            "date": start_date,
            "content_type": "stories",
            "theme": (
                f"{clean_theme}: story interativo com caixa de perguntas, enquete ou pedido de musica"
            )[:255],
            "objective": "interagir",
            "status": "sequencia: coletar respostas",
        },
        {
            "date": follow_up_date,
            "content_type": "stories",
            "theme": (
                f"{clean_theme}: responder ao publico usando o resultado da caixa/enquete; repertorio base: {repertoire}"
            )[:255],
            "objective": "interagir",
            "status": "sequencia: acao sobre resultado",
        },
    ]
