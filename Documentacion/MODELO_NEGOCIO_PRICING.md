# 💼 MODELO DE NEGOCIO - BOT INMOBILIARIO

## 🎯 ESTRATEGIA DE PRICING

---

## 💰 ESTRUCTURA DE COSTOS REAL (con Haiku + Sonnet)

### **Costo por consulta:**
```
Haiku (filtrado):  $0.005 USD (medio centavo)
Sonnet (respuesta): $0.015 USD (1.5 centavos)
────────────────────────────────────────────
TOTAL:              $0.020 USD (2 centavos)
```

### **Escalabilidad:**
- ✅ 50 propiedades: $0.020/consulta
- ✅ 100 propiedades: $0.020/consulta
- ✅ 200 propiedades: $0.020/consulta
- ✅ 500 propiedades: $0.020/consulta

**El costo NO depende de la cantidad de propiedades.**

---

## 📊 PLANES SUGERIDOS

### **OPCIÓN A: Por consultas (recomendada)**

| Plan | Consultas/mes | Precio | Costo real | Margen |
|------|---------------|--------|------------|--------|
| **Starter** | 500 | $25 USD | $10 | 150% |
| **Growth** | 1,500 | $60 USD | $30 | 100% |
| **Pro** | 3,000 | $100 USD | $60 | 67% |
| **Enterprise** | 10,000 | $250 USD | $200 | 25% |

**Consultas adicionales:** $0.05 USD c/u

---

### **OPCIÓN B: Todo incluido (más simple de vender)**

| Plan | Precio | Consultas incluidas | Excedente |
|------|--------|---------------------|-----------|
| **Básico** | $49/mes | Hasta 2,000 | $0.05 c/u |
| **Profesional** | $99/mes | Hasta 5,000 | $0.04 c/u |
| **Premium** | $199/mes | Hasta 10,000 | $0.03 c/u |

---

### **OPCIÓN C: Freemium + Performance**

```
Plan Gratis:     100 consultas/mes
                 Para probar y convencerse

Plan Base:       $39/mes
                 1,000 consultas incluidas

Plan Performance: Setup $0
                  $0.05 por consulta
                  + 5% de comisión por cierre vía bot
```

**Este último alinea incentivos:** solo ganás si ellos ganan.

---

## 🎯 PROPUESTA PARA CRISTIAN (piloto)

### **Pricing especial para primer cliente:**

```
Mes 1-3: GRATIS (piloto)
         → Recopilar datos, casos de uso, testimonial
         → Máximo 1,000 consultas/mes

Mes 4 en adelante:
Plan Starter: $25/mes (500 consultas)
o
Plan Growth: $50/mes (1,500 consultas)

Condiciones:
- Testimonial escrito
- Caso de éxito documentado
- Permiso para usar su logo en marketing
- Referencia a otros brokers
```

---

## 📈 CONTADOR Y LÍMITES

### **Sistema de tracking:**

```sql
-- Tabla de control (Google Sheets / Airtable)
cliente_id | mes | consultas_usadas | limite_plan | plan_actual | costo_acumulado
-----------+-----+------------------+-------------+-------------+----------------
cristian   | 2025-01 | 347 | 500 | starter | $6.94
inmob-navines | 2025-01 | 1823 | 1500 | growth | $36.46 (excedió)
```

### **Alertas automáticas:**

#### **Al 80% del límite:**
```
Asunto: [AVISO] Ya usaste el 80% de tus consultas

Hola [Cliente],

Llevás 400 de 500 consultas este mes (80%).
Te quedan 100 consultas disponibles.

¿Necesitás más? Podés upgradearte a:
- Plan Growth (1,500/mes): Solo $35 más

Saludos,
[Tu empresa]
```

#### **Al 95% del límite:**
```
Asunto: [URGENTE] Quedan solo 25 consultas

Hola [Cliente],

Atención: Solo te quedan 25 consultas para este mes.

Para evitar interrupciones, podés:
1. Upgradear tu plan ahora
2. Comprar paquete adicional de 500 consultas ($20)

Link de upgrade: [...]
```

#### **Al 100% - Bot se pausa:**
```
Asunto: [ACCIÓN REQUERIDA] Límite alcanzado

Tu bot se pausó temporalmente porque alcanzaste el límite de 500 consultas.

Para reactivarlo:
1. Upgradear a Plan Growth ($60/mes)
2. Comprar paquete de 500 consultas ($25)
3. Esperar al próximo mes (resetea el 1)

[Botón: Reactivar ahora]
```

---

## 🔧 IMPLEMENTACIÓN TÉCNICA DEL CONTADOR

### **En N8N - Agregar al inicio del workflow:**

```javascript
// Nodo: "Verificar Límite de Consultas"

const clienteId = "cristian"; // Dinámico desde webhook
const mesActual = new Date().toISOString().slice(0, 7); // "2025-01"

// Leer contador de Google Sheets o Airtable
const contadorActual = await obtenerContador(clienteId, mesActual);

// Verificar límite
const limitesPlan = {
  "starter": 500,
  "growth": 1500,
  "pro": 3000
};

const planCliente = "starter"; // Leer de DB
const limite = limitesPlan[planCliente];

if (contadorActual >= limite) {
  // Bot pausado - enviar a nodo de error
  return {
    json: {
      error: true,
      mensaje: "Límite de consultas alcanzado",
      consultas_usadas: contadorActual,
      limite: limite,
      plan: planCliente
    }
  };
}

// Si tiene consultas disponibles, continuar
// Incrementar contador
await incrementarContador(clienteId, mesActual);

return {
  json: {
    cliente_id: clienteId,
    consultas_usadas: contadorActual + 1,
    consultas_restantes: limite - contadorActual - 1,
    porcentaje_usado: ((contadorActual + 1) / limite * 100).toFixed(1)
  }
};
```

---

## 📊 DASHBOARD PARA CLIENTES

### **Google Sheets simple:**

```
Cliente: Cristian
Plan: Starter (500 consultas/mes)

┌─────────────────────────────────────┐
│  Uso este mes (Enero 2025)         │
├─────────────────────────────────────┤
│  Consultas usadas:    347 / 500    │
│  Progreso: ████████░░ 69%           │
│  Consultas restantes: 153           │
│                                     │
│  Costo acumulado: $6.94             │
│  Resetea en: 13 días                │
└─────────────────────────────────────┘

Historial:
Dic 2024: 423 consultas ($8.46)
Nov 2024: 512 consultas ($10.24) ⚠️ Excedió
Oct 2024: 289 consultas ($5.78)
```

---

## 🎓 ARGUMENTOS DE VENTA

### **Para convencer de upgradear:**

#### **1. Framing positivo:**
```
❌ "Te estás quedando sin consultas"
✅ "¡Tu bot está funcionando tan bien que necesitás más capacidad!"
```

#### **2. Mostrar ROI:**
```
"Con 347 consultas este mes, capturaste 15 leads.
Si cerrás solo 1 propiedad, son $3,000 de comisión.

El plan Growth ($60/mes) se paga 50 veces.
¿Por qué limitar tus oportunidades?"
```

#### **3. Comparación con alternativas:**
```
Plan Growth: $60/mes, 1,500 consultas
= $0.04 por consulta

vs.

Contratar un asistente part-time: $800/mes
Servicio de chat outsourcing: $300/mes
Perder leads fuera de horario: $0/mes pero $$$$ en comisiones perdidas
```

---

## 🔥 ESTRATEGIAS DE UPSELL

### **1. Timing perfecto:**
- Al 90% del límite: "Upgrade ahora y te regalamos 200 consultas extra"
- Después de un cierre: "¡Felicitaciones! Para más éxitos como este, upgrade a Pro"

### **2. Bundles:**
```
Plan Growth ($60/mes)
+ Setup de 20 propiedades adicionales
+ Capacitación del equipo
+ Reporte mensual personalizado
──────────────────────────────
Precio normal: $120
OFERTA: $79/mes (ahorrás $41)
```

### **3. Anual con descuento:**
```
Mensual: $60/mes × 12 = $720/año
Anual: $599/año (ahorrás $121 - 17% OFF)
```

---

## 💼 CASOS DE USO DE PRICING

### **Caso 1: Inmobiliaria chica (como Cristian)**
```
Propiedades: 50
Consultas reales: 400-600/mes
Plan recomendado: Starter ($25/mes)
ROI: 1 cierre = 120x el costo
```

### **Caso 2: Inmobiliaria mediana**
```
Propiedades: 150
Consultas: 1,500-2,000/mes
Plan recomendado: Growth ($60/mes)
ROI: 2-3 cierres/mes = 100-150x el costo
```

### **Caso 3: Inmobiliaria grande**
```
Propiedades: 300+
Consultas: 5,000+/mes
Plan recomendado: Enterprise ($250/mes) + custom
ROI: 10+ cierres/mes = 120x+ el costo
```

---

## 🎯 ESTRATEGIA DE GO-TO-MARKET

### **Fase 1: Piloto con Cristian (Mes 1-3)**
- Gratis
- Recopilar métricas
- Documentar casos de éxito
- Conseguir testimonial

### **Fase 2: Early adopters (Mes 4-6)**
- 5 inmobiliarias más
- Plan Starter a $20/mes (descuento)
- A cambio de feedback y testimoniales

### **Fase 3: Lanzamiento (Mes 7+)**
- Pricing normal
- Casos de éxito documentados
- Marketing con testimoniales
- Webinars y demos

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### **Técnico:**
- [ ] Workflow optimizado Haiku + Sonnet
- [ ] Sistema de contador de consultas
- [ ] Integración con Google Sheets/Airtable
- [ ] Alertas automáticas (80%, 95%, 100%)
- [ ] Bot pause cuando se alcanza límite
- [ ] Dashboard de uso para clientes
- [ ] Reset automático mensual
- [ ] Logs de consultas (fecha, hora, costo)

### **Comercial:**
- [ ] Definir estructura de planes
- [ ] Crear landing page con pricing
- [ ] Configurar Stripe/MercadoPago
- [ ] Email templates (alertas, upgrades)
- [ ] Proceso de upgrade (1-click)
- [ ] Contrato/términos de servicio
- [ ] SLA (99% uptime, soporte, etc.)

### **Legal:**
- [ ] Términos y condiciones
- [ ] Política de privacidad
- [ ] Política de reembolsos
- [ ] GDPR compliance (si aplica)

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Implementar workflow optimizado
2. ✅ Testear con consultas reales
3. ✅ Calcular costos reales vs proyectados
4. ✅ Agregar sistema de contador
5. ⏳ Piloto con Cristian
6. ⏳ Iterar según feedback
7. ⏳ Escalar a más clientes

---

**Documento creado:** Enero 2025  
**Próxima revisión:** Después del piloto con Cristian
