# Workflow Solo Haiku - Plan Básico

## 📋 Objetivo

Crear una versión simplificada del workflow usando **SOLO Haiku 3.5** para el **Plan Básico** (Tier 1 - $30/mes).

Este plan es más económico y directo, sin las capacidades conversacionales avanzadas de Sonnet.

---

## 🎯 Diferencias clave vs Plan Profesional (Haiku + Sonnet)

| Característica | Plan Básico (Solo Haiku) | Plan Profesional (Haiku + Sonnet) |
|---|---|---|
| **Modelos** | Solo Haiku 3.5 | Haiku 3.5 + Sonnet 4 |
| **Costo tokens** | ~$0.20/1000 consultas | ~$3.50/1000 consultas |
| **Velocidad** | 1-2 seg | 2-4 seg |
| **Comparación ubicaciones** | ❌ No | ✅ Sí (menciona barrios cercanos) |
| **Tono conversacional** | Directo y simple | Natural y profesional |
| **Multilenguaje** | Español básico | ✅ ES/EN/PT automático |
| **Formato respuestas** | Lista simple | Texto narrativo con contexto |
| **Propiedades límite** | Hasta 50 | Hasta 200 |

---

## 🔄 Cambios en el Workflow

### **Arquitectura actual (Haiku + Sonnet):**
```
Webhook → Obtener Props → Preparar Haiku → Haiku Filtrar → Preparar Sonnet → Sonnet Responder → Formatear → Stats → Webhook Response
```

### **Arquitectura nueva (Solo Haiku):**
```
Webhook → Obtener Props → Preparar Haiku Todo-en-Uno → Haiku Responder → Formatear → Stats → Webhook Response
```

### **Nodos a ELIMINAR:**
1. ❌ "Preparar Respuesta Sonnet" (código)
2. ❌ "Sonnet - Respuesta Final" (HTTP Request)
3. ❌ "Error Handler Sonnet" (código)

### **Nodos a MODIFICAR:**
1. ✏️ "Preparar Filtrado Haiku" → **RENOMBRAR a "Preparar Haiku Todo-en-Uno"**
2. ✏️ "Haiku - Filtrar Propiedades" → **RENOMBRAR a "Haiku - Respuesta Completa"**
3. ✏️ "Formatear Respuesta" → Ajustar metadata (solo Haiku)

### **Nodos a CONSERVAR (sin cambios):**
- ✅ Webhook Chat
- ✅ Obtener Propiedades (Dinámico)
- ✅ Error Handler GitHub
- ✅ Error Handler Haiku
- ✅ Preparar Stats Chat
- ✅ Execute Insert Chat
- ✅ Responder al Webhook Chat
- ✅ Todo el flujo de Webhook Contact (Telegram + Leads)

---

## 📝 Nuevo Prompt para Haiku Todo-en-Uno

Este prompt combina **filtrado + respuesta** en una sola llamada a Haiku.

### **Nodo: "Preparar Haiku Todo-en-Uno"** (Code)

```javascript
// ============================================
// PREPARAR HAIKU TODO-EN-UNO - PLAN BÁSICO
// Filtrado + Respuesta en una sola llamada
// ============================================

// OBTENER INPUT
const inputData = $input.first().json;

// VALIDAR QUE LLEGARON PROPIEDADES
if (!inputData.data || typeof inputData.data !== 'string' || inputData.data.length < 10) {
  return [{
    json: {
      error: true,
      errorType: 'GITHUB_ERROR',
      errorCode: 'ERR_NO_PROPERTIES',
      response: 'Lo siento, estamos teniendo problemas técnicos para acceder a nuestras propiedades. ¿Podrías intentar nuevamente en unos minutos?',
      timestamp: new Date().toISOString()
    }
  }];
}

// 1. OBTENER LA CONSULTA DEL USUARIO
const webhookData = $('Webhook Chat').first().json;
const body = webhookData.body || webhookData;
const consulta = body.message || body.consulta || body.query || "Busco una propiedad";

// 2. PARSEAR PROPIEDADES
const parsedData = JSON.parse(inputData.data);
let propiedades = [];

if (Array.isArray(parsedData.propiedades)) {
  propiedades = parsedData.propiedades;
} else if (parsedData.propiedades) {
  propiedades = parsedData.propiedades;
}

// 3. CREAR CATÁLOGO COMPLETO PARA HAIKU
const catalogoCompleto = propiedades.map((p, index) => {
  const id = p.id || `PROP-${String(index + 1).padStart(3, '0')}`;

  // Construir objeto con toda la info necesaria
  const propInfo = {
    id: id,
    tipo: p.tipo || 'Propiedad',
    operacion: p.operacion || 'Venta',
    titulo: p.titulo || `${p.tipo} en ${p.direccion?.barrio || 'Buenos Aires'}`,
    ubicacion: p.direccion?.barrio || p.barrio || 'Buenos Aires',
    precio: p.precio?.valor || p.precio || 'Consultar',
    moneda: p.precio?.moneda || 'USD',
    expensas: p.expensas?.valor || null,
    ambientes: p.caracteristicas?.ambientes || p.ambientes || null,
    dormitorios: p.caracteristicas?.dormitorios || p.dormitorios || null,
    banos: p.caracteristicas?.banos || p.banos || null,
    superficie: p.caracteristicas?.superficie_total || p.superficie || null,
    cochera: p.detalles?.cochera || p.cochera || false,
    balcon: p.detalles?.balcon || p.balcon || false,
    jardin: p.detalles?.jardin || p.jardin || false,
    descripcion: p.descripcion || '',
    fotos: (p.fotos?.urls || []).join(' ')
  };

  return propInfo;
});

// 4. CONSTRUIR PAYLOAD PARA HAIKU
const haikuPayload = {
  "model": "claude-3-5-haiku-20241022",
  "max_tokens": 1500,
  "messages": [
    {
      "role": "user",
      "content": `Sos un asistente inmobiliario simple y directo para Argentina.

CONSULTA DEL CLIENTE:
"${consulta}"

CATÁLOGO DE PROPIEDADES:
${JSON.stringify(catalogoCompleto, null, 2)}

=== TU TAREA ===

Analizá la consulta y respondé según corresponda:

🔹 SI ES SALUDO SIMPLE (sin búsqueda específica):
→ Saludá brevemente y preguntá qué busca

🔹 SI BUSCA ALGO QUE NO EXISTE EN EL CATÁLOGO:
→ Informá que no hay propiedades con esas características
→ Ejemplo: Si pide piscina pero ninguna propiedad tiene piscina = NO HAY

🔹 SI ES MUY GENÉRICA (sin ubicación, tipo, ni operación):
→ Pedí más detalles (ubicación, tipo, operación)

🔹 SI TIENE CRITERIOS CLAROS Y HAY COINCIDENCIAS:
→ Mostrá las 3-5 propiedades más relevantes

⚠️ MUY IMPORTANTE:
- NO expliques tu razonamiento
- NO digas "esto es tipo A/B/C/D"
- NO digas "Entendido, voy a..."
- SOLO respondé directamente según el formato de abajo

🔹 FORMATO PARA SALUDOS (Tipo A):
---
¡Hola! ¿Qué tipo de propiedad buscás?

🏢 Departamento
🏠 Casa
🏪 Local comercial
🏞️ Terreno

¿Para alquilar o comprar?
---

🔹 FORMATO PARA SIN COINCIDENCIAS (Tipo B):
---
No tenemos propiedades disponibles con esas características. ¿Te gustaría ver otras opciones?
---

🔹 FORMATO PARA GENÉRICA (Tipo C):
---
Tenemos varias propiedades disponibles. Para mostrarte las más adecuadas, necesito saber:

• ¿En qué zona buscás?
• ¿Para alquilar o comprar?
• ¿Qué tipo de propiedad?
---

🔹 FORMATO PARA PROPIEDADES (Tipo D):

Por cada propiedad, incluí OBLIGATORIAMENTE estas líneas (en este orden):

🏢 [Título completo]
📍 [Calle con número + Barrio completo]
💰 [Precio/mes o precio total] + Expensas [monto] (si es alquiler)
🛏️ [N] ambientes, [N] dormitorios, [N] baños
📏 [N] m²

Luego agregá SOLO si la propiedad tiene:
🚗 Cochera
🌿 Balcón/Jardín/Terraza
✨ Piscina/Parrilla/etc

Finalmente:
📸 [URL1] [URL2] [URL3]... (todas en una línea)

[línea vacía]

Al final de TODAS las propiedades:
¿Alguna de estas propiedades te interesa? Podés:\n✅ Dejar tus datos de contacto\n🔍 Ver otras opciones

⚠️ CRÍTICO: Usa EXACTAMENTE el formato de arriba con:
- `\n` para los saltos de línea (no saltos reales en el prompt)
- Emojis ✅ y 🔍 pegados al texto
- Todo entre comillas como un solo string

REGLAS IMPORTANTES:

1. **NO EXPLIQUES TU RAZONAMIENTO**:
   - NO digas "Entendido", "Para esta consulta", "Corresponde tipo X", etc.
   - NO expliques por qué elegiste una respuesta u otra
   - SOLO respondé directamente lo que el usuario necesita
   - Las clasificaciones internas NO deben aparecer en tu respuesta

2. **CIERRE OBLIGATORIO**: Debe ser EXACTAMENTE este string:
   "¿Alguna de estas propiedades te interesa? Podés:\n✅ Dejar tus datos de contacto\n🔍 Ver otras opciones"

   Usa `\n` para saltos de línea. Los emojis van pegados al texto.

3. **FOTOS**: Si la propiedad tiene fotos, incluí TODAS las URLs en UNA sola línea separadas por espacios
   Formato: 📸 [URL1] [URL2] [URL3]

4. **UBICACIONES**: NO compares barrios ni sugieras "cercanos"
   Solo mostrá propiedades que coincidan exactamente con lo pedido

5. **FILTRADO ESTRICTO**: Si el usuario pide características específicas (piscina, cochera, jardín, etc.),
   SOLO mostrá propiedades que REALMENTE tengan esas características
   Si NINGUNA propiedad cumple, informá que no hay disponibles con esas características

6. **LÍMITE**: Máximo 5 propiedades por respuesta

7. **IDIOMA**: Siempre en español

8. **TONO**: Directo y simple, sin mucha narrativa

9. **PRECIO**: Formato completo SIEMPRE:
   - Alquiler: "💰 USD 950/mes + Expensas $85.000"
   - Venta: "💰 USD 180.000"
   - Si no tiene expensas, solo mostrar el precio base

10. **INFORMACIÓN OBLIGATORIA** (mostrar siempre que esté disponible):
   - Dirección completa (calle + barrio)
   - Ambientes, dormitorios y baños
   - Superficie en m²
   - Expensas (para alquileres)

11. **INFORMACIÓN CONDICIONAL** (mostrar SOLO si la propiedad tiene):
   - Cochera/Garage
   - Balcón/Jardín/Terraza
   - Piscina, Parrilla, u otros destacados

12. **EMOJIS**: Usar emojis descriptivos para cada característica:
   - 🏢 Tipo de propiedad
   - 📍 Ubicación
   - 💰 Precio
   - 🛏️ Ambientes/dormitorios
   - 📏 Superficie
   - 🚗 Cochera (si tiene)
   - 🌿 Balcón/Jardín (si tiene)

13. **INTRO BREVE**: Cuando muestres propiedades, un solo renglón de intro
    Ejemplo: "Encontré 1 casa en Ramallo:" o "Encontré 3 departamentos en Palermo:"

14. **SALUDOS MIXTOS**: Si el usuario dice "hola" + consulta específica (ej: "hola busco casa"),
    mostrá las propiedades directamente. No hace falta saludo adicional.

15. **SALTOS DE LÍNEA**: En el cierre, usa `\n` como escape de salto de línea
    Haiku lo convertirá automáticamente en saltos de línea en la respuesta

16. **EJEMPLO COMPLETO** de cómo debe verse una propiedad:

Encontré 1 departamento en Palermo para alquilar:

🏢 Depto 2 ambientes luminoso en Palermo Soho
📍 Gorriti 4532, Piso 3° B - Palermo Soho
💰 USD 950/mes + Expensas $85.000
🛏️ 2 ambientes, 1 dormitorio, 1 baño
📏 45 m²
🌿 Balcón
📸 [URL1] [URL2] [URL3] [URL4] [URL5]

¿Alguna de estas propiedades te interesa? Podés:
✅ Dejar tus datos de contacto
🔍 Ver otras opciones

RESPONDE AHORA:`
    }
  ]
};

// 5. RETORNAR DATOS
return [{
  json: {
    haikuPayload: haikuPayload,
    propiedadesCompletas: propiedades,
    consulta: consulta,
    sessionId: body.sessionId || 'session-default'
  }
}];
```

---

## 📝 Ajustes en otros nodos

### **Nodo: "Haiku - Respuesta Completa"** (HTTP Request)

**RENOMBRAR** el nodo "Haiku - Filtrar Propiedades" a **"Haiku - Respuesta Completa"**

No requiere cambios en la configuración, solo el nombre.

---

### **Nodo: "Formatear Respuesta"** (Code)

Cambiar el código para reflejar que solo usa Haiku:

```javascript
// Verificar si hubo error en pasos anteriores
const inputData = $input.first().json;

if (inputData.error) {
  return [{ json: inputData }];
}

// VERIFICAR QUE HAIKU RESPONDIÓ
if (!inputData.content || !inputData.content[0] || !inputData.content[0].text) {
  return [{
    json: {
      error: true,
      errorType: 'HAIKU_ERROR',
      errorCode: 'ERR_AI_RESPONSE',
      response: 'Disculpa, tuve un problema al generar mi respuesta. Por favor, intentá de nuevo.',
      timestamp: new Date().toISOString()
    }
  }];
}

const haikuResponse = $input.first().json.content[0].text;
const sessionId = $('Preparar Haiku Todo-en-Uno').first().json.sessionId;
const consulta = $('Preparar Haiku Todo-en-Uno').first().json.consulta;

// Contar cuántas propiedades mostró (buscar emojis 🏢🏠🏪🏞️)
const propiedadesMostradas = (haikuResponse.match(/🏢|🏠|🏪|🏞️/g) || []).length;

return {
  json: {
    error: false,
    response: haikuResponse,
    sessionId: sessionId,
    consulta: consulta,
    propiedadesMostradas: propiedadesMostradas,
    timestamp: new Date().toISOString(),
    modelo: "claude-haiku-3.5",
    plan: "basico"
  }
};
```

---

## 🔗 Nuevas conexiones del workflow

```
Webhook Chat
  ↓
Obtener Propiedades (Dinámico)
  ↓ (success)              ↓ (error)
Preparar Haiku         Error Handler
Todo-en-Uno             GitHub
  ↓                          ↓
Haiku - Respuesta      Responder al
Completa                Webhook Chat
  ↓ (success)    ↓ (error)
Formatear        Error Handler
Respuesta        Haiku
  ↓                  ↓
Preparar Stats   Responder al
Chat              Webhook Chat
  ↓        ↓
Execute    Responder al
Insert     Webhook Chat
Chat
  ↓
Responder al
Webhook Chat
```

---

## 📊 Comparación de Respuestas

### **Consulta: "depto 2 amb palermo alquiler"**

#### Plan Profesional (Haiku + Sonnet):
```
¡Perfecto! Encontré estas opciones de departamentos de 2 ambientes en Palermo para alquilar:

🏢 Departamento luminoso en Palermo Soho
Este acogedor departamento de 2 ambientes cuenta con 1 dormitorio,
1 baño completo y 45 m² totales. Está ubicado en plena zona de Palermo
Soho, con balcón perfecto para disfrutar del aire libre. Ideal para
personas solas o parejas que buscan estar cerca de bares y restaurantes.

💰 USD 950/mes + $85.000 expensas
📸 https://ejemplo.com/foto1.jpg https://ejemplo.com/foto2.jpg

[También encontré esta opción en Belgrano, un barrio vecino a Palermo]

🏢 Departamento moderno en Belgrano
...

¿Alguna de estas propiedades te interesa? Podés:
✅ Dejar tus datos de contacto
🔍 Ver otras opciones
```

#### Plan Básico (Solo Haiku):
```
Encontré departamentos de 2 ambientes en Palermo para alquilar:

🏢 Departamento luminoso en Palermo Soho
📍 Palermo, Buenos Aires
💰 USD 950/mes + $85.000 expensas
🛏️ 2 ambientes, 1 dormitorio, 1 baño
📏 45 m²
Balcón
📸 https://ejemplo.com/foto1.jpg https://ejemplo.com/foto2.jpg

🏢 Monoambiente amplio en Palermo Hollywood
📍 Palermo, Buenos Aires
💰 USD 750/mes + $65.000 expensas
🛏️ 1 ambiente, 1 baño
📏 35 m²
📸 https://ejemplo.com/foto3.jpg

¿Alguna te interesa? Podés:
✅ Dejar tus datos de contacto
🔍 Ver otras opciones
```

**Diferencias clave:**
- ❌ No menciona Belgrano (no compara ubicaciones cercanas)
- ✅ Más directo y esquemático
- ❌ Sin contexto narrativo ("acogedor", "ideal para parejas", etc.)
- ✅ Lista de características con emojis
- ✅ Mismo formato de fotos (todas en una línea)

---

## 💰 Estimación de costos

### **Por cada consulta:**

| Concepto | Plan Básico | Plan Profesional |
|---|---|---|
| Haiku input | ~800 tokens | ~800 tokens |
| Haiku output | ~400 tokens | ~50 tokens |
| Sonnet input | - | ~1500 tokens |
| Sonnet output | - | ~500 tokens |
| **Total tokens** | ~1200 | ~2850 |
| **Costo** | ~$0.00020 | ~$0.0035 |

### **Por 1000 consultas:**
- Plan Básico: **$0.20**
- Plan Profesional: **$3.50**

**Ahorro: 17.5x más económico**

---

## ✅ Pasos para implementar

1. **Duplicar workflow existente** en N8N (ya hecho ✅)

2. **Eliminar nodos:**
   - Borrar "Preparar Respuesta Sonnet"
   - Borrar "Sonnet - Respuesta Final"
   - Borrar "Error Handler Sonnet"

3. **Renombrar nodos:**
   - "Preparar Filtrado Haiku" → "Preparar Haiku Todo-en-Uno"
   - "Haiku - Filtrar Propiedades" → "Haiku - Respuesta Completa"

4. **Actualizar código:**
   - Reemplazar código de "Preparar Haiku Todo-en-Uno" con el nuevo prompt
   - Actualizar código de "Formatear Respuesta"

5. **Reconectar flujo:**
   - "Haiku - Respuesta Completa" → "Formatear Respuesta" (directo, sin Sonnet)

6. **Actualizar Stats:**
   - En "Preparar Stats Chat", asegurar que solo cuente tokens de Haiku
   - Ajustar referencias a nodos eliminados

7. **Probar exhaustivamente:**
   - Saludos simples
   - Consultas genéricas
   - Sin coincidencias
   - Búsquedas específicas con múltiples resultados
   - Búsquedas con propiedades con fotos

8. **Crear nuevo webhook** (opcional):
   - Path: `/chat-basico` (para diferenciar del profesional)
   - O usar parámetro `plan=basico` en el webhook actual

---

## 🧪 Tests a realizar

### **Test 1: Saludo**
- Consulta: "hola"
- Esperado: Saludo + opciones de tipo de propiedad + pregunta operación

### **Test 2: Genérica**
- Consulta: "qué propiedades tenés"
- Esperado: Mensaje pidiendo más detalles (ubicación, tipo, operación)

### **Test 3: Sin coincidencias**
- Consulta: "casa en Ramallo"
- Esperado: Mensaje "No tenemos propiedades..."

### **Test 4: Específica con resultados**
- Consulta: "depto 2 amb palermo alquiler"
- Esperado: Lista de propiedades con formato correcto, fotos en una línea

### **Test 5: Verificar NO compara ubicaciones**
- Consulta: "algo en palermo"
- Esperado: Solo propiedades de Palermo, SIN mencionar Belgrano

---

## 📌 Notas importantes

1. **Mantener compatibilidad con parámetro `repo`**: El plan básico también debe soportar multi-tenancy

2. **Webhook separado o parámetro?**
   - Opción A: Nuevo webhook `/chat-basico` (más limpio)
   - Opción B: Parámetro `plan=basico` en webhook `/chat` (más flexible)

3. **Migración gradual**: Los clientes existentes del plan básico pueden migrar sin cambios en su widget

4. **Actualizar documentación de integración**: Especificar diferencias entre planes

5. **Dashboard de métricas**: Agregar campo `plan` a la tabla `chat_logs` para comparar performance

---

## 🎯 Ventajas del Plan Básico

✅ **Muy económico** (17.5x más barato que profesional)
✅ **Más rápido** (1 llamada AI vs 2)
✅ **Igual de efectivo** para catálogos simples
✅ **Perfecto para inmobiliarias pequeñas** (<50 propiedades)
✅ **Fácil de mantener** (menos complejidad)

---

## 🚀 Limitaciones vs Plan Profesional

❌ Sin comparación de ubicaciones cercanas
❌ Sin tono conversacional narrativo
❌ Sin multilenguaje automático (solo español)
❌ Respuestas más esquemáticas
❌ Límite de 50 propiedades recomendado

---

**Fecha de creación**: 2025-12-17
**Versión**: 1.0
**Autor**: Claude Sonnet 4.5
