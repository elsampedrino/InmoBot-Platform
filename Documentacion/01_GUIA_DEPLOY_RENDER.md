# 🚀 GUÍA COMPLETA: DEPLOY N8N EN RENDER

## 📋 ÍNDICE

1. [Requisitos previos](#requisitos-previos)
2. [Crear cuenta en Render](#crear-cuenta-en-render)
3. [Deploy de N8N](#deploy-de-n8n)
4. [Configuración inicial](#configuración-inicial)
5. [Importar workflow](#importar-workflow)
6. [Configurar webhook](#configurar-webhook)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 1️⃣ REQUISITOS PREVIOS

### **Lo que necesitás:**

- ✅ Cuenta de GitHub (gratis)
- ✅ Cuenta de Render (gratis)
- ✅ API Key de Anthropic (la que ya tenés)
- ✅ Tu workflow exportado de N8N local
- ✅ 30-40 minutos

### **Costos:**

```
Plan Free de Render:
✅ 750 horas/mes gratis
✅ 512MB RAM
✅ Suficiente para MVP
✅ Se duerme después de 15 min sin uso (se despierta automático)

Plan Starter ($7/mes):
- 24/7 sin dormir
- 1GB RAM
- Mejor performance
```

**Recomendación:** Empezar con Free, upgradear si Cristian paga.

---

## 2️⃣ CREAR CUENTA EN RENDER

### **Paso 1: Ir a Render**

🔗 https://render.com

### **Paso 2: Sign Up**

1. Click en **"Get Started"** o **"Sign Up"**
2. Elegir **"Sign up with GitHub"** (recomendado)
3. Autorizar Render a acceder a tu GitHub
4. Completar perfil básico

![Render Sign Up](https://docs.render.com/images/sign-up.png)

### **Paso 3: Verificar email**

- Revisar inbox
- Click en link de verificación
- Listo ✅

---

## 3️⃣ DEPLOY DE N8N

### **Método 1: Deploy con Blueprint (MÁS FÁCIL) ⭐**

1. **Fork del repositorio oficial de N8N:**

   Ve a: https://github.com/n8n-io/n8n-render
   
   Click en **"Fork"** (arriba derecha)
   
   Esto crea una copia en tu GitHub

2. **Deploy en Render:**

   Click en este botón:
   
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/n8n-io/n8n)
   
   O ve a tu dashboard de Render → **"New +"** → **"Blueprint"**

3. **Configurar el Blueprint:**

   ```
   Service Group Name: n8n-bot-inmobiliario
   Branch: main
   ```

4. **Variables de entorno (importantes):**

   Render te pedirá configurar estas variables:

   ```bash
   # BÁSICAS (obligatorias)
   N8N_BASIC_AUTH_ACTIVE=true
   N8N_BASIC_AUTH_USER=admin
   N8N_BASIC_AUTH_PASSWORD=tu_password_seguro_aqui
   
   # WEBHOOK (obligatorio)
   WEBHOOK_URL=https://tu-app.onrender.com
   
   # TIMEZONE
   GENERIC_TIMEZONE=America/Argentina/Buenos_Aires
   TZ=America/Argentina/Buenos_Aires
   
   # ENCRYPTION (genera una key segura)
   N8N_ENCRYPTION_KEY=genera_una_key_aleatoria_de_32_caracteres
   ```

5. **Generar N8N_ENCRYPTION_KEY:**

   Abre tu terminal y ejecuta:
   
   ```bash
   openssl rand -base64 32
   ```
   
   Copia el resultado y pegalo en N8N_ENCRYPTION_KEY

6. **Click en "Apply"**

   Render empezará a deployar. Esto tarda 5-10 minutos.

---

### **Método 2: Deploy Manual (más control)**

Si el Blueprint no funciona, hacelo manual:

1. **En Render Dashboard:**
   
   - Click **"New +"**
   - Elegir **"Web Service"**

2. **Conectar repositorio:**
   
   - Click **"Build and deploy from a Git repository"**
   - Conectar tu GitHub
   - Seleccionar el fork de n8n-render

3. **Configuración del servicio:**

   ```
   Name:              n8n-bot-inmobiliario
   Region:            Oregon (US West) - más cerca de Anthropic
   Branch:            main
   Root Directory:    (dejar vacío)
   Environment:       Docker
   Instance Type:     Free
   ```

4. **Docker Command:**

   ```bash
   n8n start
   ```

5. **Variables de entorno (mismo que arriba):**

   Click en **"Advanced"** → **"Add Environment Variable"**
   
   Agregar todas las del Método 1.

6. **Click "Create Web Service"**

   Esperar 5-10 minutos mientras deploya.

---

## 4️⃣ CONFIGURACIÓN INICIAL

### **Acceder a tu N8N en Render:**

1. **Obtener URL:**
   
   En tu dashboard de Render verás algo como:
   
   ```
   https://n8n-bot-inmobiliario.onrender.com
   ```

2. **Login:**
   
   - User: `admin` (o el que configuraste)
   - Password: `tu_password_seguro_aqui`

3. **Primera vez:**
   
   N8N te pedirá crear usuario owner. Usa los mismos datos.

---

### **Configurar credenciales de Anthropic:**

1. En N8N (ya en Render), ir a:
   
   **Settings** (⚙️) → **Credentials** → **New**

2. Buscar: **"Anthropic"**

3. Configurar:
   
   ```
   Name: Anthropic API
   API Key: tu_anthropic_api_key_aqui
   ```

4. **Save**

---

## 5️⃣ IMPORTAR WORKFLOW

### **Exportar de N8N Local:**

1. En tu N8N local, abrir tu workflow
2. Click en **"..."** (arriba derecha)
3. **Download** → Guarda el JSON

### **Importar a N8N Render:**

1. En N8N en Render, click **"Add workflow"** → **"Import from File"**
2. Seleccionar tu archivo JSON
3. Click **"Import"**

### **Actualizar credenciales:**

Todos los nodos con credenciales (Anthropic) aparecerán en rojo.

Para cada nodo:
1. Click en el nodo
2. Credential: Seleccionar **"Anthropic API"** (la que creaste)
3. **Save**

### **Actualizar URLs:**

Si tu workflow tiene URLs hardcodeadas de localhost, cambialas:

```
Antes: http://localhost:5678/webhook/...
Ahora: https://n8n-bot-inmobiliario.onrender.com/webhook/...
```

---

## 6️⃣ CONFIGURAR WEBHOOK

### **Crear nodo Webhook:**

Tu workflow ya debería tener un nodo Webhook al inicio, pero verificá:

1. **Nodo: Webhook**
   
   ```
   HTTP Method: POST
   Path: chat
   Response Mode: When Last Node Finishes
   Response Code: 200
   ```

2. **URL del webhook resultante:**
   
   ```
   https://n8n-bot-inmobiliario.onrender.com/webhook/chat
   ```
   
   Esta es la URL que usará tu widget React.

### **Activar el workflow:**

1. Click en **"Active"** (switch arriba)
2. El workflow debe estar en verde ✅

### **Importante - Keep-Alive:**

Como el plan Free se duerme, necesitás un "ping" cada 10 minutos:

**Crear workflow de keep-alive:**

1. Nuevo workflow: **"Keep Alive"**

2. **Nodo 1: Schedule Trigger**
   ```
   Mode: Every X
   Value: 10
   Unit: Minutes
   ```

3. **Nodo 2: HTTP Request**
   ```
   Method: GET
   URL: https://n8n-bot-inmobiliario.onrender.com/webhook/ping
   ```

4. **Activar este workflow**

Esto mantiene N8N despierto las 24hs.

---

## 7️⃣ TESTING

### **Test 1: Webhook básico con curl**

En tu terminal local:

```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, busco un departamento de 2 ambientes en Palermo",
    "sessionId": "test-123"
  }'
```

**Resultado esperado:**

```json
{
  "response": "¡Perfecto! Tengo exactamente lo que estás buscando...",
  "propiedades": [...],
  "costos": {...}
}
```

### **Test 2: Desde Postman**

1. **Método:** POST
2. **URL:** `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`
3. **Headers:**
   ```
   Content-Type: application/json
   ```
4. **Body (raw JSON):**
   ```json
   {
     "message": "Busco propiedades para comprar por menos de USD 200,000",
     "sessionId": "postman-test"
   }
   ```
5. **Send**

### **Test 3: Ver logs en Render**

1. Dashboard de Render → Tu servicio
2. **Logs** (arriba)
3. Ver output en tiempo real
4. Buscar errores si algo falla

---

## 8️⃣ TROUBLESHOOTING

### **Problema 1: "Service Unavailable" o 503**

**Causa:** N8N se durmió (plan Free)

**Solución:**
- Esperar 30-60 segundos (se despierta solo)
- O implementar el workflow de keep-alive (ver sección 6)

---

### **Problema 2: "Unauthorized" o 401**

**Causa:** Credenciales de Anthropic no configuradas

**Solución:**
1. Settings → Credentials
2. Verificar que la API key de Anthropic esté correcta
3. Re-guardar el workflow

---

### **Problema 3: Workflow no responde**

**Causa:** Workflow no está activo

**Solución:**
1. Abrir workflow
2. Verificar que el switch "Active" esté en verde
3. Si está gris, clickearlo para activar

---

### **Problema 4: "Error: Cannot find module..."**

**Causa:** N8N no instaló todas las dependencias

**Solución:**
1. En Render, ir a **Environment**
2. Agregar variable:
   ```
   NODE_ENV=production
   ```
3. **Manual Deploy** (botón arriba)

---

### **Problema 5: Webhook devuelve HTML en vez de JSON**

**Causa:** Estás accediendo al webhook con GET en el navegador

**Solución:**
- Webhooks solo responden a POST
- Usar curl, Postman, o el widget React

---

### **Problema 6: Build falla**

**Error común:**
```
Error: ENOSPC: no space left on device
```

**Solución:**
- Plan Free tiene poco espacio
- Simplificar el workflow (menos nodos)
- O upgradear a plan Starter ($7/mes)

---

### **Problema 7: Timeout después de 30 segundos**

**Causa:** Render Free tiene timeout de 30s

**Solución:**
- Optimizar workflow para responder en <30s
- Tu workflow actual (~15s) está bien
- Si necesitas más tiempo, upgradear a Starter

---

## 🎯 CONFIGURACIÓN OPTIMIZADA FINAL

### **Variables de entorno recomendadas:**

```bash
# Básicas
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=tu_password_ultra_seguro

# Webhook
WEBHOOK_URL=https://n8n-bot-inmobiliario.onrender.com
N8N_PATH=/

# Timezone
GENERIC_TIMEZONE=America/Argentina/Buenos_Aires
TZ=America/Argentina/Buenos_Aires

# Seguridad
N8N_ENCRYPTION_KEY=tu_key_de_32_caracteres_generada_con_openssl

# Performance (opcional)
EXECUTIONS_PROCESS=main
N8N_METRICS=false
N8N_LOG_LEVEL=info

# Para evitar sleep (plan Free)
NODE_FUNCTION_ALLOW_BUILTIN=*
NODE_FUNCTION_ALLOW_EXTERNAL=*
```

---

## ✅ CHECKLIST FINAL

Antes de continuar con el widget React, verificá:

- [ ] N8N deployado en Render
- [ ] Login funciona (admin / password)
- [ ] Workflow importado correctamente
- [ ] Credenciales de Anthropic configuradas
- [ ] Workflow activado (switch verde)
- [ ] Webhook responde correctamente
- [ ] Test con curl exitoso
- [ ] URL del webhook anotada
- [ ] Keep-alive workflow activo (opcional)

---

## 📊 MONITOREO

### **Dashboard de Render:**

```
Métricas disponibles:
- CPU Usage
- Memory Usage
- Request Count
- Response Time
- Error Rate
```

### **Logs:**

```
Acceso en tiempo real:
Dashboard → Logs → Ver stream
```

### **Alertas:**

```
Render te avisa automáticamente si:
- Build falla
- Deploy falla
- Service crashea
```

---

## 💰 COSTOS PROYECTADOS

### **Plan Free:**

```
Costo:              $0/mes
Límite:             750 horas
Horas por día:      24h
Días disponibles:   31 días (750/24 = 31.25)

Perfecto para: MVP y testing
```

### **Plan Starter ($7/mes):**

```
Ventajas:
✅ Sin sleep (24/7 despierto)
✅ Más RAM (1GB vs 512MB)
✅ Sin límite de horas
✅ Mejor performance
✅ Custom domains

Cuando upgradear:
- Cristian paga el servicio
- Necesitas 24/7 sin delays
- Tienes >1000 consultas/mes
```

---

## 🔒 SEGURIDAD

### **Recomendaciones:**

1. **Password fuerte para N8N:**
   ```bash
   # Generar password seguro
   openssl rand -base64 24
   ```

2. **No compartir credenciales:**
   - API keys son secretas
   - No commitear en GitHub
   - No compartir en Slack

3. **Monitoring:**
   - Revisar logs semanalmente
   - Alertas de errores
   - Rate limiting si es necesario

4. **Backups:**
   - Exportar workflows semanalmente
   - Guardar en GitHub privado
   - Mantener copia local

---

## 🚀 PRÓXIMOS PASOS

Una vez que N8N está en Render:

1. ✅ Anotar URL del webhook
2. ✅ Verificar que responde correctamente
3. ➡️ **SIGUIENTE:** Crear widget React
4. ➡️ Integrar widget con webhook
5. ➡️ Testing end-to-end
6. ➡️ Deploy del widget en CDN

---

## 📞 SUPPORT

### **Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### **N8N Support:**
- Docs: https://docs.n8n.io
- Community: https://community.n8n.io
- GitHub: https://github.com/n8n-io/n8n

---

## 📝 NOTAS IMPORTANTES

### **Performance:**

```
Primera request después del sleep: ~10-15 segundos
Requests subsecuentes: ~5-10 segundos
Con keep-alive activo: ~5-10 segundos siempre
```

### **Limitaciones del Free Plan:**

```
✅ Suficiente para MVP
✅ ~1000 consultas/mes sin problema
❌ Se duerme después de 15 min
❌ Solo 512MB RAM
❌ Build puede ser lento
```

### **Cuándo migrar a Starter:**

```
Cuando:
- Cristian lo usa activamente
- >50 consultas/día
- Necesitas 24/7 sin delays
- Tienes presupuesto ($7/mes es barato)
```

---

**¡N8N EN RENDER LISTO!** ✅

---

**Próximo documento:** Widget React con chatbot flotante 🎨

---

**Creado:** 15 de Enero 2025  
**Autor:** Claude  
**Para:** Damián - Bot Inmobiliario  
**Status:** READY TO USE ✅
