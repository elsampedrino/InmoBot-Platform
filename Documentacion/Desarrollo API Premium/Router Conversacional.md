# InmoBot Premium – Router Conversacional
Versión: 0.1

Este documento define el **Router Conversacional** de InmoBot Premium.
Su responsabilidad es decidir, en cada turno de la conversación, **qué camino de ejecución debe seguir el sistema**.

El Router Conversacional actúa como el **director de orquesta** entre:

- el canal de entrada
- el contexto de la conversación
- el parser determinístico
- el search engine
- la generación de respuesta
- la creación de leads
- los followups
- la analítica Premium

---

# 1. Objetivo del Router Conversacional

El objetivo del router es clasificar la intención operativa del turno actual y derivarlo al flujo correcto.

No genera la respuesta final.
No realiza la búsqueda SQL.
No reemplaza al parser.

Su función es:

- identificar el tipo de interacción
- decidir qué módulos invocar
- coordinar el flujo completo
- registrar eventos relevantes de negocio

---

# 2. Posición del router dentro del pipeline

Pipeline general:

Usuario
→ Widget / WhatsApp
→ Webhook API
→ Chat Endpoint
→ Router Conversacional
→ Flujo correspondiente
→ Respuesta final

El router se ejecuta al inicio de cada mensaje entrante.

---

# 3. Entradas del Router

El router debe tomar como entrada:

- id_empresa
- id_rubro activo
- canal
- session_id
- mensaje actual del usuario
- contexto resumido de la conversación
- último estado conversacional conocido
- metadata del canal

Ejemplo de entrada:

```json
{
  "id_empresa": 12,
  "id_rubro": 1,
  "canal": "whatsapp",
  "session_id": "wa_abc_123",
  "mensaje": "¿Tenés algo más barato?",
  "contexto": {
    "intent_previa": "buscar_item",
    "zona": "Palermo",
    "tipo": "departamento",
    "precio_max": 150000
  }
}
```

---

# 4. Salidas del Router

El router debe devolver una decisión estructurada.

Ejemplo:

```json
{
  "route": "search_catalog",
  "intent": "refinar_busqueda",
  "requires_parser": true,
  "requires_search": true,
  "requires_ai_response": true,
  "requires_lead_update": false,
  "requires_followup": false
}
```

Esta salida permite que el motor conversacional ejecute el flujo adecuado.

---

# 5. Tipos de ruta principales

El sistema debe contemplar, como mínimo, estas rutas operativas:

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
- smalltalk_controlado
- fallback

Estas rutas son más útiles a nivel de sistema que una clasificación puramente semántica.

---

# 6. Diferencia entre intención y ruta

Es importante separar dos conceptos:

## intención
Lo que el usuario parece querer.

## ruta
El flujo operativo que debe ejecutar el sistema.

Ejemplo:

Usuario:
"Quiero ver ese departamento"

Intención:
- interés comercial
- consultar detalle

Ruta:
- ver_detalle_item
- potencial capturar_lead

El router debe mapear intención → ruta.

---

# 7. Reglas de decisión del Router

El router debe basarse primero en reglas determinísticas.

Fuentes para decidir:

- texto del mensaje actual
- contexto previo
- existencia de items mostrados en turnos recientes
- existencia de lead previo
- etapa de la conversación
- canal de entrada

Ejemplos de reglas:

1. Si el mensaje contiene términos de saludo y no hay contexto previo relevante:
   → saludo

2. Si el mensaje contiene atributos, zonas, precios o tipo de producto:
   → buscar_catalogo o refinar_busqueda

3. Si el mensaje hace referencia a "ese", "este", "el primero", "la opción 2":
   → ver_detalle_item o comparar_items

4. Si el mensaje expresa intención de contacto:
   → contactar_asesor o capturar_lead

5. Si el mensaje pide visitar, coordinar o reservar:
   → agendar_visita

6. Si el mensaje pregunta por políticas, horarios o datos institucionales:
   → informacion_empresa o pregunta_kb

7. Si el mensaje no encaja claramente:
   → fallback

---

# 8. Dependencia del contexto conversacional

El router depende fuertemente del contexto.

Ejemplo:

Turno 1:
"Busco casas en Canning"

Turno 2:
"¿Y algo con pileta?"

El segundo mensaje aislado no se entiende del todo.
El router debe usar el contexto para concluir que la ruta es:

- refinar_busqueda

No una nueva búsqueda desde cero.

---

# 9. Estado conversacional

Además del resumen libre en `contextos_conversacion`, conviene manejar un estado estructurado liviano.

Ejemplo de estado:

```json
{
  "route_actual": "buscar_catalogo",
  "ultimo_item_referenciado": "uuid_x",
  "items_recientes": ["uuid_x", "uuid_y", "uuid_z"],
  "lead_capturado": false,
  "esperando_dato_contacto": false,
  "esperando_confirmacion_visita": false
}
```

Este estado ayuda al router a tomar decisiones consistentes turno a turno.

---

# 10. Subflujos principales

## 10.1 Saludo

Se activa cuando el usuario inicia la conversación sin intención operativa clara.

Acciones:
- responder saludo
- ofrecer ayuda
- registrar inicio de interacción

## 10.2 Búsqueda de catálogo

Se activa ante consultas de exploración o búsqueda inicial.

Acciones:
- invocar parser
- construir filtros
- ejecutar search engine
- generar respuesta con resultados

## 10.3 Refinamiento de búsqueda

Se activa cuando el usuario ajusta una búsqueda previa.

Ejemplos:
- "más barato"
- "con balcón"
- "solo 3 ambientes"
- "en otra zona"

Acciones:
- reutilizar contexto
- modificar filtros
- relanzar search engine

## 10.4 Detalle de item

Se activa cuando el usuario pide ampliar información de una opción específica.

Ejemplos:
- "pasame más fotos"
- "decime más del primero"
- "cuántos metros tiene"

Acciones:
- resolver referencia al item
- buscar detalle
- responder detalle
- detectar intención comercial

## 10.5 Pregunta sobre knowledge base

Se activa cuando la pregunta apunta a contenido institucional o documental.

Ejemplos:
- "qué comisión cobran"
- "cómo trabajan"
- "qué documentación necesito"

Acciones:
- consultar KB
- responder con tono comercial claro

## 10.6 Captura de lead

Se activa cuando el usuario demuestra interés suficiente o cuando el flujo necesita datos de contacto.

Ejemplos:
- "quiero que me llamen"
- "te paso mi celular"
- "me interesa"

Acciones:
- crear o actualizar lead
- registrar evento de conversión
- continuar conversación

## 10.7 Contactar asesor

Se activa cuando el usuario quiere intervención humana.

Acciones:
- registrar intención
- crear evento de derivación
- pedir o confirmar datos si faltan

## 10.8 Agendar visita

Se activa cuando el usuario desea coordinar una visita o reunión.

Acciones:
- identificar item de interés
- capturar disponibilidad si hace falta
- registrar evento
- opcionalmente generar followup

## 10.9 Fallback

Se activa cuando el sistema no logra clasificar correctamente.

Acciones:
- usar Haiku como apoyo
- pedir aclaración mínima solo si sigue siendo necesario
- evitar romper la experiencia

---

# 11. Prioridad de decisión

Cuando un mensaje coincide con varias señales, el router debe usar prioridades.

Orden sugerido:

1. agendar_visita
2. contactar_asesor
3. capturar_lead
4. ver_detalle_item
5. refinar_busqueda
6. buscar_catalogo
7. pregunta_kb
8. informacion_empresa
9. saludo
10. fallback

Ejemplo:
"Quiero coordinar una visita por el segundo departamento"

Aunque también refiere a un item, la ruta principal debe ser:
- agendar_visita

---

# 12. Uso de IA dentro del router

La IA no debe ser el mecanismo principal del router.

Debe usarse solo como fallback cuando:

- la regla determinística no alcanza
- el mensaje es muy ambiguo
- el contexto es insuficiente
- hay que clasificar entre pocas rutas posibles

Modelo sugerido:
- Claude Haiku

Salida esperada:
- intención probable
- confianza
- ruta sugerida
- entidades detectadas

Si la confianza es baja, el sistema debe responder de forma segura y simple.

---

# 13. Relación con el parser

El router no reemplaza al parser.

Separación de responsabilidades:

## Router
decide el flujo

## Parser
extrae filtros o entidades necesarias para ejecutar ese flujo

Ejemplo:

Mensaje:
"Busco un PH en Caballito"

Router:
- buscar_catalogo

Parser:
- tipo = PH
- zona = Caballito

---

# 14. Relación con el Search Engine

El router decide cuándo se invoca el search engine.

No todas las rutas lo necesitan.

Rutas que sí suelen invocarlo:

- buscar_catalogo
- refinar_busqueda
- ver_detalle_item
- comparar_items

Rutas que no necesariamente:

- saludo
- capturar_lead
- contactar_asesor
- pregunta_kb

---

# 15. Relación con leads y conversiones

El router es clave para detectar oportunidades comerciales.

Debe poder disparar eventos como:

- lead_created
- lead_updated
- asesor_requested
- visita_requested
- item_detail_viewed
- item_shared
- contacto_confirmado

Estos eventos deben registrarse en:

- premium_conversion_logs
- premium_conversion_log_items

Así se puede medir el embudo conversacional completo.

---

# 16. Integración con analítica Premium

Cada decisión del router debería dejar trazabilidad.

Ejemplos de datos a registrar:

- route_elegida
- intent_detectada
- hubo_fallback_ia
- confidence_score
- item_referenciado
- lead_event_disparado

Esto permite auditar por qué el sistema tomó una decisión.

---

# 17. Diseño recomendado de salida interna

Se recomienda una estructura estándar de decisión interna.

```json
{
  "route": "ver_detalle_item",
  "intent": "consultar_detalle_item",
  "confidence": 0.93,
  "used_ai_fallback": false,
  "entities": {
    "item_reference": "el primero"
  },
  "actions": {
    "run_parser": false,
    "run_search": true,
    "run_kb_search": false,
    "run_ai_response": true,
    "create_or_update_lead": false,
    "register_conversion_event": true
  }
}
```

Esto desacopla al router del resto de los módulos.

---

# 18. Principios de diseño del Router

1. Primero reglas, después IA
2. Siempre considerar contexto
3. Separar intención de ruta
4. Favorecer trazabilidad
5. Favorecer consistencia entre turnos
6. Detectar señales comerciales temprano
7. Minimizar ambigüedad operativa

---

# 19. Beneficios de esta arquitectura

- conversaciones más coherentes
- menor dependencia de IA
- mejor conversión comercial
- mejor trazabilidad analítica
- facilidad para extender a otros rubros
- facilidad para incorporar nuevos canales

---

# 20. Objetivo final

El Router Conversacional no solo clasifica mensajes.
Su verdadero objetivo es transformar cada turno en una decisión operativa clara, medible y escalable.

Es una de las piezas más importantes de InmoBot Premium porque conecta:

- experiencia conversacional
- lógica de negocio
- catálogo
- captación comercial
- analítica

---

Fin del documento.
