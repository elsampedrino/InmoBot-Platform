# 💼 MODELOS DE PRICING CON LÍMITES - ANÁLISIS DE MERCADO

## 🎯 OBJETIVO

Definir el modelo de facturación por consultas con límites para el Bot Inmobiliario, basándose en benchmarks de la industria SaaS.

---

## 📊 BENCHMARKS DE MERCADO - SERVICIOS REALES

### **1. TWILIO (WhatsApp Business API)**

**Modelo:** Pay-as-you-go con límites configurables

```
Pricing:
- $0.005 por mensaje entrante
- $0.016 por mensaje saliente (Argentina)

Límites:
- Sin tope por defecto → Pagás por uso real
- Alertas configurables: 80%, 90%, 100%
- Opción de Hard limit para cortar servicio automáticamente
- Notificaciones por email y SMS

Dashboard:
- Uso en tiempo real
- Gráficos de consumo
- Proyección de gasto mensual
```

**Aprendizaje:** Modelo flexible pero puede generar facturas inesperadas.

---

### **2. SENDGRID (Email Marketing)**

**Modelo:** Hard Stop - Planes por volumen

```
Plan Free:       100 emails/día → GRATIS
Plan Essentials: $19.95/mes → 50,000 emails/mes
Plan Pro:        $89.95/mes → 100,000 emails/mes

Al superar límite:
- ✅ Servicio se pausa automáticamente
- ✅ Email al administrador
- ✅ Dashboard muestra "Límite alcanzado"
- ✅ Opciones: Esperar próximo mes o upgradear

Alertas:
- 80% de uso: Email informativo
- 95% de uso: Email de warning
- 100% de uso: Servicio pausado + email urgente
```

**Aprendizaje:** Hard stop es estándar y bien aceptado por clientes.

---

### **3. ANTHROPIC (Claude API)**

**Modelo:** Pay-per-use con spending limits configurables

```
Pricing:
- Sonnet: $3/M tokens input, $15/M tokens output
- Haiku: $0.25/M tokens input, $1.25/M tokens output

Límites:
- Configurable por el cliente
- Ejemplo: "No gastar más de $100/mes"
- Al alcanzar límite: API retorna 429 error
- Notificación por email

Dashboard:
- Uso en tiempo real
- Costo acumulado
- Proyección hasta fin de mes
- Desglose por modelo
```

**Aprendizaje:** Control de gastos es crítico para APIs costosas.

---

### **4. OPENAI (ChatGPT API)**

**Modelo:** Tier system con límites incrementales

```
Tier 1: $100/mes de límite (primer mes)
Tier 2: $500/mes de límite (después de gastar $100)
Tier 3: $1,000/mes de límite (después de usar Tier 2)

Al alcanzar límite:
- Requests devuelven error 429
- Email de notificación inmediato
- Upgrade manual o automático (según config)

Rate limits adicionales:
- RPM (requests por minuto)
- TPM (tokens por minuto)
- Ayuda a evitar abusos y errores
```

**Aprendizaje:** Sistema progresivo reduce riesgo de fraude.

---

### **5. STRIPE (Procesamiento de pagos)**

**Modelo:** % por transacción sin límites

```
Pricing:
- 2.9% + $0.30 por transacción exitosa
- Sin mensualidad base
- Sin límites de volumen

Control de gastos:
- Billing alerts configurables
- Webhooks de eventos de facturación
- Dashboard con proyecciones
- Informes automáticos

Ventaja: Solo pagás si tenés transacciones
```

**Aprendizaje:** Pay-per-use puro funciona cuando el valor es proporcional.

---

### **6. ZAPIER (Automatizaciones)**

**Modelo:** Hard Stop - El más común en SaaS

```
Plan Free:         100 tareas/mes → $0
Plan Starter:      $29.99/mes → 750 tareas/mes
Plan Professional: $73.50/mes → 2,000 tareas/mes
Plan Team:         $103.50/mes → 50,000 tareas/mes

Al superar límite:
✅ Zaps se pausan automáticamente
✅ Email: "Has alcanzado tu límite de tareas"
✅ Dashboard muestra: "Paused - Upgrade to continue"
✅ Botón prominente: "Upgrade Now"
✅ Opción: Esperar al reset mensual (día 1)

Alertas preventivas:
- 50% de uso: Notificación informativa
- 80% de uso: "Acercándote al límite"
- 90% de uso: "Solo quedan X tareas"
- 100% de uso: Servicio pausado

UI/UX:
- Contador siempre visible en el dashboard
- Barra de progreso con colores (verde/amarillo/rojo)
- Proyección: "A este ritmo, alcanzarás el límite en X días"
```

**Aprendizaje:** Este es el modelo MÁS USADO y MÁS ACEPTADO por usuarios.

---

### **7. MAILCHIMP (Email Marketing)**

**Modelo:** Hard Stop con límites por contactos

```
Plan Essentials: $13/mes → 5,000 contactos
Plan Standard:   $20/mes → 6,000 contactos
Plan Premium:    $350/mes → 10,000 contactos

Al superar contactos:
- No se pueden enviar campañas
- Debe eliminar contactos o upgradear
- No hay opción de "pagar extra"

Sistema de alertas:
- 80% de contactos: "Considera upgradear"
- 95% de contactos: "Muy cerca del límite"
- 100%: "No puedes enviar hasta upgradear"
```

**Aprendizaje:** Hard limit estricto puede frustrar pero es claro.

---

### **8. AIRCALL (Telefonía VoIP)**

**Modelo:** Soft Stop con overages

```
Plan Essentials: $30/usuario/mes
- 60 minutos de llamadas incluidos
- Minutos adicionales: $0.30 c/u

Funcionamiento:
- Al llegar a 60 min: Sistema continúa funcionando
- Se cobra $0.30 por cada minuto extra
- Factura mensual incluye base + overages

Alertas:
- 50 min (83%): "Quedan 10 minutos incluidos"
- 60 min (100%): "Minutos extras se cobrarán a $0.30 c/u"
- Resumen diario de minutos consumidos

Ventaja: Servicio nunca se interrumpe
Desventaja: Factura puede variar mucho
```

**Aprendizaje:** Overages funcionan bien cuando la interrupción es inaceptable.

---

## 🎯 COMPARATIVA DE MODELOS

### **Modelo A: Hard Stop (RECOMENDADO para nosotros)**

**Características:**
```
✅ Servicio se pausa al alcanzar límite
✅ Cliente nunca tiene sorpresas en la factura
✅ Control total de gastos
✅ Incentiva upgrade proactivo
✅ Facturación predecible

❌ Puede frustrar si se alcanza en momento crítico
❌ Requiere que cliente esté atento a alertas
```

**Usado por:** Zapier, SendGrid, Mailchimp, muchos SaaS

**Cuándo usarlo:**
- Servicios no críticos
- Planes de entrada/pequeños
- Cuando quieres facturación predecible
- Para evitar costos sorpresa al cliente

---

### **Modelo B: Soft Stop + Overages**

**Características:**
```
✅ Servicio nunca se interrumpe
✅ Cliente paga por lo que usa
✅ Mejor experiencia de usuario
✅ Puede generar más revenue

❌ Facturas variables pueden sorprender
❌ Cliente puede perder control de gastos
❌ Requiere términos y condiciones claros
```

**Usado por:** Twilio, AWS, Aircall, servicios enterprise

**Cuándo usarlo:**
- Servicios mission-critical
- Clientes enterprise
- Cuando interrupción es inaceptable
- Modelo de consumo real

---

### **Modelo C: Auto-Upgrade**

**Características:**
```
✅ Cero fricción para el cliente
✅ Servicio nunca se detiene
✅ Revenue automático

❌ Cliente puede enojarse por cargo inesperado
❌ Puede generar chargebacks
❌ Requiere consentimiento explícito previo
```

**Usado por:** Algunos SaaS premium, menos común ahora

**Cuándo usarlo:**
- Con consentimiento explícito
- Clientes con alto trust
- Servicios con ROI muy claro

---

## 💡 RECOMENDACIÓN PARA NUESTRO BOT

### **Modelo seleccionado: HARD STOP (Modelo A)**

### **Estructura de planes:**

```
┌─────────────────────────────────────────────────────┐
│  PLAN STARTER                                       │
├─────────────────────────────────────────────────────┤
│  $25 USD/mes                                        │
│  500 consultas incluidas                            │
│  Al alcanzar 500: Bot se pausa automáticamente      │
│                                                      │
│  Opciones al llegar al límite:                      │
│  A) Esperar al 1° del mes (reset gratis)            │
│  B) Comprar paquete +250 consultas ($15)            │
│  C) Upgradear a Plan Growth ($50/mes)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  PLAN GROWTH                                        │
├─────────────────────────────────────────────────────┤
│  $50 USD/mes                                        │
│  1,500 consultas incluidas                          │
│  Al alcanzar 1,500: Bot se pausa                    │
│  Consultas adicionales: $0.04 c/u (opcional)        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  PLAN PRO                                           │
├─────────────────────────────────────────────────────┤
│  $90 USD/mes                                        │
│  3,000 consultas incluidas                          │
│  Consultas adicionales: $0.03 c/u                   │
│  Reportes avanzados incluidos                       │
└─────────────────────────────────────────────────────┘
```

---

## 📧 SISTEMA DE ALERTAS

### **Alert 1: 80% de uso (400/500 consultas)**

```
Asunto: ⚠️ [InmoBot] Ya usaste el 80% de tus consultas este mes

Hola [Cliente],

¡Tu bot está trabajando muy bien! 🎉

📊 Resumen del mes:
✅ 400 de 500 consultas usadas (80%)
📈 68 leads capturados
🏠 4 visitas coordinadas

⏰ Te quedan 100 consultas para este mes.

💡 ¿Necesitás más?
→ Esperar al 1/Feb (resetea automático y gratis)
→ Comprar 250 consultas extra por $15
→ Upgradear a Plan Growth (1,500/mes) por $50/mes

[Ver mi dashboard] [Comprar consultas]

Saludos,
Equipo InmoBot
```

---

### **Alert 2: 95% de uso (475/500 consultas)**

```
Asunto: 🚨 [IMPORTANTE] Quedan solo 25 consultas este mes

Hola [Cliente],

Tu bot está muy cerca del límite mensual:

📊 Consultas usadas: 475 de 500 (95%)
🔔 Consultas restantes: 25
📅 Resetea en: 6 días

⚠️ Al alcanzar 500 consultas, el bot se pausará temporalmente.

Para evitar interrupciones:
1️⃣ Comprar paquete de 250 consultas ($15) → [Comprar ahora]
2️⃣ Upgradear a Plan Growth (1,500/mes) → [Upgradear]
3️⃣ Esperar al reset del 1/Feb

🎯 Con Plan Growth tendrías 1,000 consultas adicionales 
   por solo $25 más. ¿Vale la pena perder leads?

[Reactivar consultas ahora]

Equipo InmoBot
```

---

### **Alert 3: 100% de uso - Bot pausado**

```
Asunto: 🛑 [ACCIÓN REQUERIDA] Tu bot se pausó temporalmente

Hola [Cliente],

Tu bot alcanzó el límite de 500 consultas y se pausó.

📊 Stats finales del mes:
✅ 500 consultas atendidas (100%)
📈 85 leads capturados
🏆 5 visitas coordinadas
💰 ~$15,000 en comisiones potenciales

🔴 Estado actual: BOT PAUSADO

Para reactivarlo:
┌────────────────────────────────────────────┐
│ Opción 1: Comprar 250 consultas ($15)     │
│ → Reactivación inmediata                  │
│ [Comprar y reactivar]                     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Opción 2: Upgradear a Growth ($50/mes)    │
│ → 1,500 consultas/mes                     │
│ → Nunca más te quedes sin consultas       │
│ [Upgradear ahora]                         │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Opción 3: Esperar al próximo mes          │
│ → Resetea gratis el 1/Feb                 │
│ → Pierdes consultas mientras tanto        │
└────────────────────────────────────────────┘

⏰ Cada hora sin bot = leads perdidos

[Reactivar mi bot AHORA]

---
¿Dudas? Respondé este email o llamanos al XXX-XXXX

Equipo InmoBot
```

---

## 🎨 DASHBOARD PARA EL CLIENTE

### **Vista principal:**

```
╔═══════════════════════════════════════════════════╗
║  🤖 InmoBot Dashboard - Enero 2025               ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  Plan actual: STARTER                             ║
║  Límite mensual: 500 consultas                    ║
║                                                   ║
║  ┌─────────────────────────────────────────────┐ ║
║  │  Consultas usadas este mes                  │ ║
║  │                                              │ ║
║  │   423 / 500  (85%)                          │ ║
║  │                                              │ ║
║  │   ████████████████▓▓░░  85%                 │ ║
║  │                                              │ ║
║  │   Consultas restantes: 77                   │ ║
║  └─────────────────────────────────────────────┘ ║
║                                                   ║
║  🔔 Alerta: Quedan menos de 100 consultas        ║
║                                                   ║
║  📅 Próximo reset: 8 días (1 de Febrero)         ║
║                                                   ║
║  ┌─────────────────────────────────────────────┐ ║
║  │  [Comprar 250 consultas - $15]              │ ║
║  │  [Upgradear a Growth - $50/mes]             │ ║
║  └─────────────────────────────────────────────┘ ║
║                                                   ║
║  📊 Estadísticas del mes:                        ║
║  • Leads capturados: 72                          ║
║  • Visitas coordinadas: 4                        ║
║  • Conversaciones activas: 18                    ║
║  • Tasa de respuesta: 98%                        ║
║                                                   ║
║  💰 ROI estimado:                                ║
║  • Costo del plan: $25                           ║
║  • Comisiones proyectadas: $9,000                ║
║  • ROI: 360x                                     ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### **Arquitectura del sistema de contador:**

```
┌────────────────────────────────────────────┐
│  Webhook WhatsApp                          │
│  (llega consulta del usuario)              │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│  NODO 1: Verificar Límite                  │
│                                            │
│  1. Obtener cliente_id del número          │
│  2. Leer contador de Google Sheets         │
│  3. Verificar si < límite del plan         │
│                                            │
│  SI límite alcanzado:                      │
│    → Responder: "Bot pausado, upgrade"    │
│    → Enviar email de alerta               │
│    → FIN workflow                          │
│                                            │
│  SI hay consultas disponibles:             │
│    → Incrementar contador (+1)            │
│    → Continuar workflow                    │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│  NODO 2-N: Workflow normal                 │
│  (Haiku → Sonnet → Respuesta)              │
└────────────────────────────────────────────┘
```

---

### **Google Sheets como base de datos:**

```
Hoja: "Contadores"

┌──────────────┬─────────┬──────────────┬─────────┬──────────────┬──────────────┐
│ cliente_id   │ mes     │ consultas    │ limite  │ plan         │ ultimo_reset │
├──────────────┼─────────┼──────────────┼─────────┼──────────────┼──────────────┤
│ cristian     │ 2025-01 │ 423          │ 500     │ starter      │ 2025-01-01   │
│ navines      │ 2025-01 │ 847          │ 1500    │ growth       │ 2025-01-01   │
│ polverini    │ 2025-01 │ 1250         │ 3000    │ pro          │ 2025-01-01   │
└──────────────┴─────────┴──────────────┴─────────┴──────────────┴──────────────┘

Hoja: "Alertas_Enviadas"

┌──────────────┬─────────┬─────────────┬─────────────────────┐
│ cliente_id   │ mes     │ tipo_alerta │ fecha_envio         │
├──────────────┼─────────┼─────────────┼─────────────────────┤
│ cristian     │ 2025-01 │ 80%         │ 2025-01-22 14:30:00 │
│ cristian     │ 2025-01 │ 95%         │ 2025-01-28 09:15:00 │
└──────────────┴─────────┴─────────────┴─────────────────────┘
```

---

### **Código del nodo de verificación:**

```javascript
// NODO: Verificar Límite de Consultas

// 1. Obtener datos de entrada
const clientePhone = $json.from; // Número de WhatsApp
const mesActual = new Date().toISOString().slice(0, 7); // "2025-01"

// 2. Mapear teléfono a cliente_id (temporal - después usar DB)
const clienteMap = {
  "+5491123456789": "cristian",
  "+5491198765432": "navines"
};
const clienteId = clienteMap[clientePhone] || "desconocido";

// 3. Leer contador de Google Sheets
const sheets = $('Google Sheets').first().json;
const registro = sheets.find(r => 
  r.cliente_id === clienteId && r.mes === mesActual
);

// 4. Obtener plan y límite
const planes = {
  "starter": 500,
  "growth": 1500,
  "pro": 3000
};

const consultasUsadas = registro ? registro.consultas : 0;
const planActual = registro ? registro.plan : "starter";
const limite = planes[planActual];

// 5. Verificar si alcanzó límite
if (consultasUsadas >= limite) {
  // BOT PAUSADO
  return {
    json: {
      pausado: true,
      cliente_id: clienteId,
      consultas_usadas: consultasUsadas,
      limite: limite,
      plan: planActual,
      mensaje_usuario: `⚠️ Tu bot ha alcanzado el límite de ${limite} consultas este mes.\n\n` +
                       `Para reactivarlo:\n` +
                       `1️⃣ Comprar 250 consultas: bit.ly/comprar-consultas\n` +
                       `2️⃣ Upgradear tu plan: bit.ly/upgrade-plan\n` +
                       `3️⃣ Esperar al 1° del próximo mes\n\n` +
                       `Cualquier consulta: 11-XXXX-XXXX`,
      enviar_email_alerta: consultasUsadas === limite // Solo primera vez
    }
  };
}

// 6. Calcular porcentaje y verificar alertas
const porcentajeUso = (consultasUsadas / limite) * 100;
let enviarAlerta = false;
let tipoAlerta = null;

if (porcentajeUso >= 95 && consultasUsadas < limite * 0.96) {
  enviarAlerta = true;
  tipoAlerta = "95%";
} else if (porcentajeUso >= 80 && consultasUsadas < limite * 0.81) {
  enviarAlerta = true;
  tipoAlerta = "80%";
}

// 7. Incrementar contador
const nuevasConsultas = consultasUsadas + 1;

// 8. Retornar para continuar workflow
return {
  json: {
    pausado: false,
    cliente_id: clienteId,
    consultas_usadas: nuevasConsultas,
    consultas_restantes: limite - nuevasConsultas,
    limite: limite,
    plan: planActual,
    porcentaje_uso: porcentajeUso.toFixed(1),
    enviar_alerta: enviarAlerta,
    tipo_alerta: tipoAlerta,
    // Estos datos se usan para actualizar Google Sheets
    actualizar_sheets: {
      cliente_id: clienteId,
      mes: mesActual,
      consultas: nuevasConsultas,
      limite: limite,
      plan: planActual
    }
  }
};
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### **Fase 1: MVP con Cristian (Hard Stop básico)**

- [ ] Google Sheet con tabla de contadores
- [ ] Nodo de verificación de límite en N8N
- [ ] Mensaje de bot pausado al alcanzar límite
- [ ] Reset manual mensual (día 1)
- [ ] Dashboard simple (Google Sheets visualización)

### **Fase 2: Alertas (después del piloto)**

- [ ] Sistema de alertas 80%
- [ ] Sistema de alertas 95%
- [ ] Email automático al pausarse
- [ ] Tracking de alertas enviadas (no duplicar)

### **Fase 3: Auto-gestión (escalado)**

- [ ] Dashboard web para clientes
- [ ] Link de compra de consultas adicionales
- [ ] Link de upgrade de plan
- [ ] Reset automático el día 1 del mes
- [ ] Webhooks de Stripe para pagos

### **Fase 4: Analytics (optimización)**

- [ ] Reportes mensuales automáticos
- [ ] Gráficos de uso
- [ ] Proyecciones de consumo
- [ ] Sugerencias de plan óptimo

---

## 💰 PRICING FINAL RECOMENDADO

```
╔════════════════════════════════════════════╗
║  PLAN STARTER - Para empezar              ║
╠════════════════════════════════════════════╣
║  $25 USD/mes                               ║
║  500 consultas incluidas                   ║
║  Hard stop al alcanzar límite              ║
║  Alertas en 80% y 95%                      ║
║  Dashboard básico                          ║
║  Soporte por email                         ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  PLAN GROWTH - Recomendado                ║
╠════════════════════════════════════════════╣
║  $50 USD/mes                               ║
║  1,500 consultas incluidas                 ║
║  Overages: $0.04 por consulta (opcional)   ║
║  Alertas avanzadas                         ║
║  Dashboard completo                        ║
║  Soporte prioritario                       ║
║  Reportes semanales                        ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  PLAN PRO - Alto volumen                  ║
╠════════════════════════════════════════════╣
║  $90 USD/mes                               ║
║  3,000 consultas incluidas                 ║
║  Overages: $0.03 por consulta              ║
║  Sin límite hard (solo overages)           ║
║  Dashboard premium con analytics           ║
║  Soporte por WhatsApp                      ║
║  Reportes diarios                          ║
║  Account manager dedicado                  ║
╚════════════════════════════════════════════╝
```

---

## 🎯 ESTRATEGIA COMERCIAL

### **Para Cristian (Piloto):**

```
Oferta especial - Primer cliente:

Mes 1-3: GRATIS (piloto)
  • Máximo 1,000 consultas/mes
  • Todas las features incluidas
  • A cambio de: testimonial + caso de éxito

Mes 4 en adelante:
  • Plan Starter: $25/mes (descuento de lanzamiento)
  • Precio normal: $50/mes
  • Descuento permanente por ser early adopter

Condiciones:
  ✅ Testimonial escrito y en video
  ✅ Caso de éxito documentado con métricas
  ✅ Permiso para usar su logo en marketing
  ✅ Introducción a 2 contactos de la industria
```

---

## 📚 RECURSOS Y REFERENCIAS

### **Artículos útiles:**

1. "SaaS Pricing Strategies" - Price Intelligently
2. "How to set usage limits" - Stripe Billing Guide
3. "Customer Communication for Limit Alerts" - Intercom Blog
4. "Hard Stop vs Soft Stop" - SaaS Metrics

### **Herramientas:**

1. Google Sheets - Contador inicial
2. Stripe Billing - Facturación automática
3. SendGrid - Emails transaccionales
4. n8n - Automatización de alertas

---

## 🎓 APRENDIZAJES CLAVE

1. ✅ **Hard Stop es estándar** en planes pequeños/medianos
2. ✅ **Alertas proactivas** (80%, 95%) son críticas
3. ✅ **Dashboard transparente** genera confianza
4. ✅ **Opciones claras** al pausarse (comprar/upgrade/esperar)
5. ✅ **Pricing por uso** es justo y escalable
6. ✅ **Reset automático mensual** simplifica gestión
7. ✅ **Comunicación clara** evita chargebacks y quejas

---

**Documento creado:** 15 de Enero 2025  
**Última actualización:** 15 de Enero 2025  
**Próxima revisión:** Después del piloto con Cristian

---

## 📞 PRÓXIMOS PASOS

1. ✅ Validar modelo con Cristian
2. ⏳ Implementar contador básico en N8N
3. ⏳ Crear Google Sheet de control
4. ⏳ Testear flujo de pausa/reactivación
5. ⏳ Preparar emails de alertas
6. ⏳ Lanzar piloto de 3 meses
