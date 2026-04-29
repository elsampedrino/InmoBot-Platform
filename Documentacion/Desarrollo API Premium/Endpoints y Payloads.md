# InmoBot Premium – Especificación de Endpoints y Payloads
Versión: 0.1

Este documento define la **API pública y operativa** del backend de InmoBot Premium.
Su objetivo es traducir la arquitectura, el mapa de módulos y los contratos internos a una interfaz HTTP clara, consistente y preparada para implementación en FastAPI.

Este documento cubre:

- endpoints públicos de conversación
- webhooks de canales
- endpoints operativos de catálogo
- endpoints de leads
- endpoints de analítica
- formatos de request/response
- convenciones de errores
- criterios de validación

---

# 1. Principios de diseño de la API

La API debe seguir estos principios:

- endpoints claros y consistentes
- payloads previsibles
- separación entre API conversacional y API administrativa
- diseño multi-tenant
- respuestas fáciles de consumir por widget y WhatsApp
- trazabilidad por `request_id` y `session_id`

Reglas generales:

1. JSON como formato por defecto
2. Fechas en ISO 8601
3. Identificadores con nombres explícitos
4. Errores con estructura estándar
5. La lógica de negocio vive en servicios internos, no en los routers HTTP

---

# 2. Convenciones globales

## 2.1 Headers sugeridos

- `X-Request-Id`: correlación técnica
- `X-Channel`: origen del mensaje cuando aplique
- `Authorization: Bearer <token>` para endpoints administrativos
- firma o token de validación para webhooks externos

## 2.2 Respuesta estándar exitosa

No todos los endpoints necesitan envolver la respuesta, pero cuando convenga se recomienda una estructura como esta:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_123"
  }
}
```

## 2.3 Respuesta estándar de error

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "El campo mensaje es obligatorio.",
    "details": {
      "field": "mensaje"
    }
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

---

# 3. Endpoint principal conversacional

## 3.1 POST `/chat/message`

Este es el endpoint principal del sistema conversacional.
Recibe un mensaje del usuario y ejecuta el pipeline completo del turno.

### Request

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "canal": "web",
  "session_id": "sess_abc_123",
  "message_id": "msg_ext_001",
  "mensaje": "Busco un depto de 2 ambientes en Palermo",
  "user_identity": {
    "nombre": null,
    "telefono": null,
    "email": null
  },
  "channel_metadata": {
    "user_agent": "Mozilla/5.0"
  }
}
```

### Campos obligatorios
- `empresa_slug`
- `canal`
- `session_id`
- `mensaje`

### Campos opcionales
- `message_id`
- `user_identity`
- `channel_metadata`

### Response

```json
{
  "success": true,
  "data": {
    "message_text": "Encontré algunas opciones en Palermo que podrían interesarte.",
    "items": [
      {
        "id_item": "uuid_item_1",
        "titulo": "Departamento 2 ambientes en Palermo",
        "precio": 120000,
        "moneda": "USD",
        "tipo": "departamento",
        "categoria": "venta"
      }
    ],
    "quick_replies": [
      "Ver más detalles",
      "Hablar con un asesor"
    ],
    "conversation": {
      "id_conversacion": 456,
      "id_lead": 789
    }
  },
  "meta": {
    "request_id": "req_123",
    "route": "buscar_catalogo",
    "response_time_ms": 930
  }
}
```

### Posibles códigos HTTP
- `200 OK`
- `400 Bad Request`
- `404 Not Found` si `empresa_slug` no existe
- `422 Unprocessable Entity`
- `500 Internal Server Error`

### Validaciones
- `mensaje` no puede estar vacío
- `canal` debe pertenecer a un conjunto permitido: `web`, `whatsapp`, `api`
- `empresa_slug` debe existir y estar activa

---

# 4. Endpoints de Webhooks de canales

Estos endpoints reciben payloads específicos del canal y los transforman al formato interno estándar.

## 4.1 POST `/webhook/widget`

### Objetivo
Recibir mensajes desde el widget web.

### Request ejemplo

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "session_id": "web_123",
  "mensaje": "Hola, busco una casa con pileta",
  "page_url": "https://sitio.com/propiedades",
  "user_agent": "Mozilla/5.0"
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "accepted": true
  },
  "meta": {
    "request_id": "req_124"
  }
}
```

### Observación
Este endpoint puede responder con payload mínimo si el canal no necesita formato conversacional completo en esa capa.

---

## 4.2 POST `/webhook/whatsapp`

### Objetivo
Recibir mensajes desde el proveedor de WhatsApp.

### Request
Dependerá del proveedor utilizado.
La API debe adaptarlo internamente.

Ejemplo abstracto:

```json
{
  "from": "+54911XXXXXXX",
  "message_id": "wamid-001",
  "text": "Quiero ver el segundo departamento",
  "timestamp": "2026-03-13T18:22:00Z",
  "metadata": {
    "phone_number_id": "123456"
  }
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "accepted": true
  }
}
```

### Validaciones
- firma del webhook
- idempotencia por `message_id` cuando corresponda
- normalización del payload externo

---

# 5. Endpoints de catálogo

Estos endpoints son operativos y no reemplazan al flujo conversacional.

## 5.1 GET `/catalogo/items`

### Objetivo
Consultar items de catálogo por filtros explícitos.

### Query params sugeridos
- `empresa_slug`
- `id_rubro`
- `tipo`
- `categoria`
- `activo`
- `limit`
- `offset`

### Ejemplo

`GET /catalogo/items?empresa_slug=inmobiliaria-lopez&tipo=departamento&activo=true&limit=20`

### Response

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id_item": "uuid_item_1",
        "external_id": "PROP-1001",
        "titulo": "Departamento 2 ambientes en Palermo",
        "precio": 120000,
        "moneda": "USD",
        "activo": true
      }
    ]
  },
  "meta": {
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 5.2 GET `/catalogo/items/{id_item}`

### Objetivo
Obtener detalle administrativo o técnico de un item.

### Response

```json
{
  "success": true,
  "data": {
    "id_item": "uuid_item_1",
    "external_id": "PROP-1001",
    "titulo": "Departamento 2 ambientes en Palermo",
    "descripcion": "Departamento completo...",
    "precio": 120000,
    "moneda": "USD",
    "tipo": "departamento",
    "categoria": "venta",
    "atributos": {
      "ambientes": 2,
      "metros": 54,
      "barrio": "Palermo"
    },
    "media": []
  }
}
```

### Posibles códigos
- `200 OK`
- `404 Not Found`

---

## 5.3 POST `/catalogo/import`

### Objetivo
Ejecutar importación de catálogo para el rubro inmobiliaria u otros rubros futuros.

### Request ejemplo

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "source": "csv_upload",
  "options": {
    "modo": "upsert",
    "usuario": "admin@empresa.com"
  }
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "job_status": "completed",
    "items_inserted": 120,
    "items_updated": 35,
    "items_skipped": 2
  }
}
```

### Observación
Más adelante este endpoint podría volverse asíncrono si el volumen crece.

---

## 5.4 POST `/catalogo/export`

### Objetivo
Exportar catálogo estructurado.

### Request ejemplo

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "format": "json"
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "items": []
  }
}
```

---

# 6. Endpoints de leads

## 6.1 POST `/leads`

### Objetivo
Crear lead manual o externamente, fuera del flujo conversacional.

### Request

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "nombre": "Juan Pérez",
  "telefono": "+54911XXXXXXX",
  "email": "juan@email.com",
  "canal": "web",
  "metadata": {
    "source": "landing"
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "id_lead": 789,
    "estado": "nuevo"
  }
}
```

---

## 6.2 GET `/leads`

### Objetivo
Listar leads de una empresa.

### Query params sugeridos
- `empresa_slug`
- `estado`
- `canal`
- `limit`
- `offset`

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id_lead": 789,
        "nombre": "Juan Pérez",
        "telefono": "+54911XXXXXXX",
        "email": "juan@email.com",
        "canal": "web",
        "estado": "nuevo",
        "created_at": "2026-03-13T18:15:00Z"
      }
    ]
  },
  "meta": {
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 6.3 GET `/leads/{id_lead}`

### Objetivo
Obtener detalle de un lead.

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "id_lead": 789,
    "nombre": "Juan Pérez",
    "telefono": "+54911XXXXXXX",
    "email": "juan@email.com",
    "canal": "web",
    "estado": "nuevo",
    "metadata": {
      "source": "chat_flow"
    }
  }
}
```

---

## 6.4 PATCH `/leads/{id_lead}`

### Objetivo
Actualizar parcialmente un lead.

### Request ejemplo

```json
{
  "estado": "contactado",
  "nombre": "Juan P."
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "id_lead": 789,
    "estado": "contactado"
  }
}
```

---

# 7. Endpoints de conversaciones

## 7.1 GET `/conversaciones/{id_conversacion}`

### Objetivo
Obtener metadata general de una conversación.

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "id_conversacion": 456,
    "id_lead": 789,
    "id_empresa": 12,
    "canal": "web",
    "inicio": "2026-03-13T18:10:00Z",
    "fin": null
  }
}
```

---

## 7.2 GET `/conversaciones/{id_conversacion}/mensajes`

### Objetivo
Obtener mensajes de una conversación.

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id_mensaje": 1,
        "emisor": "user",
        "mensaje": "Busco un depto de 2 ambientes en Palermo",
        "timestamp": "2026-03-13T18:10:00Z"
      },
      {
        "id_mensaje": 2,
        "emisor": "assistant",
        "mensaje": "Encontré algunas opciones...",
        "timestamp": "2026-03-13T18:10:01Z"
      }
    ]
  }
}
```

---

# 8. Endpoints de followups

## 8.1 POST `/followups`

### Objetivo
Crear followup manual o programado.

### Request ejemplo

```json
{
  "id_lead": 789,
  "id_conversacion": 456,
  "tipo": "visita_pendiente",
  "fecha_programada": "2026-03-15T15:00:00Z",
  "payload": {
    "item_id": "uuid_item_1"
  }
}
```

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "id_followup": 222,
    "estado": "pendiente"
  }
}
```

---

## 8.2 GET `/followups`

### Objetivo
Listar followups.

### Query params sugeridos
- `id_lead`
- `estado`
- `tipo`
- `limit`
- `offset`

---

# 9. Endpoints de analítica

## 9.1 GET `/analytics/chats`

### Objetivo
Consultar métricas agregadas de conversaciones.

### Query params sugeridos
- `empresa_slug`
- `fecha_desde`
- `fecha_hasta`
- `canal`
- `id_rubro`

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "total_chats": 250,
    "total_messages": 890,
    "avg_response_time_ms": 812,
    "avg_tokens_total": 940,
    "top_routes": [
      {
        "route": "buscar_catalogo",
        "count": 180
      }
    ]
  }
}
```

---

## 9.2 GET `/analytics/conversiones`

### Objetivo
Consultar eventos de conversión.

### Query params sugeridos
- `empresa_slug`
- `fecha_desde`
- `fecha_hasta`
- `event_type`

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "total_conversion_events": 34,
    "by_event_type": [
      {
        "event_type": "advisor_requested",
        "count": 10
      },
      {
        "event_type": "visit_requested",
        "count": 8
      }
    ]
  }
}
```

---

## 9.3 GET `/analytics/items`

### Objetivo
Consultar items más mostrados o con mayor interacción.

### Response ejemplo

```json
{
  "success": true,
  "data": {
    "top_items": [
      {
        "id_item": "uuid_item_1",
        "titulo": "Departamento 2 ambientes en Palermo",
        "times_shown": 21,
        "detail_views": 8
      }
    ]
  }
}
```

---

# 10. Endpoints de KB

## 10.1 GET `/kb/documents`

### Objetivo
Listar documentos de knowledge base de una empresa.

### Query params sugeridos
- `empresa_slug`
- `id_rubro`
- `activo`

---

## 10.2 GET `/kb/documents/{id_documento}`

### Objetivo
Obtener un documento específico.

---

## 10.3 POST `/kb/documents`

### Objetivo
Crear o cargar un documento KB.

### Request ejemplo

```json
{
  "empresa_slug": "inmobiliaria-lopez",
  "id_rubro": 1,
  "titulo": "Preguntas frecuentes",
  "contenido_texto": "La comisión se abona...",
  "metadata": {
    "source": "manual"
  }
}
```

---

# 11. Endpoints de salud y operación

## 11.1 GET `/health`

### Objetivo
Verificar salud general de la API.

### Response ejemplo

```json
{
  "status": "ok"
}
```

---

## 11.2 GET `/health/dependencies`

### Objetivo
Verificar dependencias críticas.

### Response ejemplo

```json
{
  "status": "ok",
  "dependencies": {
    "database": "ok",
    "ai_provider": "ok"
  }
}
```

---

# 12. Endpoints de configuración futura

Estos endpoints pueden agregarse más adelante, no necesariamente en la primera versión:

- `GET /config/empresa`
- `PATCH /config/empresa`
- `GET /prompts`
- `PATCH /prompts/{id}`
- `GET /rubros/schema/{id_rubro}`

No son prioritarios para el MVP técnico del backend, pero conviene dejarlos previstos conceptualmente.

---

# 13. Modelos de payload recomendados

Se recomienda separar modelos Pydantic por tipo:

## Chat
- `ChatMessageRequest`
- `ChatMessageResponse`

## Leads
- `LeadCreateRequest`
- `LeadResponse`
- `LeadUpdateRequest`

## Followups
- `FollowupCreateRequest`
- `FollowupResponse`

## Catalogo
- `CatalogItemResponse`
- `CatalogImportRequest`

## Analytics
- `AnalyticsChatsResponse`
- `AnalyticsConversionsResponse`

Esto ayuda a mantener consistencia y validaciones claras.

---

# 14. Convenciones de validación

## 14.1 Strings
- trim automático
- rechazo de strings vacíos cuando el campo es requerido

## 14.2 Emails
- validación de formato estándar

## 14.3 Teléfonos
- normalización sugerida a formato internacional si el canal lo permite

## 14.4 UUIDs
- validación estricta en endpoints que usen `id_item`, `id_documento`, etc.

## 14.5 Paginación
- `limit` con máximos definidos por configuración
- `offset >= 0`

---

# 15. Convenciones de versionado

Se recomienda prever versionado desde el inicio, aunque la primera implementación sea simple.

Opciones sugeridas:

- `/v1/chat/message`
- `/v1/catalogo/items`

o bien versionado por router interno y prefijo global en FastAPI.

Para una primera etapa, puede implementarse sin prefijo visible y dejar preparada la migración.

---

# 16. Errores estándar sugeridos

Códigos funcionales recomendados:

- `validation_error`
- `empresa_no_encontrada`
- `empresa_inactiva`
- `rubro_no_habilitado`
- `item_no_encontrado`
- `lead_no_encontrado`
- `conversation_no_encontrada`
- `filtros_invalidos`
- `forbidden`
- `unauthorized`
- `internal_error`

---

# 17. Priorización sugerida para implementación

## Fase 1 – Núcleo conversacional
- `POST /chat/message`
- `POST /webhook/widget`
- `POST /webhook/whatsapp`
- `GET /health`

## Fase 2 – Operación comercial
- `POST /leads`
- `GET /leads`
- `GET /conversaciones/{id}`
- `GET /conversaciones/{id}/mensajes`
- `POST /followups`

## Fase 3 – Catálogo y KB
- `GET /catalogo/items`
- `GET /catalogo/items/{id_item}`
- `GET /kb/documents`
- `POST /kb/documents`

## Fase 4 – Analítica
- `GET /analytics/chats`
- `GET /analytics/conversiones`
- `GET /analytics/items`

---

# 18. Beneficios de esta especificación

- hace implementable la arquitectura
- alinea routers HTTP con módulos internos
- reduce ambigüedad para Claude Code
- ayuda a diseñar modelos Pydantic y servicios
- facilita pruebas e integración con frontend y WhatsApp

---

# 19. Objetivo final

Si los contratos internos definen cómo se comunican los componentes del backend,
esta especificación define cómo el mundo externo conversa con la API.

Es el paso que termina de cerrar el puente entre diseño conceptual y desarrollo real.

---

Fin del documento.
