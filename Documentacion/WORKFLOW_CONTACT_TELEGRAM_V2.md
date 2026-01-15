# 📲 Workflow: Contact Telegram v2 - Con Información de Propiedades

**Fecha:** 28 de Diciembre 2025
**Workflow:** `N8N_InmoBot - Contact Telegram v2.json`
**Versión:** 2.0
**Mejora Principal:** Incluye información de propiedades vistas por el cliente

---

## 🎯 Objetivo

Mejorar las notificaciones de Telegram para que la inmobiliaria sepa **qué propiedades le interesan al cliente** cuando solicita contacto.

### ✅ Mejoras vs Versión 1.0

| Aspecto | v1.0 | v2.0 |
|---------|------|------|
| Datos del cliente | ✅ Nombre, teléfono, disponibilidad | ✅ Mismo |
| Session ID | ❌ No incluido | ✅ Incluido |
| Propiedades vistas | ❌ No | ✅ Sí (lista de IDs) |
| Consulta original | ❌ No | ✅ Primeros 100 caracteres |
| Base de datos | ✅ Registra lead | ✅ Registra lead + propiedades |

---

## 📋 Estructura del Workflow v2

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

---

## 🆕 Nuevo Nodo: Consultar Propiedades Vistas

### Query SQL

```sql
SELECT
  propiedades_ids,
  propiedades_mostradas,
  consulta,
  timestamp
FROM chat_logs
WHERE session_id = '{{ $json.body.session_id }}'
  AND propiedades_ids IS NOT NULL
  AND array_length(propiedades_ids, 1) > 0
ORDER BY timestamp DESC
LIMIT 1;
```

**Qué hace:**
- Busca la última consulta del cliente en `chat_logs` usando el `session_id`
- Obtiene el array de IDs de propiedades que vio (`propiedades_ids`)
- Obtiene la cantidad de propiedades mostradas
- Obtiene la consulta original del cliente
- Solo trae registros que tengan propiedades (no NULL y no vacío)

---

## 📧 Nuevo Formato del Mensaje de Telegram

### Ejemplo con propiedades

```
🏠 NUEVA SOLICITUD DE CONTACTO
📅 Fecha Ingreso: 28/12/2025 15:30
🔑 Session ID: abc123def456

👤 Nombre: Juan Perez
📱 Telefono: +54 9 11 1234-5678
🕐 Disponibilidad: Lunes a Viernes 14-18hs

🏘️ PROPIEDADES DE INTERES (3):
   1. PROP-001
   2. PROP-005
   3. PROP-012

💬 Consulta original: "Busco departamento 2 ambientes en Palermo con balcon, precio hasta USD 1000"

Mensaje enviado automaticamente por InmoBot
```

### Ejemplo sin propiedades

```
🏠 NUEVA SOLICITUD DE CONTACTO
📅 Fecha Ingreso: 28/12/2025 15:30
🔑 Session ID: abc123def456

👤 Nombre: Maria Lopez
📱 Telefono: +54 9 11 9876-5432
🕐 Disponibilidad: Cualquier dia despues de las 18hs

⚠️ No se registraron propiedades vistas en esta sesion

Mensaje enviado automaticamente por InmoBot
```

---

## 🗄️ Cambios en Base de Datos

### Tabla: conversion_logs

**Nuevas columnas agregadas:**

```sql
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS propiedades_ids TEXT[];
```

**Esquema completo actualizado:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id | SERIAL PRIMARY KEY | ID único del lead |
| nombre | VARCHAR(255) | Nombre del cliente |
| telefono | VARCHAR(50) | Teléfono del cliente |
| disponibilidad | TEXT | Horarios disponibles |
| source | VARCHAR(50) | Origen: 'widget', 'telegram', etc |
| session_id | VARCHAR(255) | **NUEVO:** Vincula con chat_logs |
| propiedades_ids | TEXT[] | **NUEVO:** Array de IDs de propiedades |
| timestamp | TIMESTAMP | Fecha de creación (auto) |

**Índice creado:**
```sql
CREATE INDEX IF NOT EXISTS idx_conversion_logs_session_id
ON conversion_logs(session_id);
```

---

## 🔧 Instalación Paso a Paso

### 1. Actualizar Base de Datos

**Ejecutar en PostgreSQL:**

```bash
psql -h tu-host -U tu-usuario -d tu-database -f Documentacion/alter_conversion_logs_add_propiedades.sql
```

O ejecutar manualmente en un cliente SQL:

```sql
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS propiedades_ids TEXT[];

CREATE INDEX IF NOT EXISTS idx_conversion_logs_session_id
ON conversion_logs(session_id);
```

**Verificar que se crearon correctamente:**

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversion_logs'
ORDER BY ordinal_position;
```

---

### 2. Importar Workflow v2 en N8N

1. Abre N8N en tu navegador
2. Menú superior → **Workflows**
3. Click en **Import from File**
4. Selecciona: `Flujos N8N/N8N_InmoBot - Contact Telegram v2.json`
5. El workflow se importará con el nombre: **"N8N_InmoBot - Contact Telegram v2"**

---

### 3. Verificar Credenciales PostgreSQL

El workflow usa la credencial: `Cas8eHe2cYh3vHyG`

**Si necesitas cambiarla:**

1. Click en el nodo **"Consultar Propiedades Vistas"**
2. En **Credentials** → Selecciona tu conexión PostgreSQL
3. Repite en el nodo **"Execute Insert Leads"**

---

### 4. Probar el Workflow

**Opción A: Test Manual en N8N**

1. En N8N, abre el workflow v2
2. Click en el nodo **"Webhook Contact"**
3. Click en **"Listen for test event"**
4. Copia la URL del webhook
5. Usa Postman/cURL para enviar un POST:

```bash
curl -X POST https://tu-n8n.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "telefono": "+54 9 11 1234-5678",
    "disponibilidad": "Lunes 14-18hs",
    "session_id": "test_session_123",
    "timestamp": "2025-12-28T15:30:00Z"
  }'
```

**Opción B: Desde el Widget**

1. Abre el chatbot en el navegador
2. Realiza una consulta de propiedades
3. Click en "Agendar Visita"
4. Completa el formulario
5. Verifica que llegue el mensaje a Telegram con las propiedades

---

### 5. Desactivar Workflow v1 y Activar v2

**Importante:** Solo uno debe estar activo para evitar duplicados

1. Abre el workflow **"N8N_InmoBot - Contact Telegram"** (v1)
2. Toggle **Active** → OFF
3. Abre el workflow **"N8N_InmoBot - Contact Telegram v2"**
4. Toggle **Active** → ON

---

## 🔍 Troubleshooting

### Problema 1: No se muestran propiedades en el mensaje

**Posibles causas:**
- El `session_id` no se está enviando desde el widget
- No hay registros en `chat_logs` con ese `session_id`
- El array `propiedades_ids` está vacío o NULL

**Solución:**

1. Verificar que el widget envíe `session_id` en el POST:

```javascript
// En ChatWidget.jsx
const response = await fetch(`${API_URL}/contact`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nombre,
    telefono,
    disponibilidad,
    session_id: sessionStorage.getItem('chat_session_id'), // ← VERIFICAR
    timestamp: new Date().toISOString()
  })
});
```

2. Verificar que haya datos en chat_logs:

```sql
SELECT session_id, propiedades_ids, propiedades_mostradas
FROM chat_logs
WHERE session_id = 'tu_session_id_de_prueba'
ORDER BY timestamp DESC;
```

---

### Problema 2: Error al insertar en conversion_logs

**Error:** `column "session_id" does not exist` o `column "propiedades_ids" does not exist`

**Solución:**
1. Ejecutar el script de alteración de tabla:
```bash
psql -f Documentacion/alter_conversion_logs_add_propiedades.sql
```

---

### Problema 3: Query de propiedades retorna vacío

**Posibles causas:**
- `session_id` no coincide
- Solo hay registros con `propiedades_ids = NULL`

**Solución:**

1. Ejecutar query de diagnóstico:

```sql
-- Ver todos los registros de esa sesión
SELECT id, session_id, propiedades_ids, propiedades_mostradas, timestamp
FROM chat_logs
WHERE session_id = 'tu_session_id'
ORDER BY timestamp DESC;

-- Ver si hay registros con propiedades
SELECT COUNT(*) as registros_con_propiedades
FROM chat_logs
WHERE session_id = 'tu_session_id'
  AND propiedades_ids IS NOT NULL
  AND array_length(propiedades_ids, 1) > 0;
```

---

### Problema 4: Mensaje de Telegram con caracteres raros

**Causa:** Emojis o caracteres especiales no soportados

**Solución:**
La función `toASCII()` ya convierte tildes a ASCII. Si persiste el problema, verificar encoding del bot de Telegram:

```javascript
// En el header del HTTP Request
"Content-Type": "application/json; charset=utf-8"
```

---

## 📊 Consultas SQL Útiles

### Ver últimos leads con propiedades

```sql
SELECT
  id,
  nombre,
  telefono,
  session_id,
  propiedades_ids,
  array_length(propiedades_ids, 1) as cantidad_propiedades,
  timestamp
FROM conversion_logs
WHERE propiedades_ids IS NOT NULL
ORDER BY timestamp DESC
LIMIT 10;
```

### Propiedades más solicitadas en leads

```sql
SELECT
  UNNEST(propiedades_ids) as propiedad_id,
  COUNT(*) as veces_solicitada
FROM conversion_logs
WHERE propiedades_ids IS NOT NULL
GROUP BY propiedad_id
ORDER BY veces_solicitada DESC
LIMIT 10;
```

### Leads sin información de propiedades

```sql
SELECT
  id,
  nombre,
  telefono,
  session_id,
  timestamp
FROM conversion_logs
WHERE propiedades_ids IS NULL
  OR array_length(propiedades_ids, 1) = 0
  OR array_length(propiedades_ids, 1) IS NULL
ORDER BY timestamp DESC;
```

### Vincular lead con su historial de chat

```sql
SELECT
  cl.nombre,
  cl.telefono,
  cl.propiedades_ids as propiedades_solicitadas,
  c.consulta,
  c.propiedades_mostradas,
  c.timestamp as fecha_consulta
FROM conversion_logs cl
INNER JOIN chat_logs c ON cl.session_id = c.session_id
WHERE cl.id = 123  -- Cambiar por el ID del lead
ORDER BY c.timestamp DESC;
```

---

## 🚀 Próximos Pasos

Una vez que el workflow v2 esté funcionando:

1. **Monitorear primeros leads** con información de propiedades
2. **Verificar que Cristian recibe la info correctamente** en Telegram
3. **Ajustar formato del mensaje** según feedback
4. **Considerar agregar:**
   - Link directo a las propiedades en el mensaje
   - Información resumida de cada propiedad (precio, barrio)
   - Notificación push en app móvil
   - Dashboard de leads con propiedades más solicitadas

---

## 📌 Notas Importantes

- **Webhook URL:** Debe ser la misma que usa el widget (`/contact`)
- **Session ID:** Es crítico que el widget envíe este campo correctamente
- **Compatibilidad:** El workflow v2 es compatible con v1 (si no hay session_id, funciona igual)
- **Performance:** La query de propiedades es muy rápida (índice en session_id)
- **Telegram Bot Token:** Ya configurado en el workflow (mismo que v1)

---

## 🔄 Rollback a v1

Si necesitas volver a la versión anterior:

1. Desactivar workflow v2
2. Activar workflow v1
3. No es necesario revertir cambios en la base de datos (las columnas nuevas no afectan v1)

---

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5
**Estado:** ✅ Listo para testear
