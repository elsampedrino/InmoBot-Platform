# Instrucciones de Integración - InmoBot Widget

## Para Cristian - Cómo integrar el widget en tu sitio web

### Paso 1: Agregar el código a tu sitio

Agregá este código **justo antes de la etiqueta `</body>`** en todas las páginas donde quieras que aparezca el widget:

```html
<!-- CSS del widget -->
<link rel="stylesheet" href="https://inmobot-widget.vercel.app/inmobot-widget.css">

<!-- JavaScript del widget -->
<script src="https://inmobot-widget.vercel.app/inmobot-widget.iife.js"></script>

<!-- Inicialización del widget -->
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    primaryColor: '#2563eb',
    botName: 'InmoBot',
    welcomeMessage: '¡Hola! Soy tu asistente inmobiliario virtual. ¿En qué te puedo ayudar hoy? 🏠',
    placeholderText: 'Escribe tu consulta...',
    position: 'bottom-right',
    buttonSize: '60px',
    chatWidth: '380px',
    chatHeight: '600px'
  });
</script>
```

### Paso 2: ¡Listo!

Eso es todo. El widget aparecerá automáticamente como un botón flotante en la esquina inferior derecha de tu sitio.

---

## Personalización (Opcional)

Podés cambiar estos parámetros en la configuración:

### Colores y apariencia
- **`primaryColor`**: Color principal del widget (en formato hexadecimal, ej: `'#2563eb'`)
- **`buttonSize`**: Tamaño del botón flotante (ej: `'60px'`, `'70px'`)
- **`chatWidth`**: Ancho de la ventana de chat (ej: `'380px'`, `'400px'`)
- **`chatHeight`**: Alto de la ventana de chat (ej: `'600px'`, `'500px'`)

### Textos
- **`botName`**: Nombre del asistente (ej: `'InmoBot'`, `'Asistente BBR'`)
- **`welcomeMessage`**: Mensaje de bienvenida que ve el usuario
- **`placeholderText`**: Texto que aparece en el campo de entrada

### Posición
- **`position`**: Ubicación del botón en la pantalla
  - `'bottom-right'` (abajo a la derecha) ← **recomendado**
  - `'bottom-left'` (abajo a la izquierda)
  - `'top-right'` (arriba a la derecha)
  - `'top-left'` (arriba a la izquierda)

### Ejemplo personalizado:

```html
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    primaryColor: '#e63946',  // Rojo personalizado
    botName: 'Asistente BBR',
    welcomeMessage: 'Hola, soy el asistente de BBR Grupo Inmobiliario. ¿Te puedo ayudar?',
    placeholderText: 'Hacé tu consulta aquí...',
    position: 'bottom-right',
    buttonSize: '65px',
    chatWidth: '400px',
    chatHeight: '650px'
  });
</script>
```

---

## Notas importantes

1. **No necesitás instalar nada** - Todo funciona directamente desde los archivos CDN
2. **Funciona en cualquier sitio** - HTML estático, WordPress, Shopify, etc.
3. **Es responsive** - Se adapta automáticamente a móviles y tablets
4. **No afecta tu sitio** - El widget es completamente independiente del resto de tu código

---

## Soporte

Si necesitás ayuda con la integración o querés personalizar algo más, contactá al equipo de desarrollo.

**URL de demo**: https://inmobot-widget.vercel.app
