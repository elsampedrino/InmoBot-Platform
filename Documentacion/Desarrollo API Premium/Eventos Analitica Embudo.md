# InmoBot Premium -- Eventos de Analítica y Embudo Conversacional

Versión: 0.1

Este documento define el **modelo de analítica y eventos del sistema
conversacional** de InmoBot Premium. Su objetivo es establecer qué
eventos se registran, cómo se relacionan con el flujo conversacional y
cómo permiten medir el **embudo de conversión** desde la primera
consulta hasta la generación de oportunidades comerciales.

Este documento conecta directamente con:

-   Router Conversacional
-   Estado Conversacional
-   Leads
-   Followups
-   Tablas `premium_chat_logs`
-   Tablas `premium_conversion_logs`

------------------------------------------------------------------------

# 1. Objetivo del sistema de analítica

El sistema de analítica debe permitir responder preguntas como:

-   ¿Cuántas conversaciones recibe cada empresa?
-   ¿Cuántas búsquedas realiza un usuario antes de mostrar interés?
-   ¿Qué propiedades generan más interés?
-   ¿En qué momento del flujo se generan leads?
-   ¿Cuántas conversaciones terminan en contacto comercial?
-   ¿Cuántas terminan en visitas programadas?
-   ¿Cuál es la tasa de conversión del asistente?

Para lograrlo, cada interacción relevante debe generar **eventos
estructurados**.

------------------------------------------------------------------------

# 2. Principio del modelo de eventos

Todo evento debe cumplir tres reglas:

1.  Debe ser **explicable**
2.  Debe poder asociarse a **empresa, conversación y sesión**
3.  Debe ser **reproducible en análisis posterior**

Cada evento tiene:

-   timestamp
-   empresa
-   conversación
-   lead (si existe)
-   tipo de evento
-   payload contextual

------------------------------------------------------------------------

# 3. Tipos de analítica

El sistema se divide en dos grandes categorías.

## 3.1 Analítica de conversación

Registra el comportamiento del chat:

-   consultas
-   rutas elegidas
-   tiempos de respuesta
-   uso de IA
-   items mostrados

Tablas:

-   `premium_chat_logs`
-   `premium_chat_log_items`

------------------------------------------------------------------------

## 3.2 Analítica de conversión

Registra eventos de negocio:

-   interés en propiedades
-   solicitudes de asesor
-   captura de datos
-   visitas programadas

Tablas:

-   `premium_conversion_logs`
-   `premium_conversion_log_items`

------------------------------------------------------------------------

# 4. Eventos de chat

Los eventos de chat se generan **en cada turno del usuario**.

Ejemplo de evento:

``` json
{
  "event_type": "chat_turn",
  "consulta": "Busco un depto en Palermo",
  "route": "buscar_catalogo",
  "intent": "buscar_item",
  "items_mostrados": 3,
  "response_time_ms": 900
}
```

Campos importantes:

-   `route`
-   `intent`
-   `model`
-   `tokens_total`
-   `response_time_ms`
-   `items_mostrados`

Esto permite medir:

-   performance
-   uso de IA
-   rutas más frecuentes

------------------------------------------------------------------------

# 5. Eventos de interacción con items

Cada vez que el usuario interactúa con un item se registra un evento.

Eventos sugeridos:

  Evento                 Descripción
  ---------------------- --------------------------------
  `items_shown`          se mostraron items al usuario
  `item_detail_viewed`   el usuario pidió detalle
  `item_compared`        el usuario comparó items
  `item_shared`          el item fue enviado al usuario

Ejemplo:

``` json
{
  "event_type": "item_detail_viewed",
  "item_id": "uuid_item_1",
  "route": "ver_detalle_item"
}
```

Esto permite saber:

-   qué items generan más interés
-   qué items se convierten mejor

------------------------------------------------------------------------

# 6. Eventos de interés comercial

Cuando el usuario muestra intención comercial se registran eventos
específicos.

Eventos sugeridos:

  Evento                           Descripción
  -------------------------------- ----------------------------
  `commercial_interest_detected`   interés detectado
  `advisor_requested`              solicitó asesor
  `visit_requested`                solicitó visita
  `contact_shared`                 compartió teléfono o email

Ejemplo:

``` json
{
  "event_type": "advisor_requested",
  "item_id": "uuid_item_2",
  "source_route": "ver_detalle_item"
}
```

Estos eventos marcan la transición hacia conversión.

------------------------------------------------------------------------

# 7. Eventos de lead

Cuando se crea o actualiza un lead se registran eventos.

Eventos sugeridos:

  Evento                     Descripción
  -------------------------- ---------------------
  `lead_created`             nuevo lead
  `lead_updated`             lead actualizado
  `lead_contact_confirmed`   contacto confirmado

Ejemplo:

``` json
{
  "event_type": "lead_created",
  "lead_id": 789,
  "source": "chat_flow"
}
```

Esto permite medir cuántos leads provienen del asistente.

------------------------------------------------------------------------

# 8. Eventos de followup

Los followups representan acciones posteriores a la conversación.

Eventos sugeridos:

  Evento               Descripción
  -------------------- --------------------
  `followup_created`   seguimiento creado
  `visit_scheduled`    visita programada
  `visit_confirmed`    visita confirmada

Ejemplo:

``` json
{
  "event_type": "visit_scheduled",
  "item_id": "uuid_item_1",
  "lead_id": 789
}
```

Esto permite medir conversión real del bot.

------------------------------------------------------------------------

# 9. Embudo conversacional

El embudo mide el recorrido típico del usuario.

Etapas sugeridas:

1.  Conversación iniciada
2.  Exploración de catálogo
3.  Interacción con items
4.  Interés comercial
5.  Captura de lead
6.  Solicitud de asesor o visita

Representación simplificada:

    Conversaciones
       ↓
    Búsquedas
       ↓
    Interacción con items
       ↓
    Interés
       ↓
    Lead
       ↓
    Visita / Asesor

------------------------------------------------------------------------

# 10. Métricas derivadas

A partir de los eventos se pueden calcular métricas clave.

## Métricas de conversación

-   conversaciones por empresa
-   mensajes promedio por conversación
-   tiempo medio de respuesta
-   rutas más usadas

## Métricas de catálogo

-   items más mostrados
-   items con más detalle solicitado
-   tasa de interacción por item

## Métricas de conversión

-   ratio exploración → interés
-   ratio interés → lead
-   ratio lead → visita

------------------------------------------------------------------------

# 11. Ejemplo de flujo completo de eventos

Usuario: "Busco una casa en Canning"

Eventos:

1.  `chat_turn`
2.  `items_shown`

Usuario: "Quiero ver la segunda"

Eventos:

3.  `item_detail_viewed`

Usuario: "Me interesa, quiero visitarla"

Eventos:

4.  `commercial_interest_detected`
5.  `visit_requested`
6.  `lead_created`
7.  `visit_scheduled`

Este flujo queda completamente trazado.

------------------------------------------------------------------------

# 12. Beneficios de este enfoque

-   trazabilidad completa del comportamiento del usuario
-   análisis real de conversión del bot
-   detección de propiedades más efectivas
-   mejora continua del asistente
-   base para dashboards comerciales

------------------------------------------------------------------------

# 13. Objetivo final

La analítica no debe ser un agregado posterior.

Debe formar parte del diseño desde el inicio para transformar al
asistente en una **herramienta de inteligencia comercial** para las
empresas que usan InmoBot.

------------------------------------------------------------------------

Fin del documento.
