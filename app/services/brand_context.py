from __future__ import annotations

from datetime import date
from typing import Iterable

from app.models import CalendarEvent, GeneratedContent, User


def _value(source, field: str, fallback: str = "") -> str:
    return (getattr(source, field, None) or fallback or "").strip()


def _recent_content_summary(contents: Iterable[GeneratedContent] | None) -> str:
    if not contents:
        return "Sem historico recente relevante."

    lines = []
    for content in contents:
        created = content.created_at.strftime("%d/%m/%Y") if content.created_at else ""
        lines.append(
            f"- {created}: {content.content_type} sobre {content.theme}; "
            f"objetivo {content.objective}; titulo: {content.title}"
        )
    return "\n".join(lines)


def build_brand_context(
    user: User,
    content_type: str,
    theme: str,
    objective: str,
    notes: str = "",
    recent_contents: Iterable[GeneratedContent] | None = None,
    event: CalendarEvent | None = None,
) -> dict:
    event_context = ""
    if event:
        event_context = (
            f"{event.event_type}: {event.title} em {event.event_date.strftime('%d/%m/%Y')}. "
            f"Local: {event.location or 'a definir'}. Detalhes: {event.description or 'sem detalhes adicionais'}."
        )

    return {
        "brand": _value(user, "business_name", _value(user, "instagram_page_name", "Violeiros da Terra")),
        "handle": _value(user, "instagram_handle"),
        "segment": _value(user, "business_segment", _value(user, "niche", "musica regional")),
        "description": _value(user, "business_description"),
        "brand_story": _value(user, "brand_story"),
        "products": _value(user, "products_services"),
        "offer": _value(user, "main_offer"),
        "audience": _value(user, "target_audience_description", _value(user, "target_audience")),
        "pains": _value(user, "audience_pain_points"),
        "desires": _value(user, "audience_desires"),
        "positioning": _value(user, "brand_positioning"),
        "voice": _value(user, "brand_voice", "inspirador"),
        "style": _value(user, "communication_style", "emocional"),
        "goals": _value(user, "content_goals"),
        "preferred_types": _value(user, "preferred_content_types"),
        "content_pillars": _value(user, "content_pillars"),
        "repertoire": _value(user, "repertoire"),
        "visual_references": _value(user, "visual_references"),
        "visual_identity": _value(user, "visual_identity"),
        "default_cta": _value(user, "default_cta"),
        "words_to_use": _value(user, "words_to_use"),
        "words_to_avoid": _value(user, "words_to_avoid"),
        "posting_frequency": _value(user, "posting_frequency"),
        "location": _value(user, "location"),
        "content_type": content_type,
        "theme": theme.strip(),
        "objective": objective.strip(),
        "notes": notes.strip(),
        "event_context": event_context,
        "recent_contents": _recent_content_summary(recent_contents),
        "today": date.today().strftime("%d/%m/%Y"),
    }


def context_as_prompt(context: dict) -> str:
    return "\n".join(
        [
            f"Marca: {context['brand']} ({context['handle']})",
            f"Segmento: {context['segment']}",
            f"Descricao: {context['description']}",
            f"Historia da marca: {context['brand_story']}",
            f"Produtos/servicos: {context['products']}",
            f"Oferta principal: {context['offer']}",
            f"Publico: {context['audience']}",
            f"Dores do publico: {context['pains']}",
            f"Desejos do publico: {context['desires']}",
            f"Posicionamento: {context['positioning']}",
            f"Tom e estilo: {context['voice']} / {context['style']}",
            f"Objetivos de conteudo: {context['goals']}",
            f"Pilares editoriais: {context['content_pillars']}",
            f"Repertorio e temas musicais: {context['repertoire']}",
            f"Identidade visual: {context['visual_identity']}",
            f"Referencias visuais: {context['visual_references']}",
            f"CTA padrao: {context['default_cta']}",
            f"Palavras para usar: {context['words_to_use']}",
            f"Palavras para evitar: {context['words_to_avoid']}",
            f"Formato solicitado: {context['content_type']}",
            f"Tema solicitado: {context['theme']}",
            f"Objetivo solicitado: {context['objective']}",
            f"Observacoes da equipe: {context['notes'] or 'Nenhuma.'}",
            f"Evento vinculado: {context['event_context'] or 'Nenhum.'}",
            "Historico recente para evitar repeticao:",
            context["recent_contents"],
        ]
    )
