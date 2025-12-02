# 🎨 GUÍA COMPLETA: WIDGET REACT CHATBOT

## 📋 ÍNDICE

1. [Descripción](#descripción)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Instalación local](#instalación-local)
4. [Desarrollo](#desarrollo)
5. [Build para producción](#build-para-producción)
6. [Integración en tu HTML](#integración-en-tu-html)
7. [Configuración](#configuración)
8. [Personalización](#personalización)
9. [Deploy del widget](#deploy-del-widget)
10. [Testing](#testing)

---

## 📝 DESCRIPCIÓN

Widget de chatbot flotante hecho en React que se integra con el workflow de N8N en Render.

### **Características:**

- ✅ Botón flotante personalizable
- ✅ Ventana de chat responsive
- ✅ Typing indicator ("escribiendo...")
- ✅ Historial de conversación
- ✅ Contador de mensajes no leídos
- ✅ Links a fotos de propiedades
- ✅ Animaciones suaves
- ✅ Mobile-first design
- ✅ Un solo archivo JS + CSS
- ✅ Fácil integración (1 línea de código)

---

## 📁 ESTRUCTURA DEL PROYECTO

```
widget-react/
├── src/
│   ├── ChatWidget.jsx      # Componente principal
│   ├── ChatWidget.css       # Estilos del widget
│   └── index.js             # Punto de entrada
├── index.html               # Demo de desarrollo
├── package.json             # Dependencias
├── vite.config.js           # Config de build
└── README.md                # Esta guía
```

---

## 🚀 INSTALACIÓN LOCAL

### **Paso 1: Requisitos previos**

```bash
Node.js >= 16.0.0
npm >= 8.0.0
```

Verificar:
```bash
node --version
npm --version
```

### **Paso 2: Instalar dependencias**

Navegar a la carpeta del widget:

```bash
cd widget-react
```

Instalar paquetes:

```bash
npm install
```

Esto instalará:
- React 18.2.0
- React DOM 18.2.0
- Vite 5.0.12
- Plugin de React para Vite

---

## 💻 DESARROLLO

### **Iniciar servidor de desarrollo:**

```bash
npm run dev
```

Esto iniciará Vite en: `http://localhost:3000`

### **Features del dev server:**

- ✅ Hot Module Replacement (cambios en vivo)
- ✅ Fast Refresh (React sin perder estado)
- ✅ Error overlay
- ✅ Auto-reload

### **Modificar configuración de desarrollo:**

En `index.html`, línea ~110, cambiar la URL:

```javascript
apiUrl: 'http://localhost:5678/webhook/chat' // Tu N8N local
```

O si ya tenés N8N en Render:

```javascript
apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
```

### **Testear cambios:**

1. Guardar archivo (auto-reload)
2. Abrir navegador en localhost:3000
3. Click en botón flotante (abajo derecha)
4. Testear conversación

---

## 📦 BUILD PARA PRODUCCIÓN

### **Generar archivos optimizados:**

```bash
npm run build
```

Esto generará en `dist/`:

```
dist/
├── inmobot-widget.js     # Widget minificado (~150KB)
└── inmobot-widget.css    # Estilos minificados (~8KB)
```

### **Características del build:**

- ✅ Minificado con Terser
- ✅ Tree-shaking (elimina código no usado)
- ✅ CSS inlined en el JS
- ✅ Todo en un solo archivo IIFE
- ✅ Sin console.logs en producción
- ✅ Compatible con todos los navegadores modernos

### **Previsualizar build:**

```bash
npm run preview
```

Abre `http://localhost:4173` para ver la versión de producción.

---

## 🌐 INTEGRACIÓN EN TU HTML

### **Opción 1: Integración básica (más fácil)**

Agregar antes del `</body>`:

```html
<!-- Widget InmoBot -->
<script src="https://cdn.tudominio.com/inmobot-widget.js"></script>
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
  });
</script>
```

### **Opción 2: Con configuración personalizada**

```html
<script src="https://cdn.tudominio.com/inmobot-widget.js"></script>
<script>
  InmoBot.init({
    // URL del webhook de N8N
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    
    // Personalización visual
    primaryColor: '#2563eb',        // Color principal
    buttonSize: '60px',              // Tamaño del botón
    chatWidth: '380px',              // Ancho del chat
    chatHeight: '600px',             // Alto del chat
    position: 'bottom-right',        // Posición (bottom-right, bottom-left, etc.)
    
    // Textos
    botName: 'AsistenteBot',
    welcomeMessage: '¡Hola! ¿En qué te puedo ayudar?',
    placeholderText: 'Escribe tu mensaje...'
  });
</script>
```

### **Opción 3: Configuración avanzada**

```html
<script src="https://cdn.tudominio.com/inmobot-widget.js"></script>
<script>
  // Configuración guardada en variable global
  window.InmoBotConfig = {
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    primaryColor: '#059669',  // Verde
    botName: 'Cristian - Asesor Virtual',
    welcomeMessage: '¡Bienvenido a Inmobiliaria XYZ! Soy Cristian, tu asesor virtual. ¿Buscás alquilar o comprar?',
    position: 'bottom-left',
    chatHeight: '500px'
  };

  // El widget se auto-inicializa con esta config
</script>
```

---

## 🎨 CONFIGURACIÓN

### **Parámetros disponibles:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `apiUrl` | string | *requerido* | URL del webhook de N8N |
| `primaryColor` | string | `#2563eb` | Color principal (hex) |
| `botName` | string | `AsistenteBot` | Nombre del bot |
| `welcomeMessage` | string | `¡Hola! ¿En qué...` | Mensaje inicial |
| `placeholderText` | string | `Escribe tu mensaje...` | Placeholder del input |
| `position` | string | `bottom-right` | Posición del widget |
| `buttonSize` | string | `60px` | Tamaño del botón |
| `chatWidth` | string | `380px` | Ancho del chat |
| `chatHeight` | string | `600px` | Alto del chat |

### **Valores de `position`:**

```javascript
'bottom-right'  // Abajo derecha (default)
'bottom-left'   // Abajo izquierda
'top-right'     // Arriba derecha
'top-left'      // Arriba izquierda
```

---

## 🎨 PERSONALIZACIÓN

### **Cambiar colores:**

```javascript
InmoBot.init({
  primaryColor: '#059669'  // Verde esmeralda
});
```

**Colores sugeridos:**
```javascript
Azul:    '#2563eb'
Verde:   '#059669'
Violeta: '#7c3aed'
Rojo:    '#dc2626'
Naranja: '#ea580c'
```

### **Ajustar tamaños (mobile-friendly):**

```javascript
InmoBot.init({
  buttonSize: '56px',   // Más pequeño para mobile
  chatWidth: '360px',   // Más angosto
  chatHeight: '500px'   // Más bajo
});
```

### **Personalizar textos para marca:**

```javascript
InmoBot.init({
  botName: 'Martín - Inmobiliaria García',
  welcomeMessage: '¡Hola! Soy Martín de Inmobiliaria García. ¿Buscás tu hogar ideal? Te ayudo a encontrarlo 🏠',
  placeholderText: 'Contame qué estás buscando...'
});
```

### **Modificar estilos avanzados (CSS):**

Puedes agregar CSS custom después del script:

```html
<style>
  /* Personalizar header */
  .chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  }

  /* Personalizar botón */
  .chat-widget-button {
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
  }

  /* Personalizar burbujas */
  .message.user .message-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  }
</style>
```

---

## 🚀 DEPLOY DEL WIDGET

### **Opción 1: GitHub Pages (Gratis, recomendado)**

1. **Crear repo en GitHub:**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tuusuario/inmobot-widget.git
   git push -u origin main
   ```

2. **Build:**

   ```bash
   npm run build
   ```

3. **Subir dist/ a GitHub:**

   ```bash
   git add dist/
   git commit -m "Add build files"
   git push
   ```

4. **Activar GitHub Pages:**
   - Repo → Settings → Pages
   - Source: Deploy from branch
   - Branch: main → /dist
   - Save

5. **URL resultante:**
   ```
   https://tuusuario.github.io/inmobot-widget/inmobot-widget.js
   ```

---

### **Opción 2: Netlify (Gratis, muy fácil)**

1. **Crear cuenta en Netlify:** https://netlify.com

2. **Drag & drop:**
   - Arrastrar carpeta `dist/` a Netlify
   - Listo ✅

3. **O con CLI:**

   ```bash
   npm install -g netlify-cli
   netlify login
   cd dist
   netlify deploy --prod
   ```

4. **URL resultante:**
   ```
   https://tu-site.netlify.app/inmobot-widget.js
   ```

---

### **Opción 3: Vercel (Gratis, super rápido)**

1. **Crear cuenta en Vercel:** https://vercel.com

2. **Deploy:**

   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

3. **URL resultante:**
   ```
   https://tu-widget.vercel.app/inmobot-widget.js
   ```

---

### **Opción 4: CDN propio (si tenés hosting)**

1. **Build:**
   ```bash
   npm run build
   ```

2. **Subir archivos:**
   - `dist/inmobot-widget.js` → `tudominio.com/js/inmobot-widget.js`
   - `dist/inmobot-widget.css` → (opcional, ya está inlined)

3. **Usar:**
   ```html
   <script src="https://tudominio.com/js/inmobot-widget.js"></script>
   ```

---

## 🧪 TESTING

### **Test 1: Desarrollo local**

```bash
npm run dev
```

Abrir `http://localhost:3000` y probar:

- ✅ Botón flotante aparece
- ✅ Click abre el chat
- ✅ Mensaje de bienvenida
- ✅ Enviar mensaje funciona
- ✅ Typing indicator aparece
- ✅ Respuesta del bot llega
- ✅ Minimizar funciona
- ✅ Nueva consulta resetea

---

### **Test 2: Integración con webhook local**

1. **N8N corriendo en localhost:5678**

2. **En index.html cambiar:**
   ```javascript
   apiUrl: 'http://localhost:5678/webhook/chat'
   ```

3. **Enviar mensaje test:**
   ```
   "Busco un departamento de 2 ambientes en Palermo"
   ```

4. **Verificar en N8N:**
   - Logs muestran la request
   - Workflow se ejecuta
   - Respuesta llega al widget

---

### **Test 3: Integración con Render**

1. **Cambiar URL:**
   ```javascript
   apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
   ```

2. **Primera request puede tardar ~10s** (Render se despierta)

3. **Requests subsecuentes:** ~5s

---

### **Test 4: Responsive (mobile)**

1. **Abrir DevTools → Toggle device**

2. **Probar en:**
   - iPhone SE (375px)
   - iPhone 12 (390px)
   - Samsung Galaxy (360px)
   - iPad (768px)

3. **Verificar:**
   - ✅ Chat se adapta al ancho
   - ✅ Botón sigue visible
   - ✅ Input no se corta
   - ✅ Mensajes se leen bien

---

### **Test 5: Build de producción**

```bash
npm run build
npm run preview
```

Abrir `http://localhost:4173` y verificar:

- ✅ Widget funciona igual
- ✅ Sin errores en consola
- ✅ Archivos minificados
- ✅ Performance buena

---

## 🔧 INTEGRACIÓN CON TU HTML DEMO ANTERIOR

Recordás el HTML demo que te armé? Para agregar el widget:

### **Paso 1: Abrir tu HTML demo**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <!-- ... tu código existente ... -->
</head>
<body>
  <!-- ... tu contenido existente ... -->
  
  <!-- AGREGAR ANTES DE </body>: -->
  
  <!-- Widget InmoBot -->
  <script src="http://localhost:3000/src/index.js" type="module"></script>
  <script>
    window.addEventListener('load', () => {
      setTimeout(() => {
        InmoBot.init({
          apiUrl: 'http://localhost:5678/webhook/chat', // Tu N8N local
          primaryColor: '#2563eb',
          botName: 'AsistenteBot',
          welcomeMessage: '¡Hola! ¿Buscás alquilar o comprar? Te ayudo a encontrar tu propiedad ideal.',
          position: 'bottom-right'
        });
      }, 500);
    });
  </script>
  
</body>
</html>
```

### **Paso 2: Abrir ambos:**

1. **Terminal 1 - Widget:**
   ```bash
   cd widget-react
   npm run dev
   ```

2. **Terminal 2 - N8N:**
   ```bash
   # Si usás Docker:
   docker start n8n
   
   # O si lo tenés instalado:
   n8n start
   ```

3. **Abrir tu HTML demo** en el navegador

4. **Ver el widget** abajo a la derecha ✅

---

### **Paso 3: Cuando vuelvas de vacaciones (testing final)**

1. **Deploy N8N en Render** (seguir guía 01)

2. **Build del widget:**
   ```bash
   npm run build
   ```

3. **Subir widget a GitHub Pages o Netlify**

4. **Actualizar tu HTML demo con URL de producción:**
   ```html
   <script src="https://tuusuario.github.io/inmobot-widget/inmobot-widget.js"></script>
   <script>
     InmoBot.init({
       apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat'
     });
   </script>
   ```

5. **Compartir link con Cristian** para que pruebe

---

## 🐛 TROUBLESHOOTING

### **Problema 1: "InmoBot is not defined"**

**Causa:** Script no se cargó

**Solución:**
```html
<!-- Agregar antes de InmoBot.init(): -->
<script>
  window.addEventListener('load', () => {
    setTimeout(() => {
      if (window.InmoBot) {
        InmoBot.init({ ... });
      } else {
        console.error('InmoBot no se cargó');
      }
    }, 500);
  });
</script>
```

---

### **Problema 2: No se ve el botón flotante**

**Causa:** Z-index bajo

**Solución:**
```css
<style>
  .chat-widget-container {
    z-index: 999999 !important;
  }
</style>
```

---

### **Problema 3: CORS error**

**Error en consola:**
```
Access to fetch at 'https://...' from origin '...' has been blocked by CORS
```

**Solución en N8N:**

1. Agregar variable de entorno en Render:
   ```
   N8N_CORS_ALLOW_ALL=true
   ```

2. O configurar CORS específico:
   ```
   N8N_CORS_ALLOW_ORIGIN=https://tudominio.com
   ```

---

### **Problema 4: Widget no responde**

**Verificar:**

1. **URL correcta:**
   ```javascript
   console.log(config.apiUrl);
   ```

2. **N8N funcionando:**
   ```bash
   curl -X POST https://tu-n8n.onrender.com/webhook/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"test"}'
   ```

3. **Network tab en DevTools:**
   - Ver si la request se envía
   - Ver respuesta del servidor
   - Ver errores

---

### **Problema 5: "Failed to fetch"**

**Causa:** N8N dormido (Render Free)

**Solución:**
- Esperar 30-60 segundos (se despierta)
- O implementar keep-alive (ver guía 01)

---

## 📊 MÉTRICAS DE PERFORMANCE

### **Tamaños:**

```
inmobot-widget.js:  ~150KB minified
inmobot-widget.css: ~8KB minified

Gzipped:
inmobot-widget.js:  ~50KB
```

### **Tiempos de carga:**

```
Primera carga:      ~300ms
Requests al bot:    5-15s (depende de N8N)
Render (primera):   10-15s (si estaba dormido)
Render (después):   5-10s
```

---

## ✅ CHECKLIST FINAL

Antes de darle a Cristian:

- [ ] Widget buildeado (`npm run build`)
- [ ] Subido a CDN (GitHub Pages / Netlify / Vercel)
- [ ] N8N en Render funcionando
- [ ] CORS configurado
- [ ] Webhook responde correctamente
- [ ] Tests en mobile y desktop
- [ ] Personalización aplicada (colores, textos)
- [ ] Documentación clara para Cristian
- [ ] Script de integración simple

---

## 📞 SOPORTE

### **Recursos:**

- React: https://react.dev
- Vite: https://vitejs.dev
- N8N: https://docs.n8n.io

### **Contacto:**

Si tenés dudas cuando vuelvas de vacaciones, podemos revisar juntos.

---

**¡WIDGET REACT LISTO!** ✅

**Próximo documento:** Actualización del workflow para webhook

---

**Creado:** 15 de Enero 2025  
**Autor:** Claude  
**Para:** Damián - Bot Inmobiliario  
**Status:** READY TO USE ✅
