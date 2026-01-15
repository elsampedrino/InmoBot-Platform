# 📋 Changelog - 28 de Diciembre 2025

## 🎯 Resumen del Día

Implementación exitosa de **propiedades en notificaciones de Telegram** y **estadísticas semanales por email**.

---

## ✅ 1. Workflow: Estadísticas Semanales por Email

### Implementado
- **Workflow completo** que envía estadísticas cada lunes a las 9 AM Argentina
- **Email HTML** con métricas completas del chatbot

### Archivos Creados
- `Flujos N8N/N8N_InmoBot - Estadisticas Email.json`
- `Documentacion/WORKFLOW_ESTADISTICAS_EMAIL.md`

### Características
- **Queries en paralelo** usando nodo Merge con 4 inputs
- **Cálculo de costos** basado en tokens Haiku y Sonnet
- **Uso de mediana** en vez de promedio para response_time_ms (evita outliers)
- **Timezone configurado** para Argentina (cron: `0 12 * * 1` = 9 AM ART)
- **Notificaciones de error** configuradas en todos los workflows

### Métricas Incluidas
- Total de consultas y tasa de éxito
- Tiempo de respuesta (mediana)
- Consumo de tokens y costos en USD
- Distribución por idioma (ES/EN/PT)
- Top 10 propiedades más vistas
- Tipos de errores detectados

### Problemas Resueltos
1. **Column name error**: Cambio de `created_at` a `timestamp`
2. **Parallel execution**: Uso de Merge node con 4 inputs
3. **Empty email**: Agregado `={{ $json.html }}` al campo HTML
4. **Response time outliers**: Cambio de AVG a PERCENTILE_CONT(0.5)
5. **SMTP connection**: Cambio de puerto 587 a 465 con SSL
6. **Timezone**: Ajuste de cron para UTC → Argentina

---

## ✅ 2. Workflow: Contact Telegram con Propiedades

### Implementado
- **Workflow mejorado** que incluye información de propiedades vistas por el cliente
- **Consulta a PostgreSQL** para obtener propiedades desde `chat_logs`
- **Actualización de schema** en `conversion_logs`

### Archivos Creados/Modificados
- `Flujos N8N/N8N_InmoBot - Contact Telegram.json` (versión final)
- `Documentacion/alter_conversion_logs_add_propiedades.sql`
- `Documentacion/WORKFLOW_CONTACT_TELEGRAM_V2.md`
- `Documentacion/RESUMEN_IMPLEMENTACION_PROPIEDADES_TELEGRAM.md`

### Cambios en Base de Datos

```sql
-- Nuevas columnas en conversion_logs
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS propiedades_ids TEXT[];

CREATE INDEX IF NOT EXISTS idx_conversion_logs_session_id
ON conversion_logs(session_id);
```

### Estructura del Workflow

```
Webhook Contact
    ↓
    ├─→ Consultar Propiedades Vistas (PostgreSQL)
    │       ↓
    │   Preparar Mensaje Telegram
    │       ↓
    │   Enviar Mensaje Telegram
    │       ↓
    │   Responder al Webhook Contact
    │
    └─→ Preparar Stats Leads
            ↓
        Execute Insert Leads
            ↓
        Responder al Webhook Contact
```

### Mensaje de Telegram (Formato Final)

```
🏠 NUEVA SOLICITUD DE CONTACTO
📅 Fecha Ingreso: 28/12/2025, 20:42

👤 Nombre: Damian
📱 Telefono: 115252855522
🕐 Disponibilidad: Mañana de 10 hs a 13 hs

🏘️ PROPIEDADES DE INTERES (3):
   1. PROP-006
   2. PROP-016
   3. PROP-029

💬 Consulta original: "casas en la zona de Villa Ramallo"

Mensaje enviado automaticamente por InmoBot
```

### Características Implementadas
- ✅ Consulta propiedades vistas por `sessionId`
- ✅ Lista de IDs de propiedades de interés
- ✅ Consulta original del cliente (primeros 100 caracteres)
- ✅ Guarda `session_id` y `propiedades_ids` en `conversion_logs`
- ✅ Fecha/hora en timezone Argentina (`America/Argentina/Buenos_Aires`)
- ✅ Compatibilidad con `sessionId` (camelCase) y `session_id` (snake_case)
- ✅ Conversión de tildes a ASCII con función `toASCII()`

### Problemas Resueltos

1. **Missing database columns**
   - Error: `column "session_id" does not exist`
   - Solución: Ejecutar script `alter_conversion_logs_add_propiedades.sql`

2. **Wrong timezone (+6 hours)**
   - Error: Fecha con 6 horas de adelanto
   - Solución: Agregado `timeZone: 'America/Argentina/Buenos_Aires'` en `toLocaleString()`

3. **Session ID en mensaje**
   - Decisión: Removido del mensaje (dato técnico irrelevante para la inmobiliaria)
   - El `session_id` se sigue guardando en la BD para análisis

4. **Data source confusion**
   - Error: Nodo tomaba datos del input anterior en vez del webhook
   - Solución: Usar `$('Webhook Contact').first().json` para datos del formulario y `$input.first().json` para propiedades

### Query SQL - Consultar Propiedades Vistas

```sql
SELECT
  propiedades_ids,
  propiedades_mostradas,
  consulta,
  timestamp
FROM chat_logs
WHERE session_id = '{{ $json.body.sessionId || $json.body.session_id }}'
  AND propiedades_ids IS NOT NULL
  AND array_length(propiedades_ids, 1) > 0
ORDER BY timestamp DESC
LIMIT 1;
```

### Código Clave - Preparar Mensaje Telegram

```javascript
// Obtener datos del webhook
const webhookData = $('Webhook Contact').first().json;
const body = webhookData.body || webhookData;

// Obtener propiedades del nodo anterior
const propiedadesData = $input.first().json;
const propiedadesIds = propiedadesData?.propiedades_ids || [];
const cantidadPropiedades = propiedadesData?.propiedades_mostradas || 0;
const consultaOriginal = propiedadesData?.consulta || '';

// Formatear fecha con timezone Argentina
const fecha = new Date(timestamp);
const fechaFormateada = fecha.toLocaleString('es-AR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'America/Argentina/Buenos_Aires'
});
```

---

## 🗑️ Archivos Removidos

- `Flujos N8N/N8N_InmoBot - Contact Telegram v2.json` → Archivado (reemplazado por versión final sin "v2")

---

## 🔧 Configuración de N8N

### Workflows Activos
1. ✅ `N8N_InmoBot - Estadisticas Email` - Cron: Lunes 9 AM ART
2. ✅ `N8N_InmoBot - Contact Telegram` - Webhook: /contact
3. ✅ `N8N_InmoBot - Haiku` - Webhook: /chat
4. ✅ `N8N_InmoBot - Haiku + Sonnet` - Webhook: /chat (alternativo)

### Notificaciones de Error
- ✅ Configuradas en todos los workflows
- ✅ Envía email a: elsampedrino@gmail.com
- ✅ Incluye: workflow name, execution ID, error message, failed node

### Credenciales Configuradas
- **PostgreSQL**: `Cas8eHe2cYh3vHyG` (Postgres account)
- **SMTP Gmail**: Puerto 465, SSL habilitado
- **Telegram Bot**: Token configurado en HTTP Request nodes

---

## 📊 Base de Datos

### Tabla: chat_logs
- **Campos clave**: `session_id`, `propiedades_ids`, `propiedades_mostradas`, `consulta`, `timestamp`
- **Usado por**: Workflow Contact Telegram, Estadísticas Email

### Tabla: conversion_logs (Actualizada)
- **Campos nuevos**: `session_id`, `propiedades_ids`
- **Índice**: `idx_conversion_logs_session_id`
- **Usado por**: Workflow Contact Telegram

---

## 🎨 Widget React

### Estado Actual
- ✅ Envía `sessionId` en solicitudes de contacto
- ✅ Formato: camelCase (`sessionId`)
- ✅ Almacenado en: `sessionStorage.getItem('chat_session_id')`

### Ubicación
- `widget-react/src/ChatWidget.jsx` (línea 232)

### No requiere modificaciones
El workflow ya soporta tanto `sessionId` como `session_id`

---

## 📈 Mejoras Futuras (Consideradas)

1. **Dashboard de leads con propiedades más solicitadas**
2. **Links directos a propiedades en mensaje de Telegram**
3. **Información resumida de cada propiedad** (precio, barrio) en el mensaje
4. **Comparación semanal** en estadísticas (vs semana anterior)
5. **Alertas** si métricas están fuera de rango
6. **Export a PDF** adjunto en email de estadísticas

---

## 🧪 Testing Realizado

### Workflow Estadísticas Email
- ✅ Ejecución manual exitosa
- ✅ Email recibido con formato correcto
- ✅ Queries en paralelo funcionando
- ✅ Cálculo de costos correcto
- ✅ Uso de mediana para response_time_ms

### Workflow Contact Telegram
- ✅ Test desde widget Vercel
- ✅ Test desde HTML local
- ✅ Propiedades vistas correctamente
- ✅ Session ID guardado en conversion_logs
- ✅ Timezone Argentina correcto
- ✅ Mensaje con formato esperado

---

## 🐛 Issues Conocidos

Ninguno. Todos los problemas encontrados fueron resueltos.

---

## 📝 Notas Importantes

- **Render Starter Plan**: ✅ Activo, los cron funcionan correctamente (no se duerme)
- **Tarifas Anthropic**: Actualizadas a Enero 2025
  - Haiku: $0.25 input / $1.25 output por 1M tokens (promedio: $0.75)
  - Sonnet: $3.00 input / $15.00 output por 1M tokens (promedio: $9.00)
- **GitHub Raw Cache**: Estadísticas se basan en `chat_logs` PostgreSQL, no en JSONs de GitHub
- **Unpublish = Desactivar**: En versiones nuevas de N8N, "Unpublish" desactiva el workflow

---

## 👥 Participantes

- **Usuario**: Cristian (elsampedrino@gmail.com)
- **Email estadísticas**: cristian.barbieripriotti@gmail.com
- **Telegram**: Chat ID 7861411323
- **Asistente**: Claude Sonnet 4.5

---

**Fecha:** 28 de Diciembre 2025
**Estado:** ✅ Completado y testeado
**Próxima sesión:** Pendiente de definir

---

## 🔗 Referencias

- [WORKFLOW_ESTADISTICAS_EMAIL.md](./WORKFLOW_ESTADISTICAS_EMAIL.md)
- [WORKFLOW_CONTACT_TELEGRAM_V2.md](./WORKFLOW_CONTACT_TELEGRAM_V2.md)
- [RESUMEN_IMPLEMENTACION_PROPIEDADES_TELEGRAM.md](./RESUMEN_IMPLEMENTACION_PROPIEDADES_TELEGRAM.md)
- [alter_conversion_logs_add_propiedades.sql](./alter_conversion_logs_add_propiedades.sql)
