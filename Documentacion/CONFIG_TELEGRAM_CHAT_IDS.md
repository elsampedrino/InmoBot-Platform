# 📱 Configuración de Chat IDs de Telegram

## 🎯 Mapeo de Repos a Telegram

Actualmente el workflow está configurado con estos chat_ids:

```javascript
const chatIdMap = {
  'demo': 7861411323,              // Telegram de Damian (testing)
  'bbr': 7861411323,               // ⚠️ CAMBIAR por Telegram de Cristian
  'produccion': 7861411323         // ⚠️ CAMBIAR por Telegram de Cristian
};
```

---

## 📋 Cómo Obtener el Chat ID de Cristian

### Opción 1: Usando el Bot de Telegram (Recomendada)

1. **Cristian debe hablar con el bot**:
   - Abrir Telegram
   - Buscar el bot: `@inmobot_bot` (o el nombre que le hayas puesto)
   - Enviar cualquier mensaje (ej: "Hola")

2. **Obtener el Chat ID**:
   ```bash
   curl https://api.telegram.org/bot8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI/getUpdates
   ```

3. **Buscar en la respuesta**:
   ```json
   {
     "result": [{
       "message": {
         "chat": {
           "id": 123456789,  // ← Este es el chat_id de Cristian
           "first_name": "Cristian",
           "username": "cristian_bbr"
         }
       }
     }]
   }
   ```

### Opción 2: Usando @userinfobot

1. Cristian debe buscar en Telegram: `@userinfobot`
2. Enviar `/start`
3. El bot responderá con su chat ID

### Opción 3: Usando @getidsbot

1. Cristian debe buscar en Telegram: `@getidsbot`
2. Enviar `/start`
3. El bot mostrará su ID

---

## 🔧 Actualizar el Workflow

Una vez que tengas el chat_id de Cristian:

1. Abrir N8N
2. Ir al workflow **"N8N_InmoBot - Contact Telegram"**
3. Editar el nodo **"Preparar Mensaje Telegram"**
4. Buscar esta sección:

```javascript
// Mapeo de repos a chat_ids de Telegram
const chatIdMap = {
  'demo': 7861411323,              // Telegram de Damian (testing)
  'bbr': AQUI_EL_CHAT_ID,          // ← Reemplazar
  'produccion': AQUI_EL_CHAT_ID    // ← Reemplazar
};
```

5. Reemplazar `AQUI_EL_CHAT_ID` con el número real
6. Save el workflow

---

## 📝 Ejemplo Completo

Si el chat_id de Cristian es `987654321`, quedaría así:

```javascript
const chatIdMap = {
  'demo': 7861411323,       // Telegram de Damian (testing)
  'bbr': 987654321,         // Telegram de Cristian
  'produccion': 987654321   // Telegram de Cristian (producción)
};
```

---

## ✅ Verificar que Funciona

### Test con DEMO (a tu Telegram):
```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test Demo",
    "telefono": "+54 9 11 1111-1111",
    "disponibilidad": "Test",
    "sessionId": "test123",
    "repo": "demo"
  }'
```
**Resultado esperado:** Mensaje llega a tu Telegram (7861411323)

### Test con BBR (a Telegram de Cristian):
```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/contact \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test BBR",
    "telefono": "+54 9 11 2222-2222",
    "disponibilidad": "Test",
    "sessionId": "test456",
    "repo": "bbr"
  }'
```
**Resultado esperado:** Mensaje llega al Telegram de Cristian

---

## 🔐 Notas de Seguridad

- **No commitear** chat_ids reales en el repo público
- Los chat_ids solo funcionan con ese bot específico
- Si cambiás de bot, los chat_ids cambiarán

---

## 📊 Repos Disponibles

| Repo | Descripción | Chat ID | Widget |
|------|-------------|---------|--------|
| `demo` | Testing de Damian | 7861411323 | `repo: 'demo'` |
| `bbr` | Producción BBR Grupo | ⚠️ Completar | `repo: 'bbr'` |
| `produccion` | Alias de bbr | ⚠️ Completar | `repo: 'produccion'` |

---

**Última actualización:** 28 de Diciembre 2025
**Bot Token:** `8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI`
