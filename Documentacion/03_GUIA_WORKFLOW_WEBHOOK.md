# 🔧 GUÍA COMPLETA: ACTUALIZACIÓN WORKFLOW PARA WEBHOOK

## 📋 ÍNDICE

1. [Diferencias: Workflow actual vs Webhook](#diferencias)
2. [Estructura del nuevo workflow](#estructura-del-nuevo-workflow)
3. [Nodo 1: Webhook (recibir mensaje)](#nodo-1-webhook)
4. [Nodo 2: Procesar entrada](#nodo-2-procesar-entrada)
5. [Nodo 3-N: Workflow existente](#nodo-3-n-workflow-existente)
6. [Nodo Final: Formatear respuesta](#nodo-final-formatear-respuesta)
7. [Testing completo](#testing-completo)
8. [Troubleshooting](#troubleshooting)

---

## 🔄 DIFERENCIAS: WORKFLOW ACTUAL VS WEBHOOK

### **Workflow actual (manual/test):**

```
INPUT:
- Texto hardcodeado en un nodo
- No hay sesión
- No hay contexto previo

OUTPUT:
- JSON con propiedades
- Métricas
- No se formatea para UI
```

### **Workflow para webhook (producción):**

```
INPUT:
- Request HTTP POST del widget
- Con sessionId
- Con historial de conversación

OUTPUT:
- JSON específico para el widget
- Campo "response" con texto formateado
- Campo "propiedades" con data estructurada
- Campo "metricas" con costos
```

---

## 🏗️ ESTRUCTURA DEL NUEVO WORKFLOW

```
┌────────────────────────────────────────────────────┐
│  WEBHOOK                                           │
│  POST /webhook/chat                                │
│  Recibe: { message, sessionId, timestamp }         │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  PROCESAR ENTRADA                                  │
│  - Extraer mensaje del usuario                     │
│  - Validar sessionId                               │
│  - Log de request                                  │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  CARGAR PROPIEDADES (JSON)                         │
│  Tu archivo propiedades_demo.json                  │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  PREPARAR FILTRADO HAIKU                           │
│  Tu código existente (sin cambios)                 │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  HAIKU - FILTRAR PROPIEDADES                       │
│  Tu nodo existente (sin cambios)                   │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  PREPARAR RESPUESTA SONNET                         │
│  Tu código existente (sin cambios)                 │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  SONNET - GENERAR RESPUESTA                        │
│  Tu nodo existente (sin cambios)                   │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  PROCESAR Y CALCULAR COSTOS                        │
│  Tu código existente (sin cambios)                 │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  FORMATEAR RESULTADO FINAL                         │
│  ⭐ NUEVO: Formato específico para widget          │
└──────────────────┬─────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────────────┐
│  RESPOND TO WEBHOOK                                │
│  Devuelve JSON al widget                           │
└────────────────────────────────────────────────────┘
```

**Cambios mínimos:** Solo 2 nodos nuevos (Webhook + Formatear Final)

---

## 🎯 NODO 1: WEBHOOK

### **Configuración:**

```
Tipo: Webhook
HTTP Method: POST
Path: chat
Authentication: None
Response Mode: When Last Node Finishes
Response Code: 200
```

### **Request esperado del widget:**

```json
{
  "message": "Busco un departamento de 2 ambientes en Palermo",
  "sessionId": "session-1736968234567-abc123",
  "timestamp": "2025-01-15T18:30:45.123Z"
}
```

### **Configuración en N8N:**

1. **Agregar nodo Webhook** al inicio del workflow

2. **Configurar:**
   - HTTP Method: `POST`
   - Path: `chat`
   - Response Mode: `When Last Node Finishes`

3. **URL resultante:**
   ```
   https://n8n-bot-inmobiliario.onrender.com/webhook/chat
   ```

4. **Activar el workflow** (switch en verde)

---

## 🔧 NODO 2: PROCESAR ENTRADA

### **Propósito:**

- Extraer y validar datos del webhook
- Preparar para el resto del workflow

### **Código JavaScript:**

```javascript
// NODO: Procesar Entrada Webhook

// 1. Extraer datos del webhook
const webhookData = $input.first().json.body;

// 2. Validar que tenemos los datos necesarios
if (!webhookData || !webhookData.message) {
  return {
    json: {
      error: true,
      message: "Falta el campo 'message' en la request"
    }
  };
}

// 3. Extraer campos
const userMessage = webhookData.message.trim();
const sessionId = webhookData.sessionId || `session-${Date.now()}`;
const timestamp = webhookData.timestamp || new Date().toISOString();

// 4. Log para debugging (opcional)
console.log('[WEBHOOK] Nueva consulta:', {
  sessionId: sessionId,
  message: userMessage.substring(0, 50) + '...',
  timestamp: timestamp
});

// 5. Pasar al siguiente nodo
return {
  json: {
    consulta_original: userMessage,
    session_id: sessionId,
    timestamp: timestamp,
    // Este campo será usado por "Preparar Filtrado Haiku"
    consulta: userMessage
  }
};
```

### **Output esperado:**

```json
{
  "consulta_original": "Busco un departamento de 2 ambientes en Palermo",
  "session_id": "session-1736968234567-abc123",
  "timestamp": "2025-01-15T18:30:45.123Z",
  "consulta": "Busco un departamento de 2 ambientes en Palermo"
}
```

---

## 🔗 NODO 3-N: WORKFLOW EXISTENTE

**¡BUENAS NOTICIAS!** Tu workflow actual funciona sin cambios:

```
✅ Cargar propiedades JSON
✅ Preparar Filtrado Haiku
✅ Haiku - Filtrar Propiedades
✅ Preparar Respuesta Sonnet
✅ Sonnet - Generar Respuesta
✅ Procesar y Calcular Costos
```

**Lo único que necesitás cambiar:**

En el nodo **"Preparar Filtrado Haiku"**, cambiar:

```javascript
// ANTES:
const consulta = "Busco un departamento de 2 ambientes en Palermo";

// DESPUÉS:
const consulta = $('Procesar Entrada Webhook').first().json.consulta_original;
```

O si ya estaba usando `$input.first().json.consulta`, dejarlo así y listo.

---

## 📤 NODO FINAL: FORMATEAR RESULTADO FINAL

### **Propósito:**

Convertir el output de tu workflow a un formato específico para el widget.

### **Código JavaScript:**

```javascript
// NODO: Formatear Resultado Final

// 1. Obtener datos del workflow
const costos = $('Procesar y Calcular Costos').first().json;
const respuestaBot = costos.respuesta_bot;
const propiedades = costos.propiedades_detalladas || [];
const metricas = {
  tokens_haiku: costos.tokens_haiku || 0,
  tokens_sonnet_input: costos.tokens_sonnet_input || 0,
  tokens_sonnet_output: costos.tokens_sonnet_output || 0,
  tokens_totales: costos.tokens_totales || 0,
  costo_haiku_usd: costos.costo_haiku_usd || 0,
  costo_sonnet_usd: costos.costo_sonnet_usd || 0,
  costo_total_usd: costos.costo_total_usd || 0,
  ahorro_vs_version_anterior: costos.ahorro_vs_version_anterior || 0
};

// 2. Obtener sessionId
const sessionId = $('Procesar Entrada Webhook').first().json.session_id;

// 3. Formatear response para el widget
const widgetResponse = {
  // Campo principal: texto de la respuesta
  response: respuestaBot,
  
  // Propiedades estructuradas (opcional, para mostrar cards)
  propiedades: propiedades.map(prop => ({
    id: prop.id,
    tipo: prop.tipo,
    titulo: prop.titulo,
    operacion: prop.operacion,
    precio: prop.precio,
    direccion: prop.direccion,
    caracteristicas: prop.caracteristicas,
    // URLs de fotos (si las hay)
    fotos: prop.carpeta_fotos ? [
      `https://res.cloudinary.com/dikb9wzup/image/upload/w_800,f_auto/${prop.carpeta_fotos}/foto01.jpg`
    ] : []
  })),
  
  // Metadata (para debugging/analytics)
  metadata: {
    sessionId: sessionId,
    timestamp: new Date().toISOString(),
    cantidad_propiedades: propiedades.length
  },
  
  // Métricas (opcional, para monitoreo)
  metricas: metricas
};

// 4. Log para debugging
console.log('[RESPONSE] Enviando respuesta:', {
  sessionId: sessionId,
  response_length: respuestaBot.length,
  propiedades_count: propiedades.length,
  costo_total: metricas.costo_total_usd
});

// 5. Retornar para el webhook
return {
  json: widgetResponse
};
```

### **Output final (lo que recibe el widget):**

```json
{
  "response": "¡Perfecto! Tengo exactamente lo que estás buscando...",
  "propiedades": [
    {
      "id": "PROP-001",
      "tipo": "Departamento",
      "titulo": "Depto 2 ambientes luminoso en Palermo Soho",
      "operacion": "Alquiler",
      "precio": {
        "valor": 950,
        "moneda": "USD",
        "periodo": "mes"
      },
      "direccion": {
        "calle": "Gorriti 4532",
        "barrio": "Palermo Soho",
        "ciudad": "CABA"
      },
      "caracteristicas": {
        "ambientes": 2,
        "dormitorios": 1,
        "superficie_total": 45
      },
      "fotos": [
        "https://res.cloudinary.com/.../foto01.jpg"
      ]
    }
  ],
  "metadata": {
    "sessionId": "session-1736968234567-abc123",
    "timestamp": "2025-01-15T18:30:45.123Z",
    "cantidad_propiedades": 1
  },
  "metricas": {
    "tokens_totales": 2125,
    "costo_total_usd": 0.012,
    "ahorro_vs_version_anterior": 85
  }
}
```

---

## 🔗 CONECTAR NODOS

### **Orden de conexión:**

```
1. Webhook
   ↓
2. Procesar Entrada Webhook
   ↓
3. Read Binary File (propiedades.json)
   ↓
4. Preparar Filtrado Haiku
   ↓
5. Obtener Propiedades (Haiku)
   ↓
6. Preparar Respuesta Sonnet
   ↓
7. Sonnet - Generar Respuesta
   ↓
8. Procesar y Calcular Costos
   ↓
9. Formatear Resultado Final
   ↓
10. Respond to Webhook (automático)
```

### **En N8N:**

1. Arrastra una línea desde la salida del Webhook → Procesar Entrada
2. Procesar Entrada → Read Binary File
3. Read Binary File → Preparar Filtrado (tu nodo existente)
4. ...continuar con tu workflow existente
5. Al final: Procesar Costos → Formatear Resultado Final
6. El último nodo automáticamente responde al webhook

---

## 🧪 TESTING COMPLETO

### **Test 1: Webhook con curl (básico)**

```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola",
    "sessionId": "test-123",
    "timestamp": "2025-01-15T18:30:00.000Z"
  }'
```

**Resultado esperado:**

```json
{
  "response": "¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy?",
  "propiedades": [],
  "metadata": {
    "sessionId": "test-123",
    "timestamp": "2025-01-15T18:30:45.123Z",
    "cantidad_propiedades": 0
  }
}
```

---

### **Test 2: Consulta real**

```bash
curl -X POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Busco un departamento de 2 ambientes en Palermo para alquilar",
    "sessionId": "test-456"
  }'
```

**Verificar:**
- ✅ Response tiene el texto de Claude
- ✅ Propiedades array tiene PROP-001
- ✅ Metricas tiene costos
- ✅ Tiempo de respuesta < 30 segundos

---

### **Test 3: Con Postman**

1. **Crear nueva request**
   - Method: POST
   - URL: `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`

2. **Headers:**
   ```
   Content-Type: application/json
   ```

3. **Body (raw JSON):**
   ```json
   {
     "message": "Busco propiedades para comprar por menos de USD 200,000",
     "sessionId": "postman-test-001",
     "timestamp": "2025-01-15T18:30:00.000Z"
   }
   ```

4. **Send**

5. **Verificar response:**
   - Status: 200 OK
   - Body tiene "response", "propiedades", "metadata"

---

### **Test 4: Con el widget React**

1. **Abrir index.html del widget**

2. **Configurar:**
   ```javascript
   apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
   ```

3. **Abrir en navegador**

4. **Enviar mensaje:** "Busco algo de 3 ambientes"

5. **Verificar:**
   - ✅ Mensaje se envía
   - ✅ Typing indicator aparece
   - ✅ Respuesta llega
   - ✅ Texto se formatea bien
   - ✅ No hay errores en consola

---

### **Test 5: Testing end-to-end (completo)**

```javascript
// Script de testing automático (Node.js)

const tests = [
  {
    name: "Consulta simple",
    message: "Hola",
    expected: {
      hasResponse: true,
      propiedades: 0
    }
  },
  {
    name: "Búsqueda específica",
    message: "Busco un departamento de 2 ambientes en Palermo para alquilar",
    expected: {
      hasResponse: true,
      propiedades: 1,
      propiedadId: "PROP-001"
    }
  },
  {
    name: "Búsqueda por presupuesto",
    message: "Busco propiedades para comprar por menos de USD 200,000",
    expected: {
      hasResponse: true,
      propiedades: 1,
      propiedadId: "PROP-004"
    }
  },
  {
    name: "Sin resultados",
    message: "Busco un castillo en la luna",
    expected: {
      hasResponse: true,
      propiedades: 0
    }
  }
];

async function runTests() {
  const results = [];
  
  for (const test of tests) {
    console.log(`\n🧪 Testing: ${test.name}`);
    
    try {
      const response = await fetch('https://n8n-bot-inmobiliario.onrender.com/webhook/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: test.message,
          sessionId: `test-${Date.now()}`
        })
      });
      
      const data = await response.json();
      
      // Verificar
      const passed = 
        data.response && 
        data.propiedades.length === test.expected.propiedades &&
        (!test.expected.propiedadId || data.propiedades.some(p => p.id === test.expected.propiedadId));
      
      results.push({
        test: test.name,
        passed: passed,
        response: data.response.substring(0, 100) + '...',
        propiedades: data.propiedades.length
      });
      
      console.log(passed ? '✅ PASSED' : '❌ FAILED');
      
    } catch (error) {
      console.log('❌ ERROR:', error.message);
      results.push({
        test: test.name,
        passed: false,
        error: error.message
      });
    }
  }
  
  console.log('\n📊 RESULTADOS:');
  console.table(results);
}

runTests();
```

---

## 🐛 TROUBLESHOOTING

### **Problema 1: "Webhook not found" (404)**

**Causa:** Workflow no está activo

**Solución:**
1. Abrir workflow en N8N
2. Verificar que el switch "Active" esté en verde
3. Si está rojo, clickearlo para activar

---

### **Problema 2: Timeout (30 segundos)**

**Causa:** Workflow tarda demasiado

**Solución:**
1. Verificar logs en N8N
2. Identificar nodo lento (probablemente Sonnet)
3. Reducir max_tokens de Sonnet:
   ```javascript
   max_tokens: 1000  // Reducir de 2000
   ```
4. O optimizar prompt

---

### **Problema 3: Response vacío**

**Causa:** Nodo "Formatear Resultado" no encuentra los datos

**Solución:**
1. Verificar que el nodo anterior sea "Procesar y Calcular Costos"
2. En "Formatear Resultado", cambiar:
   ```javascript
   // ANTES:
   const costos = $('Procesar y Calcular Costos').first().json;
   
   // DESPUÉS:
   const costos = $input.first().json;
   ```

---

### **Problema 4: CORS error en el widget**

**Error:**
```
Access to fetch at '...' has been blocked by CORS
```

**Solución en N8N (Render):**

1. Dashboard de Render → Tu servicio
2. Environment → Add Environment Variable
3. Agregar:
   ```
   Key: N8N_CORS_ALLOW_ALL
   Value: true
   ```
4. Manual Deploy (botón arriba)

**O para CORS específico:**
```
N8N_CORS_ALLOW_ORIGIN=https://tudominio.com,http://localhost:3000
```

---

### **Problema 5: "Field 'message' is required"**

**Causa:** Request mal formateado

**Verificar:**
```javascript
// ✅ CORRECTO:
{
  "message": "Hola",
  "sessionId": "test-123"
}

// ❌ INCORRECTO:
{
  "text": "Hola",  // Campo incorrecto
  "session": "test-123"
}
```

---

### **Problema 6: Widget muestra "undefined"**

**Causa:** Campo "response" no existe en el JSON

**Solución en "Formatear Resultado Final":**
```javascript
// Verificar que existe:
const respuestaBot = costos.respuesta_bot || "Lo siento, no pude procesar tu consulta.";

// Y retornar:
response: respuestaBot,  // NO: response: undefined
```

---

## 📊 MONITOREO Y LOGS

### **Ver ejecuciones en N8N:**

1. Dashboard → Workflows
2. Click en tu workflow
3. **Executions** (tab superior)
4. Ver todas las ejecuciones recientes

### **Filtrar por resultado:**

```
Success: Solo exitosas
Error: Solo con errores
```

### **Ver detalles:**

Click en una ejecución para ver:
- ✅ Input de cada nodo
- ✅ Output de cada nodo
- ✅ Tiempo de ejecución
- ✅ Errores (si hay)

---

## 📈 MÉTRICAS IMPORTANTES

### **Tiempos esperados:**

```
Webhook recibe request:     <100ms
Procesar entrada:           <50ms
Cargar propiedades:         <100ms
Haiku filtrado:             1-2 segundos
Sonnet respuesta:           5-10 segundos
Calcular costos:            <50ms
Formatear resultado:        <50ms
Total:                      7-13 segundos
```

### **Costos esperados:**

```
Por consulta: $0.015 - $0.025 USD
Por 100 consultas: $1.50 - $2.50 USD
Por 1000 consultas: $15 - $25 USD
```

### **Límites de Render Free:**

```
Timeout: 30 segundos
RAM: 512MB
Requests/month: Ilimitadas
Horas/month: 750 (suficiente para 31 días)
```

---

## ✅ CHECKLIST PRE-PRODUCCIÓN

Antes de darle el link a Cristian:

- [ ] Workflow activo en Render
- [ ] Webhook responde correctamente
- [ ] Tests con curl exitosos
- [ ] Tests con Postman exitosos
- [ ] Widget conectado y funcionando
- [ ] CORS configurado
- [ ] Logs sin errores
- [ ] Tiempos de respuesta aceptables (<20s)
- [ ] Costos monitoreados
- [ ] Keep-alive activo (opcional)
- [ ] Documentación lista para Cristian

---

## 🎯 RESUMEN DE CAMBIOS

### **Lo que cambia:**

1. ✅ Agregar nodo **Webhook** al inicio
2. ✅ Agregar nodo **Procesar Entrada** después del webhook
3. ✅ Agregar nodo **Formatear Resultado** al final
4. ✅ Actualizar referencia en "Preparar Filtrado Haiku" (si es necesario)

### **Lo que NO cambia:**

- ✅ Toda tu lógica de filtrado (Haiku)
- ✅ Toda tu lógica de respuesta (Sonnet)
- ✅ Cálculo de costos
- ✅ Estructura de propiedades
- ✅ Prompts

**Total: ~30 minutos de trabajo** para adaptar tu workflow existente.

---

## 🚀 DEPLOYMENT FINAL

### **Paso 1: Exportar workflow actualizado**

1. En N8N local, abrir workflow
2. **Settings** → **Export**
3. Guardar JSON

### **Paso 2: Importar en Render**

1. N8N en Render → **Import Workflow**
2. Seleccionar JSON
3. Actualizar credenciales
4. **Save**

### **Paso 3: Activar**

1. Switch "Active" → Verde
2. Verificar URL del webhook
3. Copiar URL

### **Paso 4: Configurar widget**

1. En widget, actualizar:
   ```javascript
   apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
   ```
2. Build del widget
3. Deploy

### **Paso 5: Testing final**

1. Abrir widget en producción
2. Enviar mensaje de prueba
3. Verificar respuesta
4. ✅ LISTO PARA CRISTIAN

---

## 📞 SOPORTE

Si al volver de vacaciones tenés algún problema:

1. Revisar esta guía
2. Verificar logs en N8N
3. Testear con curl para aislar el problema
4. Revisar CORS si el widget no conecta

---

**¡WORKFLOW ACTUALIZADO PARA WEBHOOK!** ✅

**Próximo documento:** Documentación para Cristian

---

**Creado:** 15 de Enero 2025  
**Autor:** Claude  
**Para:** Damián - Bot Inmobiliario  
**Status:** READY TO IMPLEMENT ✅
