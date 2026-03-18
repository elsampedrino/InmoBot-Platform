# InmoBot Premium — API Backend

Backend FastAPI del Plan Premium de InmoBot. Núcleo conversacional multi-tenant y multi-rubro para agentes de IA inmobiliarios.

## Principio rector

> **"La IA no busca, la IA explica."**
> PostgreSQL hace la búsqueda determinística. La API contiene la lógica de negocio. La IA se usa solo cuando aporta valor.

## Stack

- **FastAPI** — framework web async
- **PostgreSQL 15+** — motor de búsqueda y almacenamiento principal
- **SQLAlchemy 2.0 async** — ORM
- **asyncpg** — driver async para PostgreSQL
- **Claude Haiku** — clasificación / fallback de intención
- **Claude Sonnet** — redacción de respuestas conversacionales

## Estructura del proyecto

```
app/
├── main.py                     # Entry point FastAPI
├── core/
│   ├── config.py               # Settings (pydantic-settings)
│   ├── database.py             # Engine async, sesión, Base ORM
│   ├── logging.py              # Logging estructurado
│   └── security.py             # API key auth dependency
├── models/
│   ├── db_models.py            # SQLAlchemy ORM (mapeo de tablas)
│   ├── api_models.py           # Pydantic request/response schemas
│   └── domain_models.py        # Objetos internos del dominio (dataclasses)
├── routers/
│   ├── chat.py                 # POST /chat/message
│   ├── catalogo.py             # GET /catalogo/items
│   ├── leads.py                # POST/GET /leads
│   ├── analytics.py            # GET /analytics/*
│   ├── webhook_widget.py       # POST /webhook/widget
│   └── webhook_whatsapp.py     # POST /webhook/whatsapp
├── services/
│   ├── chat_orchestrator.py    # Orquestador del pipeline conversacional
│   ├── router_conversacional.py# Decide la ruta operativa de cada turno
│   ├── context_manager.py      # Gestiona estado y contexto multi-turno
│   ├── query_parser.py         # Lenguaje natural → filtros estructurados
│   ├── search_engine.py        # Filtros → SQL → resultados rankeados
│   ├── kb_service.py           # Consultas sobre knowledge base
│   ├── leads_service.py        # Creación y actualización de leads
│   ├── followups_service.py    # Programación de seguimientos
│   ├── prompt_service.py       # Composición dinámica de prompts
│   ├── ai_service.py           # Integración Haiku + Sonnet
│   ├── response_assembler.py   # Armado del payload de respuesta final
│   ├── analytics_service.py    # Registro de eventos de chat y conversión
│   ├── tenant_resolver.py      # Resolución de empresa y rubro activo
│   └── catalog_service.py      # Operaciones no-conversacionales de catálogo
└── repositories/
    ├── conversations_repository.py
    ├── items_repository.py
    ├── kb_repository.py
    ├── leads_repository.py
    ├── followups_repository.py
    └── analytics_repository.py
```

## Pipeline de un mensaje

```
Canal → Webhook → Chat Orchestrator
  → Tenant Resolver
  → Context Manager (carga estado)
  → Router Conversacional (decide ruta)
  → [Query Parser → Search Engine] | [KB Service] | [Leads Service]
  → Prompt Service
  → AI Service (Sonnet redacta)
  → Response Assembler
  → Analytics Service (registra evento)
  → Context Manager (actualiza estado)
  → Respuesta al canal
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

pip install -r requirements.txt
cp .env.example .env
# Editar .env con las credenciales reales
```

## Levantar en desarrollo

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/chat/message` | Endpoint principal del pipeline conversacional |
| `POST` | `/webhook/widget` | Recibe mensajes del widget web |
| `POST` | `/webhook/whatsapp` | Recibe webhooks de WhatsApp |
| `GET`  | `/catalogo/items` | Listado de items (admin) |
| `POST` | `/leads` | Crear lead manualmente |
| `GET`  | `/analytics/chats` | Métricas de chats |
| `GET`  | `/health` | Health check |

## Autenticación

Todos los endpoints (excepto `/health`) requieren el header:

```
X-API-Key: <API_SECRET_KEY>
```

## Fases de desarrollo

- **Fase 1** ✅ Esqueleto + Core + Modelos + Estructura
- **Fase 2** — Chat Orchestrator + pipeline mínimo funcional
- **Fase 3** — Router Conversacional + Context Manager
- **Fase 4** — Query Parser + Search Engine
- **Fase 5** — AI Service (Haiku + Sonnet)
- **Fase 6** — Leads, Analytics, KB
- **Fase 7** — Webhooks (Widget + WhatsApp)
