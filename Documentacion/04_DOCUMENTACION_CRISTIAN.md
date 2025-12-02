# 📘 DOCUMENTACIÓN PARA CRISTIAN - INMOBOT WIDGET

## 🎯 ¿QUÉ ES ESTO?

Un chatbot con Inteligencia Artificial que responde consultas sobre tus propiedades automáticamente, 24/7, directamente en tu sitio web.

---

## 🌟 BENEFICIOS

✅ **Atención 24/7:** El bot responde incluso cuando dormís o estás ocupado  
✅ **Califica leads:** Identifica clientes serios antes de que los contactes  
✅ **Ahorra tiempo:** No respondés 100 veces "¿Cuánto sale el depto de X?"  
✅ **Mejora conversión:** Los visitantes obtienen respuestas inmediatas  
✅ **Datos valiosos:** Sabés qué busca la gente en tiempo real  

---

## 💰 PRICING

### **Plan Starter (Recomendado para empezar)**

```
$25 USD/mes
500 consultas incluidas
```

**¿Cuánto son 500 consultas?**
- ~16 consultas por día
- Perfecto para testear el sistema
- Suficiente para capturar 15-20 leads/mes

**¿Qué pasa si me paso?**
- El bot se pausa automáticamente
- Te avisamos por email
- Podés comprar 250 consultas extra por $15
- O upgradear al siguiente plan

### **Plan Growth (Para escalar)**

```
$50 USD/mes
1,500 consultas incluidas
```

**Ideal si:**
- Tenés más de 30 consultas/día
- Querés capturar más leads
- El bot ya te generó ventas

---

## 🚀 CÓMO INTEGRARLO EN TU WEB

### **Paso 1: Copiar este código**

```html
<!-- Chatbot InmoBot - Pegar antes de </body> -->
<script src="https://tudominio.com/inmobot-widget.js"></script>
<script>
  InmoBot.init({
    apiUrl: 'https://n8n-bot-inmobiliario.onrender.com/webhook/chat',
    primaryColor: '#2563eb',
    botName: 'AsistenteBot',
    welcomeMessage: '¡Hola! Soy tu asistente virtual de [TU INMOBILIARIA]. ¿Buscás alquilar o comprar?'
  });
</script>
```

### **Paso 2: Personalizar (opcional)**

Podés cambiar:

```javascript
primaryColor: '#059669',  // Color de tu marca (en formato hexadecimal)
botName: 'Cristian',      // Tu nombre o el de tu inmobiliaria
welcomeMessage: '...'     // El mensaje inicial
```

**Cómo conseguir el color de tu marca:**
1. Ir a: https://htmlcolorcodes.com
2. Hacer click en tu logo
3. Copiar el código (ej: #2563eb)

### **Paso 3: Pegar en tu web**

**Si tenés WordPress:**
1. Panel → Apariencia → Editor de temas
2. Buscar `footer.php`
3. Pegar el código ANTES de `</body>`
4. Guardar

**Si tenés HTML directo:**
1. Abrir tu `index.html`
2. Buscar `</body>` (casi al final)
3. Pegar el código ANTES de `</body>`
4. Guardar y subir por FTP

**Si usás Wix/Squarespace:**
1. Settings → Custom Code
2. Pegar en "Footer Code"
3. Guardar

---

## 🎨 PERSONALIZACIÓN

### **Cambiar colores:**

```javascript
primaryColor: '#2563eb'  // Azul (default)
primaryColor: '#059669'  // Verde
primaryColor: '#dc2626'  // Rojo
primaryColor: '#7c3aed'  // Violeta
```

### **Cambiar posición:**

```javascript
position: 'bottom-right'  // Abajo derecha (default)
position: 'bottom-left'   // Abajo izquierda
position: 'top-right'     // Arriba derecha
position: 'top-left'      // Arriba izquierda
```

### **Cambiar tamaño:**

```javascript
buttonSize: '60px',   // Tamaño del botón flotante
chatWidth: '380px',   // Ancho de la ventana de chat
chatHeight: '600px'   // Alto de la ventana de chat
```

---

## 📊 CÓMO MONITOREAR TU BOT

### **Dashboard (próximamente)**

Te vamos a dar acceso a un dashboard donde vas a ver:

- 📈 Consultas por día/semana/mes
- 💬 Conversaciones completas
- 🏠 Propiedades más consultadas
- 📍 Zonas más buscadas
- 💰 ROI del bot

### **Por ahora:**

Te mandamos un reporte semanal por email con:
- Total de consultas
- Leads capturados
- Propiedades más vistas
- Preguntas frecuentes

---

## ❓ PREGUNTAS FRECUENTES

### **¿Funciona en móviles?**

Sí, 100% responsive. Se adapta automáticamente a cualquier tamaño de pantalla.

### **¿Puedo probarlo antes de integrarlo?**

Sí, te damos un link de demo para que lo pruebes durante 1 semana gratis.

### **¿Qué pasa si el bot no sabe responder algo?**

El bot está entrenado con tus propiedades. Si alguien pregunta algo muy específico que no está en la base de datos, responde: "No tengo esa información, pero te puedo contactar con nuestro equipo. Dejame tu email/teléfono."

### **¿Puedo pausar el servicio?**

Sí, en cualquier momento. Sin permanencia mínima.

### **¿El bot reemplaza mi trabajo?**

No, te complementa. El bot califica leads y responde preguntas básicas. Vos cerrás las operaciones y coordinás visitas.

### **¿Cómo actualizo mis propiedades?**

Te damos acceso a un Google Sheet donde subís/editás propiedades. Se actualiza automático en el bot.

### **¿Funciona si mi web está en Mercado Libre / Zonaprop?**

No, el widget solo funciona en tu sitio web propio. Pero podés compartir el link del widget directamente.

### **¿Puedo tener varios bots (uno por sucursal)?**

Sí, pero cada bot es un plan separado.

---

## 🛠️ SOPORTE TÉCNICO

### **Si algo no funciona:**

1. **Verificar que el código esté bien pegado:**
   - Debe estar ANTES de `</body>`
   - No debe tener errores de tipeo
   - Debe tener comillas correctas (`'` o `"`)

2. **Limpiar caché del navegador:**
   - Chrome: Ctrl + Shift + R (Windows) o Cmd + Shift + R (Mac)
   - Firefox: Ctrl + F5
   - Safari: Cmd + Option + R

3. **Ver errores en consola:**
   - F12 → Console
   - Buscar mensajes en rojo
   - Mandarnos screenshot

### **Contacto:**

📧 Email: soporte@inmobot.com  
📱 WhatsApp: +54 9 11 XXXX-XXXX  
⏰ Horario: Lun-Vie 9-18hs (respondemos en <2 horas)  

---

## 📈 CASO DE ÉXITO (EJEMPLO)

**Inmobiliaria García - Belgrano**

```
Antes del bot:
- 50 consultas/mes por WhatsApp
- 30% respondidas (las demás se pierden)
- 5 visitas coordinadas/mes
- 1-2 operaciones cerradas/mes

Con el bot (después de 3 meses):
- 200 consultas/mes (el bot responde 24/7)
- 100% atendidas
- 25 visitas coordinadas/mes (5x más)
- 6 operaciones cerradas/mes (3x más)

ROI: $50/mes de inversión → ~$45,000 más en comisiones
```

---

## 🎁 BONUS: TIPS PARA MAXIMIZAR RESULTADOS

### **1. Promocioná el bot:**

Agregá en tu web:
```
"Preguntale a nuestro asistente virtual 👉"
"Encontrá tu propiedad ideal en 30 segundos 🤖"
```

### **2. Compartí el link directo:**

El widget también funciona como página standalone:
```
https://tudominio.com/chatbot

Compartir en:
- WhatsApp Status
- Instagram Bio
- Facebook Ads
- Email signature
```

### **3. Usalo para calificar:**

El bot pregunta:
- ¿Buscás alquilar o comprar?
- ¿Qué presupuesto tenés?
- ¿En qué zona?
- ¿Cuántos ambientes?

Vos recibís leads pre-calificados listos para contactar.

---

## 🚀 PRÓXIMOS PASOS

1. ✅ **Probar el demo** (te mandamos link)
2. ✅ **Decidir si seguir** (primera semana gratis)
3. ✅ **Integrar en tu web** (nosotros te ayudamos)
4. ✅ **Empezar a capturar leads** 
5. ✅ **Monitorear resultados**
6. ✅ **Optimizar** (ajustamos según tus datos)

---

## 💬 TESTIMONIOS

> "El bot responde mejor que mi secretaria. Ahora solo atiendo visitas, no consultas básicas." - Martín G., Inmobiliaria MG

> "Capturé 3 clientes en el primer día. Ya se pagó solo." - Laura S., Remax

> "Mis clientes aman la atención inmediata. Aumenté 40% las consultas." - Roberto P., Century 21

---

## 📞 ¿LISTO PARA EMPEZAR?

Escribinos a:
- 📧 ventas@inmobot.com
- 📱 WhatsApp: +54 9 11 XXXX-XXXX

O agendá una demo de 15 minutos:
🗓️ https://calendly.com/inmobot/demo

---

**¡Bienvenido a la nueva era de la atención al cliente inmobiliaria!** 🚀

---

## 📋 CHECKLIST DE INTEGRACIÓN

Usá esta lista para verificar que todo esté ok:

- [ ] Código copiado correctamente
- [ ] Pegado antes de `</body>`
- [ ] Colores personalizados
- [ ] Mensaje de bienvenida personalizado
- [ ] Probado en navegador
- [ ] Probado en móvil
- [ ] Sin errores en consola
- [ ] Botón aparece abajo a la derecha
- [ ] Click abre el chat
- [ ] Bot responde correctamente
- [ ] ✅ TODO LISTO

---

**Documento creado:** 15 de Enero 2025  
**Para:** Cristian (Cliente piloto)  
**Versión:** 1.0 - MVP  
**Próxima revisión:** Después del piloto de 3 meses
