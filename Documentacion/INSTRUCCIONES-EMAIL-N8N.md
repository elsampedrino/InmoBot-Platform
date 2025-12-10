# 📧 Configuración de Email en N8N - InmoBot

Guía paso a paso para agregar el sistema de envío de emails al workflow de N8N.

---

## 🎯 Objetivo

Cuando un usuario completa el formulario "Agendar una visita" en el widget, se enviará un email automático con los datos del contacto.

---

## 📋 Requisitos previos

- [ ] Workflow de N8N funcionando en Render
- [ ] Widget React actualizado (ya lo tenés)
- [ ] Cuenta de Gmail para envío de emails
- [ ] Contraseña de aplicación de Google

---

## 🔑 PASO 1: Obtener contraseña de aplicación de Google

### 1.1 Ir a tu cuenta de Google

Abrí este link: https://myaccount.google.com/apppasswords

### 1.2 Crear contraseña de aplicación

1. Si te pide autenticación de 2 pasos, activala primero
2. Seleccioná **"Correo"** como aplicación
3. Seleccioná **"Otro (nombre personalizado)"** como dispositivo
4. Escribí: **"N8N InmoBot"**
5. Click en **"Generar"**

### 1.3 Guardar la contraseña

**IMPORTANTE:** Copiá la contraseña de 16 caracteres que aparece. La vas a necesitar en el siguiente paso.

Ejemplo: `abcd efgh ijkl mnop`

---

## 🔧 PASO 2: Configurar credenciales SMTP en N8N

### 2.1 Abrir configuración de credenciales

1. Andá a tu N8N en Render: https://n8n-bot-inmobiliario.onrender.com
2. En el menú lateral, click en **"Credentials"**
3. Click en **"Add Credential"**

### 2.2 Crear credencial SMTP

1. Buscar y seleccionar **"SMTP"**
2. Completar los campos:

```
Name: Gmail SMTP InmoBot
User: elsampedrino@gmail.com
Password: [Pegá aquí la contraseña de aplicación que copiaste antes]
Host: smtp.gmail.com
Port: 587
Secure Connection: SSL/TLS ✓
```

3. Click en **"Save"**

---

## ➕ PASO 3: Agregar nodos al workflow

### 3.1 Abrir tu workflow

1. Ir a **"Workflows"** en N8N
2. Abrir el workflow **"Bot Inmobiliaria - Haiku + Sonnet (FINAL)"**

### 3.2 Agregar Nodo 1: Webhook Contact

1. Click en el botón **"+"** para agregar nodo
2. Buscar **"Webhook"**
3. Configurar:
   - HTTP Method: **POST**
   - Path: **contact**
   - Response Mode: **Using 'Respond to Webhook' Node**
4. Posicionarlo debajo del "Webhook Chat" (en paralelo, no conectado)

### 3.3 Agregar Nodo 2: Preparar Email

1. Click en el botón **"+"** después de "Webhook Contact"
2. Buscar **"Code"** y seleccionar
3. Abrir el archivo `nodos-contacto-n8n.js` de este proyecto
4. Copiar todo el código del **NODO 2: Preparar Email**
5. Pegarlo en el campo de código del nodo
6. Click en **"Execute Node"** para probar

### 3.4 Agregar Nodo 3: Enviar Email

1. Click en el botón **"+"** después de "Preparar Email"
2. Buscar **"Send Email"** y seleccionar
3. Configurar:
   - From Email: `={{ $json.destinatario }}`
   - To Email: `={{ $json.destinatario }}`
   - Subject: `={{ $json.asunto }}`
   - Email Type: **HTML**
   - Message: `={{ $json.cuerpoHTML }}`
4. En **"Credential to connect with"**:
   - Seleccionar **"Gmail SMTP InmoBot"** (la que creaste antes)
5. Click en **"Execute Node"** para probar

### 3.5 Agregar Nodo 4: Responder al Webhook

1. Click en el botón **"+"** después de "Enviar Email"
2. Buscar **"Respond to Webhook"**
3. Configurar:
   - Respond With: **JSON**
   - Response Body:
   ```json
   {
     "success": true,
     "message": "¡Perfecto! Recibimos tu solicitud. Te contactaremos a la brevedad para coordinar la visita."
   }
   ```

### 3.6 Conectar los nodos

Asegurate de que los nodos estén conectados en este orden:

```
Webhook Contact → Preparar Email → Enviar Email → Respond to Webhook
```

---

## ✅ PASO 4: Activar y probar

### 4.1 Activar el workflow

1. Click en **"Save"** arriba a la derecha
2. Mover el switch a **"Active"**

### 4.2 Verificar la URL del webhook

1. Click en el nodo **"Webhook Contact"**
2. Copiar la URL que aparece (debería ser algo como):
   ```
   https://n8n-bot-inmobiliario.onrender.com/webhook/contact
   ```
3. Verificá que coincida con la URL configurada en el widget

### 4.3 Probar el formulario

1. Abrir el widget en tu navegador: http://localhost:3001/demo.html
2. Hacer una consulta (ej: "Busco depto en Palermo")
3. Cuando aparezcan las propiedades, click en **"Agendar una visita"**
4. Completar el formulario con datos de prueba:
   - Nombre: Damián Test
   - Teléfono: 011 1234-5678
   - Disponibilidad: Lunes a viernes 14-18hs
5. Click en **"Enviar solicitud"**

### 4.4 Verificar el email

Revisá tu casilla **elsampedrino@gmail.com** y deberías ver un email con:
- Asunto: 🏠 Nueva solicitud de visita - Damián Test
- Cuerpo con todos los datos formateados

---

## 🔍 TROUBLESHOOTING

### ❌ Error: "Authentication failed"

**Problema:** La contraseña de aplicación no es correcta.

**Solución:**
1. Generar una nueva contraseña de aplicación en Google
2. Actualizar las credenciales SMTP en N8N

### ❌ Error: "Connection timeout"

**Problema:** El puerto SMTP está bloqueado.

**Solución:**
1. Cambiar el puerto a **465**
2. Verificar que "Secure Connection" esté en **SSL/TLS**

### ❌ No llega el email

**Problema:** El email puede estar en spam o el destinatario es incorrecto.

**Solución:**
1. Revisar la carpeta de spam
2. Verificar que el email en "Preparar Email" sea correcto
3. Revisar los logs del nodo "Enviar Email" en N8N

### ❌ Widget muestra error al enviar

**Problema:** La URL del webhook no es correcta o N8N está dormido.

**Solución:**
1. Verificar que el workflow esté **Active**
2. Hacer un ping manual al webhook desde Postman o curl
3. Esperar 1-2 minutos si Render estaba dormido

---

## 🚀 PASO 5: Pasar a producción (cuando esté listo)

### Cambiar email destinatario

1. Abrir el nodo **"Preparar Email"**
2. Buscar la línea:
   ```javascript
   destinatario: 'elsampedrino@gmail.com',
   ```
3. Reemplazar por el email de Cristian:
   ```javascript
   destinatario: 'cristian@inmobiliaria.com',
   ```
4. Guardar el workflow

### Opcional: Configurar email de Cristian como remitente

Si Cristian quiere enviar desde su propio email:

1. Crear nuevas credenciales SMTP con su cuenta de Gmail
2. Obtener contraseña de aplicación de su cuenta
3. Actualizar el nodo "Enviar Email" para usar esas credenciales

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
                             Preparar Email
                                ↓
                             Enviar Email
                                ↓
                           Responder Webhook
```

---

## 📝 Notas importantes

1. **Keep-alive:** El workflow de GitHub Actions también mantendrá activo el webhook de contacto
2. **Logs:** Podés ver todos los envíos en la sección "Executions" de N8N
3. **Rate limits:** Gmail tiene límite de ~500 emails/día en cuentas gratuitas
4. **Testing:** Siempre probá con tu email primero antes de pasarlo a producción

---

## ✅ Checklist final

- [ ] Contraseña de aplicación de Google obtenida
- [ ] Credenciales SMTP configuradas en N8N
- [ ] 4 nodos agregados al workflow
- [ ] Nodos conectados correctamente
- [ ] Workflow activado
- [ ] Prueba realizada con éxito
- [ ] Email de prueba recibido
- [ ] Widget funcionando correctamente
- [ ] Ready para producción

---

**Última actualización:** 2 de Diciembre 2024
**Contacto para pruebas:** elsampedrino@gmail.com
