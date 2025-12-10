# 📱 Configuración de Telegram en N8N - InmoBot

Guía paso a paso para agregar el sistema de notificaciones por Telegram al workflow de N8N.

---

## 🎯 Objetivo

Cuando un usuario completa el formulario "Agendar una visita" en el widget, se enviará una notificación automática a tu Telegram con los datos del contacto.

---

## 📋 Datos que ya tenemos

✅ **Bot Token:** `8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI`
✅ **Chat ID:** `7861411323`
✅ **Bot Username:** `@inmobot_contactos_bot`

---

## 🔧 PASO 1: Abrir tu workflow en N8N

1. Andá a: https://n8n-bot-inmobiliario.onrender.com
2. Abrí el workflow: **"Bot Inmobiliaria - Haiku + Sonnet (FINAL)"**

---

## ➕ PASO 2: Agregar los nodos

Vas a agregar 4 nodos nuevos que funcionarán en paralelo al flujo de chat principal.

### 🔹 NODO 1: Webhook Contact

**Tipo:** Webhook

**Configuración:**
- **HTTP Method:** POST
- **Path:** `contact`
- **Response Mode:** "Using 'Respond to Webhook' Node"

**Posición:** Debajo del "Webhook Chat" (en paralelo, NO conectado)

---

### 🔹 NODO 2: Preparar Mensaje Telegram

**Tipo:** Code (JavaScript)

**Configuración:**

Copiá este código completo en el nodo:

```javascript
const webhookData = $input.first().json;
const body = webhookData.body || webhookData;

// Extraer datos del formulario
const nombre = body.nombre || 'No especificado';
const telefono = body.telefono || 'No especificado';
const disponibilidad = body.disponibilidad || 'No especificada';
const timestamp = body.timestamp || new Date().toISOString();
const sessionId = body.sessionId || 'unknown';

// Formatear fecha
const fecha = new Date(timestamp);
const fechaFormateada = fecha.toLocaleString('es-AR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
});

// Construir mensaje para Telegram con formato MarkdownV2
const mensajeTelegram = `🏠 *NUEVA SOLICITUD DE VISITA*

👤 *Nombre:*
${nombre}

📱 *Teléfono:*
${telefono}

🕐 *Disponibilidad:*
${disponibilidad}

📅 *Fecha:* ${fechaFormateada}
🔑 *Session:* \`${sessionId}\`

_Mensaje enviado automáticamente por InmoBot_`;

return {
  json: {
    chatId: '7861411323',
    mensaje: mensajeTelegram,
    nombre: nombre,
    telefono: telefono,
    disponibilidad: disponibilidad,
    timestamp: timestamp
  }
};
```

---

### 🔹 NODO 3: Enviar Mensaje Telegram

**Tipo:** HTTP Request

**Configuración:**

- **Method:** POST
- **URL:** `https://api.telegram.org/bot8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI/sendMessage`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "chat_id": "={{ $json.chatId }}",
  "text": "={{ $json.mensaje }}",
  "parse_mode": "Markdown"
}
```

**Nota:** Asegurate de que "Send Body" esté en **ON** y "Body Content Type" en **JSON**

---

### 🔹 NODO 4: Responder al Webhook

**Tipo:** Respond to Webhook

**Configuración:**

- **Respond With:** JSON
- **Response Body:**
```json
{
  "success": true,
  "message": "¡Perfecto! Recibimos tu solicitud. Te contactaremos a la brevedad para coordinar la visita."
}
```

---

## 🔗 PASO 3: Conectar los nodos

Conectá los nodos en este orden:

```
Webhook Contact → Preparar Mensaje Telegram → Enviar Mensaje Telegram → Responder al Webhook
```

---

## ✅ PASO 4: Activar el workflow

1. Click en **"Save"** arriba a la derecha
2. Asegurate de que el switch esté en **"Active"**

---

## 🧪 PASO 5: Probar el flujo

### 5.1 Probar desde el widget local

1. Abrí el widget en tu navegador: `http://localhost:3001/demo.html`
2. Hacé una consulta (ej: "Busco depto 2 ambientes")
3. Cuando aparezcan las propiedades, click en **"✅ Agendar una visita"**
4. Completá el formulario:
   - **Nombre:** Damián Test
   - **Teléfono:** 011 1234-5678
   - **Disponibilidad:** Lunes a viernes 14-18hs
5. Click en **"Enviar solicitud"**

### 5.2 Verificar en Telegram

Deberías recibir un mensaje en tu Telegram como este:

```
🏠 NUEVA SOLICITUD DE VISITA

👤 Nombre:
Damián Test

📱 Teléfono:
011 1234-5678

🕐 Disponibilidad:
Lunes a viernes 14-18hs

📅 Fecha: 02/12/2024 20:15
🔑 Session: session-1733170500000-abc123

Mensaje enviado automáticamente por InmoBot
```

---

## 🔍 TROUBLESHOOTING

### ❌ Error: "Unauthorized"

**Problema:** El token del bot es incorrecto.

**Solución:**
1. Revisá que el token en el nodo "Enviar Mensaje Telegram" sea exactamente:
   `8082846550:AAEYYII1ci7-F9ncENysrMKeoubqcdcwMnI`
2. No debe tener espacios ni saltos de línea

### ❌ Error: "Chat not found"

**Problema:** El chat ID es incorrecto.

**Solución:**
1. Verificá que el chat ID en el nodo "Preparar Mensaje Telegram" sea:
   `7861411323`
2. Sin comillas extras ni espacios

### ❌ No llega el mensaje a Telegram

**Problema:** El bot no está iniciado o el webhook está durmiendo.

**Solución:**
1. Enviá `/start` a `@inmobot_contactos_bot` en Telegram
2. Verificá que el workflow esté **Active** en N8N
3. Hacé un ping manual al webhook desde Postman

### ❌ Widget muestra error al enviar

**Problema:** La URL del webhook no es correcta.

**Solución:**
1. Verificá que el `contactUrl` en el widget sea:
   `https://n8n-bot-inmobiliario.onrender.com/webhook/contact`
2. Si Render estaba dormido, esperá 1-2 minutos

---

## 📊 Diagrama del flujo completo

```
┌─────────────────────┐
│   Widget React      │
└──────────┬──────────┘
           │
           ├──── Consultas ────▶ /webhook/chat
           │                     ↓
           │                  Haiku → Sonnet → Respuesta
           │
           └──── Formulario ──▶ /webhook/contact
                                ↓
                             Preparar Mensaje
                                ↓
                          Enviar a Telegram
                                ↓
                           Responder Webhook
```

---

## 🔐 Seguridad

**IMPORTANTE:** El token del bot es sensible. Cuando pases a producción:

1. **NO compartas** el token públicamente
2. Considerá usar variables de entorno en N8N
3. Si el token se expone, revocalo desde BotFather con `/revoke`

---

## 🚀 Próximos pasos

Una vez que todo funcione:

1. ✅ Probá el flujo completo varias veces
2. ✅ Verificá que los mensajes lleguen correctamente
3. ✅ Cuando esté todo OK, desplegá el widget a producción
4. ✅ Compartí la URL del widget con Cristian

---

## 📝 Notas importantes

- **Keep-alive:** El workflow de GitHub Actions mantiene activo ambos webhooks (/chat y /contact)
- **Logs:** Podés ver todos los envíos en la sección "Executions" de N8N
- **Rate limits:** Telegram tiene límite de ~30 mensajes/segundo (más que suficiente)
- **Formato:** Usamos Markdown para formato del mensaje (negritas, código, etc.)

---

**Última actualización:** 2 de Diciembre 2024
**Bot:** @inmobot_contactos_bot
**Chat ID:** 7861411323
