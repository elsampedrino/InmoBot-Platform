# InmoBot Premium -- Motor Conversacional

Versión: 0.1

Este documento define el funcionamiento del **motor conversacional de
InmoBot Premium**. Es el componente central del sistema y determina cómo
el asistente interpreta las consultas del usuario, busca información y
genera respuestas.

Principio fundamental del sistema:

**La IA no busca, la IA explica.**

El motor conversacional utiliza principalmente: - lógica
determinística - SQL - estructuras de datos - contexto conversacional

La IA se utiliza únicamente cuando es necesario.

------------------------------------------------------------------------

# 1. Arquitectura General del Motor Conversacional

Pipeline completo de una consulta:

Usuario → Canal (Widget / WhatsApp) → Webhook API → Router
Conversacional → Parser determinístico → Motor de búsqueda SQL → Ranking
de resultados → Generador de respuesta (IA) → Respuesta al usuario

Cada etapa tiene responsabilidades bien definidas.

------------------------------------------------------------------------

# 2. Router Conversacional

El router conversacional es el primer componente que procesa la
consulta.

Su función es determinar **qué tipo de consulta realizó el usuario**.

Tipos de intención posibles:

buscar_item pregunta_general consultar_detalle_item contactar_asesor
agendar_visita informacion_empresa saludo

Ejemplo:

Usuario: "Busco un departamento en Palermo"

Router:

intent = buscar_item

------------------------------------------------------------------------

# 3. Parser Determinístico

El parser convierte lenguaje natural en filtros estructurados.

Ejemplo:

Usuario: "Busco una casa con pileta en Nordelta"

Resultado del parser:

{ "intent": "buscar_item", "tipo": "casa", "zona": "nordelta",
"atributos": { "pileta": true } }

El parser funciona mediante:

-   diccionarios de términos
-   reglas
-   normalización de texto
-   sinónimos

Si el parser no logra interpretar la consulta correctamente, se utiliza
IA para clasificación.

------------------------------------------------------------------------

# 4. Clasificación con IA (Fallback)

Cuando el parser no puede determinar la intención, se utiliza un modelo
pequeño de IA.

Modelo recomendado:

Claude Haiku

Responsabilidad de Haiku:

-   clasificar intención
-   sugerir filtros

Este paso debe ejecutarse solo cuando sea necesario.

------------------------------------------------------------------------

# 5. Motor de Búsqueda SQL

Una vez interpretada la consulta, se ejecuta la búsqueda en PostgreSQL.

La búsqueda se realiza sobre la tabla:

items

Filtros principales:

id_empresa id_rubro tipo categoria atributos (jsonb)

Ejemplo de consulta SQL:

SELECT \* FROM items WHERE id_empresa = :empresa AND activo = true AND
tipo = 'departamento' LIMIT 5

El sistema debe utilizar índices para optimizar las consultas.

------------------------------------------------------------------------

# 6. Ranking de Resultados

Los resultados encontrados deben ordenarse para mostrar los mejores
primero.

Criterios de ranking:

destacado precio recencia score de coincidencia

El ranking puede combinar varios factores.

------------------------------------------------------------------------

# 7. Generación de Respuesta

Una vez obtenidos los resultados, se genera la respuesta al usuario.

Responsabilidad de este paso:

-   explicar los resultados
-   mantener tono conversacional
-   invitar a continuar la interacción

Modelo recomendado:

Claude Sonnet

Ejemplo de respuesta generada:

"Encontré algunas opciones en Palermo que podrían interesarte:

🏡 Departamento 2 ambientes -- USD 120.000 🏡 Departamento 3 ambientes
-- USD 160.000

¿Querés que te pase más detalles o fotos de alguno?"

------------------------------------------------------------------------

# 8. Manejo de Contexto Conversacional

El sistema debe mantener contexto entre mensajes.

Ejemplo:

Usuario: "Busco deptos en Palermo"

Luego:

"¿Tenés algo más barato?"

El sistema debe entender que el usuario sigue hablando de
**departamentos en Palermo**.

El contexto se almacena en:

contextos_conversacion

------------------------------------------------------------------------

# 9. Conversión a Lead

Cuando el usuario muestra interés real, el sistema puede crear un lead.

Ejemplo:

"Quiero ver el departamento de Palermo"

Acción:

crear lead

Tabla:

leads

También puede programarse un followup.

------------------------------------------------------------------------

# 10. Registro de Analítica

Cada interacción debe registrarse para análisis.

Tablas utilizadas:

premium_chat_logs premium_chat_log_items premium_conversion_logs

Información registrada:

consulta modelo utilizado tiempo de respuesta items mostrados

Esto permite mejorar el sistema con el tiempo.

------------------------------------------------------------------------

# 11. Principios del Motor Conversacional

Reglas fundamentales:

1.  SQL primero
2.  IA solo cuando es necesario
3.  contexto persistente
4.  respuestas cortas y claras
5.  promover interacción
6.  registrar analítica

------------------------------------------------------------------------

# 12. Objetivo del Motor Conversacional

El objetivo no es solo responder preguntas.

El objetivo es:

-   guiar al usuario
-   mostrar opciones relevantes
-   generar contacto comercial
-   convertir consultas en leads

------------------------------------------------------------------------

Fin del documento.
