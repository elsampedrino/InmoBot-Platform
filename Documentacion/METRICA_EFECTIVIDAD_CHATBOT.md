# Métrica de Efectividad del Chatbot

**Fecha de implementación:** 6 de enero 2026
**Versión workflow:** N8N_InmoBot - Estadisticas Semanales v2

---

## ¿Qué mide esta métrica?

Esta métrica compara **cuántos usuarios interactuaron con el chatbot** vs **cuántos efectivamente dejaron su contacto** como lead.

Es el **funnel de conversión del chatbot** que permite evaluar si el bot está siendo efectivo en convertir visitantes en leads.

---

## Métricas incluidas

### 1. **Sesiones Totales**
- Total de usuarios únicos que iniciaron una conversación con el chatbot
- Se obtiene contando `DISTINCT session_id` en `chat_logs`

### 2. **Sesiones Convertidas** ✅
- Usuarios que completaron el formulario de contacto
- Se obtiene contando `DISTINCT session_id` en `conversion_logs`

### 3. **Sesiones sin Conversión** ⚠️
- Usuarios que chatearon pero NO dejaron su contacto
- Cálculo: `Sesiones Totales - Sesiones Convertidas`

### 4. **Tasa de Conversión del Bot** 🎯
- Porcentaje de efectividad del chatbot
- Cálculo: `(Sesiones Convertidas / Sesiones Totales) * 100`

### 5. **Tasa de Abandono**
- Porcentaje de usuarios que abandonaron sin convertir
- Cálculo: `100 - Tasa de Conversión`

---

## Interpretación

### ✅ Tasa de Conversión ≥ 20%
**Excelente** - El chatbot es muy efectivo convirtiendo visitantes en leads

### ⚠️ Tasa de Conversión entre 10% - 19%
**Buena** - El chatbot funciona bien, hay margen de mejora

### ❌ Tasa de Conversión < 10%
**Mejorable** - El chatbot no está siendo efectivo, necesita optimización

---

## Ejemplo práctico

**Datos de la semana:**
- 100 usuarios únicos chatearon con el bot (Sesiones Totales)
- 18 usuarios dejaron su contacto (Sesiones Convertidas)
- 82 usuarios no convirtieron (Sesiones sin Conversión)

**Resultado:**
- **Tasa de Conversión del Bot:** 18%
- **Tasa de Abandono:** 82%

**Interpretación:** El chatbot está funcionando bien (18% > 15%), pero hay una oportunidad de optimizar el flujo conversacional para reducir la tasa de abandono.

---

## Diferencia con otras métricas

### vs. Tasa de Conversión General
- **Tasa de Conversión del Bot:** Mide efectividad del chatbot (sesiones → leads)
- **Tasa de Conversión General:** Mide leads sobre consultas totales (consultas → leads)

### Ejemplo de la diferencia:
- 100 sesiones únicas generan 200 consultas totales (2 consultas por sesión)
- 18 sesiones convierten en leads
- **Tasa del Bot:** 18/100 = 18% (efectividad del chatbot)
- **Tasa General:** 18/200 = 9% (conversión sobre consultas)

---

## Query SQL utilizado

```sql
-- Efectividad del Chatbot: Funnel de conversión
WITH sesiones_totales AS (
  SELECT COUNT(DISTINCT session_id) as total_sesiones
  FROM chat_logs
  WHERE timestamp >= NOW() - INTERVAL '7 days'
    AND repo = 'bbr'
),
sesiones_convertidas AS (
  SELECT COUNT(DISTINCT session_id) as sesiones_con_lead
  FROM conversion_logs
  WHERE timestamp >= NOW() - INTERVAL '7 days'
    AND repo = 'bbr'
)
SELECT
  st.total_sesiones,
  COALESCE(sc.sesiones_con_lead, 0) as sesiones_con_lead,
  st.total_sesiones - COALESCE(sc.sesiones_con_lead, 0) as sesiones_sin_conversion,
  CASE
    WHEN st.total_sesiones > 0 THEN
      ROUND((COALESCE(sc.sesiones_con_lead, 0)::numeric / st.total_sesiones::numeric) * 100, 1)
    ELSE 0
  END as tasa_conversion_chatbot
FROM sesiones_totales st
CROSS JOIN sesiones_convertidas sc;
```

---

## Visualización en el email

La métrica se muestra en una nueva sección **"🎯 Efectividad del Chatbot"** con:

1. **4 cards de métricas:**
   - Sesiones Totales
   - Sesiones Convertidas (verde)
   - Sesiones sin Conversión (amarillo)
   - Tasa de Conversión del Bot (color dinámico según valor)

2. **Descripción textual:**
   - Explicación del funnel de conversión
   - Contexto: "De X usuarios que chatearon, Y (Z%) completaron el formulario"

3. **Tip educativo:**
   - "Esta métrica mide qué tan efectivo es el chatbot en convertir visitantes en leads"
   - "Una tasa superior al 15% se considera buena"

4. **Colores dinámicos:**
   - Verde (≥20%): Excelente
   - Amarillo (10-19%): Buena
   - Rojo (<10%): Mejorable

---

## Casos de uso

### 1. Optimizar el flujo conversacional
Si la tasa de abandono es muy alta, revisar:
- ¿El bot responde correctamente?
- ¿La oferta de propiedades es relevante?
- ¿El formulario es fácil de completar?

### 2. A/B Testing
Probar diferentes versiones del chatbot y comparar tasas de conversión

### 3. Identificar problemas técnicos
Una caída súbita en la tasa puede indicar bugs o errores

### 4. Justificar ROI
Demostrar que el chatbot está generando leads efectivamente

---

## Implementación técnica

### Nuevo nodo agregado:
- **Nombre:** "Stats Efectividad Chatbot"
- **Tipo:** PostgreSQL
- **Posición en Merge:** Input 5 (índice 5)

### Modificaciones al workflow:
1. **Merge node:** Aumentado de 5 a 6 inputs
2. **Consolidar Estadísticas:** Agregada sección `efectividad` con 5 campos
3. **Generar HTML Email:** Nueva sección HTML entre "Resumen General" y "Conversiones"
4. **Schedule Trigger:** Conectado al nuevo nodo SQL

---

## Mantenimiento

- Query optimizado con CTEs (Common Table Expressions)
- Filtrado por repo='bbr' para multi-tenancy
- Manejo de casos NULL con COALESCE
- Índices existentes en session_id aceleran la consulta

---

## Referencias

- Workflow: `Flujos N8N/N8N_InmoBot - Estadisticas Semanales.json`
- Tablas: `chat_logs`, `conversion_logs`
- Campo clave: `session_id` (UUID único por usuario)
