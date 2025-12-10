# 🤖 InmoBot - Chatbot Inmobiliario con IA

Chatbot inteligente para inmobiliarias con IA de Claude, integrado con N8N y desplegado en Render.

## 📋 Componentes

### 1. Widget React (`/widget-react`)
- Widget de chat flotante para sitios web
- Diseño moderno y responsive
- Integración simple con una línea de código
- **Ver:** [widget-react/INSTRUCCIONES.md](widget-react/INSTRUCCIONES.md)

### 2. Workflow N8N
- Flujo de procesamiento de consultas
- Integración con Claude AI (Haiku + Sonnet)
- Webhook API en Render
- **URL:** https://n8n-bot-inmobiliario.onrender.com/webhook/chat

### 3. Documentación (`/Documentacion`)
- Guías de deploy
- Documentación técnica
- Casos de uso y ejemplos

## 🚀 Quick Start

### Desarrollo del Widget

```bash
cd widget-react
npm install
npm run dev
```

Abre: http://localhost:3000/demo.html

### Build para Producción

```bash
cd widget-react
npm run build
npm run preview
```

## 📦 Deploy

### Widget → Vercel
```bash
cd widget-react
npm run build
# Subir carpeta dist/ a Vercel
```

### N8N → Render
- Ya deployado en: https://n8n-bot-inmobiliario.onrender.com
- Keep-alive automático con GitHub Actions

## 🔧 Keep Alive

Este repo incluye un workflow de GitHub Actions que mantiene N8N activo:
- **Archivo:** `.github/workflows/keep-alive.yml`
- **Frecuencia:** Cada 10 minutos
- **Ver:** [.github/workflows/README.md](.github/workflows/README.md)

## ✅ Estado Actual

- ✅ Widget React funcionando
- ✅ Conectado con N8N en Render
- ✅ Build de producción listo
- ✅ Keep-alive configurado
- ⏳ Pendiente: Deploy a Vercel

## 📚 Documentación Completa

- [Widget React - Instrucciones](widget-react/INSTRUCCIONES.md)
- [Keep Alive - GitHub Actions](.github/workflows/README.md)
- [Guías Técnicas](Documentacion/)

## 🛠️ Stack Tecnológico

- **Frontend:** React 18 + Vite
- **Backend:** N8N (Workflow Automation)
- **IA:** Claude AI (Anthropic)
- **Deploy:** Render + Vercel
- **Keep-Alive:** GitHub Actions

---

**Última actualización:** 1 de Diciembre 2024


