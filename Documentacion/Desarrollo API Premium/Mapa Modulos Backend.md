# InmoBot Premium – Mapa de Módulos del Backend
Versión: 0.1

Este documento define el **mapa de módulos del backend** de InmoBot Premium y las responsabilidades de cada componente.
Su objetivo es servir como puente entre la arquitectura conceptual ya definida y la futura implementación en FastAPI.

La meta principal es evitar superposición de responsabilidades y establecer una separación clara entre:

- orquestación conversacional
- lógica de negocio
- acceso a datos
- integración con IA
- analítica
- canales de entrada

---

# 1. Objetivo de este documento

Este documento busca responder cuatro preguntas clave:

1. Qué módulos concretos tendrá el backend
2. Qué responsabilidad tiene cada módulo
3. Qué cosas no debe hacer cada módulo
4. Cómo se relacionan entre sí

No define todavía el detalle de clases, funciones o endpoints finales.
Define la **estructura funcional del sistema**.

---

# 2. Principio rector del diseño

El backend de InmoBot Premium debe seguir estos principios:

- responsabilidades bien separadas
- lógica de negocio centralizada en la API
- búsqueda determinística con PostgreSQL
- IA utilizada solo cuando aporta valor
- trazabilidad analítica completa
- diseño multi-tenant y multi-rubro desde el inicio

Principio operativo ya definido:

**La IA no busca, la IA explica.**

---

# 3. Vista general de módulos

Mapa general propuesto:

```text
Canales de Entrada
    ├── Widget Web Adapter
    └── WhatsApp Adapter

API Orchestration
    ├── Chat Application Layer
    ├── Router Conversacional
    ├── Conversation Context Manager
    └── Response Assembly Layer

Core Business Modules
    ├── Query Parser
    ├── Search Engine
    ├── Knowledge Base Service
    ├── Leads Service
    ├── Followups Service
    ├── Prompt Service
    └── AI Response Service

Support Modules
    ├── Analytics Service
    ├── Tenant & Rubro Resolver
    ├── Catalog Service
    ├── Auth / Security
    ├── Config / Feature Flags
    └── Observability / Logging

Persistence Layer
    ├── Conversations Repository
    ├── Items Repository
    ├── KB Repository
    ├── Leads Repository
    ├── Followups Repository
    └── Analytics Repository
```

---

# 4. Módulo: Canales de Entrada

## 4.1 Widget Web Adapter

Responsabilidad:
- recibir mensajes desde el widget web
- validar payload de entrada
- transformar el formato del canal a un formato interno estándar
- reenviar al flujo central

No debe:
- contener lógica conversacional
- consultar catálogo directamente
- generar respuestas por sí mismo

---

## 4.2 WhatsApp Adapter

Responsabilidad:
- recibir y validar webhooks de WhatsApp
- normalizar mensajes entrantes
- mapear metadata del canal
- reenviar al flujo central

No debe:
- contener lógica de negocio
- decidir rutas conversacionales
- persistir directamente lógica compleja

Observación:
El sistema debe tratar ambos canales como adaptadores del mismo flujo interno.

---

# 5. Módulo: Chat Application Layer

Este es el punto de entrada interno del sistema conversacional.

Responsabilidad:
- recibir el mensaje ya normalizado
- iniciar el pipeline conversacional
- coordinar de forma general la ejecución del turno
- devolver la respuesta final al canal correspondiente

No debe:
- contener reglas de routing detalladas
- implementar parsing o búsqueda directamente
- construir SQL
- generar prompts directamente

Es el módulo orquestador de alto nivel.

---

# 6. Módulo: Router Conversacional

Responsabilidad:
- decidir qué flujo operativo corresponde ejecutar
- usar el mensaje actual, el contexto y el estado conversacional
- derivar a búsqueda, KB, lead, visita, asesor o fallback
- disparar señales de negocio

No debe:
- parsear filtros detallados
- ejecutar búsquedas SQL
- redactar la respuesta final

Este módulo ya fue definido en el documento específico de router conversacional.

---

# 7. Módulo: Conversation Context Manager

Responsabilidad:
- recuperar el contexto actual de la conversación
- actualizar resumen conversacional
- mantener estado estructurado mínimo
- resolver referencias recientes a items y acciones pendientes

Ejemplos de datos a mantener:
- última intención relevante
- items mostrados recientemente
- último item referenciado
- flags como esperando_contacto o esperando_visita
- filtros activos de búsqueda

No debe:
- decidir rutas por sí solo
- ejecutar lógica comercial
- reemplazar al router

Este módulo es clave para coherencia multi-turno.

---

# 8. Módulo: Query Parser

Responsabilidad:
- traducir lenguaje natural en filtros estructurados
- detectar atributos, zonas, tipo, precio, categoría y otras entidades
- normalizar sinónimos y variantes del lenguaje
- producir una estructura utilizable por el Search Engine

No debe:
- decidir la ruta operativa principal
- generar texto al usuario
- acceder directamente a la base sin pasar por servicios/repositorios

Debe funcionar preferentemente con reglas y diccionarios.
Solo usar IA en fallback.

---

# 9. Módulo: Search Engine

Responsabilidad:
- recibir filtros estructurados
- construir consultas SQL dinámicas
- ejecutar búsqueda en PostgreSQL
- rankear candidatos
- devolver resultados consistentes y explicables

No debe:
- interpretar intención del usuario
- redactar la respuesta final
- manejar leads o followups
- interactuar directamente con el canal

Este módulo ya fue definido en el documento específico de Search Engine.

---

# 10. Módulo: Knowledge Base Service

Responsabilidad:
- responder preguntas institucionales o documentales
- consultar `kb_documents` y `kb_chunks`
- recuperar contenido útil según empresa y rubro
- preparar contexto para que la IA redacte la respuesta si corresponde

No debe:
- reemplazar la búsqueda de catálogo
- capturar leads salvo que el flujo lo indique externamente
- definir el estilo global de respuesta por sí solo

Ejemplos de uso:
- horarios
- comisiones
- documentación requerida
- forma de trabajo de la empresa

---

# 11. Módulo: Leads Service

Responsabilidad:
- crear y actualizar leads
- consolidar datos de contacto
- registrar señales de interés comercial
- asociar leads con conversaciones y eventos

No debe:
- decidir por sí solo cuándo capturar un lead
- gestionar la conversación completa
- enviar respuestas conversacionales largas

Debe operar a pedido del flujo definido por el router y la capa de orquestación.

---

# 12. Módulo: Followups Service

Responsabilidad:
- crear y actualizar followups
- programar acciones futuras
- reflejar estados del seguimiento comercial
- dejar trazabilidad de las interacciones comerciales posteriores

No debe:
- reemplazar CRM completo
- tomar decisiones autónomas de conversación
- consultar catálogo

Su rol es operativo y comercial.

---

# 13. Módulo: Prompt Service

Responsabilidad:
- construir el prompt final a partir de:
  - rubro_prompts
  - empresa_prompt_overrides
  - contexto del turno
  - resultados de búsqueda o KB
- unificar brand voice y reglas del rubro

No debe:
- decidir qué flujo ejecutar
- consultar directamente el catálogo
- medir analítica por sí solo

Este módulo centraliza la composición de prompts y evita duplicación.

---

# 14. Módulo: AI Response Service

Responsabilidad:
- invocar modelos de IA cuando el flujo lo requiera
- usar Haiku para clasificación o fallback
- usar Sonnet para redacción final
- devolver salidas estructuradas o texto según el caso

No debe:
- reemplazar al router ni al parser determinístico
- decidir la arquitectura del flujo
- acceder directamente a datos sin contexto preparado

Este módulo es una integración controlada con IA, no el núcleo del negocio.

---

# 15. Módulo: Response Assembly Layer

Responsabilidad:
- tomar la salida del flujo ejecutado
- formatear la respuesta final según canal
- adjuntar metadata útil
- asegurar consistencia del payload de salida

No debe:
- decidir intención
- volver a buscar datos
- ejecutar lógica comercial compleja

Sirve para desacoplar la lógica del negocio del formato de respuesta.

---

# 16. Módulo: Analytics Service

Responsabilidad:
- registrar eventos de chat
- registrar items mostrados
- registrar eventos de conversión
- dejar trazabilidad del uso de IA, tiempos, tokens y rutas elegidas

Tablas involucradas:
- premium_chat_logs
- premium_chat_log_items
- premium_conversion_logs
- premium_conversion_log_items

No debe:
- tomar decisiones conversacionales
- depender del canal
- modificar la lógica principal del turno

Su rol es observabilidad y medición del negocio.

---

# 17. Módulo: Tenant & Rubro Resolver

Responsabilidad:
- resolver empresa activa
- resolver rubro activo o por defecto
- validar que la empresa tenga habilitado ese rubro
- cargar configuración contextual necesaria

No debe:
- ejecutar búsqueda
- generar respuestas
- capturar leads

Este módulo es clave para el aislamiento multi-tenant y multi-rubro.

---

# 18. Módulo: Catalog Service

Responsabilidad:
- exponer operaciones de catálogo no conversacionales
- obtener item por id
- importar/exportar catálogo
- consultar listados administrativos si fueran necesarios

No debe:
- asumir comportamiento conversacional
- reemplazar al Search Engine para búsquedas semánticas o guiadas

Es el módulo orientado al catálogo como entidad de negocio.

---

# 19. Módulo: Auth / Security

Responsabilidad:
- autenticación y autorización de endpoints administrativos
- validación de integridad de webhooks
- protección de datos sensibles
- control de acceso entre empresas

No debe:
- mezclar seguridad con lógica de negocio
- almacenar reglas conversacionales

---

# 20. Módulo: Config / Feature Flags

Responsabilidad:
- centralizar configuraciones operativas
- permitir activar/desactivar funcionalidades por empresa o plan
- soportar evolución gradual del producto

Ejemplos:
- IA habilitada
- followups habilitados
- límite de items
- modo de búsqueda especial por rubro

No debe:
- contener lógica del flujo en sí misma

---

# 21. Módulo: Observability / Logging Técnico

Responsabilidad:
- logging técnico del backend
- trazas de errores
- correlación por request_id / session_id
- métricas de infraestructura

No debe:
- reemplazar analytics funcional
- mezclar métricas técnicas con métricas comerciales

Es complementario al Analytics Service.

---

# 22. Capa de Persistencia: Repositories

Los repositories encapsulan el acceso a datos.

Principio:
**ningún módulo de negocio debería consultar SQL directamente salvo a través de repositories o componentes equivalentes bien delimitados.**

Repositorios esperados:

## Conversations Repository
- conversaciones
- mensajes
- contextos_conversacion

## Items Repository
- items
- búsquedas específicas
- lookup por item

## KB Repository
- kb_documents
- kb_chunks

## Leads Repository
- leads

## Followups Repository
- followups

## Analytics Repository
- premium_chat_logs
- premium_chat_log_items
- premium_conversion_logs
- premium_conversion_log_items

Los repositories no deben contener reglas conversacionales complejas.
Su responsabilidad es acceso consistente a los datos.

---

# 23. Relación entre módulos

Flujo típico de búsqueda:

1. Canal Adapter normaliza mensaje
2. Chat Application Layer inicia turno
3. Tenant & Rubro Resolver carga contexto base
4. Conversation Context Manager recupera estado
5. Router Conversacional decide ruta
6. Query Parser extrae filtros
7. Search Engine busca candidatos
8. Prompt Service arma prompt
9. AI Response Service redacta respuesta
10. Response Assembly Layer arma payload final
11. Analytics Service registra evento
12. Context Manager actualiza contexto
13. Se responde al canal

Flujo típico de pregunta KB:

1. Canal Adapter
2. Chat Application Layer
3. Tenant & Rubro Resolver
4. Context Manager
5. Router Conversacional
6. Knowledge Base Service
7. Prompt Service
8. AI Response Service
9. Response Assembly Layer
10. Analytics Service

Flujo típico de lead:

1. Canal Adapter
2. Chat Application Layer
3. Router Conversacional
4. Leads Service
5. Analytics Service
6. Response Assembly Layer

---

# 24. Separaciones clave de responsabilidad

Para evitar errores de diseño, estas separaciones deben respetarse siempre:

## Router ≠ Parser
- Router decide flujo
- Parser extrae filtros

## Search Engine ≠ Catalog Service
- Search Engine busca conversacionalmente
- Catalog Service expone operaciones de catálogo

## Analytics funcional ≠ Logging técnico
- Analytics mide negocio
- Logging técnico mide infraestructura

## Prompt Service ≠ AI Response Service
- Prompt Service construye contexto de prompt
- AI Response Service ejecuta el modelo

## Context Manager ≠ Leads Service
- Context Manager mantiene estado conversacional
- Leads Service maneja entidad comercial

---

# 25. Propuesta de agrupación en FastAPI

Estructura de alto nivel sugerida:

```text
app/
  main.py

  routers/
    chat.py
    webhook_widget.py
    webhook_whatsapp.py
    catalogo.py
    leads.py
    analytics.py

  services/
    chat_orchestrator.py
    router_conversacional.py
    context_manager.py
    query_parser.py
    search_engine.py
    kb_service.py
    leads_service.py
    followups_service.py
    prompt_service.py
    ai_service.py
    response_assembler.py
    analytics_service.py
    tenant_resolver.py
    catalog_service.py

  repositories/
    conversations_repository.py
    items_repository.py
    kb_repository.py
    leads_repository.py
    followups_repository.py
    analytics_repository.py

  core/
    config.py
    database.py
    security.py
    logging.py

  models/
    api_models.py
    domain_models.py
    db_models.py
```

Esto puede ajustarse más adelante, pero ya ofrece una base clara para implementación.

---

# 26. Beneficios de este mapa de módulos

- evita mezcla de responsabilidades
- facilita implementación incremental
- permite testear cada componente por separado
- ayuda a Claude Code a generar piezas coherentes
- mejora mantenibilidad
- prepara el sistema para crecimiento futuro

---

# 27. Objetivo final

El backend Premium no debe crecer como un workflow disperso ni como una colección de scripts.
Debe crecer como un sistema modular, medible y extensible.

Este mapa de módulos es el primer paso para transformar la arquitectura conceptual ya definida en una arquitectura implementable.

---

Fin del documento.
