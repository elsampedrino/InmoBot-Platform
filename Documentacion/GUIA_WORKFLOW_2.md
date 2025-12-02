# 🤖 WORKFLOW 2 - CON CLAUDE API

## 🎯 ¿QUÉ HACE ESTE WORKFLOW?

**El upgrade del WF1:** Ahora Claude entiende lenguaje natural y busca inteligentemente.

### Diferencias con WF1:

| WF1 (básico) | WF2 (con IA) |
|--------------|--------------|
| Filtros hardcodeados | Claude analiza la consulta |
| "Tipo = Departamento" | "Busco un depto en Palermo" |
| 1 criterio a la vez | Múltiples criterios simultáneos |
| Respuesta técnica | Respuesta conversacional |

---

## 🚀 IMPORTAR EL WORKFLOW

### Paso 1: Abrir N8N
```
http://localhost:5678
```

### Paso 2: Importar
1. **Ctrl+O** o botón "Import"
2. Pegá el contenido de `n8n_workflow_2_claude_api.json`
3. Click "Import"

---

## 🔑 CONFIGURAR CLAUDE API

### Paso 1: Obtener API Key de Anthropic

1. Andá a: https://console.anthropic.com
2. Login o Create Account
3. Settings → API Keys
4. "Create Key"
5. Copiá la key (empieza con `sk-ant-...`)

### Paso 2: Agregar credenciales en N8N

1. En N8N, arriba a la derecha: **Credentials** (ícono de llave)
2. Click **"Add Credential"**
3. Buscar: **"Anthropic API"**
4. Pegá tu API Key
5. Nombre: "Anthropic - Claude API"
6. **Save**

### Paso 3: Conectar al nodo

1. Click en el nodo **"Claude - Búsqueda Inteligente"**
2. En "Credential to connect with": Seleccionar tu credential
3. Save

---

## ⚙️ CONFIGURACIÓN INICIAL

### Ajustar URL de propiedades:

En el nodo **"Obtener Propiedades"**:
```
http://192.168.0.10:8000/propiedades_demo.json
```

(Reemplazá la IP si usás otra)

### Verificar que http-server esté corriendo:

En tu terminal de VS Code:
```powershell
npx http-server -p 8000 -c-1
```

---

## 💬 PROBAR EL WORKFLOW

### Test 1: Búsqueda básica

Nodo "Simular Consulta Usuario" → Cambiar consulta a:
```
Busco un departamento de 2 ambientes en Palermo para alquilar
```

**Execute Workflow**

**Resultado esperado:**
- Encuentra PROP-001
- Respuesta conversacional de Claude
- Detalles completos de la propiedad

---

### Test 2: Búsqueda por precio

```
Necesito algo para comprar por menos de 200.000 dólares
```

**Resultado esperado:**
- Encuentra PROP-002 (Belgrano - USD 185k)

---

### Test 3: Búsqueda por características

```
Quiero una casa con jardín y cochera
```

**Resultado esperado:**
- Encuentra PROP-003 (Villa Urquiza)
- Claude explica por qué coincide

---

### Test 4: Local comercial

```
Busco un local en microcentro sobre avenida
```

**Resultado esperado:**
- Encuentra PROP-004
- Claude menciona la vidriera y alto tránsito

---

### Test 5: Consulta compleja (múltiples criterios)

```
Necesito un departamento de 3 ambientes con cochera que acepte mascotas en Belgrano
```

**Resultado esperado:**
- Claude analiza TODOS los criterios
- Encuentra PROP-002 (cumple todo)
- Respuesta detallada explicando el match

---

### Test 6: Sin resultados

```
Busco un penthou se 10 ambientes con pileta olímpica
```

**Resultado esperado:**
- Claude dice que no hay resultados exactos
- Sugiere alternativas (la casa con jardín, deptos amplios)

---

## 🧠 CÓMO FUNCIONA EL PROMPT DE CLAUDE

El prompt que diseñé hace que Claude:

### 1. Extraiga criterios de búsqueda
```
Usuario: "Busco un depto 2 amb en Palermo"

Claude identifica:
- Tipo: Departamento
- Ambientes: 2
- Zona: Palermo
- Operación: No especificada (asume alquiler o ambas)
```

### 2. Filtre propiedades
```
Claude analiza TODAS las propiedades y determina:
- Alta relevancia: Coincide perfectamente
- Media relevancia: Coincide parcialmente
- Baja relevancia: Podría interesar
```

### 3. Genere respuesta conversacional
```
❌ MAL: "Se encontró 1 resultado. ID: PROP-001"

✅ BIEN: "¡Perfecto! Tengo un hermoso departamento de 2 ambientes 
         en Palermo Soho que te va a encantar. Está a USD 950/mes,
         muy luminoso con balcón..."
```

### 4. Incluya datos relevantes
- Precio claro
- Ubicación específica
- Características destacadas
- URLs de fotos

### 5. Ofrezca siguiente paso
- Agendar visita
- Más información
- Ver otras opciones

---

## 🎨 PERSONALIZAR EL PROMPT

### Modificar el tono:

Click en **"Claude - Búsqueda Inteligente"** → Editar el prompt:

**Más formal:**
```
Sos un asesor inmobiliario profesional...
```

**Más casual:**
```
Sos un amigo que ayuda a buscar deptos...
```

**Más técnico:**
```
Sos un especialista en mercado inmobiliario...
```

### Agregar reglas específicas:

```
REGLAS ADICIONALES:
- Nunca ofrecer propiedades sobre el presupuesto del cliente
- Siempre mencionar expensas si es alquiler
- Destacar si acepta mascotas
- Priorizar propiedades disponibles inmediatamente
```

### Limitar resultados:

```
- Incluye máximo 2 propiedades (en vez de 3)
```

---

## 📊 ESTRUCTURA DEL FLUJO

```
1. Usuario consulta
   "Busco depto 2 amb Palermo"
   ↓
2. Obtiene propiedades (HTTP)
   [PROP-001, PROP-002, PROP-003, PROP-004]
   ↓
3. Claude analiza
   - Extrae: tipo=depto, amb=2, zona=Palermo
   - Filtra: encuentra PROP-001
   - Evalúa relevancia: ALTA
   ↓
4. Claude genera respuesta
   "¡Perfecto! Tengo justo lo que buscás..."
   ↓
5. Procesa y enriquece
   - Parsea JSON de Claude
   - Agrega datos completos de propiedades
   - Genera URLs de fotos
   ↓
6. Formatea resultado final
   - Respuesta conversacional
   - Detalles de cada propiedad
   - Fotos con URLs listas
   - Call to action
```

---

## 🔧 TROUBLESHOOTING

### Error: "Credential not found"
**Problema:** No configuraste las credenciales de Anthropic
**Solución:** 
1. Arriba derecha: Credentials
2. Add Credential → Anthropic API
3. Pegá tu API Key

### Error: "Invalid API key"
**Problema:** La API key está mal o expiró
**Solución:**
1. Verificá en console.anthropic.com
2. Regenerá la key si es necesario
3. Actualizá en N8N

### Error: "HTTP Request failed"
**Problema:** El servidor HTTP no está corriendo
**Solución:**
```powershell
cd C:/Desarrollo/InmoBot/ChatBOT-Inmobiliaria-VCode
npx http-server -p 8000 -c-1
```

### Claude no encuentra resultados correctos
**Problema:** El prompt no está bien calibrado
**Solución:**
1. Revisá que las propiedades tengan todos los campos
2. Ajustá el prompt para ser más específico
3. Agregá ejemplos en el prompt

### La respuesta no viene en JSON
**Problema:** Claude a veces responde en texto plano
**Solución:** El nodo "Procesar Respuesta" ya maneja esto
- Si viene JSON → lo parsea
- Si viene texto → lo usa tal cual

---

## 💰 COSTOS DE CLAUDE API

### Claude Sonnet 4:
- **Input:** ~$3 USD por millón de tokens
- **Output:** ~$15 USD por millón de tokens

### Estimación por consulta:
```
Tokens de entrada (prompt + propiedades):  ~1,500 tokens
Tokens de salida (respuesta de Claude):    ~500 tokens

Costo por consulta: ~$0.01 USD (1 centavo)
```

### Para 1000 consultas/mes:
```
Costo mensual: ~$10 USD
```

**Súper accesible** para el MVP.

---

## 🎯 CASOS DE USO AVANZADOS

### 1. Comparación de propiedades

**Consulta:**
```
Comparame las opciones de departamentos para alquiler
```

**Claude responde:**
- Lista las 2 opciones (PROP-001 y PROP-004 si es local)
- Compara precios, ubicación, características
- Sugiere cuál es mejor según necesidades comunes

### 2. Presupuesto específico

**Consulta:**
```
Tengo 180 mil dólares, ¿qué puedo comprar?
```

**Claude responde:**
- Encuentra PROP-002 (USD 185k - un poco más)
- Explica que está apenas sobre presupuesto
- Sugiere negociar o buscar financiación

### 3. Requerimientos específicos

**Consulta:**
```
Tengo 2 perros grandes, necesito lugar con espacio
```

**Claude responde:**
- Identifica: mascotas=sí, espacio=jardín/terraza
- Encuentra PROP-003 (casa con jardín)
- Destaca que acepta mascotas y tiene jardín amplio

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de pasar al Workflow 3:

- [ ] API Key de Anthropic configurada
- [ ] Credenciales conectadas al nodo
- [ ] HTTP server corriendo
- [ ] Test 1: Búsqueda básica funciona
- [ ] Test 2: Búsqueda por precio funciona
- [ ] Test 3: Búsqueda por características funciona
- [ ] Test 4: Sin resultados sugiere alternativas
- [ ] Claude responde conversacionalmente (no técnico)
- [ ] URLs de Cloudinary se generan correctamente
- [ ] Entendés cómo modificar el prompt

---

## 🚀 PRÓXIMO PASO

**Workflow 3:** Integración con WhatsApp
- Webhook real
- Conversaciones persistentes
- Captura automática de leads
- Recordatorios

---

## 💡 TIPS FINALES

### Mejorar las respuestas de Claude:

1. **Agregar contexto de negocio:**
```
La inmobiliaria se especializa en propiedades premium
en zonas consolidadas de CABA...
```

2. **Definir tono de marca:**
```
Responde como: [joven y cercano / profesional / experto]
```

3. **Incluir promociones:**
```
Menciona si hay descuentos o promociones activas
```

4. **Sugerir upsells:**
```
Si buscan algo económico, menciona opciones premium cercanas
```

---

¡Probalo y avisame cómo funciona! 🎉
