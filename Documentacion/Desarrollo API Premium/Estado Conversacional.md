# InmoBot Premium – Estado Conversacional y Ciclo de Vida de la Conversación
Versión: 0.1

Este documento define el **modelo de estado conversacional** de InmoBot Premium y el **ciclo de vida de una conversación**.
Su objetivo es especificar cómo el sistema mantiene contexto entre turnos, cómo evoluciona una conversación en el tiempo y cómo se conecta con catálogo, leads, visitas, followups y analítica.

Este documento complementa especialmente:

- motor conversacional
- router conversacional
- contratos internos
- endpoints y payloads

---

# 1. Objetivo de este documento

Este documento responde a estas preguntas:

1. Qué información de estado debe recordar el sistema entre mensajes
2. Qué diferencia hay entre historial, resumen y estado estructurado
3. Cómo evoluciona una conversación desde que empieza hasta que termina
4. Cómo se relaciona una conversación con leads, items, visitas y followups
5. Cómo persistir contexto sin depender de mandar todo el historial a la IA

El objetivo es que el sistema sea:

- coherente entre turnos
- eficiente en costo
- estable en producción
- explicable y auditable

---

# 2. Principio rector

El sistema no debe depender del historial completo en cada turno.

Debe trabajar con tres capas distintas de memoria conversacional:

1. **historial reciente acotado**
2. **resumen conversacional**
3. **estado estructurado**

Esto permite mantener contexto sin inflar prompts ni volver frágil la arquitectura.

---

# 3. Entidades relacionadas

El estado conversacional se apoya principalmente en estas entidades ya definidas en la base:

- `conversaciones`
- `mensajes`
- `contextos_conversacion`
- `leads`
- `followups`

Y se vincula operativamente con:

- `items`
- `premium_chat_logs`
- `premium_conversion_logs`

---

# 4. Componentes de memoria conversacional

## 4.1 Historial reciente

Es una ventana corta de mensajes recientes.
Sirve para entender referencias inmediatas.

Ejemplo:
- “el primero”
- “ese me gusta más”
- “¿y algo más barato?”

### Características
- corto
- cronológico
- útil para referencias locales
- no debe crecer indefinidamente

### Recomendación
Mantener entre 6 y 12 mensajes recientes como máximo, según canal y complejidad.

---

## 4.2 Resumen conversacional

Es una síntesis textual breve de lo importante acumulado en la conversación.

Ejemplo:

> El usuario busca departamentos en Palermo para compra, prefiere 2 ambientes, mostró sensibilidad al precio y pidió más detalles de una opción puntual.

### Función
- condensar el contexto acumulado
- reducir dependencia del historial largo
- mejorar continuidad entre turnos
- servir de base para prompts y decisiones del router

### Recomendación
Actualizarlo cuando cambie significativamente la intención, los filtros o el interés comercial.

---

## 4.3 Estado estructurado

Es la parte más importante a nivel operativo.

Debe guardar información en formato claro, estable y fácil de consumir por router, parser y servicios.

Ejemplo:

```json
{
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
  "comparacion_activa": false,
  "esperando_contacto": false,
  "esperando_visita": false,
  "lead_capturado": true,
  "advisor_requested": false,
  "visit_requested": false
}
```

---

# 5. Separación entre mensaje, contexto y estado

Es importante no mezclar conceptos.

## Mensajes
Registro literal de lo que dijeron usuario y asistente.

## Resumen
Interpretación compacta de lo relevante.

## Estado estructurado
Variables operativas para toma de decisiones.

El sistema debe poder seguir funcionando aunque la IA no lea todos los mensajes viejos, porque el resumen y el estado ya concentran lo esencial.

---

# 6. Propuesta de estructura del estado conversacional

Se recomienda que el estado estructurado incluya, como mínimo, estos bloques.

## 6.1 Identidad del flujo actual

```json
{
  "route_actual": "buscar_catalogo",
  "intent_previa": "buscar_item"
}
```

Sirve para saber en qué clase de interacción estaba el usuario.

---

## 6.2 Filtros activos

```json
{
  "filters_activos": {
    "tipo": "departamento",
    "categoria": "venta",
    "barrio": "Palermo",
    "ambientes": 2,
    "precio_max": 150000
  }
}
```

Sirve para refinamientos como:
- “más barato”
- “solo con balcón”
- “en otra zona”

---

## 6.3 Referencias a items

```json
{
  "items_recientes": ["uuid_1", "uuid_2", "uuid_3"],
  "ultimo_item_referenciado": "uuid_2"
}
```

Sirve para resolver:
- “el segundo”
- “ese”
- “mandame fotos del primero”

---

## 6.4 Señales comerciales

```json
{
  "lead_capturado": false,
  "advisor_requested": false,
  "visit_requested": false
}
```

Sirve para conectar conversación con conversión.

---

## 6.5 Esperas operativas

```json
{
  "esperando_contacto": false,
  "esperando_visita": false,
  "esperando_confirmacion": false
}
```

Sirve para saber si el sistema hizo una pregunta y está esperando un dato puntual.

Ejemplo:
- “Pasame tu teléfono y te contacta un asesor”
- “¿Qué día te queda bien para la visita?”

---

## 6.6 Metadata contextual opcional

```json
{
  "channel_last_seen": "web",
  "last_user_message_at": "2026-03-13T18:20:00Z",
  "conversation_stage": "exploracion"
}
```

---

# 7. Etapas del ciclo de vida conversacional

Una conversación no es solo una secuencia de mensajes.
Tiene etapas funcionales.

Se propone este modelo de etapas.

## 7.1 Inicio

La conversación se crea cuando llega el primer mensaje válido.

Características:
- puede no existir lead aún
- no hay filtros activos previos
- se inicializa contexto

Ejemplos:
- saludo
- búsqueda inicial
- pregunta general

---

## 7.2 Exploración

El usuario está buscando, navegando o entendiendo opciones.

Características:
- búsqueda de catálogo
- refinamientos
- comparaciones
- preguntas de contexto sobre productos o servicios

Ejemplos:
- “Busco una casa en Canning”
- “Algo más barato”
- “Comparame esas dos”

---

## 7.3 Interés

El usuario ya muestra preferencia concreta o intención comercial más fuerte.

Características:
- consulta detalle
- pide fotos
- quiere saber metros, condiciones, disponibilidad
- refiere items puntuales

Ejemplos:
- “Quiero ver más del primero”
- “¿Sigue disponible?”
- “¿Cuántos metros tiene?”

---

## 7.4 Conversión

La conversación entra en modo comercial explícito.

Características:
- comparte contacto
- pide asesor
- quiere coordinar visita
- acepta seguimiento

Ejemplos:
- “Quiero que me llamen”
- “Te paso mi teléfono”
- “Podemos coordinar visita”

---

## 7.5 Cierre

La conversación se considera cerrada cuando:
- se completa una conversión
- el usuario deja de interactuar por cierto tiempo
- el flujo queda terminado sin acción pendiente

El cierre no implica borrar contexto.
Implica marcar una pausa o final lógico.

---

## 7.6 Reapertura

Una conversación puede reactivarse después.

Ejemplo:
- el usuario vuelve al día siguiente
- el mismo lead retoma la consulta
- se continúa una visita pendiente

El sistema debe decidir si:
- reutiliza la misma conversación
- abre una nueva conversación
- reutiliza el lead y parte del contexto

Esto se definirá por reglas de negocio y ventana temporal.

---

# 8. Propuesta de estados de etapa

Se recomienda un campo estructurado como:

```json
{
  "conversation_stage": "exploracion"
}
```

Valores sugeridos:
- `inicio`
- `exploracion`
- `interes`
- `conversion`
- `cerrada`

Este campo ayuda al router y a analítica.

---

# 9. Eventos que modifican el estado

No todos los mensajes cambian el estado.
Pero ciertos eventos sí deben actualizarlo.

## Eventos típicos
- búsqueda inicial
- refinamiento de filtros
- referencia a item puntual
- solicitud de asesor
- captura de teléfono o email
- solicitud de visita
- creación de followup
- cierre por inactividad

---

# 10. Reglas de transición sugeridas

## De inicio → exploración
Cuando el usuario inicia una búsqueda o consulta operativa.

## De exploración → interés
Cuando refiere un item específico o pide detalle.

## De interés → conversión
Cuando muestra intención comercial clara.

## De conversión → cerrada
Cuando ya se registró una acción comercial final o la conversación quedó concluida.

## De cerrada → exploración / interés / conversión
Cuando se reabre por nueva interacción.

Estas transiciones no deben ser rígidas al 100%, pero sí orientativas y trazables.

---

# 11. Relación entre conversación y lead

No toda conversación genera lead inmediato.

## Recomendación
- crear `conversacion` al primer mensaje válido
- crear `lead` solo cuando haya señal suficiente o dato identificatorio
- vincular `id_lead` a la conversación cuando corresponda

Esto evita inflar leads con conversaciones irrelevantes.

### Señales típicas para creación de lead
- comparte teléfono
- comparte email
- pide asesor
- pide visita
- declara interés explícito

---

# 12. Relación entre conversación e items

Una conversación puede referirse a múltiples items a lo largo del tiempo.

El estado debe poder recordar:

- items mostrados recientemente
- item más relevante del turno
- item actualmente referenciado
- items involucrados en conversión

Esto es importante para:
- detalle
- comparación
- analítica
- followups
- conversión

---

# 13. Relación entre conversación y followups

No todo followup nace automáticamente, pero cuando aparece debe reflejarse en el estado.

Ejemplo:

```json
{
  "visit_requested": true,
  "esperando_visita": false,
  "followup_open": true
}
```

Esto evita que el bot vuelva a pedir algo ya solicitado o que pierda trazabilidad.

---

# 14. Propuesta de persistencia en base

## Tabla `conversaciones`
Debe almacenar:
- identidad de la conversación
- canal
- timestamps de inicio/fin
- vínculo con lead y empresa

## Tabla `mensajes`
Debe almacenar:
- cada turno literal
- emisor
- payload crudo si aplica
- timestamp

## Tabla `contextos_conversacion`
Debe almacenar:
- resumen_contexto
- updated_at

## Recomendación adicional
Conviene evaluar extender `contextos_conversacion` con un campo JSON estructurado, por ejemplo:

- `estado_json`

Si no se quiere cambiar esa tabla ahora, el estado estructurado podría mantenerse en otra tabla o serializado temporalmente, pero conceptualmente es muy valioso tenerlo persistido.

---

# 15. Recomendación de evolución del modelo de base

Aunque hoy `contextos_conversacion` tiene solo `resumen_contexto`, a nivel de arquitectura convendría evolucionar hacia algo como:

```text
CONTEXTOS_CONVERSACION
- id_contexto
- id_conversacion
- resumen_contexto
- estado_json
- updated_at
```

Donde `estado_json` guarde el estado estructurado.

### Beneficios
- decisiones más consistentes
- menos lógica derivada a partir de texto
- mejor soporte multi-turno
- mayor trazabilidad

---

# 16. Estrategia de actualización del contexto

No es necesario recalcular todo en cada turno.
Se recomienda un enfoque incremental.

## En cada turno:
1. leer contexto actual
2. ejecutar flujo
3. detectar cambios relevantes
4. actualizar resumen si cambió algo importante
5. actualizar estado estructurado
6. persistir

### Qué cambios suelen gatillar actualización
- nuevos filtros activos
- nuevo item referenciado
- cambio de etapa conversacional
- captura de lead
- solicitud de visita o asesor

---

# 17. Estrategia de resolución de referencias

Uno de los problemas más comunes en conversación es resolver expresiones como:
- “el primero”
- “ese”
- “la opción 2”
- “el de Palermo”

Para eso el estado debe recordar:
- orden de items mostrados
- identificadores
- atributos mínimos de cada item reciente

## Recomendación
Además de `items_recientes`, podría ser útil una estructura temporal tipo:

```json
{
  "items_recientes_resumen": [
    {
      "id_item": "uuid_1",
      "label": "opcion_1",
      "titulo": "Departamento 2 ambientes en Palermo"
    },
    {
      "id_item": "uuid_2",
      "label": "opcion_2",
      "titulo": "Departamento 3 ambientes en Belgrano"
    }
  ]
}
```

Esto facilita mucho el router y el detalle de item.

---

# 18. Estrategia de limpieza del estado

El estado no debe crecer sin control.

## Recomendaciones
- conservar solo items recientes relevantes
- limpiar flags de espera cuando se resuelven
- reemplazar filtros activos cuando cambian de tema
- detectar cambio de intención fuerte y resetear partes del estado

Ejemplo:
si el usuario pasa de buscar propiedades a preguntar comisiones, no conviene perder todo, pero sí distinguir que cambió el foco actual.

---

# 19. Reglas de cambio de tema

Una conversación puede cambiar de tema.

Ejemplo:
- primero busca departamento
- luego pregunta por comisión
- después vuelve a pedir visita

El sistema no debe borrar todo ante cada cambio, pero sí debe poder manejar:

- foco actual
- subcontexto de búsqueda
- contexto comercial acumulado

## Recomendación
Mantener:
- un estado global liviano
- un bloque específico de búsqueda activa
- un bloque de señales comerciales

---

# 20. Relación con la IA

La IA no debe ser la fuente primaria del estado.

La IA puede ayudar a:
- resumir contexto
- interpretar ambigüedades
- inferir cambios de etapa si hace falta

Pero el estado operativo debe quedar persistido y controlado por la lógica de la API.

---

# 21. Relación con analítica

El ciclo de vida conversacional alimenta directamente la analítica.

Métricas derivadas posibles:
- duración promedio por etapa
- ratio exploración → interés
- ratio interés → conversión
- cantidad de reaperturas
- cantidad de conversaciones cerradas sin lead
- tiempo hasta primera señal comercial

Esto vuelve muy valioso persistir `conversation_stage` y eventos asociados.

---

# 22. Modelo sugerido de estado completo

Ejemplo consolidado:

```json
{
  "conversation_stage": "interes",
  "route_actual": "ver_detalle_item",
  "intent_previa": "consultar_detalle_item",
  "filters_activos": {
    "tipo": "departamento",
    "categoria": "venta",
    "barrio": "Palermo",
    "ambientes": 2,
    "precio_max": 150000
  },
  "items_recientes": [
    "uuid_item_1",
    "uuid_item_2",
    "uuid_item_3"
  ],
  "items_recientes_resumen": [
    {
      "id_item": "uuid_item_1",
      "label": "opcion_1",
      "titulo": "Departamento 2 ambientes en Palermo"
    },
    {
      "id_item": "uuid_item_2",
      "label": "opcion_2",
      "titulo": "Departamento 3 ambientes en Palermo"
    }
  ],
  "ultimo_item_referenciado": "uuid_item_1",
  "comparacion_activa": false,
  "lead_capturado": true,
  "advisor_requested": false,
  "visit_requested": false,
  "esperando_contacto": false,
  "esperando_visita": false,
  "esperando_confirmacion": false,
  "last_user_message_at": "2026-03-13T18:24:00Z"
}
```

---

# 23. Recomendación de implementación

A nivel de implementación futura, conviene representar este modelo con esquemas explícitos.

Ejemplo de modelos internos:
- `ConversationContext`
- `ConversationState`
- `ContextUpdateCommand`
- `ConversationStageTransition`

Esto facilita validación, testing y persistencia.

---

# 24. Beneficios de este enfoque

- continuidad real entre turnos
- menor costo de IA
- mayor precisión del router
- mejor resolución de referencias
- mejor trazabilidad comercial
- analítica más rica
- arquitectura más robusta y explicable

---

# 25. Objetivo final

El estado conversacional es una de las piezas que transforma un chatbot básico en un sistema conversacional serio.

No alcanza con guardar mensajes.
Hay que guardar **qué está pasando** en la conversación.

Ese “qué está pasando” es justamente lo que representa este modelo de estado y ciclo de vida.

---

Fin del documento.
