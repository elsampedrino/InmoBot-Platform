# 🤖 WORKFLOW 1 - TESTING BÁSICO

## 🎯 ¿QUÉ HACE ESTE WORKFLOW?

Este workflow demuestra la funcionalidad básica del bot:

1. ✅ Lee el archivo `propiedades_FINAL.json`
2. ✅ Parsea las propiedades
3. ✅ Filtra según criterios (ejemplo: deptos de 2 ambientes)
4. ✅ Formatea el resultado para mostrarlo
5. ✅ Genera URLs de Cloudinary automáticamente

**Es un MVP sin Claude API** - solo para verificar que todo funciona.

---

## 📦 IMPORTAR EL WORKFLOW

### Paso 1: Copiar el archivo JSON

El archivo es: `n8n_workflow_1_testing.json`

### Paso 2: En N8N

1. Abrí N8N: http://localhost:5678
2. Click en el **+** (arriba a la derecha) → **Import from File**
3. O también: **Ctrl+O** (Import)
4. Pegá el contenido del JSON
5. Click **Import**

¡Listo! El workflow aparece en tu canvas.

---

## ⚙️ CONFIGURAR ANTES DE EJECUTAR

### 🔧 Nodo: "Leer Propiedades JSON"

**IMPORTANTE:** Ajustar la ruta del archivo según dónde tengas el JSON.

**Click en el nodo** → En "File Path":

```
Opción 1 (recomendada): Ruta absoluta
/ruta/completa/a/tu/proyecto/propiedades_FINAL.json

Ejemplo Windows:
C:/Desarrollo/InmoBot/CHATBOT-INMOBILIARIA-VCODE/propiedades_FINAL.json

Ejemplo Linux/Mac:
/home/tuusuario/bot-inmobiliaria/propiedades_FINAL.json
```

**¿Cómo saber la ruta completa?**

En tu terminal de VS Code:
```bash
# Windows (PowerShell)
pwd

# Linux/Mac
pwd
```

Eso te da la ruta actual. Agregá `/propiedades_FINAL.json` al final.

---

## 🚀 EJECUTAR EL WORKFLOW

### Primera ejecución:

1. Click en **"Execute Workflow"** (botón arriba)
2. Mirá cómo fluyen los datos por cada nodo
3. Al final verás el resultado formateado

### Resultado esperado:

```
✅ PROPIEDAD ENCONTRADA

📋 ID: PROP-001
🏠 Tipo: Departamento
💰 Precio: USD 950/mes
📍 Dirección: Gorriti 4532, Piso 3° B, Palermo Soho
🛏️ Ambientes: 2
🚪 Dormitorios: 1
🚿 Baños: 1
📏 Superficie: 45 m²

📸 Fotos:
🔗 https://res.cloudinary.com/dikb9wzup/image/upload/fotos_demo/depto-palermo-001/foto01.jpg
🔗 https://res.cloudinary.com/dikb9wzup/image/upload/fotos_demo/depto-palermo-001/foto02.jpg

📝 Descripción:
Hermoso departamento de 2 ambientes en el corazón de Palermo Soho...
```

---

## 🎨 ENTENDER EL FLUJO

### Nodo 1: Manual Trigger
- **Qué hace:** Dispara el workflow manualmente (para testing)
- **Cuándo usarlo:** Cada vez que quieras probar

### Nodo 2: Leer Propiedades JSON
- **Qué hace:** Lee el archivo JSON del disco
- **Output:** Contenido del archivo en formato binario

### Nodo 3: Parsear y Separar
- **Qué hace:** Convierte el JSON en items individuales (1 propiedad = 1 item)
- **Output:** 4 items (las 4 propiedades)
- **Código importante:** 
  ```javascript
  // Lee el binario y lo convierte a JSON
  const jsonContent = Buffer.from($input.first().binary.data.data, 'base64').toString('utf8');
  const data = JSON.parse(jsonContent);
  
  // Retorna cada propiedad como un item separado
  return data.propiedades.map(prop => ({
    json: prop
  }));
  ```

### Nodo 4: Filtrar
- **Qué hace:** Filtra propiedades según criterios
- **Criterios actuales:**
  - Tipo = "Departamento"
  - Ambientes = 2
- **Output:** Solo las propiedades que cumplen (PROP-001 en este caso)

### Nodo 5a: Formatear Resultado (TRUE)
- **Qué hace:** Si encuentra resultados, los formatea bonito
- **Genera URLs de Cloudinary automáticamente**

### Nodo 5b: Sin Resultados (FALSE)
- **Qué hace:** Si no encuentra nada, muestra mensaje de error

---

## 🔧 PERSONALIZAR LOS FILTROS

### Cambiar criterios de búsqueda:

**Click en el nodo "Filtrar"** → Modificá las condiciones:

**Ejemplo 1: Buscar casas**
```
Tipo = "Casa"
```

**Ejemplo 2: Buscar propiedades de más de 3 ambientes**
```
Ambientes > 3
```

**Ejemplo 3: Buscar alquileres baratos**
```
Operación = "Alquiler"
AND
Precio.valor < 1000
```

**Ejemplo 4: Buscar con cochera**
```
Detalles.cochera = true
```

---

## 🧪 CASOS DE PRUEBA

### Test 1: Depto 2 ambientes (por defecto)
**Configuración actual**
**Resultado esperado:** PROP-001 (Palermo)

### Test 2: Depto 3 ambientes
**Modificar filtro:**
- Tipo = "Departamento"
- Ambientes = 3

**Resultado esperado:** PROP-002 (Belgrano)

### Test 3: Casa
**Modificar filtro:**
- Tipo = "Casa"

**Resultado esperado:** PROP-003 (Villa Urquiza)

### Test 4: Local comercial
**Modificar filtro:**
- Tipo = "Local"

**Resultado esperado:** PROP-004 (Microcentro)

### Test 5: Propiedades en venta
**Modificar filtro:**
- Operación = "Venta"

**Resultado esperado:** PROP-002 y PROP-003

---

## 🐛 TROUBLESHOOTING

### Error: "File not found"
**Problema:** La ruta del JSON está mal
**Solución:**
1. Verificá la ruta completa con `pwd` en terminal
2. Usá barras normales `/` (no `\` en Windows)
3. Asegurate que el archivo existe en esa ubicación

### Error: "Cannot read property 'data'"
**Problema:** El nodo "Leer" no está configurado correctamente
**Solución:**
1. El nodo debe ser "Read Binary File"
2. Verificá que el tipo de operación sea "Read File"

### No aparece ninguna propiedad
**Problema:** Los filtros son muy restrictivos
**Solución:**
1. Revisá los valores de los filtros
2. Click en el nodo "Parsear" para ver todas las propiedades disponibles
3. Verificá que los valores coincidan (mayúsculas/minúsculas)

### Las URLs de Cloudinary no funcionan
**Problema:** El Cloud Name está hardcodeado en el workflow
**Solución:**
1. Click en nodo "Formatear Resultado"
2. Buscá `dikb9wzup` y reemplazá con tu Cloud Name si es diferente
3. En tu caso es `dikb9wzup` así que debería funcionar

---

## 📊 VER LOS DATOS EN CADA PASO

Para entender qué pasa en cada nodo:

1. Ejecutá el workflow
2. Click en cualquier nodo
3. Mirá la pestaña "OUTPUT" abajo
4. Ahí ves exactamente qué datos recibió/generó ese nodo

**Tip:** Click en el número verde que aparece arriba de cada nodo (ej: "4") para ver cuántos items procesó.

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de pasar al Workflow 2:

- [ ] El workflow se importó correctamente
- [ ] La ruta del JSON está configurada
- [ ] Ejecuta sin errores
- [ ] Encuentra la propiedad PROP-001
- [ ] Las URLs de Cloudinary se generan correctamente
- [ ] Probaste modificar los filtros
- [ ] Entendés el flujo de datos

---

## 🎓 LO QUE APRENDISTE

✅ Cómo leer archivos en N8N  
✅ Cómo parsear JSON  
✅ Cómo filtrar datos  
✅ Cómo formatear output  
✅ Cómo usar expresiones de N8N (`={{ $json.campo }}`)  
✅ Cómo generar URLs de Cloudinary dinámicamente  

---

## 🚀 PRÓXIMO PASO

Cuando este workflow funcione perfecto:

**Workflow 2:** Vamos a agregar Claude API para que:
- Entienda consultas en lenguaje natural
- Busque propiedades inteligentemente
- Responda de forma conversacional
- Maneje múltiples criterios a la vez

---

## 💡 NOTAS IMPORTANTES

### Sobre las rutas de archivos:

En **producción** (cuando deployes), vas a querer:
- Subir el JSON a un servidor
- Usar HTTP Request en vez de Read File
- O migrar a Airtable

Pero para **desarrollo local**, leer del disco es perfecto.

### Sobre los filtros:

Este workflow usa filtros "hardcodeados" (fijos). En el Workflow 2, Claude API va a determinar qué filtros aplicar según lo que el usuario pida.

---

¿Funciona todo? ¡Avisame cuando lo tengas andando! 🎉
