# InmoBot Premium -- Arquitectura de la API

Versión: 0.1 (Documento base para desarrollo con Claude Code)

## 1. Contexto del Proyecto

InmoBot Premium es un SaaS de asistentes conversacionales para
inmobiliarias y, en el futuro, otros rubros. El sistema es multi‑tenant
y multi‑rubro y utiliza PostgreSQL como motor principal de búsqueda y
almacenamiento.

Principio arquitectónico clave:

**"La IA no busca, la IA explica."**

Esto significa que: - PostgreSQL realiza la búsqueda determinística. -
La API contiene la lógica de negocio. - La IA se utiliza solo cuando es
necesario.

Objetivos: - baja latencia - bajo costo de IA - control total del
sistema - estabilidad en producción

------------------------------------------------------------------------

# 2. Arquitectura General

Flujo del sistema:

Usuario → Widget Web / WhatsApp → Webhook API → Router Conversacional →
Parser determinístico → SQL Search Engine → Postprocesamiento → IA
(redacción) → Respuesta al usuario

------------------------------------------------------------------------

# 3. Base de Datos

La base de datos está diseñada en PostgreSQL con arquitectura:

-   multi‑tenant
-   multi‑rubro

Tablas principales:

Empresas Rubros Empresa_Rubros Items (catálogo) KB_Documents KB_Chunks
Leads Conversaciones Mensajes Followups Contextos_Conversacion

Tablas de analítica premium:

premium_chat_logs premium_chat_log_items premium_conversion_logs
premium_conversion_log_items

------------------------------------------------------------------------

# 4. Arquitectura de la API

La API se desarrollará en **FastAPI**.

Estructura de proyecto:

app/ main.py

    core/
        config.py
        database.py
        logging.py

    routers/
        chat.py
        catalogo.py
        leads.py
        analytics.py
        webhook_whatsapp.py
        webhook_widget.py

    services/
        conversation_service.py
        search_service.py
        catalog_service.py
        lead_service.py

    parsers/
        query_parser.py
        intent_classifier.py

    ai/
        haiku_classifier.py
        sonnet_responder.py
        prompt_builder.py

    repositories/
        items_repository.py
        conversations_repository.py
        leads_repository.py
        analytics_repository.py

    models/
        schemas_api.py
        schemas_db.py

------------------------------------------------------------------------

# 5. Endpoint Principal

POST /chat/message

Ejemplo:

{ "empresa_slug": "inmobiliaria-lopez", "canal": "web", "session_id":
"abc123", "mensaje": "Busco un depto de 2 ambientes en Palermo" }

Este endpoint ejecuta todo el pipeline conversacional.

------------------------------------------------------------------------

# 6. Endpoints secundarios

Catálogo

GET /catalogo/items GET /catalogo/items/{id}

Leads

POST /leads GET /leads

Analítica

GET /analytics/conversiones GET /analytics/chats

------------------------------------------------------------------------

# 7. Pipeline de Consulta

chat_router → conversation_service → query_parser → search_service →
repository SQL → result_ranker → sonnet_responder → respuesta

------------------------------------------------------------------------

# 8. Parser determinístico

Transforma lenguaje natural en filtros estructurados.

Ejemplo:

Usuario: "Busco casa con pileta en nordelta"

Parser:

{ "intent": "buscar_item", "tipo": "casa", "atributos": { "pileta": true
}, "zona": "nordelta" }

------------------------------------------------------------------------

# 9. SQL Search Engine

Ejemplo de consulta:

SELECT \* FROM items WHERE id_empresa = :empresa AND activo = true AND
tipo = 'casa' LIMIT 5

------------------------------------------------------------------------

# 10. Uso de IA

La IA se usa solo en dos lugares.

Clasificación (Haiku) - consultas ambiguas

Generación de respuesta (Sonnet) - redacción final

------------------------------------------------------------------------

# 11. Sistema de Prompts

El prompt se construye dinámicamente con:

rubro_prompts empresa_prompt_overrides

prompt final:

system_prompt + style_prompt + brand_voice + prompt_extra

------------------------------------------------------------------------

# 12. Logging y Analítica

Cada interacción genera registros en:

premium_chat_logs premium_chat_log_items

Datos registrados:

response_time_ms model tokens_input tokens_output items_mostrados

------------------------------------------------------------------------

# 13. Contexto Conversacional

Se almacena en:

contextos_conversacion

Esto permite mantener el contexto entre mensajes.

------------------------------------------------------------------------

# 14. Integración con Canales

Widget

POST /webhook/widget

WhatsApp

POST /webhook/whatsapp

Ambos terminan en:

POST /chat/message

------------------------------------------------------------------------

# 15. Principios de Diseño

1.  SQL primero
2.  IA mínima necesaria
3.  lógica centralizada en API
4.  arquitectura multi‑tenant
5.  observabilidad completa
6.  diseño preparado para múltiples rubros

------------------------------------------------------------------------

Fin del documento base.
