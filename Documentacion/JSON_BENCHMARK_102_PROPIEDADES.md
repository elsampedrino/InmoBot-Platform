# JSON de Benchmark - 102 Propiedades

**Fecha de creación:** 6 de enero 2026
**Archivo:** `BBR Grupo Inmobiliario/propiedades_bbr_benchmark_102.json`
**Script generador:** `Scripts-Templates/generar_json_benchmark.py`

---

## Objetivo

Generar un catálogo de prueba con **102 propiedades** para evaluar:
- Tiempos de respuesta del chatbot con catálogos grandes
- Consumo de tokens (Haiku/Sonnet)
- Costos estimados de operación
- Performance de búsquedas semánticas

---

## Metodología

Se triplicaron las 34 propiedades originales del JSON de BBR (`propiedades_bbr.json`), modificando **únicamente el campo `id`** de cada propiedad.

### Estructura de IDs:

```
Lote 1 (Originales):  PROP-001 → PROP-034  (34 propiedades)
Lote 2 (Copia 1):     PROP-035 → PROP-068  (34 propiedades)
Lote 3 (Copia 2):     PROP-069 → PROP-102  (34 propiedades)
─────────────────────────────────────────────────────────────
Total:                                       102 propiedades
```

---

## Características del JSON

### ✅ Datos idénticos (excepto ID)
- Todos los demás campos permanecen iguales
- Mismas fotos, descripciones, precios, características
- Mismas URLs de Cloudinary
- Misma estructura de datos

### 📊 Distribución por tipo (x3):
- 25 casas → **75 casas**
- 2 departamentos → **6 departamentos**
- 3 terrenos → **9 terrenos**
- 3 campos → **9 campos**
- 1 local comercial → **3 locales comerciales**

### 💰 Rango de precios (se replica):
- Mínimo: USD 10,000 (terreno)
- Máximo: USD 532,000 (campo)
- Alquileres: ARS 250,000 - ARS 500,000

---

## Tamaño del archivo

| Archivo | Propiedades | Tamaño |
|---------|-------------|--------|
| `propiedades_bbr.json` (original) | 34 | 39 KB |
| `propiedades_bbr_benchmark_102.json` | 102 | 115 KB |

**Factor de crecimiento:** ~3x en tamaño (coherente con 3x propiedades)

---

## Cómo usar el JSON de benchmark

### Opción 1: Reemplazar temporalmente el JSON en GitHub

1. **Backup del JSON actual:**
   ```bash
   cp BBR\ Grupo\ Inmobiliario/propiedades_bbr.json BBR\ Grupo\ Inmobiliario/propiedades_bbr_backup_temp.json
   ```

2. **Reemplazar con el benchmark:**
   ```bash
   cp BBR\ Grupo\ Inmobiliario/propiedades_bbr_benchmark_102.json BBR\ Grupo\ Inmobiliario/propiedades_bbr.json
   ```

3. **Subir a GitHub:**
   ```bash
   git add BBR\ Grupo\ Inmobiliario/propiedades_bbr.json
   git commit -m "Test: Usar JSON benchmark de 102 propiedades para testing"
   git push
   ```

4. **Hacer pruebas con el chatbot**

5. **Restaurar JSON original:**
   ```bash
   git revert HEAD
   git push
   ```

### Opción 2: Crear un endpoint de testing

Modificar el código del chatbot para que pueda apuntar a diferentes JSONs según un parámetro.

---

## Escenarios de testing

### 1. **Búsquedas amplias**
- Consulta: "Quiero una casa en Ramallo"
- Resultado esperado: ~75 casas
- Métrica a observar: Tiempo de filtrado y ranking

### 2. **Búsquedas específicas**
- Consulta: "Casas con pileta de más de 100,000 USD"
- Resultado esperado: Subconjunto de las 75 casas
- Métrica a observar: Precisión del filtrado

### 3. **Búsquedas por rango de precio**
- Consulta: "Propiedades entre 50,000 y 100,000 USD"
- Métrica a observar: Correctitud del filtrado numérico

### 4. **Límite de resultados**
- Consulta: "Todas las propiedades disponibles"
- Métrica a observar: ¿Cuántas muestra el bot? ¿Pagina resultados?

---

## Métricas a evaluar

### ⏱️ Tiempos de respuesta
- **Baseline (34 propiedades):** X segundos
- **Benchmark (102 propiedades):** Y segundos
- **Factor de degradación:** Y/X

### 💰 Consumo de tokens
- **Haiku tokens:** Filtrado y búsqueda inicial
- **Sonnet tokens:** Generación de respuestas
- **Total tokens:** Por consulta

### 💵 Costos estimados
- **Costo por consulta (34 props):** $X
- **Costo por consulta (102 props):** $Y
- **Proyección mensual:** (consultas/mes) × Y

### 📊 Calidad de respuestas
- ¿El bot sigue respondiendo correctamente?
- ¿Respeta el límite de propiedades mostradas?
- ¿La relevancia de resultados es buena?

---

## Resultados esperados

### Hipótesis:

1. **Tiempo de respuesta:**
   - Debería aumentar linealmente (~3x más tiempo)
   - Si aumenta más, hay un problema de eficiencia

2. **Consumo de tokens:**
   - Haiku: Aumento proporcional al catálogo
   - Sonnet: Debería mantenerse similar (solo genera texto de respuesta)

3. **Costos:**
   - El costo principal debería seguir siendo Sonnet
   - Haiku aumentará pero es más económico

4. **Calidad:**
   - No debería degradarse
   - Si se degrada, revisar lógica de ranking/filtrado

---

## Limpieza después del testing

Después de completar las pruebas, **restaurar el JSON original**:

```bash
# Si usaste Opción 1 (reemplazo)
git revert HEAD
git push

# Eliminar backup temporal
rm BBR\ Grupo\ Inmobiliario/propiedades_bbr_backup_temp.json
```

**Importante:** El archivo benchmark (`propiedades_bbr_benchmark_102.json`) puede quedar en el repo como referencia para futuras pruebas.

---

## Regenerar el benchmark

Si necesitas regenerar el JSON (por ejemplo, si actualizaste las propiedades originales):

```bash
python Scripts-Templates/generar_json_benchmark.py
```

El script:
1. Lee `propiedades_bbr.json` (34 propiedades)
2. Triplica las propiedades
3. Modifica solo los IDs: PROP-001 → PROP-102
4. Guarda en `propiedades_bbr_benchmark_102.json`

---

## Próximos pasos

1. **Ejecutar testing con 102 propiedades**
2. **Documentar resultados** (crear archivo BENCHMARK_RESULTS.md)
3. **Comparar con baseline de 34 propiedades**
4. **Decidir si se necesita optimización**
5. **Evaluar escalabilidad** (¿qué pasa con 200+ propiedades?)

---

## Notas

- Las URLs de fotos son las mismas (las propiedades duplicadas apuntan a las mismas imágenes)
- Esto es **solo para testing**, no para producción
- Los IDs duplicados no afectarán el testing porque el chatbot no hace operaciones CRUD
- Para testing realista, considera que un catálogo real de 100 props tendría más diversidad
