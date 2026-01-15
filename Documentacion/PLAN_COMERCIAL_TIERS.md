# 💼 InmoBot - Plan Comercial por Tiers

**Fecha:** 2025-01-13
**Autor:** Claude Code (propuesta inicial)
**Status:** BORRADOR - Pendiente de revisión y discusión

---

## 🎯 Filosofía del modelo de negocio

### Concepto base:
Ofrecer **soluciones escalables** que crecen con el cliente, desde inmobiliarias pequeñas hasta grandes empresas.

### Principios:
1. **Entry point accesible:** Tier básico económico para captar clientes
2. **Migración natural:** Cuando crecen, migran a tiers superiores
3. **Valor incremental claro:** Cada tier agrega funcionalidad tangible
4. **Sticky products:** Una vez que usan IA, difícil volver atrás

---

## 📊 Estructura de Tiers (3 niveles)

---

## 🥉 TIER 1: BÁSICO (Solo Haiku)

### 🎯 Target:
- Inmobiliarias pequeñas (1-3 agentes)
- Catálogo: 10-50 propiedades
- Tráfico web: <1,000 visitas/mes
- Presupuesto limitado

### 🔧 Stack Técnico:

**IA:**
- 1 modelo: **Claude Haiku 3.5** (todo en un paso)
- Sin filtrado previo, Haiku hace filtro + respuesta

**Datos:**
- JSON estático en GitHub
- Actualizaciones manuales (mensual)
- Sin base de datos

**Hosting:**
- N8N: Render Starter
- Widget: Vercel free tier
- Imágenes: Cloudinary free tier (25GB/mes)

### ✅ Funcionalidades incluidas:

**Bot conversacional:**
- ✅ Respuestas en tiempo real
- ✅ Filtrado por ubicación, tipo, precio
- ✅ 1 Foto por Propiedad

**Gestión:**
- ✅ Actualización de propiedades vía Excel estandarizado
- ✅ Widget personalizable (colores, textos)
- ✅ Integración simple a la Web de la Inmobiliaria

### ❌ Limitaciones:

- ❌ Respuestas menos "humanas" (más técnicas)
- ❌ Sin búsqueda semántica avanzada
- ❌ Sin analytics/métricas
- ❌ Sin leads de contactos
- ❌ Sin actualizaciones en tiempo real
- ❌ Soporte: email (respuesta 24-48hs)

### 💰 Pricing sugerido:

| Concepto | Precio (USD) | Precio (ARS)* |
|----------|--------------|---------------|
| Setup inicial | $50 | $50,000 |
| Mensual | $150 | $150,000 |


**Incluye:**
- Configuración inicial del bot
- Carga de hasta 50 propiedades
- Optimización y subida de imágenes
- Personalización del widget
- 1 mes gratis de prueba

---

## 🥈 TIER 2: PROFESIONAL (Haiku + Sonnet)

### 🎯 Target:
- Inmobiliarias medianas (4-10 agentes)
- Catálogo: 50-200 propiedades
- Tráfico web: 1,000-5,000 visitas/mes
- Necesitan imagen profesional

### 🔧 Stack Técnico:

**IA:**
- 2 modelos en pipeline:
  - **Haiku 3.5:** Filtrado rápido (500ms)
  - **Sonnet 4:** Respuesta conversacional (1.5s)
- Total: ~2 segundos respuesta

**Datos:**
- JSON estático en GitHub
- Actualizaciones manuales (2 al mes)

**Hosting:**
- N8N: Render Starter
- Widget: Vercel Pro ($20/mes) - dominio custom
- Imágenes: Cloudinary Pro ($89/mes) - 100GB

### ✅ Funcionalidades incluidas:

**Todo del Tier 1, MÁS:**

**Bot conversacional mejorado:**
- ✅ Respuestas muy naturales y profesionales
- ✅ Comprensión de consultas complejas
- ✅ Manejo inteligente de "sin coincidencias"
- ✅ Sugerencias proactivas de alternativas
- ✅ Tono personalizado por marca
- ✅ Captura de leads por Telegram
- ✅ Reportes estadísticos semanales
- ✅ Multi-Idioma (Español - Inglés - Portugués)

**Gestión avanzada:**
- ✅ Múltiples repositorios (1 bot, N inmobiliarias)
- ✅ Parámetro `repo` para seleccionar catálogo
- ✅ Versionado de cambios en propiedades

**Soporte:**
- ✅ Email + WhatsApp (respuesta <12hs)
- ✅ 1 actualización de diseño/mes incluida
- ✅ Reportes mensuales básicos (consultas, conversiones)

### ❌ Limitaciones:

- ❌ Sin búsqueda semántica (solo keyword)
- ❌ Sin analytics en tiempo real
- ❌ Sin CRM integrado
- ❌ Sin A/B testing

### 💰 Pricing sugerido:

| Concepto | Precio (USD) | Precio (ARS)* |
|----------|--------------|---------------|
| Setup inicial | $50 | $50,000 |
| Mensual | $200 | $220,000 |

**Incluye:**
- Todo del Tier 1
- Migración desde Tier 1 (si aplica): -$100 USD setup
- Configuración avanzada de prompts
- Integración con dominio custom
- 2 revisiones de optimización/año

---

## 🥇 TIER 3: PREMIUM (Sonnet + PostgreSQL)

### 🎯 Target:
- Inmobiliarias grandes (10+ agentes, franquicias)
- Catálogo: 200+ propiedades
- Tráfico web: 5,000+ visitas/mes
- Necesitan escalabilidad y control total

### 🔧 Stack Técnico:

**IA:**
- **Sonnet 4** con búsqueda semántica
- **Embeddings** para búsqueda por similitud
- **RAG** (Retrieval Augmented Generation)

**Datos:**
- **PostgreSQL** en la nube (Supabase/Railway)
- **pgvector** para embeddings
- Actualizaciones en **tiempo real**
- API REST para integración con CRM

**Hosting:**
- N8N: Render Starter
- Widget: Vercel Enterprise
- Imágenes: Cloudinary Advanced ($224/mes) - 500GB
- DB: Supabase Pro ($25/mes) o Railway ($20/mes)

### ✅ Funcionalidades incluidas:

**Todo del Tier 2, MÁS:**

**IA Avanzada:**
- ✅ Búsqueda semántica ("busco algo tranquilo cerca del parque")
- ✅ Comprensión de preferencias implícitas
- ✅ Recomendaciones personalizadas
- ✅ Memoria de conversaciones (por sesión)

**Gestión Premium:**
- ✅ Panel de administración web (CRUD propiedades)
- ✅ Actualización de propiedades en tiempo real
- ✅ Integración con CRM (Zoho, HubSpot, custom)
- ✅ API para sincronización automática
- ✅ Webhooks para eventos (nueva consulta, contacto)

**Analytics y Optimización:**
- ✅ Dashboard en tiempo real (consultas, conversiones)
- ✅ Heatmaps de búsquedas
- ✅ A/B testing de prompts
- ✅ Métricas de satisfacción (thumbs up/down)
- ✅ Reportes semanales automáticos

**Escalabilidad:**
- ✅ Múltiples bots (diferentes sitios/marcas)
- ✅ White-label completo
- ✅ CDN global (baja latencia mundial)
- ✅ SLA 99.9% uptime

**Soporte:**
- ✅ Soporte prioritario 24/7
- ✅ Slack/Discord dedicado
- ✅ Onboarding personalizado (2hs)
- ✅ Revisión mensual de performance
- ✅ Ajustes ilimitados de prompts

### 💰 Pricing sugerido:

| Concepto | Precio (USD) | Precio (ARS)* |
|----------|--------------|---------------|
| Setup inicial | $800 | $800,000 |
| Mensual | $300 | $300,000 |

**Incluye:**
- Todo del Tier 2
- Migración desde Tier 1/2: -$200 USD setup
- Desarrollo de integraciones custom
- Capacitación del equipo (2 sesiones)
- Soporte dedicado
- SLA garantizado

---

## 📈 Comparativa de Tiers (tabla resumen)

| Feature | Básico | Profesional | Premium |
|---------|--------|-------------|---------|
| **Modelo IA** | Haiku | Haiku + Sonnet | Sonnet + RAG |
| **Velocidad** | <1 seg | ~2 seg | ~2 seg |
| **Calidad respuestas** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Propiedades** | Hasta 50 | Hasta 200 | Ilimitadas |
| **Actualización** | Manual (JSON) | Manual (JSON) | Tiempo real (DB) |
| **Búsqueda semántica** | ❌ | ❌ | ✅ |
| **Analytics** | ❌ | Básico | Avanzado |
| **Integración CRM** | ❌ | ❌ | ✅ |
| **Multi-sitio** | ❌ | ✅ (repo param) | ✅ (ilimitado) |
| **Soporte** | Email 24-48hs | Email/WA 12hs | 24/7 prioritario |
| **Setup** | $150 | $300 | $800 |
| **Mensual** | $30 | $80 | $250 |

---

## 🚀 Estrategia de Migración (Upsell)

### Path típico del cliente:

```
Tier 1 (Básico)
   ↓ (3-6 meses)
   ↓ Crece catálogo, necesita mejor conversación
   ↓
Tier 2 (Profesional)
   ↓ (6-12 meses)
   ↓ Muchas consultas, necesita analytics y CRM
   ↓
Tier 3 (Premium)
```

### Triggers para upsell:

**Tier 1 → Tier 2:**
- Cliente tiene >40 propiedades
- >500 consultas/mes
- Feedback: "respuestas muy técnicas"
- Quiere multi-sitio

**Tier 2 → Tier 3:**
- Cliente tiene >150 propiedades
- >2,000 consultas/mes
- Necesita CRM integrado
- Quiere automatización completa

### Incentivos de migración:
- **Descuento setup:** -50% si migran dentro de 6 meses
- **Crédito:** 1 mes gratis al migrar a Tier superior
- **Lock-in:** Contrato anual: -15% descuento

---

## 💡 Features Adicionales (Cross-sell)

### Add-ons opcionales (todos los tiers):

| Add-on | Descripción | Precio/mes |
|--------|-------------|------------|
| **SMS Notifications** | Alertas por SMS cuando hay consulta | $20 |
| **WhatsApp Bot** | Bot también en WhatsApp Business | $50 |
| **Video Tours** | Integración con tours virtuales 360° | $30 |
| **Lead Scoring** | IA clasifica calidad de leads | $40 |
| **Auto-follow-up** | Emails automáticos a leads fríos | $35 |
| **Multilisting** | Sincroniza con Zonaprop, MercadoLibre | $60 |

---

## 📊 Proyección de Costos (por cliente)

### Tier 1 (Básico):

**Costos fijos:**
- Hosting N8N: $0 (free tier)
- Vercel: $0 (free tier)
- Cloudinary: $0 (free tier)
- GitHub: $0

**Costos variables:**
- Claude Haiku API: ~$2-5/mes (según uso)

**Margen:** ~85-90%

### Tier 2 (Profesional):

**Costos fijos:**
- Hosting N8N: $7/mes
- Vercel Pro: $20/mes
- Cloudinary: $0-89/mes (según volumen)

**Costos variables:**
- Claude Haiku + Sonnet: ~$10-20/mes

**Margen:** ~50-70%

### Tier 3 (Premium):

**Costos fijos:**
- Hosting N8N: $25/mes
- Vercel: $20/mes
- Cloudinary: $89-224/mes
- PostgreSQL: $25/mes

**Costos variables:**
- Claude Sonnet + Embeddings: ~$30-60/mes

**Margen:** ~40-60%

---

## 🎁 Estrategia de Lanzamiento

### Fase 1: MVP con early adopters (Mes 1-3)
- 5 clientes Tier 1 con **50% descuento** (pricing de prueba)
- Feedback intensivo
- Casos de éxito documentados

### Fase 2: Validación Tier 2 (Mes 4-6)
- Migrar 2-3 clientes de Tier 1 a Tier 2
- Refinar pricing según mercado
- Crear contenido (blog, videos)

### Fase 3: Tier 3 y escalamiento (Mes 7-12)
- Lanzar Tier 3 con 1-2 anchor clients
- Marketing digital (Google Ads, LinkedIn)
- Partner con agencias de marketing inmobiliario

---

## 🤝 Modelo de Contratos

### Tier 1:
- **Mes a mes** (sin compromiso)
- Cancelación: aviso 15 días
- Setup fee no reembolsable

### Tier 2:
- **Trimestral** recomendado (5% desc)
- **Anual:** 15% descuento
- Garantía: 30 días satisfacción o reembolso

### Tier 3:
- **Anual mínimo**
- Garantía SLA 99.9%
- Revisión de contrato semestral

---

## 📝 Próximos pasos para discusión

### Temas a revisar:

1. **Pricing:** ¿Precios en USD o ARS? ¿Ajuste por inflación?
2. **Roadmap:** Comparar con tu plan existente
3. **Prioridad:** ¿Empezar con qué tier?
4. **Competencia:** Benchmarking vs otras soluciones
5. **Go-to-market:** ¿Cómo conseguir primeros clientes?
6. **Recursos:** ¿Qué necesitás para desarrollar cada tier?

---

## 📚 Anexos

### A. Benchmark de competencia (investigar)
- Chatbots inmobiliarios en Argentina
- Pricing de soluciones similares
- Features que ofrecen

### B. Customer Journey Map
- Desde awareness hasta cliente recurrente
- Puntos de dolor en cada etapa
- Cómo InmoBot los resuelve

### C. Casos de uso por tier
- Tier 1: Inmobiliaria Ramallo (BBR) - catálogo pequeño, ciudad interior
- Tier 2: Inmobiliaria CABA - múltiples barrios, volumen medio
- Tier 3: Franquicia nacional - cientos de propiedades, múltiples ciudades

---

**Autor:** Claude Code
**Fecha creación:** 2025-01-13
**Status:** BORRADOR
**Próxima revisión:** Pendiente de reunión con roadmap existente
