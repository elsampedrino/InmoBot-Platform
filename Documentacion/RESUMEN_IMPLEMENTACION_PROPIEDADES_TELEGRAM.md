# ✅ Implementación Completada: Propiedades en Notificaciones Telegram

**Fecha:** 28 de Diciembre 2025
**Estado:** ✅ Listo para instalar y testear

---

## 🎯 Problema Resuelto

**Antes:** El mensaje de Telegram solo mostraba nombre, teléfono y disponibilidad del cliente.

**Ahora:** El mensaje incluye las propiedades que el cliente vio antes de solicitar contacto.

---

## 📦 Archivos Creados

### 1. Workflow v2
📄 `Flujos N8N/N8N_InmoBot - Contact Telegram v2.json`

**Novedades:**
- ✅ Consulta automática de propiedades vistas por session_id
- ✅ Mensaje de Telegram enriquecido con lista de propiedades
- ✅ Incluye consulta original del cliente
- ✅ Compatibilidad con `sessionId` (camelCase) y `session_id` (snake_case)

### 2. Script SQL de Migración
📄 `Documentacion/alter_conversion_logs_add_propiedades.sql`

**Qué hace:**
- Agrega columna `session_id` a `conversion_logs`
- Agrega columna `propiedades_ids` (array) a `conversion_logs`
- Crea índice para búsquedas rápidas por session_id

### 3. Documentación Completa
📄 `Documentacion/WORKFLOW_CONTACT_TELEGRAM_V2.md`

**Contenido:**
- Guía paso a paso de instalación
- Troubleshooting completo
- Queries SQL útiles
- Ejemplos de mensajes Telegram

### 4. Este Resumen
📄 `Documentacion/RESUMEN_IMPLEMENTACION_PROPIEDADES_TELEGRAM.md`

---

## 🚀 Pasos para Instalar

### Paso 1: Actualizar Base de Datos (PostgreSQL)

Ejecutar este comando desde tu terminal o cliente SQL:

```bash
psql -h tu-host -U tu-usuario -d tu-database -f Documentacion/alter_conversion_logs_add_propiedades.sql
```

O ejecutar manualmente:

```sql
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS propiedades_ids TEXT[];

CREATE INDEX IF NOT EXISTS idx_conversion_logs_session_id
ON conversion_logs(session_id);
```

**Verificar:**
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'conversion_logs'
ORDER BY ordinal_position;
```

---

### Paso 2: Importar Workflow v2 en N8N

1. Abrir N8N en el navegador
2. **Workflows** → **Import from File**
3. Seleccionar: `Flujos N8N/N8N_InmoBot - Contact Telegram v2.json`
4. Se importará con el nombre: **"N8N_InmoBot - Contact Telegram v2"**

---

### Paso 3: Verificar Credenciales en N8N

El workflow usa la credencial PostgreSQL: `Cas8eHe2cYh3vHyG`

**Verificar en estos nodos:**
- ✅ "Consultar Propiedades Vistas"
- ✅ "Execute Insert Leads"

Si la credencial no existe o es diferente:
1. Click en cada nodo
2. Seleccionar tu credencial PostgreSQL
3. Save

---

### Paso 4: Probar el Workflow

**Test Manual con Postman/cURL:**

```bash
curl -X POST https://tu-n8n.render.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Test",
    "telefono": "+54 9 11 1234-5678",
    "disponibilidad": "Lunes 14-18hs",
    "sessionId": "test_session_abc123",
    "timestamp": "2025-12-28T15:30:00Z"
  }'
```

**IMPORTANTE:** Antes de testear, asegúrate de tener datos de prueba en `chat_logs`:

```sql
-- Verificar que existe la sesión de prueba
SELECT session_id, propiedades_ids, propiedades_mostradas, consulta
FROM chat_logs
WHERE session_id = 'test_session_abc123';

-- Si no existe, insertar datos de prueba
INSERT INTO chat_logs (
  session_id, consulta, idioma, success, response_time_ms,
  tokens_haiku, tokens_sonnet, tokens_total,
  propiedades_mostradas, propiedades_ids
) VALUES (
  'test_session_abc123',
  'Busco depto 2 ambientes en Palermo',
  'es',
  1,
  5000,
  1200,
  800,
  2000,
  3,
  ARRAY['PROP-001', 'PROP-005', 'PROP-012']::TEXT[]
);
```

---

### Paso 5: Desactivar v1 y Activar v2

**MUY IMPORTANTE:** Solo uno debe estar activo para evitar notificaciones duplicadas.

1. Ir a workflow **"N8N_InmoBot - Contact Telegram"** (v1)
2. Toggle **Active** → **OFF**
3. Ir a workflow **"N8N_InmoBot - Contact Telegram v2"**
4. Toggle **Active** → **ON**

---

## 📧 Ejemplo de Mensaje Telegram (Nuevo Formato)

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

---

## 🔧 Diferencias Técnicas: v1 vs v2

| Característica | v1 | v2 |
|----------------|----|----|
| **Nodos totales** | 5 | 6 |
| **Query de propiedades** | ❌ No | ✅ Sí |
| **Session ID en mensaje** | ❌ No | ✅ Sí |
| **Lista de propiedades** | ❌ No | ✅ Sí |
| **Consulta original** | ❌ No | ✅ Sí (100 chars) |
| **DB: session_id** | ❌ No guarda | ✅ Guarda |
| **DB: propiedades_ids** | ❌ No guarda | ✅ Guarda (array) |

---

## 🛠️ Estructura del Workflow v2

```
┌─────────────────────┐
│  Webhook Contact    │ (recibe POST /contact)
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────────┐ ┌──────────────────────┐
│ Preparar    │ │ Consultar Propiedades│ (PostgreSQL)
│ Stats Leads │ │ Vistas               │
└──────┬──────┘ └──────────┬───────────┘
       │                   │
       ▼                   ▼
┌─────────────┐ ┌──────────────────────┐
│ Execute     │ │ Preparar Mensaje     │ (JS Code)
│ Insert Leads│ │ Telegram             │
└──────┬──────┘ └──────────┬───────────┘
       │                   │
       │                   ▼
       │        ┌──────────────────────┐
       │        │ Enviar Mensaje       │ (HTTP Request)
       │        │ Telegram             │
       │        └──────────┬───────────┘
       │                   │
       └───────────┬───────┘
                   ▼
       ┌──────────────────────┐
       │ Responder al Webhook │
       │ Contact              │
       └──────────────────────┘
```

---

## ✅ Checklist de Instalación

Marcar cuando completes cada paso:

- [ ] Ejecutar script SQL en PostgreSQL
- [ ] Verificar que las columnas se crearon correctamente
- [ ] Importar workflow v2 en N8N
- [ ] Verificar credenciales PostgreSQL en ambos nodos
- [ ] Insertar datos de prueba en `chat_logs`
- [ ] Probar con cURL/Postman
- [ ] Verificar que llegó mensaje a Telegram con propiedades
- [ ] Desactivar workflow v1
- [ ] Activar workflow v2
- [ ] Probar desde el widget en producción

---

## 🔍 Verificación Rápida

### ¿Funcionó correctamente?

Ejecutar esta query después de un test:

```sql
-- Ver el último lead registrado
SELECT
  id,
  nombre,
  telefono,
  session_id,
  propiedades_ids,
  array_length(propiedades_ids, 1) as cantidad_propiedades,
  timestamp
FROM conversion_logs
ORDER BY timestamp DESC
LIMIT 1;
```

**Resultado esperado:**
- `session_id` debe tener el valor enviado desde el widget
- `propiedades_ids` debe ser un array con los IDs (ej: `{PROP-001,PROP-005,PROP-012}`)
- `cantidad_propiedades` debe coincidir con el número de elementos

---

## 📊 Queries Útiles Post-Instalación

### Ver propiedades más solicitadas

```sql
SELECT
  UNNEST(propiedades_ids) as propiedad_id,
  COUNT(*) as veces_solicitada
FROM conversion_logs
WHERE propiedades_ids IS NOT NULL
  AND timestamp >= NOW() - INTERVAL '30 days'
GROUP BY propiedad_id
ORDER BY veces_solicitada DESC
LIMIT 10;
```

### Ver leads con su historial de chat

```sql
SELECT
  cl.nombre,
  cl.telefono,
  cl.timestamp as fecha_contacto,
  cl.propiedades_ids as propiedades_solicitadas,
  c.consulta,
  c.propiedades_mostradas
FROM conversion_logs cl
INNER JOIN chat_logs c ON cl.session_id = c.session_id
WHERE cl.timestamp >= NOW() - INTERVAL '7 days'
ORDER BY cl.timestamp DESC;
```

---

## 🚨 Troubleshooting Rápido

### Problema: "No se registraron propiedades vistas en esta sesión"

**Causas posibles:**
1. El `sessionId` no se está enviando desde el widget
2. No hay registros en `chat_logs` con ese `sessionId`
3. El campo `propiedades_ids` está vacío o NULL

**Verificar:**
```sql
SELECT session_id, propiedades_ids, propiedades_mostradas
FROM chat_logs
WHERE session_id = 'el_session_id_del_test'
ORDER BY timestamp DESC;
```

---

### Problema: Error al insertar en conversion_logs

**Error típico:** `column "session_id" does not exist`

**Solución:**
```sql
-- Verificar que las columnas existan
\d conversion_logs

-- Si no existen, ejecutar:
ALTER TABLE conversion_logs ADD COLUMN session_id VARCHAR(255);
ALTER TABLE conversion_logs ADD COLUMN propiedades_ids TEXT[];
```

---

## 📌 Notas Finales

- **Widget ya envía sessionId:** No necesitas modificar el widget, ya envía el campo `sessionId` correctamente
- **Compatibilidad:** El workflow v2 soporta tanto `sessionId` como `session_id`
- **Rollback:** Si algo falla, simplemente desactiva v2 y reactiva v1
- **Base de datos:** Las columnas nuevas no afectan el funcionamiento de v1
- **Testing:** Usa datos reales de `chat_logs` para mejores pruebas

---

## 📚 Documentación Relacionada

- [Documentación completa del workflow](./WORKFLOW_CONTACT_TELEGRAM_V2.md)
- [Script SQL de migración](./alter_conversion_logs_add_propiedades.sql)
- [Workflow v2 JSON](../Flujos%20N8N/N8N_InmoBot%20-%20Contact%20Telegram%20v2.json)

---

**¡Listo para implementar!** 🚀

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5
