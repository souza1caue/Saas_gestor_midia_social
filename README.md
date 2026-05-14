# Social Media SaaS

Plataforma web SaaS em Python para gerar e organizar ideias de posts, legendas, roteiros, prompts de imagem, histórico e calendário de conteúdo para Instagram. Esta primeira versão não publica no Instagram e usa geradores locais em Python, sem API externa de IA.

## Stack

- Python 3.11+
- FastAPI
- Jinja2 Templates
- SQLite
- SQLAlchemy
- Passlib
- Python-dotenv
- Bootstrap 5
- Uvicorn

## Como instalar

```bash
cd social-media-saas
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```bash
copy .env.example .env
```

No Linux/macOS:

```bash
cp .env.example .env
```

## Como rodar

```bash
uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
```

O banco SQLite e as tabelas são criados automaticamente ao iniciar a aplicação.

## Estrutura de pastas

```text
social-media-saas/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── routers/
│   ├── services/
│   ├── templates/
│   └── static/
├── data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Funcionalidades atuais

- Cadastro de usuario com onboarding e briefing profissional de marca
- Login e logout com sessão em cookie
- Senha com hash seguro
- Dashboard personalizado
- Edicao de briefing em `/briefing`
- Geracao local de conteudo para feed, stories, carrossel e reels usando dados estrategicos da marca
- Histórico de conteúdos por usuário
- Visualização de detalhes do conteúdo
- Geracao e persistencia de calendario de conteudo
- Calendario mensal com eventos, como ensaio, show e gravacao
- Geracao de post a partir de eventos do calendario

## Próximas evoluções

- Alembic para migrations
- Recuperação de senha
- Editor avançado de conteúdo
- Status de aprovação e publicação manual
- Integração opcional com APIs de IA
- Integração futura com Instagram Graph API
