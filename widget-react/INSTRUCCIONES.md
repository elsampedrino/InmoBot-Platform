# 🚀 InmoBot Widget - Instrucciones de Uso

## 📋 Resumen

Widget de chatbot inmobiliario conectado con N8N en Render, completamente funcional y listo para usar.

---

## 🔧 DESARROLLO LOCAL

### 1. Levantar el servidor de desarrollo

```bash
# Navegar a la carpeta del widget
cd widget-react

# Iniciar el servidor
npm run dev
```

### 2. Abrir en el navegador

- **Demo funcional**: http://localhost:3000/demo.html
- **Demo con diseño**: http://localhost:3000/index.html

### 3. Detener el servidor

Presionar `Ctrl + C` en la terminal

---

## 📦 BUILD PARA PRODUCCIÓN

### 1. Generar archivos de producción

```bash
cd widget-react
npm run build
```

### 2. Archivos generados en `dist/`

- `inmobot-widget.iife.js` (478 KB → 149 KB gzipped)
- `inmobot-widget.css` (5.70 KB → 1.72 KB gzipped)

### 3. Probar la versión de producción

```bash
cd widget-react
npm run preview
```

Luego abre: http://localhost:41|3

**IMPORTANTE:** No abras `dist/index.html` directamente con doble click, ya que el navegador bloqueará los scripts por seguridad. Usa siempre `npm run preview`.

---

## 🌐 INTEGRACIÓN EN TU SITIO WEB

### Opción 1: Script simple (Recomendado)

Agregar antes del `</body>`:

```html
<!-- Cargar el widget -->
<script src="URL_DE_TU_CDN/inmobot-widget.iife.js"></script>
<script>
  if (window.InmoBot) {
    window.InmoBot.init({
      apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
      primaryColor: '#2563eb',
      botName: 'AsistenteBot',
      welcomeMessage: '¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy? 🏠',
      position: 'bottom-right'
    });
  }
</script>
```

### Opción 2: Con módulo ES6

```html
<script type="module">
  import('/URL_DE_TU_CDN/inmobot-widget.iife.js').then(() => {
    setTimeout(() => {
      if (window.InmoBot) {
        window.InmoBot.init({
          apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
          primaryColor: '#2563eb',
          botName: 'AsistenteBot',
          position: 'bottom-right'
        });
      }
    }, 100);
  });
</script>
```

---

## 🎨 CONFIGURACIÓN

### Parámetros disponibles:

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

### Ejemplo de configuración personalizada:

```javascript
window.InmoBot.init({
  apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
  primaryColor: '#059669',        // Verde
  botName: 'Cristian Asistente',
  welcomeMessage: '¡Bienvenido! Soy Cristian, tu asesor inmobiliario. ¿Buscás alquilar o comprar?',
  position: 'bottom-left',
  chatHeight: '500px'
});
```

---

## 🚀 DEPLOY

### GitHub Pages (Gratis)

1. Crear repo en GitHub
2. Subir la carpeta `dist/`
3. Activar GitHub Pages en Settings
4. URL resultante: `https://tuusuario.github.io/repo/inmobot-widget.iife.js`

### Netlify (Gratis)

1. Crear cuenta en https://netlify.com
2. Arrastrar carpeta `dist/` a Netlify
3. Listo!

### Vercel (Gratis)

```bash
npm install -g vercel
vercel --prod
```

---

## ✅ CHECKLIST PRODUCCIÓN

- [x] Widget funcionando localmente
- [x] Build generado sin errores
- [x] Conectado con N8N en Render
- [x] Versión de producción probada
- [ ] Archivos subidos a CDN
- [ ] URL de CDN actualizada en sitio web
- [ ] Probado en diferentes navegadores
- [ ] Probado en mobile

---

## 🐛 TROUBLESHOOTING

### El widget no aparece

1. Verificar que `window.InmoBot` esté definido (abrir consola)
2. Verificar que el script se cargó correctamente
3. Revisar errores en la consola del navegador

### No responde a los mensajes

1. Verificar que N8N esté activo en Render
2. Verificar CORS en N8N (`N8N_CORS_ALLOW_ALL=true`)
3. Verificar URL del webhook en la configuración

### Error al hacer build

1. Limpiar caché: `rm -rf dist node_modules/.vite`
2. Reinstalar dependencias: `npm install`
3. Intentar build de nuevo: `npm run build`

---

## 📞 COMANDOS ÚTILES

```bash
# Desarrollo
npm run dev          # Iniciar servidor de desarrollo
npm run build        # Generar archivos de producción
npm run preview      # Previsualizar build de producción

# Limpieza
rm -rf dist                    # Eliminar build anterior
rm -rf node_modules/.vite      # Limpiar caché de Vite
```

---

## ✨ ESTADO ACTUAL

✅ Widget funcionando perfectamente
✅ Conectado con N8N en Render
✅ Build de producción generado
✅ Listo para deploy

**Última actualización:** 1 de Diciembre 2024
