from sqlalchemy.orm import Session

from app.models import User


BRAND_EMAIL = "violeiros-da-terra@local"

BRAND_PROFILE = {
    "name": "Equipe Violeiros da Terra",
    "email": BRAND_EMAIL,
    "hashed_password": "exclusive-page",
    "business_name": "Violeiros da Terra",
    "instagram_handle": "@violeirosdaterra",
    "business_segment": "Musica caipira, moda de viola e shows regionais",
    "business_description": (
        "Grupo musical dedicado a moda de viola, musica sertaneja raiz e apresentacoes "
        "ao vivo que valorizam a cultura do interior, a viola caipira e as historias da terra."
    ),
    "products_services": (
        "Shows ao vivo, apresentacoes culturais, eventos corporativos, festas tradicionais, "
        "conteudos musicais e divulgacao de agenda."
    ),
    "main_offer": "Contratacao de shows e acompanhamento da agenda de apresentacoes.",
    "target_audience_description": (
        "Pessoas que gostam de musica sertaneja raiz, moda de viola, cultura regional, "
        "festas tradicionais e experiencias musicais afetivas ligadas ao interior."
    ),
    "audience_pain_points": (
        "Saudade da musica raiz, dificuldade de encontrar eventos autenticos, falta de "
        "conteudos que representem a cultura caipira com respeito e qualidade."
    ),
    "audience_desires": (
        "Reviver boas memorias, acompanhar shows, celebrar a cultura regional e se sentir "
        "perto da viola, da terra e das tradicoes."
    ),
    "brand_positioning": (
        "Um grupo autentico, acolhedor e profissional que preserva a musica de raiz com "
        "presenca de palco, emocao e respeito pela cultura popular."
    ),
    "brand_voice": "Inspirador",
    "communication_style": "Emocional",
    "content_goals": "Divulgar shows, Gerar engajamento, Fortalecer marca, Atrair seguidores",
    "preferred_content_types": "Feed, Stories, Reels, Bastidores, Oferta",
    "competitors": "Bandas e duplas regionais de moda de viola, perfis de cultura sertaneja raiz.",
    "visual_references": (
        "Viola caipira, palco, estrada de terra, por do sol, fazenda, plateia, bastidores "
        "de show, elementos rusticos e fotografia documental."
    ),
    "brand_story": (
        "Violeiros da Terra nasce da vontade de manter viva a moda de viola e aproximar "
        "o publico das lembrancas, causos e emocoes da musica sertaneja raiz."
    ),
    "content_pillars": (
        "Agenda de shows, bastidores da banda, moda de viola, repertorio e letras, cultura "
        "caipira, datas comemorativas, depoimentos do publico, contratacao de shows."
    ),
    "repertoire": (
        "Moda de viola, sertanejo raiz, classicos regionais, musicas autorais e cancoes "
        "que remetem ao interior, familia, estrada, saudade e tradicao."
    ),
    "visual_identity": (
        "Visual rustico e elegante, cores terrosas com contraste, luz quente, textura de "
        "madeira, viola em destaque, fotos reais da banda, legibilidade forte para cartazes."
    ),
    "default_cta": (
        "Acompanhe a agenda, compartilhe com quem gosta de moda de viola e chame no direct "
        "para informacoes sobre shows."
    ),
    "words_to_use": "moda de viola, sertanejo raiz, viola caipira, nossa terra, tradicao, show, agenda",
    "words_to_avoid": "termos urbanos demais, girias fora do universo da marca, promessas exageradas",
    "posting_frequency": "3 vezes por semana",
    "location": "Brasil",
    "website_url": "",
    "whatsapp_contact": "",
    "instagram_page_name": "Violeiros da Terra",
    "niche": "Musica caipira e sertaneja raiz",
    "target_audience": "Publico que acompanha moda de viola, shows regionais e cultura caipira.",
}


def get_or_create_brand_user(db: Session) -> User:
    user = db.query(User).filter(User.email == BRAND_EMAIL).first()
    force_profile = False
    if not user:
        user = db.query(User).order_by(User.id.asc()).first()
        if not user:
            user = User(**BRAND_PROFILE)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        force_profile = True

    changed = False
    for field in ("name", "email", "hashed_password"):
        if getattr(user, field) != BRAND_PROFILE[field]:
            setattr(user, field, BRAND_PROFILE[field])
            changed = True

    for field, value in BRAND_PROFILE.items():
        current_value = getattr(user, field, None)
        if force_profile or (current_value in (None, "") and value):
            setattr(user, field, value)
            changed = True

    if changed:
        db.commit()
        db.refresh(user)
    return user
