from random import choice

from app.models import User


POST_TIMES = {
    "feed": ["08:30", "12:15", "18:30"],
    "stories": ["09:00", "14:00", "20:00"],
    "carrossel": ["11:00", "17:30", "19:30"],
    "reels": ["12:00", "18:00", "21:00"],
}


def _value(user: User, field: str, fallback: str = "") -> str:
    return (getattr(user, field, None) or fallback or "").strip()


def _brand_context(user: User) -> dict:
    return {
        "brand": _value(user, "business_name", _value(user, "instagram_page_name", "sua marca")),
        "handle": _value(user, "instagram_handle"),
        "segment": _value(user, "business_segment", _value(user, "niche", "mercado")),
        "description": _value(user, "business_description", "negocio em crescimento"),
        "products": _value(user, "products_services", "produtos e servicos"),
        "offer": _value(user, "main_offer", "oferta principal"),
        "audience": _value(user, "target_audience_description", _value(user, "target_audience", "publico-alvo")),
        "pains": _value(user, "audience_pain_points", "duvidas, objecoes e falta de clareza"),
        "desires": _value(user, "audience_desires", "melhores resultados e mais seguranca na decisao"),
        "positioning": _value(user, "brand_positioning", "uma marca confiavel e especialista"),
        "voice": _value(user, "brand_voice", "profissional"),
        "style": _value(user, "communication_style", "consultivo"),
        "goals": _value(user, "content_goals", "gerar autoridade e engajamento"),
        "preferred_types": _value(user, "preferred_content_types", "feed, stories e reels"),
        "words_to_use": _value(user, "words_to_use"),
        "words_to_avoid": _value(user, "words_to_avoid"),
    }


def _hashtags(user: User, theme: str, objective: str) -> str:
    context = _brand_context(user)
    words = [context["segment"], theme, objective, context["brand"]]
    tags = []
    for word in words:
        cleaned = "".join(ch for ch in word.lower() if ch.isalnum())
        if cleaned:
            tags.append(f"#{cleaned}")
    tags.extend(["#instagrambrasil", "#conteudodigital", "#marketingdeconteudo"])
    return " ".join(dict.fromkeys(tags))


def generate_content(user: User, content_type: str, theme: str, objective: str, notes: str = "") -> dict:
    context = _brand_context(user)
    words_line = f" Use palavras e expressoes como: {context['words_to_use']}." if context["words_to_use"] else ""
    avoid_line = f" Evite: {context['words_to_avoid']}." if context["words_to_avoid"] else ""
    notes_line = f"\n\nObservacao da equipe: {notes.strip()}" if notes.strip() else ""

    title = f"{theme}: {objective} com foco em {context['segment']}"
    caption = (
        f"{context['brand']} fala com {context['audience']} sobre {theme}.\n\n"
        f"Contexto da marca: {context['description']}. A comunicacao deve reforcar o posicionamento de "
        f"{context['positioning']} e apresentar {context['products']} com um tom {context['voice']} "
        f"e estilo {context['style']}.\n\n"
        f"Este conteudo deve conectar a dor do publico ({context['pains']}) ao desejo principal "
        f"({context['desires']}), usando a oferta {context['offer']} como caminho natural para a proxima acao."
        f"{words_line}{avoid_line}{notes_line}"
    )
    call_to_action = choice(
        [
            "Chame no direct para entender o melhor proximo passo.",
            "Salve este conteudo para consultar antes de decidir.",
            "Compartilhe com alguem que precisa dessa solucao.",
            "Comente sua principal duvida para receber uma orientacao.",
        ]
    )
    visual_script = (
        f"Formato: {content_type}.\n"
        f"1. Gancho sobre {theme}, ligado a uma dor real: {context['pains']}.\n"
        f"2. Mostrar como {context['brand']} resolve ou orienta esse problema.\n"
        f"3. Conectar com o desejo do publico: {context['desires']}.\n"
        f"4. Inserir prova, bastidor, exemplo ou oferta: {context['offer']}.\n"
        f"5. Fechar com CTA: {call_to_action}"
    )
    image_prompt = (
        f"Arte profissional para Instagram da marca {context['brand']} ({context['handle']}), "
        f"segmento {context['segment']}, tema {theme}, publico {context['audience']}, "
        f"tom {context['voice']} e estilo {context['style']}. Visual alinhado ao posicionamento "
        f"{context['positioning']}, legivel no celular, sem usar termos proibidos: {context['words_to_avoid'] or 'nenhum'}."
    )

    return {
        "title": title,
        "caption": caption,
        "call_to_action": call_to_action,
        "hashtags": _hashtags(user, theme, objective),
        "visual_script": visual_script,
        "image_prompt": image_prompt,
        "suggested_post_time": choice(POST_TIMES.get(content_type, ["18:00"])),
        "status": "rascunho",
    }


def generate_content_from_event(user: User, event, content_type: str, objective: str) -> dict:
    context = _brand_context(user)
    event_date = event.event_date.strftime("%d/%m/%Y")
    theme = f"{event.title} em {event_date}"
    notes = (
        f"Evento do tipo {event.event_type}. "
        f"Local: {event.location or 'a definir'}. "
        f"Detalhes: {event.description or 'sem detalhes adicionais'}."
    )
    generated = generate_content(user, content_type, theme, objective, notes)
    generated["title"] = f"{event.title}: conteudo para {context['brand']}"
    generated["caption"] = (
        f"{context['brand']} tem um evento marcado: {event.title}, em {event_date}.\n\n"
        f"Use este conteudo para gerar expectativa em {context['audience']}, reforcar o posicionamento "
        f"de {context['positioning']} e conectar o evento aos desejos do publico: {context['desires']}.\n\n"
        f"{notes}"
    )
    generated["visual_script"] = (
        f"Formato: {content_type}.\n"
        f"1. Abertura com data e nome do evento: {event.title}.\n"
        f"2. Mostrar bastidores, preparacao ou beneficio para {context['audience']}.\n"
        f"3. Reforcar o segmento {context['segment']} e o diferencial da marca.\n"
        f"4. Fechar com CTA: {generated['call_to_action']}"
    )
    generated["image_prompt"] = (
        f"Arte de Instagram para divulgar {event.title}, data {event_date}, tipo {event.event_type}, "
        f"marca {context['brand']}, segmento {context['segment']}, tom {context['voice']}, "
        f"estilo visual profissional e legivel no celular."
    )
    return generated
