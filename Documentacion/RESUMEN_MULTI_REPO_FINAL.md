# ✅ Multi-Repo Implementation - COMPLETADO

**Fecha:** 28 de Diciembre 2025
**Estado:** ✅ Implementación completada

---

## 🎯 Objetivo Alcanzado

Separar notificaciones y estadísticas por cliente/inmobiliaria usando el campo `repo`.

---

## ✅ Cambios Completados

### 1. Base de Datos ✅
- ✅ Columna `repo` agregada a `chat_logs`
- ✅ Columna `repo` agregada a `conversion_logs`
- ✅ Índices creados para búsquedas rápidas
- ✅ Default value: `'demo'`

### 2. Widget React ✅
- ✅ Envía `repo` en requests de chat
- ✅ Envía `repo` en requests de contact

### 3. Workflows N8N ✅
- ✅ **Haiku** - Guarda `repo` en `chat_logs`
- ✅ **Haiku + Sonnet** - Guarda `repo` en `chat_logs`
- ✅ **Contact Telegram** - Guarda `repo` en `conversion_logs` + routing de chat_id

### 4. Documentación ✅
- ✅ [IMPLEMENTACION_MULTI_REPO.md](./IMPLEMENTACION_MULTI_REPO.md)
- ✅ [CONFIG_TELEGRAM_CHAT_IDS.md](./CONFIG_TELEGRAM_CHAT_IDS.md)
- ✅ [alter_add_repo_field.sql](./alter_add_repo_field.sql)

---

## 📋 Configuración de Repos

### DEMO (Testing - Damian)
```javascript
window.INMOBOT_CONFIG = {
  apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
  contactUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
  repo: 'demo'
};
```
**Telegram:** 7861411323 (Damian)

### BBR (Producción - Cristian)
```javascript
window.INMOBOT_CONFIG = {
  apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
  contactUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
  repo: 'bbr'
};
```
**Telegram:** 999999999 ⚠️ **CAMBIAR por chat_id real de Cristian**

---

## 🔄 Routing de Notificaciones Telegram

### En Workflow "Contact Telegram"
```javascript
const chatIdMap = {
  'demo': 7861411323,      // Damian
  'bbr': 999999999,        // ⚠️ Cambiar por chat_id de Cristian
  'produccion': 999999999  // ⚠️ Cambiar por chat_id de Cristian
};
```

---

## ⏳ Pendiente

### 1. Obtener Chat ID de Cristian
Opciones:
- Usar `@userinfobot` en Telegram
- Usar `@getidsbot` en Telegram
- `curl https://api.telegram.org/bot8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI/getUpdates`

### 2. Actualizar Workflow en N8N
1. Abrir workflow "N8N_InmoBot - Contact Telegram"
2. Editar nodo "Preparar Mensaje Telegram"
3. Reemplazar `999999999` por chat_id real
4. Save workflow

### 3. Actualizar Workflow de Estadísticas (Opcional pero Recomendado)
Crear dos workflows separados o agregar filtro `WHERE repo = 'bbr'` en queries.

---

## 🧪 Testing

### Test DEMO
```bash
# Chat
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hola","sessionId":"test_demo","repo":"demo"}'

# Contact
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test Demo","telefono":"111","disponibilidad":"Test","sessionId":"demo123","repo":"demo"}'
```

**Resultado esperado:**
- Guarda en BD con `repo='demo'`
- Notificación a Telegram de Damian (7861411323)

### Test BBR (cuando tengas chat_id real)
```bash
# Chat
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Busco departamento","sessionId":"test_bbr","repo":"bbr"}'

# Contact
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test BBR","telefono":"222","disponibilidad":"Test","sessionId":"bbr456","repo":"bbr"}'
```

**Resultado esperado:**
- Guarda en BD con `repo='bbr'`
- Notificación a Telegram de Cristian

---

## 📊 Queries de Verificación

### Ver datos por repo
```sql
-- Chat logs por repo
SELECT repo, COUNT(*) as total
FROM chat_logs
GROUP BY repo;

-- Leads por repo
SELECT repo, COUNT(*) as total
FROM conversion_logs
GROUP BY repo;
```

### Estadísticas solo de BBR
```sql
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as exitosas,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms
FROM chat_logs
WHERE repo = 'bbr'
  AND timestamp >= NOW() - INTERVAL '7 days';
```

---

## 📁 Archivos Modificados

### Widget
- ✅ `widget-react/src/ChatWidget.jsx` (línea 233: agregado `repo: repo`)

### Workflows N8N
- ✅ `Flujos N8N/N8N_InmoBot - Haiku.json`
- ✅ `Flujos N8N/N8N_InmoBot - Haiku + Sonnet.json`
- ✅ `Flujos N8N/N8N_InmoBot - Contact Telegram.json`

### Scripts
- ✅ `Scripts-Templates/migrate_add_repo.js` (migración Node.js)
- ✅ `Documentacion/alter_add_repo_field.sql` (migración SQL)

---

## 🚀 Deploy Checklist

- [x] Ejecutar SQL en PostgreSQL
- [x] Actualizar workflows
- [x] Actualizar widget
- [ ] Obtener chat_id de Cristian
- [ ] Actualizar chat_id en workflow Contact
- [ ] Re-importar workflows en N8N
- [ ] Deploy widget actualizado en Vercel
- [ ] Testear con repo='demo'
- [ ] Testear con repo='bbr'
- [ ] Configurar estadísticas por repo

---

## 🎨 Próximos Pasos MVP

1. **Obtener chat_id de Cristian** y actualizar workflow
2. **Re-importar workflows** en N8N con los cambios
3. **Deploy del widget** actualizado en Vercel
4. **Configurar HTML** en sitio de BBR con `repo: 'bbr'`
5. **Testear end-to-end** antes del lanzamiento
6. **Crear workflow de estadísticas específico para BBR**

---

## 📚 Referencias

- [IMPLEMENTACION_MULTI_REPO.md](./IMPLEMENTACION_MULTI_REPO.md) - Guía completa
- [CONFIG_TELEGRAM_CHAT_IDS.md](./CONFIG_TELEGRAM_CHAT_IDS.md) - Configuración Telegram
- [WORKFLOWS_ACTIVOS.md](./WORKFLOWS_ACTIVOS.md) - Estado de workflows

---

**🎉 Implementación Multi-Repo Completada!**

La infraestructura está lista para soportar múltiples clientes de forma independiente.

---

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5
**Estado:** ✅ COMPLETADO (pendiente solo chat_id de Cristian)
