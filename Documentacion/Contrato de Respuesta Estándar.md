InmoBot – Respuesta Unificada (Plan Básico / Pro / Premium)

🎯 Objetivo

Definir una estructura JSON única y estable para todas las respuestas del asistente inmobiliario, independientemente de:

  ## Modelo utilizado (Haiku, Sonnet u otro)
  ## Idioma
  ## Tipo de consulta
  ## Plan contratado

Este contrato permite:

  ## Desacoplar frontend ↔ lógica IA
  ## Facilitar escalabilidad (API, CRM, dashboard)
  ## Diferenciar planes sin duplicar flujos
  ## Simplificar métricas y logging

🧱 Estructura General (obligatoria)

Toda respuesta del sistema DEBE cumplir esta estructura base:

{
  "status": "ok",
  "type": "",
  "language": "",
  "message": "",
  "properties": [],
  "actions": [],
  "meta": {}
}

🔍 Definición de Campos
1️⃣ status

Indica el estado general de la respuesta.

Valores posibles:

  > "ok"
  > "error"

Ejemplo:

"status": "ok"

2️⃣ type (campo clave)

Define qué tipo de respuesta es, independientemente del texto.

Valores definidos:

| type          | Descripción                            |
| ------------- | -------------------------------------- |
| `greeting`    | Saludo inicial sin mostrar propiedades |
| `properties`  | Respuesta con propiedades              |
| `no_match`    | No hay coincidencias                   |
| `too_generic` | Consulta muy amplia                    |
| `error`       | Error técnico                          |

Ejemplo:

"type": "properties"

3️⃣ language

Idioma detectado automáticamente según la consulta del usuario.

Valores:

  > "es" (Español)
  > "en" (Inglés)
  > "pt" (Portugués)

Ejemplo:

"language": "es"

4️⃣ message

Texto final que ve el usuario.
Debe estar:

  - En el idioma detectado
  - Listo para renderizar (web / WhatsApp / Telegram)

Ejemplo:

"message": "Tengo casas disponibles:"

5️⃣ properties (opcional según type)

Solo se incluye cuando type = "properties".

Estructura por propiedad:

  {
    "id": "PROP-001",
    "titulo": "Casa en venta - Ramallo",
    "tipo": "Casa",
    "operacion": "Venta",
    "precio": {
      "valor": 139000,
      "moneda": "USD"
    },
    "ubicacion": {
      "calle": "Colón al 1100",
      "barrio": "Ramallo",
      "ciudad": "Ramallo"
    },
    "caracteristicas": {
      "dormitorios": 2,
      "banios": 1,
      "superficie_total": "462 m²",
      "superficie_cubierta": "140 m²"
    },
    "detalles": [
      "patio",
      "pileta",
      "quincho",
      "parrilla"
    ],
    "fotos": [
      "https://res.cloudinary.com/.../foto01.jpg",
      "https://res.cloudinary.com/.../foto02.jpg"
    ]
  }


Notas:

  > No es obligatorio renderizar todo en el frontend
  > Sirve para leads, CRM, métricas, dashboards

6️⃣ actions (habilitador comercial)

Define qué acciones puede mostrar el frontend según el plan.

Ejemplos:

  "actions": []

  "actions": [
    { "type": "contact_form" },
    { "type": "see_more" }
  ]


Posibles acciones futuras:

  > contact_form
  > whatsapp
  > schedule_visit
  > crm_sync

👉 Permite diferenciar planes sin cambiar prompts ni flujos.

7️⃣ meta (uso interno)

Información técnica y de negocio (no visible para el cliente).

Ejemplo:

  "meta": {
    "sessionId": "abc123",
    "source": "sonnet",
    "processingTimeMs": 10047,
    "propertiesCount": 3
  }


Uso:

  > Métricas
  > Optimización
  > Debug
  > Dashboard futuro

🧪 Ejemplos de Respuesta
🔹 Saludo (greeting)
{
  "status": "ok",
  "type": "greeting",
  "language": "es",
  "message": "¡Hola! 👋 ¿Qué estás buscando?",
  "properties": [],
  "actions": [],
  "meta": {}
}

🔹 Propiedades (properties)
{
  "status": "ok",
  "type": "properties",
  "language": "es",
  "message": "Encontré casas disponibles:",
  "properties": [ ... ],
  "actions": [
    { "type": "contact_form" }
  ],
  "meta": {
    "propertiesCount": 3
  }
}

🔹 Sin coincidencias (no_match)
{
  "status": "ok",
  "type": "no_match",
  "language": "es",
  "message": "Actualmente no tenemos propiedades disponibles con esas características.",
  "properties": [],
  "actions": [],
  "meta": {}
}

📌 Decisiones de Diseño

  > El frontend NO debe inferir lógica desde texto
  > El backend NO depende del canal
  > El contrato es agnóstico del modelo IA
  > Permite evolución sin breaking changes

Estado:
🟡 Diseño