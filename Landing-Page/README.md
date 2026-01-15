# InmoBot - Landing Page

Landing page profesional para InmoBot, el asistente inmobiliario con IA desarrollado por Automatizaciones IA.

## Stack Tecnológico

- **Astro** - Framework de generación de sitios estáticos
- **Tailwind CSS v4** - Framework de CSS utility-first
- **TypeScript** - Para el chat demo interactivo
- 100% Responsive
- SEO optimizado

## Estructura del Proyecto

```
Landing Page/
├── src/
│   ├── components/       # Componentes de las secciones
│   │   ├── Hero.astro
│   │   ├── HowItWorks.astro
│   │   ├── Demo.astro
│   │   ├── Benefits.astro
│   │   ├── Pricing.astro
│   │   ├── TechDifferentiators.astro
│   │   ├── FutureVision.astro
│   │   ├── Contact.astro
│   │   └── Footer.astro
│   ├── layouts/
│   │   └── Layout.astro  # Layout principal
│   ├── pages/
│   │   └── index.astro   # Página principal
│   └── styles/
│       └── global.css    # Estilos globales con Tailwind
└── public/               # Archivos estáticos
```

## Instalación

```bash
# Instalar dependencias
npm install
```

## Comandos Disponibles

```bash
# Desarrollo - Inicia servidor en http://localhost:4321
npm run dev

# Build - Genera versión de producción
npm run build

# Preview - Previsualiza el build de producción
npm run preview
```

## Características Implementadas

### 1. Hero Section
- Headline y subheadline principales
- CTA destacado con scroll suave a la demo
- **Fondo animado futurista con CSS & SVG**:
  - Red de nodos conectados con líneas animadas (efecto de flujo de datos)
  - 13 nodos pulsantes con efecto glow
  - 6 partículas flotantes
  - 3 gradient blobs en movimiento suave
  - Colores: violet, cyan, purple
  - 100% CSS/SVG, sin JavaScript
  - Optimizado para 60fps y bajo uso de CPU
  - GPU accelerated con transform3d
  - Soporte para prefers-reduced-motion (accesibilidad)
- Mock de interfaz de chat con animaciones

### 2. Cómo Funciona
- 4 pasos visuales con íconos
- Grid responsive
- Líneas conectoras (desktop)

### 3. Demo en Vivo
- **Widget de chat conectado a N8N real**:
  - Llamadas HTTP al webhook: `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`
  - Workflow: Haiku + Sonnet (filtrado + respuesta)
  - Repo: `demo` (catálogo de propiedades de prueba)
  - SessionStorage para tracking de sesión
  - **Limitación: 3 consultas por sesión**
  - Contador de consultas restantes
  - Mensaje de límite alcanzado con CTA a contacto
  - Opción de recargar página para reset
- Scroll automático de mensajes
- Indicador de escritura animado
- Renderizado de respuestas con formato markdown
- Manejo de errores de conexión

### 4. Beneficios
- 6 cards con animaciones hover
- Iconos grandes y descriptivos
- CTA secundario integrado

### 5. Planes y Precios
- 3 planes: Básico, Pro (recomendado), Premium
- Datos tomados exclusivamente de `pricing.md`
- Tabla comparativa completa
- Badges de recomendación
- Información de implementación inicial

### 6. Diferenciadores Tecnológicos
- Sección dark mode
- 4 diferenciadores principales
- Stats destacados (99.9%, <2s, 24/7)
- Fondo con efectos visuales

### 7. Visión Futura
- Roadmap con 4 features próximas
- Estados: En desarrollo, Planificado, Visión 2026
- Form de suscripción (preparado, disabled)
- Mensaje multi-rubro

### 8. Contacto
- Botones de WhatsApp y Email
- FAQ con 4 preguntas frecuentes
- Efectos hover elaborados

### 9. Footer
- Branding y descripción
- Links de navegación
- Información de contacto
- Login placeholder
- "Desarrollado en Argentina 🇦🇷"

## Personalización

### Actualizar datos de contacto

Editar en [`src/components/Contact.astro`](src/components/Contact.astro):
- Número de WhatsApp (línea 17)
- Email de contacto (línea 37)

### Actualizar precios

Los precios están sincronizados con [`Documentacion/Analisis-ChatGPT/Pricing.md`](../Documentacion/Analisis-ChatGPT/Pricing.md). Para modificarlos, editar ese archivo y luego actualizar [`src/components/Pricing.astro`](src/components/Pricing.astro).

### Personalizar animaciones del Hero

El fondo animado usa CSS y SVG puro, sin JavaScript. Para ajustar:

**Velocidad de animaciones**:
- Blobs: línea 173 (`animation: blob 20s`)
- Nodos: línea 198 (`animation: nodePulse 3s`)
- Líneas: línea 228 (`animation: lineFlow 8s`)
- Partículas: línea 262 (`animation: particleFloat 12s`)

**Colores**:
- Líneas 12-19 en `Hero.astro`: gradientes SVG
- Líneas 78-80: gradient blobs (cambiar `bg-violet-400`, `bg-cyan-400`, etc.)

**Cantidad de elementos**:
- Agregar/quitar nodos: modificar grupo `<g class="ai-nodes">` (líneas 47-63)
- Agregar/quitar líneas: modificar grupo `<g class="ai-lines">` (líneas 32-44)
- Agregar/quitar partículas: modificar grupo `<g class="ai-particles">` (líneas 66-73)

### Cambiar colores

Los colores principales están definidos en [`src/styles/global.css`](src/styles/global.css) usando `@theme`:
- `--color-violet-600`, `--color-violet-700`
- `--color-cyan-400`, `--color-cyan-500`

## Deployment

### Vercel (Recomendado)

1. Conectar el repositorio a Vercel
2. Configurar dominio: `automatizacionesia.com.ar`
3. Build command: `npm run build`
4. Output directory: `dist`

```bash
# O deployar manualmente
npm run build
npx vercel --prod
```

### Netlify

1. Build command: `npm run build`
2. Publish directory: `dist`

## SEO y Performance

- HTML estático generado en build time
- Minimal JavaScript (solo chat demo interactivo)
- **Animaciones optimizadas**:
  - GPU accelerated con `transform3d`
  - `will-change` para optimización del navegador
  - CSS animations (no JavaScript)
  - Soporte para `prefers-reduced-motion`
- Lighthouse Score objetivo: 95+
- Meta tags configurados en `Layout.astro`
- Scroll suave implementado
- SVG inline (sin requests HTTP adicionales)
- Imágenes optimizables con `<Image>` de Astro

## Próximas Mejoras

- [x] ~~Agregar video hero background~~ → Implementado con animaciones CSS/SVG
- [ ] Integrar analytics (Google Analytics o Plausible)
- [ ] Agregar formulario de contacto con backend
- [ ] Implementar sistema de newsletter
- [ ] Agregar página de login (cuando esté el dashboard)
- [ ] Optimizar imágenes con componente Image de Astro
- [ ] Agregar sitemap.xml y robots.txt

## Notas Importantes

- **No inventar precios**: Todos los precios vienen de `pricing.md`
- **Escalabilidad multi-rubro**: El diseño está preparado para expandirse más allá de inmobiliarias
- **Dominio**: `automatizacionesia.com.ar` (ya registrado)
- **WhatsApp**: Actualizar número real antes de producción
- **Email**: Configurar `contacto@automatizacionesia.com.ar` cuando esté el dominio activo

### Demo Widget - Configuración

El widget de demo en la landing page se conecta al workflow **real** de N8N:

- **Webhook URL**: `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`
- **Repo**: `demo` (configurado en el body del request)
- **Workflow**: N8N_InmoBot - Haiku + Sonnet
- **Limitación**: 3 consultas por sesión (almacenado en sessionStorage)
- **SessionID**: Generado automáticamente con formato `demo-{timestamp}-{random}`

Para modificar la configuración, editar en [`src/components/Demo.astro`](src/components/Demo.astro):
```typescript
const WEBHOOK_URL = 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat';
const MAX_QUERIES = 3;
```

**Importante**: El repo `demo` debe existir en tu GitHub con propiedades de prueba. Ver [RESUMEN_MULTI_REPO_FINAL.md](../Documentacion/RESUMEN_MULTI_REPO_FINAL.md) para configuración de repositorios.

## Contacto

Desarrollado por Automatizaciones IA
- Web: automatizacionesia.com.ar
- Email: contacto@automatizacionesia.com.ar

---

**Desarrollado en Argentina 🇦🇷**
