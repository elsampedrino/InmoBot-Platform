# 🤖 InmoBot - Asistente Virtual Inmobiliario

Widget de chat interactivo para inmobiliarias con inteligencia artificial powered by Claude AI.

## ✨ Características

- 💬 **Chat en tiempo real** - Respuestas instantáneas con IA
- 🏠 **Búsqueda inteligente de propiedades** - Encuentra la propiedad ideal según criterios
- 📋 **Formulario de contacto** - Captura leads directamente desde el chat
- 🌐 **Multiidioma** - Soporte para español, inglés y portugués
- 📱 **Responsive** - Funciona perfecto en desktop, tablet y móvil
- 📊 **Estadísticas** - Tracking de conversaciones y conversiones
- 📲 **Notificaciones Telegram** - Alertas en tiempo real de nuevos leads

## 🚀 Demo en vivo

Probá el widget en acción: [Demo InmoBot](https://demo-chatbot-inmobiliaria.vercel.app)

## 🛠️ Tecnologías

- **Frontend**: React + Vite
- **Backend**: N8N + Claude AI (Anthropic API)
- **Base de datos**: PostgreSQL
- **Deployment**: Vercel
- **Notificaciones**: Telegram Bot API

## 📦 Instalación

### Para usar el widget en tu sitio

Agregá estos scripts en tu HTML:

```html
<!-- CSS del widget -->
<link rel="stylesheet" href="https://demo-chatbot-inmobiliaria.vercel.app/inmobot-widget.css">

<!-- JavaScript del widget -->
<script src="https://demo-chatbot-inmobiliaria.vercel.app/inmobot-widget.iife.js"></script>

<!-- Inicialización -->
<script>
  InmoBot.init({
    apiUrl: 'TU_URL_DE_N8N_WEBHOOK',
    primaryColor: '#2563eb',
    botName: 'InmoBot',
    welcomeMessage: '¡Hola! ¿En qué puedo ayudarte?',
    position: 'bottom-right'
  });
</script>
```

### Para desarrollo local

```bash
cd widget-react
npm install
npm run dev
```

Abrí http://localhost:3000/demo.html

### Para compilar

```bash
npm run build
```

Los archivos compilados estarán en `widget-react/dist/`

## ⚙️ Configuración

### Opciones de inicialización

```javascript
InmoBot.init({
  apiUrl: string,           // URL del webhook de N8N (requerido)
  primaryColor: string,     // Color principal del widget (default: '#2563eb')
  botName: string,          // Nombre del bot (default: 'InmoBot')
  welcomeMessage: string,   // Mensaje de bienvenida
  placeholderText: string,  // Texto del input
  position: string,         // 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  buttonSize: string,       // Tamaño del botón (default: '60px')
  chatWidth: string,        // Ancho del chat (default: '380px')
  chatHeight: string        // Alto del chat (default: '600px')
});
```

## 📊 Estructura del proyecto

```
.
├── widget-react/          # Widget React
│   ├── src/              # Código fuente
│   │   ├── ChatWidget.jsx
│   │   ├── ChatWidget.css
│   │   └── index.js
│   ├── dist/             # Build de producción
│   ├── public/           # Assets públicos
│   └── demo.html         # Demo local
├── Documentacion/        # Documentación técnica
└── vercel.json          # Configuración de Vercel
```

## 🔧 Integración con N8N

El widget se conecta a un workflow de N8N que:
1. Recibe la consulta del usuario
2. Procesa con Claude AI (Haiku + Sonnet)
3. Busca propiedades en la base de datos
4. Genera respuesta personalizada
5. Guarda estadísticas en PostgreSQL
6. Envía notificaciones por Telegram

## 📈 Estadísticas

El sistema trackea:
- Consultas realizadas
- Tiempo de respuesta
- Tokens consumidos (costos)
- Conversiones (leads capturados)
- Propiedades mostradas

## 📝 Licencia

Desarrollado por InmoBot para uso en proyectos inmobiliarios.

## 🤝 Soporte

Para consultas o personalizaciones, contactá al equipo de desarrollo.

---

**Powered by Claude AI** 🤖
