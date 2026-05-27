import json
import re
from random import choice

from app.config import get_settings
from app.models import User
from app.services.brand_context import build_brand_context, context_as_prompt


POST_TIMES = {
    "feed": ["08:30", "12:15", "18:30"],
    "stories": ["09:00", "14:00", "20:00"],
    "carrossel": ["11:00", "17:30", "19:30"],
    "reels": ["12:00", "18:00", "21:00"],
}

INTERACTION_CTAS = [
    "Comente qual moda de viola nao pode faltar no proximo repertorio.",
    "Marque alguem que canta essa junto do comeco ao fim.",
    "Responda nos comentarios: essa lembra qual momento da sua vida?",
    "Vote nos stories e ajude a escolher a proxima musica.",
    "Envie para quem tambem gosta de sertanejo raiz e moda de viola.",
]

OBJECTIVE_GUIDANCE = {
    "interagir": {
        "angle": "abrir conversa com o publico e estimular resposta simples",
        "interaction": "pergunta direta, enquete, pedido de musica, marcacao de amigos ou caixinha de perguntas",
    },
    "engajar": {
        "angle": "gerar identificacao emocional e comentarios espontaneos",
        "interaction": "pergunta afetiva ligada a memoria, repertorio ou experiencia em show",
    },
    "divulgar": {
        "angle": "apresentar agenda, novidade ou servico sem perder proximidade",
        "interaction": "convite para salvar, compartilhar e chamar no direct",
    },
    "vender": {
        "angle": "conduzir para contratacao ou contato com clareza",
        "interaction": "chamada para direct, WhatsApp ou indicacao de evento",
    },
    "educar": {
        "angle": "ensinar algo curto sobre moda de viola, repertorio ou cultura caipira",
        "interaction": "pergunta de conhecimento ou convite para contar uma lembranca",
    },
    "autoridade": {
        "angle": "mostrar experiencia, repertorio, bastidores e profissionalismo",
        "interaction": "pergunta sobre preferencia de show, formacao ou repertorio",
    },
}

FORMAT_PLAYBOOK = {
    "reels": {
        "hook": "comece nos 2 primeiros segundos com imagem forte, trecho cantado, pergunta ou frase de alto reconhecimento",
        "structure": "roteiro em cortes curtos: gancho, contexto rapido, momento musical/bastidor, prova emocional e CTA",
        "metric": "retencao, compartilhamentos, salvamentos e comentarios",
    },
    "carrossel": {
        "hook": "primeiro card com promessa clara, curiosidade ou pergunta que faca a pessoa arrastar",
        "structure": "sequencia de cards com uma ideia por tela, contraste entre tradicao e bastidor, fechamento com resumo e CTA",
        "metric": "salvamentos, compartilhamentos, avancos de card e comentarios",
    },
    "stories": {
        "hook": "primeiro story direto, com sticker de enquete, caixa de perguntas, quiz ou controle deslizante",
        "structure": "sequencia curta: contexto, sticker interativo, resposta/repost e chamada para proxima acao",
        "metric": "respostas, toques no sticker, DMs, cliques e retencao da sequencia",
    },
    "feed": {
        "hook": "primeira linha da legenda e texto da arte precisam deixar claro por que o post importa agora",
        "structure": "post de relacionamento: promessa, historia curta, valor pratico/emocional, prova e CTA",
        "metric": "comentarios qualificados, salvamentos, compartilhamentos e visitas ao perfil",
    },
}


def _value(user: User, field: str, fallback: str = "") -> str:
    return (getattr(user, field, None) or fallback or "").strip()


def _hashtags(user: User, theme: str, objective: str) -> str:
    context = build_brand_context(user, "", theme, objective)
    words = [context["segment"], theme, objective, context["brand"]]
    tags = []
    for word in words:
        cleaned = "".join(ch for ch in word.lower() if ch.isalnum())
        if cleaned:
            tags.append(f"#{cleaned}")
    tags.extend(["#modadeviola", "#sertanejoraiz", "#violacaipira"])
    return " ".join(dict.fromkeys(tags))


def _fallback_content(user: User, content_type: str, theme: str, objective: str, notes: str = "") -> dict:
    context = build_brand_context(user, content_type, theme, objective, notes)
    guidance = OBJECTIVE_GUIDANCE.get(objective, OBJECTIVE_GUIDANCE["engajar"])
    playbook = FORMAT_PLAYBOOK.get(content_type, FORMAT_PLAYBOOK["feed"])
    words_line = f" Use palavras e expressoes como: {context['words_to_use']}." if context["words_to_use"] else ""
    avoid_line = f" Evite: {context['words_to_avoid']}." if context["words_to_avoid"] else ""
    notes_line = f"\n\nObservacao da equipe: {notes.strip()}" if notes.strip() else ""

    title = f"{theme}: roteiro {content_type} para {context['brand']}"
    caption = (
        f"GANCHO: {theme}.\n\n"
        f"{context['brand']} quer puxar uma conversa real com quem acompanha {context['segment']}. "
        f"A ideia e {guidance['angle']} e conectar com o desejo do publico: "
        f"{context['desires'] or 'se sentir perto da musica, da tradicao e dos bastidores'}.\n\n"
        f"CONVERSA: conte uma lembranca, bastidor ou detalhe de repertorio que aproxime a banda das pessoas.\n\n"
        f"INTERACAO: {guidance['interaction']}.\n\n"
        f"FECHAMENTO: qual musica, lembranca ou momento voce quer ver por aqui?"
        f"{words_line}{avoid_line}{notes_line}"
    )
    cta_options = [context["default_cta"]] if context["default_cta"] else []
    cta_options.extend(INTERACTION_CTAS)
    if objective in {"vender", "divulgar"}:
        cta_options.extend(
            [
                "Chame no direct para saber mais sobre a agenda.",
                "Salve este post para conferir a proxima apresentacao.",
            ]
        )
    call_to_action = choice([option for option in cta_options if option])
    visual_script = (
        f"Brief de agencia para {content_type}\n"
        f"Objetivo do post: {guidance['angle']}.\n"
        f"Gancho: {playbook['hook']}.\n"
        f"Estrutura: {playbook['structure']}.\n\n"
        "Roteiro completo:\n"
        f"1. Abertura: use uma frase curta sobre {theme}, sem introducao longa.\n"
        "2. Contexto: explique em uma frase por que isso importa para o publico agora.\n"
        "3. Valor: entregue bastidor, memoria, curiosidade, trecho musical ou prova social.\n"
        f"4. Interacao: {guidance['interaction']}.\n"
        f"5. Conversao leve: conecte com agenda, repertorio, contratacao ou relacionamento com a comunidade.\n"
        f"6. Fechamento: {call_to_action}.\n\n"
        f"Metrica principal: {playbook['metric']}.\n"
        "Follow-up recomendado: no dia seguinte, publicar story respondendo comentarios, votos ou perguntas recebidas."
    )
    image_prompt = (
        f"Direcao visual e de producao para {content_type} da marca {context['brand']} ({context['handle']}), tema {theme}. "
        f"Identidade visual: {context['visual_identity']}. Referencias: {context['visual_references']}. "
        "Priorize leitura no celular, rosto/instrumento em destaque, texto curto na tela, contraste alto e linguagem nativa de Instagram. "
        "Defina enquadramento, cena principal, elementos de apoio, texto que aparece no post, ritmo de cortes quando for video, "
        "ordem dos cards quando for carrossel e sticker quando for story. "
        f"Evite termos ou abordagens: {context['words_to_avoid'] or 'nenhum'}. "
        "Inclua uma chamada curta que estimule comentario, voto, resposta, salvamento ou compartilhamento."
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


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _ai_content(context: dict) -> dict:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY nao configurada.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    instructions = (
        "Voce e diretor de estrategia de uma grande agencia de social media para uma banda brasileira de moda de viola. "
        "Crie conteudos prontos para Instagram com pensamento de funil, narrativa, retencao, distribuicao e comunidade. "
        "Aplique praticas atuais de Instagram: gancho imediato, conteudo nativo por formato, Reels com ritmo e retencao, "
        "carrossel com promessa forte e salvavel, stories com stickers interativos e follow-up, legendas conversacionais, "
        "CTAs especificos, incentivo a compartilhamento/salvamento e consistencia editorial. "
        "Nao use acentos em chaves JSON. Responda somente JSON valido com as chaves: "
        "title, caption, call_to_action, hashtags, visual_script, image_prompt, suggested_post_time. "
        "A legenda deve soar pronta para publicar, sem explicar o briefing, e abrir com uma primeira linha forte. "
        "A legenda deve terminar com convite claro para interacao, especialmente quando o objetivo for engajar ou interagir. "
        "O visual_script deve ser um roteiro completo de producao, com gancho, sequencia de cenas/cards/stories, texto de tela, "
        "fala sugerida quando fizer sentido, CTA, metrica principal e follow-up recomendado. "
        "No campo image_prompt, nao escreva prompt para IA criar imagem; escreva direcao visual para a equipe produzir "
        "o post, incluindo composicao, cena, texto na arte, ritmo, enquadramento, sticker/interacao e legibilidade no celular."
    )
    response = client.responses.create(
        model=settings.text_model,
        instructions=instructions,
        input=context_as_prompt(context),
        max_output_tokens=2400,
        temperature=0.7,
    )
    payload = _extract_json(response.output_text)
    return {
        "title": str(payload.get("title", "")).strip()[:255],
        "caption": str(payload.get("caption", "")).strip(),
        "call_to_action": str(payload.get("call_to_action", "")).strip()[:255],
        "hashtags": str(payload.get("hashtags", "")).strip(),
        "visual_script": str(payload.get("visual_script", "")).strip(),
        "image_prompt": str(payload.get("image_prompt", "")).strip(),
        "suggested_post_time": str(payload.get("suggested_post_time", "")).strip()[:40],
        "status": "rascunho",
    }


def _complete_missing(generated: dict, fallback: dict) -> dict:
    for key, value in fallback.items():
        if not generated.get(key):
            generated[key] = value
    generated["status"] = generated.get("status") or "rascunho"
    return generated


def generate_content(
    user: User,
    content_type: str,
    theme: str,
    objective: str,
    notes: str = "",
    recent_contents=None,
    event=None,
) -> dict:
    fallback = _fallback_content(user, content_type, theme, objective, notes)
    context = build_brand_context(
        user,
        content_type,
        theme,
        objective,
        notes,
        recent_contents=recent_contents,
        event=event,
    )
    try:
        return _complete_missing(_ai_content(context), fallback)
    except Exception:
        return fallback


def generate_content_from_event(user: User, event, content_type: str, objective: str, recent_contents=None) -> dict:
    context = build_brand_context(user, content_type, event.title, objective, event=event, recent_contents=recent_contents)
    event_date = event.event_date.strftime("%d/%m/%Y")
    theme = f"{event.title} em {event_date}"
    notes = (
        f"Evento do tipo {event.event_type}. "
        f"Local: {event.location or 'a definir'}. "
        f"Detalhes: {event.description or 'sem detalhes adicionais'}."
    )
    generated = generate_content(user, content_type, theme, objective, notes, recent_contents=recent_contents, event=event)
    generated["title"] = f"{event.title}: conteudo para {context['brand']}"
    return generated
