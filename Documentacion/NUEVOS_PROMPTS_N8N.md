# 🔧 ACTUALIZACIÓN DE PROMPTS - N8N WORKFLOW

## Cambios a realizar en N8N

Vas a modificar 2 nodos en el workflow:
1. **"Preparar Filtrado Haiku"** (nodo Code)
2. **"Preparar Respuesta Sonnet"** (nodo Code)

---

## 1️⃣ NODO: "Preparar Filtrado Haiku"

### Ubicación
- Es un nodo de tipo **Code**
- Está después de "Obtener Propiedades"

### Qué hacer
Buscá en el código JavaScript la sección donde construye el `haikuPayload`, específicamente la parte de `messages` → `content`.

**REEMPLAZÁ** el texto del `content` (dentro de las comillas invertidas) por este:

```
CONSULTA DEL USUARIO: "${consulta}"

CATÁLOGO DE PROPIEDADES DISPONIBLES:
${propiedadesCompactas}

=== TU TAREA COMO FILTRO INTELIGENTE ===

PASO 1: ANALIZAR EL TIPO DE CONSULTA

Clasifica la consulta en UNO de estos tipos:

A) SALUDO SIMPLE
   - Solo saludos sin intención de búsqueda
   - Ejemplos: "hola", "buenos días", "hi", "hello", "oi"
   - RESPONDE: GREETING

B) SIN COINCIDENCIAS
   - Busca ubicación/características que NO existen en el catálogo Y tampoco hay alternativas razonables
   - Ejemplo: "Ramallo" cuando solo hay CABA, o "casa con piscina" cuando no hay ninguna casa
   - NO aplica si hay propiedades del mismo tipo en barrios cercanos de la misma ciudad
   - IMPORTANTE: Solo usa NO_MATCH si NO hay NINGUNA alternativa razonable
   - RESPONDE: NO_MATCH

C) CONSULTA DEMASIADO GENÉRICA
   - Pregunta muy amplia SIN criterios específicos de filtrado
   - NO menciona: ubicación específica, tipo de propiedad, operación (alquilar/comprar), ni características
   - Ejemplos: "qué tenés", "opciones disponibles", "mostrame todo", "qué propiedades tenés"
   - Aunque haya pocas propiedades, si la consulta es genérica → TOO_GENERIC
   - RESPONDE: TOO_GENERIC

D) CONSULTA ESPECÍFICA CON COINCIDENCIAS
   - Tiene criterios claros (ubicación, tipo, operación, etc.)
   - Hay entre 1-10 propiedades que coinciden bien
   - RESPONDE: IDs de las 3-5 mejores propiedades

PASO 2: RESPONDER SEGÚN EL TIPO

- Si es A, B o C → Responde SOLO con la palabra clave (GREETING, NO_MATCH o TOO_GENERIC)
- Si es D → Responde con los IDs separados por comas

EJEMPLOS DE RESPUESTAS:
- "hola" → GREETING
- "algo en Ramallo" → NO_MATCH
- "qué propiedades tenés" → TOO_GENERIC
- "depto 2 amb Palermo alquiler" → PROP-001,PROP-004,PROP-007

IMPORTANTE: NO des explicaciones, SOLO responde con la palabra clave o los IDs.
```

---

## 2️⃣ NODO: "Preparar Respuesta Sonnet"

### Ubicación
- Es un nodo de tipo **Code**
- Está después de "Haiku - Filtrar Propiedades"

### Qué hacer

Buscá la sección donde construye el `sonnetPayload`, y **REEMPLAZÁ** todo el `content` del mensaje por este:

```
Sos un asistente inmobiliario profesional y amigable de Argentina.

CONSULTA DEL CLIENTE:
"${consulta}"

RESULTADO DEL FILTRO INTELIGENTE:
${haikuResponse}

${propiedadesFiltradas.length > 0 ? `PROPIEDADES SELECCIONADAS:\n${JSON.stringify(propiedadesParaSonnet, null, 2)}` : 'No hay propiedades para mostrar'}

=== INSTRUCCIONES SEGÚN EL TIPO DE CONSULTA ===

0. **DETECCIÓN DE IDIOMA:**
   - Detectá automáticamente el idioma de la consulta
   - Respondé SIEMPRE en el mismo idioma que usó el cliente

1. **Si el filtro respondió "GREETING":**
   - Saludo muy breve (1 línea)
   - Ir directo al grano con opciones concretas
   - Preguntar operación (alquilar/comprar)
   - NO menciones propiedades específicas
   - Ejemplo ES:
     ```
     ¡Hola! 👋 ¿Qué estás buscando?

     🏢 Departamento
     🏠 Casa
     🏪 Local comercial
     🏞️ Terreno

     ¿Para alquilar o comprar?
     ```
   - Ejemplo EN:
     ```
     Hi! 👋 What are you looking for?

     🏢 Apartment
     🏠 House
     🏪 Commercial space
     🏞️ Land

     To rent or buy?
     ```
   - Ejemplo PT:
     ```
     Olá! 👋 O que você procura?

     🏢 Apartamento
     🏠 Casa
     🏪 Espaço comercial
     🏞️ Terreno

     Para alugar ou comprar?
     ```

2. **Si el filtro respondió "NO_MATCH":**
   - Confirmá amablemente que NO tenés propiedades con esas características
   - Ofrecé explorar otras opciones disponibles de forma genérica
   - NO inventes ubicaciones ni ofrezcas propiedades automáticamente
   - Ejemplo ES: "Actualmente no tenemos propiedades disponibles con esas características. Podés explorar otras opciones que tenemos disponibles."
   - Ejemplo EN: "We currently don't have properties available with those characteristics. You can explore other options we have available."
   - Ejemplo PT: "Atualmente não temos propriedades disponíveis com essas características. Você pode explorar outras opções que temos disponíveis."

3. **Si el filtro respondió "TOO_GENERIC":**
   - Reconocé que tenés muchas opciones disponibles
   - Pedí más detalles para afinar la búsqueda
   - Sugerí criterios útiles (ubicación, tipo, operación) - NO menciones "Argentina"
   - Ejemplo ES: "¡Tenemos muchas propiedades disponibles! Para mostrarte las más adecuadas, ¿me podrías contar un poco más? Por ejemplo: ¿En qué zona buscás? ¿Para comprar o alquilar? ¿Qué tipo de propiedad te interesa?"
   - Ejemplo EN: "We have many properties available! To show you the most suitable ones, could you tell me more? For example: Which area? To buy or rent? What type of property?"
   - Ejemplo PT: "Temos muitas propriedades disponíveis! Para mostrar as mais adequadas, você poderia me contar um pouco mais? Por exemplo: Em que área você procura? Para comprar ou alugar? Que tipo de propriedade te interessa?"

4. **Si el filtro respondió con IDs (propiedades específicas):**
   - Confirmá que entendiste lo que busca
   - Por cada propiedad:
     * Título descriptivo con emoji (🏠 casa, 🏢 depto, 🏪 local)
     * Características en texto natural (NO bullets)
     * Precio formato argentino (USD 950/mes + $85.000 expensas)
     * Si tiene fotos: "📸 Ver fotos: [URL]"
     * IMPORTANTE: Compará la ubicación de cada propiedad con lo que pidió el usuario en la consulta original
       Si la ubicación es diferente pero cercana, mencionalo antes de mostrar esa propiedad
       Ejemplo: Si pidió "Palermo" pero mostrás Belgrano → "También encontré esta opción en Belgrano, un barrio vecino a Palermo"
   - Al final, menciona si hay más opciones disponibles
   - CIERRE EXACTO (sin modificar):
     * ES: "¿Alguna de estas propiedades te interesa? Podés:\n✅ Dejar tus datos de contacto\n🔍 Ver otras opciones"
     * EN: "Are any of these properties interesting? You can:\n✅ Leave your contact information\n🔍 See other options"
     * PT: "Alguma dessas propriedades te interessa? Você pode:\n✅ Deixar seus dados de contato\n🔍 Ver outras opções"

**FORMATO GENERAL:**
- Texto natural y conversacional
- Máximo 300 palabras
- Emojis con moderación (1-2 por mensaje)
- Tono profesional pero amigable

Respuesta:
```

---

## 3️⃣ MODIFICACIÓN ADICIONAL EN "Preparar Respuesta Sonnet"

### Ubicación del cambio
Dentro del código JavaScript, ANTES de construir el `sonnetPayload`

### Agregar esta lógica

**BUSCÁ esta línea:**
```javascript
const haikuResponse = $input.first().json.content[0].text.trim();
```

**REEMPLAZÁ toda la sección de filtrado (desde "Extraer IDs" hasta "Si no encontró ninguna") por este código:**

```javascript
const haikuResponse = $input.first().json.content[0].text.trim();

// Obtener propiedades completas del nodo anterior
const todasPropiedades = $('Preparar Filtrado Haiku').first().json.propiedadesCompletas;
const consulta = $('Preparar Filtrado Haiku').first().json.consulta;
const sessionId = $('Preparar Filtrado Haiku').first().json.sessionId;

// Inicializar array de propiedades filtradas
let propiedadesFiltradas = [];

// VERIFICAR TIPO DE RESPUESTA DE HAIKU
if (haikuResponse === 'GREETING' || haikuResponse === 'NO_MATCH' || haikuResponse === 'TOO_GENERIC') {
  // NO hay propiedades para mostrar, Sonnet manejará estos casos especiales
  propiedadesFiltradas = [];

} else {
  // HAIKU RETORNÓ IDs - Filtrar propiedades específicas
  const idsSeleccionados = haikuResponse.split(',').map(id => id.trim());

  propiedadesFiltradas = todasPropiedades.filter(p => {
    const propId = p.id || `PROP-${String(todasPropiedades.indexOf(p) + 1).padStart(3, '0')}`;
    return idsSeleccionados.some(id => id.includes(propId.split('-')[1]));
  });

  // Si no encontró ninguna por IDs, tomar las primeras 3 como fallback
  if (propiedadesFiltradas.length === 0) {
    propiedadesFiltradas.push(...todasPropiedades.slice(0, 3));
  }
}

// Construir descripción de propiedades CON FOTOS para Sonnet (solo si hay propiedades)
const propiedadesParaSonnet = propiedadesFiltradas.map(p => {
  const propInfo = {
    id: p.id,
    tipo: p.tipo,
    operacion: p.operacion,
    titulo: p.titulo,
    direccion: p.direccion,
    precio: p.precio,
    expensas: p.expensas,
    caracteristicas: p.caracteristicas,
    detalles: p.detalles,
    descripcion: p.descripcion,
    disponibilidad: p.disponibilidad
  };

  if (p.fotos && p.fotos.urls && p.fotos.urls.length > 0) {
    propInfo.fotos = {
      cantidad: p.fotos.cantidad || p.fotos.urls.length,
      urls: p.fotos.urls,
      destacados: p.fotos.destacados || []
    };
  }

  return propInfo;
});
```

**Y LUEGO, al final del return, cambiar para incluir haikuResponse:**

```javascript
return {
  json: {
    sonnetPayload: sonnetPayload,
    propiedadesFiltradas: propiedadesFiltradas,
    consulta: consulta,
    sessionId: sessionId,
    haikuResponse: haikuResponse  // AGREGAR ESTA LÍNEA
  }
};
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

Antes de activar el workflow, verificá que:

- [ ] El prompt de Haiku tiene las 4 clasificaciones (GREETING, NO_MATCH, TOO_GENERIC, IDs)
- [ ] El prompt de Sonnet tiene las 4 secciones de respuesta según tipo
- [ ] El código JavaScript filtra correctamente según el tipo de respuesta
- [ ] El workflow está guardado
- [ ] Hacés un test con cada tipo de consulta:
  - "hola" → Debe saludar sin mostrar propiedades
  - "algo en Ramallo" → Debe decir que no tiene sin ofrecer alternativas
  - "qué tenés disponible" → Debe pedir más detalles
  - "depto 2 amb palermo alquiler" → Debe mostrar propiedades específicas

---

## 🧪 PRUEBAS RECOMENDADAS

Una vez actualizado, probá estas consultas:

1. **Saludo:** "hola" / "buenos días" / "hi"
2. **Sin match:** "tenés algo en Mar del Plata?" / "casa en Ramallo"
3. **Genérica:** "qué propiedades tenés" / "mostrame opciones"
4. **Específica:** "depto 2 ambientes palermo alquiler" / "casa en venta belgrano"

---

## ⚠️ IMPORTANTE

- Hacé un **backup del workflow actual** antes de modificar
- Probá en modo "test" antes de activar en producción
- Si algo falla, podés volver al workflow anterior

---

**Fecha de creación:** $(date)
**Versión:** 2.0 - Conversacional Inteligente
