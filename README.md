# Violeiros da Terra - Gestor de Conteudo

Pagina web exclusiva em Python para gerar e organizar ideias de posts, legendas, roteiros, direcoes visuais, historico e calendario de conteudo para a conta Violeiros da Terra.

O projeto nao funciona mais como SaaS multi-conta. Ao abrir a aplicacao, o sistema usa automaticamente o briefing fixo da marca definido em `app/brand.py`.

## Stack

- Python 3.11+
- FastAPI
- Jinja2 Templates
- SQLite
- SQLAlchemy
- Python-dotenv
- Bootstrap 5
- Uvicorn

## Como instalar

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```bash
copy .env.example .env
```

Para habilitar geracao de texto por IA, informe sua chave da OpenAI no `.env`:

```env
OPENAI_API_KEY=sua_chave_aqui
TEXT_MODEL=gpt-5-mini
```

## Como rodar

```bash
uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
```

O banco SQLite e as tabelas sao criados automaticamente ao iniciar a aplicacao.

## Funcionalidades atuais

- Perfil unico da marca Violeiros da Terra
- Acesso direto sem cadastro ou login
- Dashboard exclusivo
- Edicao da estrategia da marca em `/briefing`
- Geracao de conteudo por IA para feed, stories, carrossel e reels, com fallback local
- Contexto rico com estrategia, pilares editoriais, repertorio, identidade visual, historico recente e eventos
- Direcao visual para orientar arte, foto, video, carrossel ou edicao do post
- Historico de conteudos da marca
- Status editorial: rascunho, aprovado, publicado e arquivado
- Visualizacao de detalhes do conteudo
- Geracao e persistencia de calendario de conteudo
- Calendario mensal com eventos, como ensaio, show e gravacao
- Geracao de post a partir de eventos do calendario
