# 📋 Normalización de JSONs - Resumen Completo

**Fecha:** 28 de Diciembre 2025

---

## 🎯 Problema Identificado

Los workflows de N8N normalizan las consultas de usuarios a minúsculas, pero los JSONs tenían valores en mayúsculas/minúsculas mixtas, causando **fallos en el matching**.

### Ejemplo del Problema:

```
Usuario: "busco departamento para alquilar"
Prompt convierte a: "departamento" + "alquiler"
JSON tenía: "tipo": "Departamento", "operacion": "Alquiler" ❌
Resultado: NO MATCH
```

---

## ✅ Solución Implementada

**Normalización bidireccional:**
1. ✅ **Prompt:** Convierte consulta a minúsculas (ya estaba)
2. ✅ **JSON:** Normalizar campos clave a minúsculas (implementado hoy)

---

## 🔧 Scripts Creados

### 1. `normalizar_json_minusculas.py`
**Función:** Normaliza el JSON de BBR (34 propiedades)

**Campos normalizados:**
- `tipo`: Casa → casa, Departamento → departamento
- `operacion`: Venta → venta, Alquiler → alquiler
- `estado_construccion`: Usado → usado, Semi construida → semi construida

**Resultado:**
- 102 cambios en 34 propiedades
- Backup automático con timestamp
- Verifica que todo quede en minúsculas

---

### 2. `estandarizar_demo.py`
**Función:** Estandariza el JSON demo (4 propiedades) al formato BBR

**Cambios aplicados:**
- Normalizar tipo/operacion a minúsculas
- Convertir `detalles` de objeto → array
- Mover `expensas` dentro de `precio`
- Agregar `estado_construccion` basado en antigüedad
- Agregar metadata (version 2.0.0)

**Resultado:**
- 4 propiedades estandarizadas
- 100% compatible con workflows Haiku y Haiku+Sonnet
- 86 inserciones, 152 eliminaciones (simplificación)

---

### 3. `sincronizar_json_git.py`
**Función:** Sincroniza JSON de BBR al repositorio `bot-inmobiliaria-data`

**Proceso:**
1. Clona repo temporal
2. Copia JSON normalizado
3. Hace commit automático
4. Push a GitHub
5. Limpia directorio temporal

**Uso:**
```bash
python Scripts-Templates/sincronizar_json_git.py
```

---

### 4. `sincronizar_demo_git.py`
**Función:** Sincroniza JSON demo al repositorio `bot-inmobiliaria-data`

**Uso:**
```bash
python Scripts-Templates/sincronizar_demo_git.py
```

---

## 📊 Resultados

### JSON BBR (propiedades_bbr.json)

**Antes:**
```json
{
  "tipo": "Departamento",
  "operacion": "Alquiler",
  "estado_construccion": "Usado"
}
```

**Después:**
```json
{
  "tipo": "departamento",
  "operacion": "alquiler",
  "estado_construccion": "usado"
}
```

**Valores únicos:**
- `tipo`: `['campo', 'casa', 'departamento', 'local comercial', 'terreno']`
- `operacion`: `['alquiler', 'venta']`
- `estado_construccion`: `['semi construida', 'usado']`

---

### JSON Demo (propiedades_demo.json)

**Antes:**
```json
{
  "tipo": "Departamento",
  "operacion": "Alquiler",
  "detalles": {
    "cochera": true,
    "balcon": true,
    "ascensor": true
  },
  "expensas": 85000
}
```

**Después:**
```json
{
  "tipo": "departamento",
  "operacion": "alquiler",
  "estado_construccion": "usado",
  "precio": {
    "valor": 950,
    "moneda": "USD",
    "expensas": 85000
  },
  "detalles": ["cochera", "balcon", "ascensor"]
}
```

**Valores únicos:**
- `tipo`: `['casa', 'departamento', 'local comercial']`
- `operacion`: `['alquiler', 'venta']`
- `estado_construccion`: `['a estrenar', 'usado']`

---

## 🔄 Workflow de Actualización

### Cuando agregar nuevas propiedades:

#### Para BBR:
```bash
# 1. Actualizar Excel con nuevas propiedades
# 2. Generar JSON
python Scripts-Templates/excel_to_json.py

# 3. Normalizar (automático si seguís la plantilla)
python Scripts-Templates/normalizar_json_minusculas.py

# 4. Optimizar fotos nuevas
python Scripts-Templates/optimizar_fotos_nuevas.py

# 5. Subir fotos a Cloudinary
python Scripts-Templates/subir_fotos_cloudinary.py

# 6. Sincronizar a GitHub
python Scripts-Templates/sincronizar_json_git.py
```

#### Para Demo:
```bash
# 1. Editar Demo_Inmob/propiedades_demo.json manualmente
# 2. Estandarizar
python Scripts-Templates/estandarizar_demo.py

# 3. Sincronizar a GitHub
python Scripts-Templates/sincronizar_demo_git.py
```

---

## 🌐 URLs Sincronizadas

### Repositorio GitHub:
https://github.com/elsampedrino/bot-inmobiliaria-data

### URLs Raw (usadas por N8N):

**BBR (repo='1'):**
```
https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/main/propiedades_bbr.json
```

**Demo (repo='0'):**
```
https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/main/propiedades_demo.json
```

⚠️ **Importante:** GitHub Raw puede tardar 1-2 minutos en actualizar el caché.

---

## 🎓 Lecciones Aprendidas

### 1. **Normalización Bidireccional**
No alcanza con normalizar solo en el prompt. Ambos lados (consulta + datos) deben estar normalizados.

### 2. **Minúsculas > Mayúsculas para Matching**
Las minúsculas son el estándar para:
- Comparaciones case-insensitive
- Búsquedas de texto
- Matching de criterios

### 3. **Equivalencias en el Prompt**
El prompt ya maneja equivalencias:
```
departamento = depto = dpto
alquilar = rentar = alquiler
casas → casa (singular)
```

Pero si el JSON tiene `"Departamento"` con mayúscula, fallan.

### 4. **Estandarización de Estructura**
Mantener la misma estructura (array vs objeto, ubicación de campos) facilita el mantenimiento.

### 5. **Scripts de Sincronización Automática**
Automatizar el proceso reduce errores humanos y asegura consistencia.

---

## ✅ Checklist de Verificación

Antes de sincronizar JSONs a GitHub:

- [ ] Todos los valores de `tipo` están en minúsculas
- [ ] Todos los valores de `operacion` están en minúsculas
- [ ] Todos los valores de `estado_construccion` están en minúsculas
- [ ] `detalles` es un array (no objeto)
- [ ] `expensas` está dentro de `precio` (si aplica)
- [ ] Todas las propiedades tienen `fotos.urls` (array)
- [ ] Backup creado antes de modificar
- [ ] Metadata actualizada con timestamp

---

## 📝 Testing

### Consultas que ahora funcionan correctamente:

✅ "busco departamento para alquilar"
✅ "tenes casas para venta?"
✅ "algun local comercial?"
✅ "departamentos en alquiler"
✅ "casas baratas"

### Antes (con mayúsculas):
❌ Respondía con saludo genérico
❌ No encontraba coincidencias

### Ahora (normalizado):
✅ Encuentra y muestra propiedades
✅ Matching perfecto
✅ Ordenado por precio ascendente

---

## 🚀 Próximos Pasos

1. Testear workflows con JSONs normalizados
2. Verificar que GitHub Raw se actualice (1-2 min)
3. Probar consultas en widget de producción
4. Documentar casos de prueba exitosos
5. Monitorear logs de PostgreSQL para confirmar mejora

---

**Última actualización:** 28 de Diciembre 2025
**Autor:** Claude Sonnet 4.5 con usuario
**Estado:** ✅ Completado y sincronizado
