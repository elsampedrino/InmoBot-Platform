
# InmoBot Premium – Arquitectura de Runtime y Deployment
Versión: 0.1

Este documento describe **cómo se ejecuta el sistema InmoBot Premium en producción**.
Conecta la arquitectura lógica definida previamente con la infraestructura real necesaria
para operar el SaaS.

Complementa:

- arquitectura general
- mapa de módulos
- contratos internos
- endpoints
- analítica
- estado conversacional

---

# 1. Objetivo de esta arquitectura

Definir cómo interactúan en runtime:

- Widget Web
- WhatsApp
- API FastAPI
- PostgreSQL
- Modelos de IA
- Workers de procesamiento
- Analítica

El objetivo es que el sistema sea:

- escalable
- resiliente
- observable
- eficiente en costo

---

# 2. Vista general del sistema

Arquitectura simplificada:

Widget Web
   ↓
API Gateway / CDN
   ↓
FastAPI Backend
   ↓
Servicios internos
   ↓
PostgreSQL

Paralelamente:

FastAPI → Modelos de IA  
FastAPI → Sistema de analítica

---

# 3. Componentes principales

## 3.1 Widget Web

Responsabilidades:

- interfaz de chat
- envío de mensajes al backend
- renderizado de resultados
- manejo de session_id

No contiene lógica conversacional.

---

## 3.2 Integración WhatsApp

Proveedor externo (ej: Meta Cloud API).

Flujo:

WhatsApp → Webhook → API → Motor Conversacional

---

## 3.3 API Backend (FastAPI)

Es el **núcleo del sistema**.

Responsabilidades:

- orquestar el pipeline conversacional
- ejecutar router
- invocar parser
- ejecutar search engine
- construir prompts
- llamar modelos IA
- registrar analítica
- actualizar contexto

Este backend debe ser **stateless** para escalar horizontalmente.

---

## 3.4 PostgreSQL

Base central del sistema.

Almacena:

- catálogo
- prompts
- conversaciones
- mensajes
- leads
- followups
- knowledge base
- analítica

Recomendaciones:

- índices optimizados
- JSONB para atributos de catálogo
- conexiones pool

---

## 3.5 Servicios de IA

Modelos utilizados:

Claude Haiku
Claude Sonnet

Uso:

Haiku → clasificación y fallback  
Sonnet → generación de respuesta

Las llamadas deben estar encapsuladas en el **AI Response Service**.

---

## 3.6 Workers opcionales

Para tareas pesadas o asincrónicas:

- importación de catálogo
- procesamiento de KB
- reindexación
- cálculos de analítica

Tecnologías posibles:

- Celery
- RQ
- workers simples FastAPI + cola

---

# 4. Flujo de una consulta completa

Usuario envía mensaje.

1. Widget / WhatsApp envía request
2. API recibe mensaje
3. Se resuelve empresa y rubro
4. Se recupera contexto conversacional
5. Router decide flujo
6. Parser genera filtros
7. Search Engine consulta PostgreSQL
8. Prompt Service construye prompt
9. Sonnet genera respuesta
10. Se registran eventos de analítica
11. Se actualiza contexto
12. Se devuelve respuesta

Tiempo objetivo:

500–1000 ms promedio.

---

# 5. Escalabilidad

El backend debe ser **horizontalmente escalable**.

Estrategia:

- múltiples instancias FastAPI
- balanceador de carga
- backend stateless
- PostgreSQL central

Escalado típico:

Usuarios ↑ → Instancias API ↑

---

# 6. Observabilidad

El sistema debe registrar:

Logs técnicos
Métricas de performance
Eventos de negocio

Herramientas posibles:

- Prometheus
- Grafana
- OpenTelemetry
- logging estructurado

---

# 7. Seguridad

Puntos clave:

- validación de webhooks
- autenticación en endpoints administrativos
- aislamiento multi-tenant
- sanitización de inputs

---

# 8. Estrategia de despliegue

Opciones posibles:

Docker + VPS
Docker + Kubernetes
Serverless containers

Configuración recomendada para inicio:

- API container
- PostgreSQL
- Redis opcional
- Worker container

---

# 9. Entornos

Se recomienda separar:

dev
staging
production

Cada uno con:

- base de datos separada
- configuración propia
- claves de IA distintas

---

# 10. Objetivo final

La arquitectura de runtime debe permitir que InmoBot funcione como
un **SaaS robusto**, capaz de atender múltiples empresas simultáneamente
con baja latencia y alta confiabilidad.

---

Fin del documento.
