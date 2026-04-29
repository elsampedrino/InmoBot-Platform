# InmoBot Premium -- Search Engine Multirubro

Versión: 0.1

Este documento define el **Search Engine del catálogo** utilizado por
InmoBot Premium. Es el componente encargado de transformar una consulta
del usuario en una búsqueda estructurada en PostgreSQL.

El objetivo es que el motor funcione para **múltiples rubros**
utilizando la misma arquitectura.

Principio fundamental:

**La base de datos es el motor de búsqueda.** La API construye consultas
SQL dinámicas a partir de filtros estructurados.

------------------------------------------------------------------------

# 1. Objetivo del Search Engine

El motor de búsqueda debe:

-   interpretar filtros provenientes del parser
-   construir consultas SQL eficientes
-   soportar múltiples rubros
-   aprovechar índices PostgreSQL
-   devolver los mejores candidatos posibles

El resultado del search engine **no es la respuesta final**, sino un
conjunto de items candidatos.

------------------------------------------------------------------------

# 2. Entidad central: ITEMS

Tabla principal del catálogo:

items

Campos principales utilizados en búsqueda:

id_item id_empresa id_rubro tipo categoria titulo descripcion precio
moneda atributos (jsonb) activo destacado created_at

Los atributos específicos de cada rubro se almacenan en:

atributos (jsonb)

Ejemplo para inmobiliaria:

{ "ambientes": 3, "banos": 2, "pileta": true, "barrio": "Palermo" }

------------------------------------------------------------------------

# 3. Esquema por rubro

Cada rubro define su esquema de búsqueda en:

rubro_schema

Campos principales:

search_mode required_keys facet_keys validation_rules

Ejemplo:

{ "required_keys": \["tipo"\], "facet_keys":
\["barrio","ambientes","precio"\], "validation_rules": { "ambientes":
"integer", "precio": "numeric" } }

Esto permite que el mismo motor funcione para distintos rubros.

------------------------------------------------------------------------

# 4. Pipeline del Search Engine

Pipeline de búsqueda:

consulta usuario → parser → filtros estructurados → construcción de SQL
→ ejecución en PostgreSQL → ranking de resultados → retorno de
candidatos

------------------------------------------------------------------------

# 5. Filtros estructurados

El parser genera un objeto como este:

{ "tipo": "departamento", "barrio": "Palermo", "ambientes": 2 }

Estos filtros se traducen a SQL.

------------------------------------------------------------------------

# 6. Construcción dinámica de SQL

Ejemplo de consulta generada:

SELECT \* FROM items WHERE id_empresa = :empresa AND id_rubro = :rubro
AND activo = true AND tipo = 'departamento' AND atributos-\>\>'barrio' =
'Palermo' AND (atributos-\>\>'ambientes')::int \>= 2 ORDER BY destacado
DESC LIMIT 5

La construcción de SQL debe ser dinámica según los filtros disponibles.

------------------------------------------------------------------------

# 7. Índices recomendados

Para optimizar el search engine se recomiendan:

btree index:

(id_empresa, id_rubro, tipo)

GIN index:

atributos jsonb_path_ops

index precio:

(id_empresa, precio)

Esto permite consultas muy rápidas incluso con grandes catálogos.

------------------------------------------------------------------------

# 8. Ranking de resultados

Una vez obtenidos los candidatos se aplica ranking.

Criterios posibles:

destacado precio recencia coincidencia de atributos

El ranking puede calcularse en SQL o en la API.

------------------------------------------------------------------------

# 9. Facetas

El motor puede devolver información de facetas para mejorar la
conversación.

Ejemplo:

cantidad por barrio cantidad por tipo rangos de precio

Esto permite que el bot sugiera refinamientos.

Ejemplo:

"Encontré 12 propiedades en Palermo. ¿Preferís 2 o 3 ambientes?"

------------------------------------------------------------------------

# 10. Multiempresa

Todas las consultas deben filtrar por:

id_empresa

Esto asegura aislamiento entre clientes del SaaS.

------------------------------------------------------------------------

# 11. Multi rubro

El motor soporta distintos rubros utilizando:

id_rubro rubro_schema atributos jsonb

Ejemplos de rubros futuros:

inmobiliaria autos hoteles productos ecommerce

La lógica del motor permanece igual.

------------------------------------------------------------------------

# 12. Resultado del Search Engine

El motor devuelve una lista de items candidatos.

Ejemplo:

\[ { "id_item": "...", "titulo": "Departamento 2 ambientes Palermo",
"precio": 120000 }, { "id_item": "...", "titulo": "Departamento 3
ambientes Palermo", "precio": 160000 }\]

Estos resultados se envían al generador de respuesta IA.

------------------------------------------------------------------------

# 13. Responsabilidades del Search Engine

El search engine **no debe**:

-   generar texto conversacional
-   interpretar intención del usuario
-   interactuar con el usuario

Solo debe:

-   buscar
-   filtrar
-   rankear

------------------------------------------------------------------------

# 14. Beneficios de esta arquitectura

-   baja latencia
-   menor costo de IA
-   control total del sistema
-   escalabilidad SaaS
-   soporte multirubro

------------------------------------------------------------------------

Fin del documento.
