# 🏢 Implementación Multi-Repo (Multi-Tenancy)

**Fecha:** 28 de Diciembre 2025
**Objetivo:** Separar datos y notificaciones por cliente/inmobiliaria

---

## 🎯 Problema a Resolver

Cuando el MVP salga a producción en la web de BBR, necesitamos:
1. ✅ Que las notificaciones de **DEMO** vayan a Damian
2. ✅ Que las notificaciones de **BBR** vayan a Cristian
3. ✅ Que las estadísticas sean **independientes** por cliente
4. ✅ Que ambos catálogos funcionen en paralelo

---

## 📋 Solución Implementada

### Campo `repo` Identifica al Cliente

Cada request lleva un campo `repo` que identifica de qué catálogo/cliente viene:
- `demo` → Testing de Damian
- `bbr` → Producción de BBR Grupo Inmobiliario
- `produccion` → Alias de `bbr`

---

## 🗄️ 1. Cambios en Base de Datos

### Script SQL
📄 `Documentacion/alter_add_repo_field.sql`

```sql
-- Agregar columna repo a chat_logs
ALTER TABLE chat_logs
ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo';

-- Agregar columna repo a conversion_logs
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo';

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_chat_logs_repo ON chat_logs(repo);
CREATE INDEX IF NOT EXISTS idx_conversion_logs_repo ON conversion_logs(repo);
```

### Ejecución
```bash
psql -h tu-host -U tu-usuario -d tu-database -f Documentacion/alter_add_repo_field.sql
```

---

## 📱 2. Cambios en Widget React

### Archivo Modificado
📄 `widget-react/src/ChatWidget.jsx`

#### Envío en Chat (línea ~113)
```javascript
body: JSON.stringify({
  message: inputValue,
  sessionId: sessionId,
  timestamp: new Date().toISOString(),
  repo: repo  // ← Ya existía
})
```

#### Envío en Contact (línea ~232)
```javascript
body: JSON.stringify({
  nombre: contactFormData.nombre,
  telefono: contactFormData.telefono,
  disponibilidad: contactFormData.disponibilidad || 'No especificada',
  timestamp: new Date().toISOString(),
  sessionId: sessionId,
  repo: repo  // ← AGREGADO
})
```

### Configuración en HTML
```html
<script>
  window.INMOBOT_CONFIG = {
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    contactUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
    repo: 'demo'  // ← 'demo' o 'bbr'
  };
</script>
```

---

## 🔄 3. Cambios en Workflow Contact Telegram

### Archivo Modificado
📄 `Flujos N8N/N8N_InmoBot - Contact Telegram.json`

### Nodo: "Preparar Mensaje Telegram"

#### Agregado: Mapeo de Chat IDs
```javascript
const repo = body.repo || 'demo';

// Mapeo de repos a chat_ids de Telegram
const chatIdMap = {
  'demo': 7861411323,              // Telegram de Damian (testing)
  'bbr': 7861411323,               // ⚠️ CAMBIAR por chat_id de Cristian
  'produccion': 7861411323         // ⚠️ CAMBIAR por chat_id de Cristian
};

const chat_id = chatIdMap[repo] || 7861411323;
```

#### Cambiado: Chat ID Dinámico
```javascript
// ANTES (hardcoded)
const payload = JSON.stringify({
  chat_id: 7861411323,
  text: mensajeTelegram
});

// AHORA (dinámico)
const payload = JSON.stringify({
  chat_id: chat_id,
  text: mensajeTelegram
});
```

### Nodo: "Preparar Stats Leads"

#### Agregado: Campo repo
```javascript
const repo = String(body.repo || 'demo');

const query = `INSERT INTO conversion_logs (
  nombre,
  telefono,
  disponibilidad,
  source,
  session_id,
  propiedades_ids,
  repo  -- ← AGREGADO
) VALUES (
  ${escapeSql(nombre)},
  ${escapeSql(telefono)},
  ${escapeSql(disponibilidad)},
  ${escapeSql(source)},
  ${session_id ? escapeSql(session_id) : 'NULL'},
  ${propiedadesArray},
  ${escapeSql(repo)}  -- ← AGREGADO
)`;
```

---

## 🔄 4. Cambios en Workflows de Chat (TODO)

### Archivos a Modificar
- `Flujos N8N/N8N_InmoBot - Haiku.json`
- `Flujos N8N/N8N_InmoBot - Haiku + Sonnet.json`

### Cambio Necesario
En el nodo que inserta en `chat_logs`, agregar el campo `repo`:

```javascript
const repo = body.repo || 'demo';

// En el INSERT
INSERT INTO chat_logs (
  session_id,
  consulta,
  idioma,
  success,
  error_type,
  response_time_ms,
  tokens_haiku,
  tokens_sonnet,
  tokens_total,
  propiedades_mostradas,
  propiedades_ids,
  repo  -- ← AGREGAR
) VALUES (...)
```

---

## 📊 5. Estadísticas Separadas por Repo

### Workflow de Estadísticas
📄 `Flujos N8N/N8N_InmoBot - Estadisticas Email.json`

#### Modificación Necesaria
Agregar filtro `WHERE repo = 'bbr'` en todas las queries:

```sql
-- ANTES
SELECT COUNT(*) as total_consultas
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- AHORA (solo BBR)
SELECT COUNT(*) as total_consultas
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
  AND repo = 'bbr';  -- ← AGREGAR
```

#### Opción: Estadísticas por Email Dinámicas

Crear **dos workflows separados**:
1. `Estadisticas Email - DEMO` → repo='demo', email a Damian
2. `Estadisticas Email - BBR` → repo='bbr', email a Cristian

O usar un solo workflow con parámetros.

---

## 🧪 Testing

### 1. Test DEMO (a Telegram de Damian)
```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Demo",
    "telefono": "+54 9 11 1111-1111",
    "disponibilidad": "Lunes 10-12hs",
    "sessionId": "test_demo_123",
    "repo": "demo"
  }'
```

**Resultado esperado:**
- ✅ Mensaje llega a Telegram de Damian (7861411323)
- ✅ Se guarda en `conversion_logs` con `repo='demo'`

### 2. Test BBR (a Telegram de Cristian)
```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test BBR",
    "telefono": "+54 9 11 2222-2222",
    "disponibilidad": "Martes 14-18hs",
    "sessionId": "test_bbr_456",
    "repo": "bbr"
  }'
```

**Resultado esperado:**
- ✅ Mensaje llega a Telegram de Cristian (chat_id pendiente)
- ✅ Se guarda en `conversion_logs` con `repo='bbr'`

### 3. Verificar en Base de Datos
```sql
-- Ver leads por repo
SELECT repo, COUNT(*) as total
FROM conversion_logs
GROUP BY repo;

-- Ver chats por repo
SELECT repo, COUNT(*) as total
FROM chat_logs
GROUP BY repo;
```

---

## 📝 Checklist de Implementación

### ✅ Completado
- [x] Script SQL para agregar columna `repo`
- [x] Widget envía `repo` en contact
- [x] Workflow Contact Telegram usa `repo` para chat_id
- [x] Workflow Contact Telegram guarda `repo` en BD
- [x] Documentación de Chat IDs

### ⏳ Pendiente
- [ ] Ejecutar script SQL en PostgreSQL producción
- [ ] Obtener chat_id de Cristian
- [ ] Actualizar workflow con chat_id real de Cristian
- [ ] Modificar workflows de Chat (Haiku/Sonnet) para guardar `repo`
- [ ] Modificar workflow de Estadísticas para filtrar por `repo`
- [ ] Crear workflow de estadísticas específico para BBR
- [ ] Testear con ambos repos
- [ ] Deploy de widget actualizado en Vercel

---

## 🎨 Configuración por Cliente

### DEMO (Testing de Damian)
```html
<script>
  window.INMOBOT_CONFIG = {
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    contactUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
    repo: 'demo'
  };
</script>
<script src="https://inmobot-widget.vercel.app/chatbot-widget.umd.js"></script>
```

### BBR (Producción)
```html
<script>
  window.INMOBOT_CONFIG = {
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    contactUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
    repo: 'bbr'
  };
</script>
<script src="https://inmobot-widget.vercel.app/chatbot-widget.umd.js"></script>
```

---

## 📊 Queries Útiles

### Estadísticas Solo de BBR
```sql
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as exitosas,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms,
  SUM(tokens_total) as tokens_totales
FROM chat_logs
WHERE repo = 'bbr'
  AND timestamp >= NOW() - INTERVAL '7 days';
```

### Comparación DEMO vs BBR
```sql
SELECT
  repo,
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as exitosas,
  ROUND(100.0 * SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito_pct,
  SUM(tokens_total) as tokens_totales
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY repo
ORDER BY total_consultas DESC;
```

### Leads por Repo
```sql
SELECT
  repo,
  COUNT(*) as total_leads,
  COUNT(DISTINCT DATE(timestamp)) as dias_activos
FROM conversion_logs
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY repo;
```

---

## 🚀 Próximos Pasos

1. **Ejecutar script SQL** en producción
2. **Obtener chat_id de Cristian** ([ver guía](./CONFIG_TELEGRAM_CHAT_IDS.md))
3. **Actualizar workflows de Chat** con campo `repo`
4. **Crear workflows de estadísticas separados** por repo
5. **Testear exhaustivamente** antes del deploy
6. **Documentar proceso de onboarding** para nuevos clientes

---

## 📚 Referencias

- [alter_add_repo_field.sql](./alter_add_repo_field.sql) - Script de migración
- [CONFIG_TELEGRAM_CHAT_IDS.md](./CONFIG_TELEGRAM_CHAT_IDS.md) - Configuración de Telegram
- [WORKFLOWS_ACTIVOS.md](./WORKFLOWS_ACTIVOS.md) - Estado de workflows

---

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5
**Estado:** 🟡 Implementación parcial (falta ejecutar SQL y obtener chat_id de Cristian)
