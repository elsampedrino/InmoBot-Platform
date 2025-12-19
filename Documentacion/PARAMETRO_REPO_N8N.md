# 🔧 Parámetro REPO - Selector de Repositorio GitHub

**Fecha:** 2025-01-13
**Objetivo:** Permitir que el mismo workflow de N8N sirva múltiples clientes
**Implementación:** Parámetro `repo` en webhook para seleccionar repositorio de propiedades

---

## 🎯 Objetivo

Queremos que el mismo flujo de N8N pueda servir tanto:
- **Demo** → Repositorio con propiedades de prueba
- **BBR Grupo Inmobiliario** → Repositorio con propiedades reales de Cristian

**Ventajas:**
- ✅ Un solo workflow para mantener
- ✅ Misma lógica de filtrado y respuesta
- ✅ Fácil de escalar a más clientes
- ✅ Sin duplicar código

---

## 📊 Flujo actual vs nuevo

### ANTES (sin parámetro repo):
```
Widget → N8N → GitHub (SIEMPRE el mismo repo)
```
URL hardcodeada: `https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/refs/heads/main/propiedades_demo.json`

### DESPUÉS (con parámetro repo):
```
Widget → N8N → GitHub (repo según parámetro)
   ↓
repo = '0' → propiedades_demo.json
repo = '1' → propiedades_bbr.json
```

---

## 🛠️ Cambios en el Widget (YA IMPLEMENTADOS)

### ChatWidget.jsx

**1. Parámetro agregado a configuración:**
```javascript
const {
  apiUrl = 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
  contactUrl = 'https://n8n-bot-inmobiliario.onrender.com/webhook/contact',
  // ... otros parámetros ...
  repo = '0' // 0 = demo, 1 = Cristian BBR
} = config || {};
```

**2. Parámetro enviado en el fetch:**
```javascript
body: JSON.stringify({
  message: inputValue,
  sessionId: sessionId,
  timestamp: new Date().toISOString(),
  repo: repo // Parámetro para seleccionar repositorio (0=demo, 1=BBR)
})
```

### Ejemplo de uso en sitio web:

**Para DEMO:**
```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    botName: 'InmoBot Demo',
    repo: '0'  // Catálogo demo
  });
</script>
```

**Para BBR:**
```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    botName: 'Asistente BBR',
    welcomeMessage: 'Hola, soy el asistente de BBR Grupo Inmobiliario',
    repo: '1'  // Catálogo BBR
  });
</script>
```

---

## 🔧 Cambios en N8N (PENDIENTE DE IMPLEMENTAR)

### Ubicación del cambio:
**Nodo:** "Obtener Propiedades" (HTTP Request)

### ANTES:
```json
{
  "parameters": {
    "url": "https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/refs/heads/main/propiedades_demo.json",
    "options": {}
  },
  "name": "Obtener Propiedades",
  "type": "n8n-nodes-base.httpRequest"
}
```

### DESPUÉS:
Necesitamos **cambiar el nodo** de HTTP Request a **Code (JavaScript)** para poder leer el parámetro y decidir qué URL usar.

---

## 📝 Implementación en N8N - Paso a paso

### Paso 1: Backup del workflow
1. Abrir workflow en N8N
2. Click derecho → "Duplicate"
3. Renombrar: "Bot Inmobiliaria - BACKUP [FECHA]"

### Paso 2: Modificar nodo "Obtener Propiedades"

**Opción A: Convertir a Code node**

1. **Eliminar** el nodo actual "Obtener Propiedades" (HTTP Request)

2. **Agregar** un nodo nuevo tipo "Code" en el mismo lugar

3. **Código JavaScript para el nodo:**

```javascript
// ============================================
// OBTENER PROPIEDADES DESDE GITHUB
// Selecciona repositorio según parámetro 'repo'
// ============================================

// 1. Leer parámetro 'repo' del webhook
const webhookData = $('Webhook Chat').first().json;
const body = webhookData.body || webhookData;
const repo = body.repo || '0'; // Default: demo

// 2. Definir URLs según repositorio
const REPOS = {
  '0': 'https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/refs/heads/main/propiedades_demo.json',
  '1': 'https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/refs/heads/main/propiedades_bbr.json'
};

// 3. Seleccionar URL
const url = REPOS[repo] || REPOS['0'];

console.log(`[REPO SELECTOR] repo=${repo}, url=${url}`);

// 4. Hacer request HTTP usando helpers de N8N
const response = await this.helpers.httpRequest({
  method: 'GET',
  url: url,
  returnFullResponse: true
});

if (response.statusCode !== 200) {
  throw new Error(`HTTP error! status: ${response.statusCode}`);
}

// 5. Convertir a string si viene como objeto (N8N puede parsear automáticamente)
let data = response.body;
if (typeof data === 'object') {
  data = JSON.stringify(data);
}

return {
  json: {
    data: data,
    repo: repo,
    url: url,
    timestamp: new Date().toISOString()
  }
};
```

4. **Configurar el nodo:**
   - Nombre: "Obtener Propiedades (Dinámico)"
   - Continuar en error: ✅ ON
   - Retry on fail: ✅ ON (3 intentos)

5. **Conectar:**
   - Input: "Webhook Chat"
   - Output: "Preparar Filtrado Haiku"

### Paso 3: Verificar que todo fluye correctamente

**El flujo completo debe ser:**
```
Webhook Chat
  ↓
Obtener Propiedades (Dinámico) ← LEE 'repo' y decide URL
  ↓
Preparar Filtrado Haiku
  ↓
Haiku - Filtrar Propiedades
  ↓
Preparar Respuesta Sonnet
  ↓
Sonnet - Generar Respuesta
  ↓
Responder
```

### Paso 4: Guardar y activar
1. Click en "Save" (arriba a la derecha)
2. Verificar que "Active" esté en ON
3. Probar con el widget

---

## 🧪 Pruebas de verificación

### Test 1: Demo (repo='0')
```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    repo: '0'
  });
</script>
```

**Consulta:** "Busco un departamento de 2 ambientes en Palermo"
**Resultado esperado:** Propiedades del catálogo demo

### Test 2: BBR (repo='1')
```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    repo: '1'
  });
</script>
```

**Consulta:** "Busco una casa en Ramallo"
**Resultado esperado:** Propiedades del catálogo BBR

### Test 3: Sin parámetro (default a demo)
```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
    // Sin especificar 'repo'
  });
</script>
```

**Consulta:** Cualquiera
**Resultado esperado:** Propiedades del catálogo demo (fallback)

---

## 📋 Checklist de implementación

- [x] Widget modificado para enviar parámetro `repo`
- [x] Documentación actualizada
- [ ] Nodo N8N modificado para leer parámetro
- [ ] Workflow guardado y activado
- [ ] Test con repo='0' (demo)
- [ ] Test con repo='1' (BBR)
- [ ] Test sin parámetro (fallback a demo)
- [ ] Widget rebuildeado y deployado a Vercel

---

## 🚀 Próximos pasos después de implementar

1. **Rebuild del widget:**
   ```bash
   cd widget-react
   npm run build:vercel
   ```

2. **Deploy a Vercel:**
   - Git commit + push
   - Vercel detecta cambios automáticamente
   - Esperar deploy (~1-2 min)

3. **Crear repositorio BBR en GitHub:**
   - Subir `propiedades_bbr.json` cuando esté listo
   - URL: `https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/refs/heads/main/propiedades_bbr.json`

4. **Probar integración completa:**
   - Widget con repo='0' → debe mostrar demo
   - Widget con repo='1' → debe mostrar BBR
   - Sin parámetro → debe mostrar demo

---

## 🔍 Debugging

### Ver qué repo se está usando:
En el código del nodo, agregamos `console.log`:
```javascript
console.log(`[REPO SELECTOR] repo=${repo}, url=${url}`);
```

Para ver los logs en N8N:
1. Click derecho en el nodo → "Execute Node"
2. Ver output en la pestaña "Output"
3. Revisar los logs del workflow

### Errores comunes:

**Error: "Cannot read property 'repo'"**
- Solución: El widget no está enviando el parámetro
- Verificar que el widget esté rebuildeado

**Error: "404 Not Found"**
- Solución: El JSON no existe en GitHub
- Verificar que el archivo esté subido

**Siempre devuelve demo:**
- Solución: Verificar que el código esté leyendo `body.repo` correctamente
- Agregar console.log para debuggear

---

## ✅ Resultado final

Una vez implementado:

1. **Mismo workflow N8N** sirve múltiples clientes
2. **Cada cliente** tiene su propio catálogo de propiedades
3. **Fácil de escalar** - solo agregar nuevo repo='2', repo='3', etc.
4. **Mantenimiento simple** - un solo flujo para actualizar

**Autor:** Claude Code
**Fecha creación:** 2025-01-13
**Última actualización:** 2025-01-13
