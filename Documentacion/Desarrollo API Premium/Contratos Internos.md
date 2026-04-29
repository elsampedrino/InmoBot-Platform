# InmoBot Premium – Contratos Internos entre Componentes
Versión: 0.1

Este documento define los **contratos internos** entre los principales componentes del backend de InmoBot Premium.
Su objetivo es establecer interfaces claras entre módulos para que la implementación pueda avanzar de forma consistente, desacoplada y testeable.

Este documento actúa como puente entre:

- la arquitectura conceptual
- el mapa de módulos
- la futura codificación en FastAPI

---

# 1. Objetivo de los contratos internos

Los contratos internos responden a estas preguntas:

1. Qué datos recibe cada componente
2. Qué datos devuelve
3. Qué formato deben respetar las estructuras internas
4. Qué campos son obligatorios y cuáles opcionales
5. Qué errores o estados especiales puede producir cada módulo

La finalidad es que los módulos puedan desarrollarse por separado sin ambigüedades.

---

# 2. Principios de diseño

Los contratos internos deben cumplir estos principios:

- ser explícitos
- ser estables
- ser serializables
- ser fáciles de loguear
- separar input, output y metadata
- distinguir claramente datos de negocio de datos técnicos

Regla general:
**los módulos no deben pasarse texto libre ambiguo cuando pueden pasarse estructuras bien definidas.**

---

# 3. Contrato raíz del turno conversacional

Todo turno entrante debería transformarse primero en una estructura interna común.

## TurnInput

```json
{
  "request_id": "req_123",
  "timestamp": "2026-03-13T18:10:00Z",
  "empresa_slug": "inmobiliaria-lopez",
  "canal": "web",
  "session_id": "sess_abc",
  "message_id": "msg_ext_001",
  "user_message": "Busco un depto de 2 ambientes en Palermo",
  "user_identity": {
    "nombre": null,
    "telefono": null,
    "email": null
  },
  "channel_metadata": {
    "user_agent": "Mozilla/5.0",
    "ip": null
  }
}
```

### Campos obligatorios
- request_id
- timestamp
- empresa_slug
- canal
- session_id
- user_message

### Campos opcionales
- message_id
- user_identity
- channel_metadata

Este contrato es la entrada del Chat Application Layer.

---

# 4. Contrato de resolución de tenant y rubro

El módulo Tenant & Rubro Resolver recibe un `TurnInput` y devuelve una estructura enriquecida.

## TenantResolutionResult

```json
{
  "id_empresa": 12,
  "id_rubro": 1,
  "empresa_nombre": "Inmobiliaria López",
  "plan": {
    "id_plan": 2,
    "nombre": "Premium",
    "followup_habilitado": true,
    "ia_habilitada": true
  },
  "empresa_config": {
    "timezone": "America/Argentina/Buenos_Aires",
    "permite_followup": true,
    "slug": "inmobiliaria-lopez"
  },
  "rubro_config": {
    "nombre": "inmobiliaria",
    "search_mode": "structured_sql"
  }
}
```

### Errores posibles
- empresa_no_encontrada
- empresa_inactiva
- rubro_no_habilitado
- configuracion_invalida

---

# 5. Contrato de contexto conversacional

El Context Manager recibe la identidad del turno y devuelve el contexto persistido.

## ConversationContext

```json
{
  "id_conversacion": 456,
  "id_lead": 789,
  "context_summary": "El usuario está buscando departamentos en Palermo, 2 ambientes, presupuesto medio.",
  "state": {
    "route_actual": "buscar_catalogo",
    "intent_previa": "buscar_item",
    "filters_activos": {
      "tipo": "departamento",
      "barrio": "Palermo",
      "ambientes": 2
    },
    "items_recientes": [
      "uuid_item_1",
      "uuid_item_2",
      "uuid_item_3"
    ],
    "ultimo_item_referenciado": "uuid_item_1",
    "esperando_contacto": false,
    "esperando_visita": false
  },
  "message_history_window": [
    {
      "emisor": "user",
      "mensaje": "Busco un depto de 2 ambientes en Palermo"
    },
    {
      "emisor": "assistant",
      "mensaje": "Te muestro algunas opciones..."
    }
  ]
}
```

### Notas
- `context_summary` es resumen libre
- `state` es estado estructurado
- `message_history_window` debe ser acotado, no el historial completo

---

# 6. Contrato de decisión del router conversacional

El Router recibe:
- TurnInput
- TenantResolutionResult
- ConversationContext

Y devuelve una decisión operativa.

## RouteDecision

```json
{
  "route": "buscar_catalogo",
  "intent": "buscar_item",
  "confidence": 0.94,
  "used_ai_fallback": false,
  "entities_hint": {
    "item_reference": null,
    "comparison_reference": null
  },
  "actions": {
    "run_parser": true,
    "run_search": true,
    "run_kb_search": false,
    "run_ai_response": true,
    "create_or_update_lead": false,
    "create_followup": false,
    "register_conversion_event": false
  },
  "business_signals": {
    "commercial_interest": "low",
    "advisor_request": false,
    "visit_intent": false
  }
}
```

### Valores sugeridos para `route`
- saludo
- buscar_catalogo
- refinar_busqueda
- ver_detalle_item
- comparar_items
- pregunta_kb
- informacion_empresa
- capturar_lead
- contactar_asesor
- agendar_visita
- followup
- fallback

### Errores o estados especiales
- baja_confianza
- contexto_insuficiente
- ambiguedad_referencia_item

---

# 7. Contrato del parser de consulta

El Query Parser recibe:
- user_message
- route
- context.state.filters_activos
- rubro_config / rubro_schema

Y devuelve filtros estructurados.

## ParsedQuery

```json
{
  "normalized_query": "busco departamento 2 ambientes en palermo",
  "intent": "buscar_item",
  "operation": "search",
  "filters": {
    "tipo": "departamento",
    "barrio": "Palermo",
    "ambientes": {
      "operator": ">=",
      "value": 2
    }
  },
  "sort": {
    "field": "relevance",
    "direction": "desc"
  },
  "limit": 5,
  "parser_metadata": {
    "used_synonyms": true,
    "used_context_merge": false,
    "confidence": 0.91
  }
}
```

### Reglas
- `filters` debe ser una estructura explícita, no SQL embebido
- los operadores deben venir normalizados
- `limit` puede venir por default desde configuración

### Operadores recomendados
- =
- !=
- >
- >=
- <
- <=
- in
- between
- contains
- ilike

---

# 8. Contrato de búsqueda de catálogo

El Search Engine recibe:
- id_empresa
- id_rubro
- ParsedQuery
- opcionalmente contexto adicional

Y devuelve resultados candidatos.

## SearchResult

```json
{
  "query_applied": {
    "filters": {
      "tipo": "departamento",
      "barrio": "Palermo",
      "ambientes": {
        "operator": ">=",
        "value": 2
      }
    },
    "limit": 5
  },
  "items": [
    {
      "id_item": "uuid_item_1",
      "external_id": "PROP-1001",
      "titulo": "Departamento 2 ambientes en Palermo",
      "descripcion_corta": "Muy luminoso, con balcón",
      "precio": 120000,
      "moneda": "USD",
      "tipo": "departamento",
      "categoria": "venta",
      "atributos_resumidos": {
        "ambientes": 2,
        "barrio": "Palermo",
        "balcon": true
      },
      "media": [],
      "score": 0.97,
      "rank": 1
    }
  ],
  "facets": {
    "barrio": {
      "Palermo": 12,
      "Belgrano": 4
    },
    "ambientes": {
      "2": 7,
      "3": 5
    }
  },
  "search_metadata": {
    "total_found": 12,
    "returned": 5,
    "used_ranking": true,
    "execution_ms": 24
  }
}
```

### Errores o estados especiales
- sin_resultados
- filtros_invalidos
- rubro_schema_incompatible

---

# 9. Contrato de recuperación de KB

El Knowledge Base Service recibe:
- id_empresa
- id_rubro
- user_message
- contexto opcional

Y devuelve chunks o documentos relevantes.

## KBSearchResult

```json
{
  "results": [
    {
      "id_documento": "uuid_doc_1",
      "id_chunk": "uuid_chunk_5",
      "titulo": "Preguntas frecuentes",
      "chunk_texto": "La comisión inmobiliaria se abona al momento de la firma...",
      "score": 0.89,
      "metadata": {
        "version": 2
      }
    }
  ],
  "kb_metadata": {
    "results_found": 3,
    "returned": 3
  }
}
```

### Regla
El output de KB no es respuesta final, sino contexto para responder.

---

# 10. Contrato de detalle de item

Cuando una ruta necesita ampliar un item puntual, el flujo debe devolver una estructura específica.

## ItemDetailResult

```json
{
  "item": {
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
      "balcon": true,
      "barrio": "Palermo"
    },
    "media": [
      {
        "type": "image",
        "url": "https://..."
      }
    ]
  },
  "detail_metadata": {
    "source": "catalog_service"
  }
}
```

---

# 11. Contrato del servicio de leads

El Leads Service debería trabajar con comandos explícitos.

## LeadUpsertCommand

```json
{
  "id_empresa": 12,
  "id_conversacion": 456,
  "lead_data": {
    "nombre": "Juan Pérez",
    "telefono": "+54911...",
    "email": "juan@email.com",
    "canal": "whatsapp"
  },
  "metadata": {
    "source": "chat_flow",
    "reason": "advisor_request"
  }
}
```

## LeadUpsertResult

```json
{
  "id_lead": 789,
  "action": "created",
  "lead_state": {
    "nombre": "Juan Pérez",
    "telefono": "+54911...",
    "email": "juan@email.com",
    "estado": "nuevo"
  }
}
```

### Valores sugeridos para `action`
- created
- updated
- unchanged

---

# 12. Contrato del servicio de followups

## FollowupCreateCommand

```json
{
  "id_empresa": 12,
  "id_lead": 789,
  "id_conversacion": 456,
  "tipo": "visita_pendiente",
  "fecha_programada": "2026-03-15T15:00:00Z",
  "payload": {
    "item_id": "uuid_item_1",
    "motivo": "usuario interesado en coordinar visita"
  }
}
```

## FollowupCreateResult

```json
{
  "id_followup": 222,
  "estado": "pendiente",
  "fecha_programada": "2026-03-15T15:00:00Z"
}
```

---

# 13. Contrato del prompt service

El Prompt Service recibe entradas estructuradas y devuelve un prompt armado.

## PromptBuildInput

```json
{
  "id_empresa": 12,
  "id_rubro": 1,
  "route": "buscar_catalogo",
  "user_message": "Busco un depto de 2 ambientes en Palermo",
  "context_summary": "El usuario busca departamentos en Palermo.",
  "search_result": {
    "items": [
      {
        "titulo": "Departamento 2 ambientes en Palermo",
        "precio": 120000,
        "moneda": "USD"
      }
    ]
  },
  "kb_result": null,
  "response_guidelines": {
    "max_items_to_mention": 3,
    "tone": "comercial_claro",
    "cta_mode": "soft"
  }
}
```

## PromptBuildResult

```json
{
  "system_prompt": "Sos el asistente de una inmobiliaria...",
  "final_prompt": "Contexto: ...\nResultados: ...\nInstrucciones: ...",
  "prompt_metadata": {
    "used_company_override": true,
    "used_kb": false,
    "used_search_items": true
  }
}
```

---

# 14. Contrato del servicio de IA

El AI Response Service debería soportar dos modos internos.

## 14.1 AIClassificationInput

```json
{
  "task": "route_fallback",
  "user_message": "Quiero algo lindo para mudarme con mi familia",
  "context_summary": "No hay filtros activos previos.",
  "candidate_routes": [
    "buscar_catalogo",
    "pregunta_kb",
    "capturar_lead"
  ]
}
```

## AIClassificationResult

```json
{
  "predicted_route": "buscar_catalogo",
  "predicted_intent": "buscar_item",
  "confidence": 0.72,
  "entities": {
    "tipo": "casa"
  }
}
```

## 14.2 AIGenerationInput

```json
{
  "model": "sonnet",
  "route": "buscar_catalogo",
  "prompt": "Contexto: ...",
  "output_format": "plain_text"
}
```

## AIGenerationResult

```json
{
  "text": "Encontré algunas opciones en Palermo que podrían interesarte...",
  "usage": {
    "tokens_input": 820,
    "tokens_output": 145,
    "tokens_total": 965
  },
  "model": "sonnet",
  "latency_ms": 812
}
```

---

# 15. Contrato de ensamblado de respuesta

El Response Assembly Layer recibe el resultado del flujo y lo convierte al formato de salida.

## ResponseAssemblyInput

```json
{
  "route": "buscar_catalogo",
  "channel": "web",
  "generated_text": "Encontré algunas opciones...",
  "items": [
    {
      "id_item": "uuid_item_1",
      "titulo": "Departamento 2 ambientes en Palermo",
      "precio": 120000,
      "moneda": "USD"
    }
  ],
  "suggested_actions": [
    "ver_detalle",
    "contactar_asesor"
  ]
}
```

## ChannelResponse

```json
{
  "message_text": "Encontré algunas opciones...",
  "items": [
    {
      "id_item": "uuid_item_1",
      "titulo": "Departamento 2 ambientes en Palermo",
      "precio": 120000,
      "moneda": "USD"
    }
  ],
  "quick_replies": [
    "Ver más detalles",
    "Hablar con un asesor"
  ],
  "channel_metadata": {}
}
```

### Regla
La respuesta interna debe ser independiente del canal y luego adaptarse al canal si hace falta.

---

# 16. Contrato de actualización de contexto

Al finalizar el turno, el sistema debe persistir contexto actualizado.

## ContextUpdateCommand

```json
{
  "id_conversacion": 456,
  "new_summary": "El usuario sigue buscando departamentos en Palermo y mostró interés en una opción puntual.",
  "new_state": {
    "route_actual": "ver_detalle_item",
    "intent_previa": "consultar_detalle_item",
    "filters_activos": {
      "tipo": "departamento",
      "barrio": "Palermo",
      "ambientes": 2
    },
    "items_recientes": [
      "uuid_item_1",
      "uuid_item_2",
      "uuid_item_3"
    ],
    "ultimo_item_referenciado": "uuid_item_1",
    "esperando_contacto": false,
    "esperando_visita": false
  }
}
```

---

# 17. Contrato de analítica de chat

El Analytics Service debería recibir un payload estructurado por turno.

## ChatAnalyticsEvent

```json
{
  "created_at": "2026-03-13T18:10:01Z",
  "id_empresa": 12,
  "id_rubro": 1,
  "id_conversacion": 456,
  "id_lead": 789,
  "canal": "web",
  "session_id": "sess_abc",
  "consulta": "Busco un depto de 2 ambientes en Palermo",
  "route": "buscar_catalogo",
  "intent": "buscar_item",
  "success": true,
  "error_type": null,
  "response_time_ms": 930,
  "model": "sonnet",
  "tokens_input": 820,
  "tokens_output": 145,
  "tokens_total": 965,
  "items_mostrados": 3,
  "repo": "premium_api"
}
```

## ChatAnalyticsItemsEvent

```json
{
  "id_chat_log": 1001,
  "items": [
    {
      "id_item": "uuid_item_1",
      "rank": 1,
      "score": 0.97
    },
    {
      "id_item": "uuid_item_2",
      "rank": 2,
      "score": 0.91
    }
  ]
}
```

---

# 18. Contrato de analítica de conversión

## ConversionAnalyticsEvent

```json
{
  "created_at": "2026-03-13T18:11:10Z",
  "id_empresa": 12,
  "id_rubro": 1,
  "id_conversacion": 456,
  "id_lead": 789,
  "canal": "web",
  "session_id": "sess_abc",
  "event_type": "advisor_requested",
  "payload": {
    "source_route": "ver_detalle_item",
    "item_id": "uuid_item_1"
  },
  "repo": "premium_api"
}
```

### Valores sugeridos para `event_type`
- lead_created
- lead_updated
- item_detail_viewed
- advisor_requested
- visit_requested
- contact_shared
- followup_created

---

# 19. Contrato estándar de errores internos

Conviene un formato común para errores entre módulos.

## InternalError

```json
{
  "error_code": "filtros_invalidos",
  "error_message": "El filtro ambientes no cumple el formato esperado.",
  "error_source": "query_parser",
  "retryable": false,
  "details": {
    "field": "ambientes"
  }
}
```

### Campos recomendados
- error_code
- error_message
- error_source
- retryable
- details

Esto permite loguear, diagnosticar y responder mejor.

---

# 20. Convenciones generales para todos los contratos

## 20.1 IDs
- usar nombres explícitos: `id_empresa`, `id_rubro`, `id_item`
- evitar nombres ambiguos como `id`

## 20.2 Fechas
- usar ISO 8601
- idealmente en UTC dentro del backend

## 20.3 Nullables
- declarar explícitamente qué puede ser null
- no usar ausencia de campo y null mezclados sin criterio

## 20.4 Metadata
- la metadata técnica debe estar separada de los datos de negocio

## 20.5 Campos calculados
- `score`, `rank`, `confidence` deben identificarse como derivados, no como datos persistidos base

---

# 21. Separación sugerida entre modelos internos

Conviene pensar 3 tipos de modelos:

## Input Models
Lo que entra a un componente

## Result Models
Lo que devuelve ese componente

## Command Models
Lo que ordena una acción de negocio o persistencia

Ejemplos:
- `TurnInput`
- `RouteDecision`
- `LeadUpsertCommand`
- `SearchResult`

Esta separación ayuda mucho en FastAPI + Pydantic.

---

# 22. Beneficios de definir estos contratos

- reduce ambigüedad de implementación
- permite programar módulo por módulo
- facilita testing unitario
- evita acoplamiento innecesario
- mejora observabilidad
- hace que Claude Code genere piezas compatibles entre sí

---

# 23. Objetivo final

Estos contratos internos no son un detalle menor.
Son la base que permite que la arquitectura se convierta en software real sin perder coherencia.

Si el mapa de módulos define **quién hace qué**, los contratos internos definen **cómo se hablan entre sí**.

---

Fin del documento.
