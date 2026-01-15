# 📊 Workflow: Estadísticas Semanales por Email

**Fecha:** 28 de Diciembre 2025
**Workflow:** `N8N_Estadisticas_Email.json`
**Frecuencia:** Cada lunes a las 9:00 AM
**Destinatario:** cristian.barbieripriotti@gmail.com

---

## 🎯 Objetivo

Enviar un reporte semanal automático a Cristian con estadísticas completas del chatbot InmoBot, incluyendo:
- Total de consultas y tasa de éxito
- Consumo de tokens y costos estimados
- Distribución por idioma
- Propiedades más vistas
- Errores detectados

---

## 📋 Estructura del Workflow

```
Schedule Trigger (Lunes 9 AM)
    ↓
    ├─→ Stats General ──────┐
    ├─→ Stats Por Idioma ───┤
    ├─→ Top 10 Propiedades ─┼─→ Consolidar Estadísticas
    └─→ Tipos de Errores ───┘         ↓
                              Generar HTML Email
                                      ↓
                                Enviar Email
```

---

## 🔧 Configuración Paso a Paso

### 1. Importar el Workflow en N8N

1. Abre N8N en tu navegador
2. Menú superior → **Workflows**
3. Click en **Import from File**
4. Selecciona el archivo: `Flujos N8N/N8N_Estadisticas_Email.json`
5. El workflow se importará con el nombre: **"Estadísticas Semanales - Email a Cristian"**

---

### 2. Configurar Credenciales SMTP (Gmail)

El workflow necesita credenciales SMTP para enviar emails.

#### Opción A: Gmail con App Password (Recomendado)

1. En N8N, ve a **Settings** → **Credentials**
2. Click en **Add Credential** → Busca **SMTP**
3. Completa los campos:

```
Name: Gmail SMTP
User: tu-email@gmail.com
Password: [App Password - ver instrucciones abajo]
Host: smtp.gmail.com
Port: 587
SSL/TLS: Enable
```

**Cómo obtener App Password de Gmail:**
1. Ve a https://myaccount.google.com/security
2. Habilita **Verificación en 2 pasos** si no lo hiciste
3. Busca **Contraseñas de aplicaciones**
4. Genera una nueva contraseña para "Correo"
5. Copia la contraseña de 16 caracteres
6. Pégala en el campo "Password" de N8N

#### Opción B: Otro proveedor SMTP

Si prefieres usar otro proveedor (SendGrid, Mailgun, etc.), ajusta los valores según tu proveedor.

---

### 3. Actualizar Credential ID en el Workflow

Una vez creada la credencial SMTP:

1. Abre el workflow importado en N8N
2. Click en el nodo **"Enviar Email"**
3. En el panel derecho, sección **Credentials**
4. Selecciona la credencial "Gmail SMTP" que creaste
5. N8N asignará automáticamente el ID correcto
6. **Save** el workflow

---

### 4. Verificar Conexión PostgreSQL

El workflow ya tiene configurada la conexión a PostgreSQL con ID: `Cas8eHe2cYh3vHyG`

**Si necesitas cambiar la conexión:**

1. Click en cualquier nodo de query (Stats General, Stats Por Idioma, etc.)
2. En **Credentials** → Selecciona tu conexión PostgreSQL
3. Repite para los 4 nodos de queries

---

### 5. Ajustar Email Destinatario (Opcional)

Si necesitas cambiar el destinatario:

1. Click en el nodo **"Enviar Email"**
2. Modifica el campo **To Email**
3. Valor actual: `cristian.barbieripriotti@gmail.com`

---

### 6. Probar el Workflow Manualmente

Antes de activar el cron, prueba el workflow:

1. Click en **Execute Workflow** (botón en la esquina superior derecha)
2. Verifica que todos los nodos se ejecuten correctamente (✅ verde)
3. Revisa el email enviado en la bandeja de entrada de Cristian
4. Si hay errores, revisa los logs en cada nodo

---

### 7. Activar el Workflow

Una vez que funcione correctamente:

1. Toggle **Active** en la esquina superior derecha
2. El workflow se ejecutará automáticamente cada lunes a las 9 AM
3. N8N mostrará "Active" en verde

---

## 📊 Queries SQL Explicadas

### Query 1: Stats General

```sql
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
  SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as consultas_fallidas,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms,
  SUM(tokens_haiku) as tokens_haiku_total,
  SUM(tokens_sonnet) as tokens_sonnet_total,
  SUM(tokens_total) as tokens_totales,
  SUM(propiedades_mostradas) as propiedades_mostradas_total
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days';
```

**Retorna:**
- Total de consultas en los últimos 7 días
- Cuántas fueron exitosas/fallidas
- Tiempo promedio de respuesta
- Tokens consumidos por modelo
- Total de propiedades mostradas

---

### Query 2: Stats Por Idioma

```sql
SELECT
  idioma,
  COUNT(*) as cantidad,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as porcentaje
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY idioma
ORDER BY cantidad DESC;
```

**Retorna:**
- Cantidad de consultas por idioma (es, en, pt)
- Porcentaje de cada idioma

---

### Query 3: Top 10 Propiedades

```sql
SELECT
  UNNEST(propiedades_ids) as propiedad_id,
  COUNT(*) as veces_mostrada
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND propiedades_ids IS NOT NULL
GROUP BY propiedad_id
ORDER BY veces_mostrada DESC
LIMIT 10;
```

**Retorna:**
- Las 10 propiedades más mostradas
- Cuántas veces fue mostrada cada una

**Nota:** `UNNEST()` expande el array de IDs para contar individualmente.

---

### Query 4: Tipos de Errores

```sql
SELECT
  error_type,
  COUNT(*) as cantidad
FROM chat_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
  AND success = 0
GROUP BY error_type
ORDER BY cantidad DESC;
```

**Retorna:**
- Tipos de error y cuántas veces ocurrieron
- Solo consultas fallidas (success = 0)

---

## 💰 Cálculo de Costos

El workflow calcula costos aproximados basados en tarifas de Anthropic:

```javascript
// Tarifas (en USD por 1M tokens)
const HAIKU_RATE = 0.25;   // $0.25 por 1M tokens
const SONNET_RATE = 3.00;  // $3.00 por 1M tokens

// Cálculo
const costoHaiku = (tokens_haiku_total / 1000000) * 0.25;
const costoSonnet = (tokens_sonnet_total / 1000000) * 3.00;
const costoTotal = costoHaiku + costoSonnet;
```

**Para actualizar las tarifas:**
1. Abre el nodo **"Consolidar Estadísticas"**
2. Modifica las líneas 53-54 con las nuevas tarifas
3. Save el workflow

---

## 📧 Formato del Email

El email HTML incluye:

### 1. Header
- Título: "📊 Estadísticas InmoBot"
- Periodo: Fecha inicio - Fecha fin (últimos 7 días)
- Gradient morado/azul

### 2. Resumen General (Metric Cards)
- **Total Consultas**: Cantidad total
- **Éxito**: Porcentaje en verde
- **Tiempo Promedio**: En segundos
- **Propiedades Mostradas**: Total

### 3. Consumo de Tokens y Costos
- **Tokens Haiku**: Cantidad en miles + costo
- **Tokens Sonnet**: Cantidad en miles + costo
- **Costo Total**: Suma total en USD

### 4. Tabla: Consultas por Idioma
- Español 🇦🇷
- Inglés 🇺🇸
- Portugués 🇧🇷
- Cantidad y porcentaje

### 5. Tabla: Top 10 Propiedades
- IDs de propiedades más vistas
- Medallas 🥇🥈🥉 para las top 3
- Cantidad de veces mostrada

### 6. Tabla: Errores Detectados (si hay)
- Tipo de error
- Cantidad de ocurrencias

### 7. Footer
- "Reporte generado automáticamente por N8N"
- "InmoBot - BBR Grupo Inmobiliario"

---

## 🎨 Personalizar el Email

### Cambiar Colores

Abre el nodo **"Generar HTML Email"** y busca estas líneas en el CSS:

```css
/* Gradient del header */
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }

/* Color principal (botones, títulos) */
.metric-value { color: #667eea; }
table th { background-color: #667eea; }
```

Reemplaza `#667eea` (morado) con tu color preferido.

---

### Cambiar Asunto del Email

Busca esta línea en el nodo **"Generar HTML Email"**:

```javascript
subject: `📊 Estadísticas InmoBot - ${data.periodo.inicio} a ${data.periodo.fin}`
```

---

### Agregar Sección Nueva

En el nodo **"Generar HTML Email"**, agrega una nueva sección antes del footer:

```html
<div class="section">
  <h2>🆕 Mi Nueva Sección</h2>
  <p>Contenido aquí...</p>
</div>
```

---

## ⏰ Modificar la Frecuencia

**Actual:** Lunes a las 9:00 AM

**Para cambiar:**

1. Click en el nodo **"Schedule Trigger"**
2. Modifica el campo **Cron Expression**

**Ejemplos:**

```
0 9 * * 1   → Lunes a las 9 AM (actual)
0 9 * * 5   → Viernes a las 9 AM
0 18 * * *  → Todos los días a las 6 PM
0 9 1 * *   → Primer día del mes a las 9 AM
0 9 * * 1,4 → Lunes y jueves a las 9 AM
```

**Formato cron:** `minuto hora día_mes mes día_semana`

---

## 🔍 Troubleshooting

### Problema 1: Email no se envía

**Posibles causas:**
- Credenciales SMTP incorrectas
- App Password de Gmail no generada
- Puerto bloqueado (prueba 465 en vez de 587)

**Solución:**
1. Verifica que la App Password esté copiada correctamente
2. Revisa que TLS/SSL esté habilitado
3. Testea la conexión SMTP directamente desde N8N

---

### Problema 2: Queries PostgreSQL fallan

**Posibles causas:**
- Conexión PostgreSQL incorrecta
- Tabla `chat_logs` no existe
- Campos de la tabla diferentes

**Solución:**
1. Verifica la conexión en N8N Settings → Credentials
2. Ejecuta manualmente las queries en PostgreSQL para verificar

---

### Problema 3: El cron no se ejecuta

**Posibles causas:**
- Workflow no está activo (toggle OFF)
- Render free plan (se duerme) → Ya resuelto con Starter
- Expresión cron incorrecta

**Solución:**
1. Verifica que el toggle "Active" esté en verde
2. Confirma que Render no esté en sleep mode
3. Valida la expresión cron en https://crontab.guru/

---

### Problema 4: Email se ve mal en Gmail

**Posibles causas:**
- HTML mal formado
- CSS no soportado por Gmail

**Solución:**
1. Gmail soporta CSS inline limitado (evita `display: grid` si no funciona)
2. Prueba en otro cliente de email (Outlook, etc.)
3. Usa tablas HTML en vez de divs para mejor compatibilidad

---

## 📝 Logs y Monitoreo

### Ver Ejecuciones Pasadas

1. En N8N, abre el workflow
2. Click en **Executions** (panel lateral)
3. Verás todas las ejecuciones con:
   - Fecha/hora
   - Estado (Success/Error)
   - Duración

### Ver Detalles de una Ejecución

1. Click en cualquier ejecución de la lista
2. Verás el flujo completo con:
   - Datos de entrada/salida de cada nodo
   - Errores específicos si los hubo
   - Tiempo de ejecución por nodo

---

## 🚀 Próximos Pasos

Una vez que el workflow esté funcionando:

1. **Monitorear primera ejecución** (próximo lunes)
2. **Verificar que el email llegue correctamente**
3. **Ajustar contenido según feedback de Cristian**
4. **Considerar agregar:**
   - Gráficos (Chart.js embebido)
   - Comparación con semana anterior
   - Alertas si métricas están fuera de rango
   - Export a PDF adjunto

---

## 📌 Notas Importantes

- **GitHub Raw Cache:** Las estadísticas se basan en `chat_logs`, no en JSONs de GitHub
- **Zona Horaria:** N8N usa UTC por defecto. Si necesitas ART (UTC-3), ajusta la hora en el cron
- **Render Starter Plan:** ✅ Ya no hay problema de sleep, los cron funcionarán correctamente
- **Costos:** Las tarifas de Anthropic pueden cambiar, actualiza el nodo de consolidación si es necesario

---

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5
**Estado:** ✅ Listo para importar y testear
