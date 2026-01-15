# 🔄 Workflows N8N Activos

**Última actualización:** 28 de Diciembre 2025

---

## 📊 Resumen

| Workflow | Estado | Tipo | Frecuencia | Descripción |
|----------|--------|------|------------|-------------|
| **N8N_InmoBot - Haiku** | ✅ Activo | Webhook | On-demand | Chat principal (solo Haiku) |
| **N8N_InmoBot - Haiku + Sonnet** | ✅ Activo | Webhook | On-demand | Chat avanzado (Haiku + Sonnet) |
| **N8N_InmoBot - Contact Telegram** | ✅ Activo | Webhook | On-demand | Notificaciones de contacto con propiedades |
| **N8N_InmoBot - Estadisticas Email** | ✅ Activo | Cron | Lunes 9 AM ART | Estadísticas semanales por email |

---

## 1️⃣ Chat Principal - Haiku

### Información
- **Archivo:** `Flujos N8N/N8N_InmoBot - Haiku.json`
- **Webhook:** `/webhook/chat`
- **Modelo:** Claude 3 Haiku únicamente
- **Propósito:** Respuestas rápidas y económicas

### Endpoints
- **Producción:** `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`
- **Método:** POST
- **Body:** `{ "message": "consulta del usuario", "sessionId": "..." }`

### Características
- Búsqueda de propiedades en catálogo BBR
- Respuestas en español, inglés y portugués
- Logging en PostgreSQL (`chat_logs`)
- Tracking de tokens y costos

---

## 2️⃣ Chat Avanzado - Haiku + Sonnet

### Información
- **Archivo:** `Flujos N8N/N8N_InmoBot - Haiku + Sonnet.json`
- **Webhook:** `/webhook/chat` (mismo endpoint)
- **Modelos:** Claude 3 Haiku (búsqueda) + Claude 3.5 Sonnet (respuesta)
- **Propósito:** Respuestas de mayor calidad

### Características
- Búsqueda con Haiku (rápida)
- Generación de respuesta con Sonnet (mejor calidad)
- Mayor costo pero mejor experiencia
- Mismo logging que versión Haiku

---

## 3️⃣ Notificaciones de Contacto

### Información
- **Archivo:** `Flujos N8N/N8N_InmoBot - Contact Telegram.json`
- **Webhook:** `/webhook/contact`
- **Propósito:** Enviar leads a Telegram con información de propiedades vistas

### Endpoints
- **Producción:** `https://n8n-bot-inmobiliario.onrender.com/webhook/contact`
- **Método:** POST
- **Body:** `{ "nombre": "...", "telefono": "...", "disponibilidad": "...", "sessionId": "..." }`

### Características
- **Query automática** de propiedades vistas por `sessionId`
- **Mensaje a Telegram** con:
  - Datos del cliente (nombre, teléfono, disponibilidad)
  - Lista de propiedades de interés
  - Consulta original del cliente
  - Fecha/hora en timezone Argentina
- **Guarda en BD** (`conversion_logs`):
  - `session_id` para vincular con `chat_logs`
  - `propiedades_ids` (array de IDs)

### Ejemplo de Mensaje Telegram

```
🏠 NUEVA SOLICITUD DE CONTACTO
📅 Fecha Ingreso: 28/12/2025, 20:42

👤 Nombre: Juan Perez
📱 Telefono: +54 9 11 1234-5678
🕐 Disponibilidad: Lunes a Viernes 14-18hs

🏘️ PROPIEDADES DE INTERES (3):
   1. PROP-001
   2. PROP-005
   3. PROP-012

💬 Consulta original: "Busco depto 2 ambientes en Palermo..."

Mensaje enviado automaticamente por InmoBot
```

### Tabla: conversion_logs

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | SERIAL PRIMARY KEY | ID único del lead |
| nombre | VARCHAR(255) | Nombre del cliente |
| telefono | VARCHAR(50) | Teléfono del cliente |
| disponibilidad | TEXT | Horarios disponibles |
| source | VARCHAR(50) | Origen: 'widget', 'telegram', etc |
| session_id | VARCHAR(255) | Vincula con chat_logs |
| propiedades_ids | TEXT[] | Array de IDs de propiedades |
| timestamp | TIMESTAMP | Fecha de creación (auto) |

---

## 4️⃣ Estadísticas Semanales

### Información
- **Archivo:** `Flujos N8N/N8N_InmoBot - Estadisticas Email.json`
- **Trigger:** Cron schedule
- **Frecuencia:** `0 12 * * 1` (Lunes 12:00 UTC = 9:00 AM Argentina)
- **Propósito:** Enviar reporte semanal a Cristian

### Destinatario
- **Email:** cristian.barbieripriotti@gmail.com
- **Formato:** HTML responsive

### Métricas Incluidas

#### 📊 Resumen General
- Total de consultas (últimos 7 días)
- Tasa de éxito (%)
- Tiempo promedio de respuesta (mediana en segundos)
- Total de propiedades mostradas

#### 💰 Consumo y Costos
- Tokens Haiku (total + costo en USD)
- Tokens Sonnet (total + costo en USD)
- Costo total acumulado

#### 🌍 Distribución por Idioma
- Español 🇦🇷 (cantidad + porcentaje)
- Inglés 🇺🇸 (cantidad + porcentaje)
- Portugués 🇧🇷 (cantidad + porcentaje)

#### 🏘️ Top 10 Propiedades
- IDs de propiedades más vistas
- Cantidad de veces mostrada cada una
- Medallas 🥇🥈🥉 para las top 3

#### ⚠️ Errores Detectados
- Tipos de error
- Cantidad de ocurrencias

### Queries SQL Ejecutadas

```sql
-- 1. Stats General
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
  SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as consultas_fallidas,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms)::numeric, 0) as tiempo_promedio_ms,
  SUM(tokens_haiku) as tokens_haiku_total,
  SUM(tokens_sonnet) as tokens_sonnet_total,
  SUM(tokens_total) as tokens_totales,
  SUM(propiedades_mostradas) as propiedades_mostradas_total
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- 2. Stats Por Idioma
SELECT
  idioma,
  COUNT(*) as cantidad,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as porcentaje
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY idioma
ORDER BY cantidad DESC;

-- 3. Top 10 Propiedades
SELECT
  UNNEST(propiedades_ids) as propiedad_id,
  COUNT(*) as veces_mostrada
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
  AND propiedades_ids IS NOT NULL
GROUP BY propiedad_id
ORDER BY veces_mostrada DESC
LIMIT 10;

-- 4. Tipos de Errores
SELECT
  error_type,
  COUNT(*) as cantidad
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
  AND success = 0
GROUP BY error_type
ORDER BY cantidad DESC;
```

### Tarifas Anthropic (Enero 2025)

| Modelo | Input | Output | Promedio (50/50) |
|--------|-------|--------|------------------|
| Haiku | $0.25/1M tokens | $1.25/1M tokens | $0.75/1M tokens |
| Sonnet | $3.00/1M tokens | $15.00/1M tokens | $9.00/1M tokens |

---

## 🔔 Notificaciones de Error

**Configuradas en todos los workflows**

### Cuando se Activa
- Cualquier nodo falla en el workflow

### Email Enviado
- **To:** elsampedrino@gmail.com
- **Subject:** `⚠️ ERROR - [Nombre del Workflow]`
- **Contenido:**
  - Nombre del workflow
  - Execution ID
  - Error message
  - Nodo que falló

---

## 🗄️ Base de Datos PostgreSQL

### Conexión N8N
- **Credential ID:** `Cas8eHe2cYh3vHyG`
- **Nombre:** Postgres account

### Tablas Principales

#### chat_logs
```sql
CREATE TABLE chat_logs (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255),
  consulta TEXT,
  idioma VARCHAR(10),
  success INTEGER,
  error_type VARCHAR(100),
  response_time_ms INTEGER,
  tokens_haiku INTEGER,
  tokens_sonnet INTEGER,
  tokens_total INTEGER,
  propiedades_mostradas INTEGER,
  propiedades_ids TEXT[],
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_logs_session_id ON chat_logs(session_id);
CREATE INDEX idx_chat_logs_timestamp ON chat_logs(timestamp);
```

#### conversion_logs
```sql
CREATE TABLE conversion_logs (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(255),
  telefono VARCHAR(50),
  disponibilidad TEXT,
  source VARCHAR(50),
  session_id VARCHAR(255),
  propiedades_ids TEXT[],
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversion_logs_session_id ON conversion_logs(session_id);
```

---

## 🔧 Configuración SMTP (Gmail)

### Credenciales
- **Host:** smtp.gmail.com
- **Port:** 465
- **SSL/TLS:** Enabled
- **User:** [configurado en N8N]
- **Password:** App Password de 16 caracteres

### Obtener App Password
1. https://myaccount.google.com/security
2. Habilitar verificación en 2 pasos
3. Buscar "Contraseñas de aplicaciones"
4. Generar nueva para "Correo"
5. Copiar contraseña de 16 caracteres

---

## 📂 Archivos de Workflows

```
Flujos N8N/
├── N8N_InmoBot - Haiku.json
├── N8N_InmoBot - Haiku + Sonnet.json
├── N8N_InmoBot - Contact Telegram.json
└── N8N_InmoBot - Estadisticas Email.json
```

---

## 📝 Documentación Relacionada

- [CHANGELOG_28_DIC_2025.md](./CHANGELOG_28_DIC_2025.md) - Cambios del día
- [WORKFLOW_ESTADISTICAS_EMAIL.md](./WORKFLOW_ESTADISTICAS_EMAIL.md) - Estadísticas detalladas
- [WORKFLOW_CONTACT_TELEGRAM_V2.md](./WORKFLOW_CONTACT_TELEGRAM_V2.md) - Contact con propiedades
- [alter_conversion_logs_add_propiedades.sql](./alter_conversion_logs_add_propiedades.sql) - Script de migración

---

## 🚀 Deploy en Render

### Servicio N8N
- **URL:** https://n8n-bot-inmobiliario.onrender.com
- **Plan:** Starter ($7/mes)
- **Estado:** ✅ Activo (no se duerme)

### Beneficios del Starter Plan
- ✅ Cron jobs funcionan 24/7
- ✅ No hay sleep mode
- ✅ Webhooks siempre disponibles
- ✅ Mayor estabilidad

---

**Mantenido por:** Cristian Barbieri Priotti
**Asistente:** Claude Sonnet 4.5
**Última revisión:** 28 de Diciembre 2025
