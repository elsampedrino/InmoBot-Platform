# Flujo de Actualización Mensual - InmoBot

Este documento describe el proceso completo para manejar actualizaciones mensuales del catálogo de propiedades de una inmobiliaria en el plan básico (JSON en GitHub).

## 📋 Resumen del Sistema

- **Plan Básico**: Catálogo en formato JSON almacenado en GitHub
- **Frecuencia de Actualización**: Mensual
- **Fotos**: Almacenadas en Cloudinary
- **Identificador Único**: ID en formato `PROP-NNN` (ejemplo: PROP-001, PROP-002, PROP-003)

## 🔄 Flujo Completo

### Mes 1: Carga Inicial

#### Paso 1: Crear Excel con Propiedades Iniciales

El cliente completa el template Excel con todas sus propiedades:

```
Template_Propiedades_BBR_Diciembre2025.xlsx
```

**Estructura de carpetas de fotos**:
```
fotos/
├── 1/
│   ├── 01.jpg
│   ├── 02.jpg
│   └── 03.jpg
├── 2/
│   ├── 01.jpg
│   └── 02.jpg
└── 3/
    ├── 01.jpg
    ├── 02.jpg
    ├── 03.jpg
    └── 04.jpg
```

#### Paso 2: Generar JSON desde Excel

```bash
python excel_to_json.py "Template_Propiedades_BBR_Diciembre2025.xlsx"
```

**Output**:
```
propiedades_template_propiedades_bbr_diciembre2025.json
```

**Estado**: Todas las propiedades tienen `fotos.urls: []` (pendientes)

#### Paso 3: Subir Fotos a Cloudinary

```bash
# Configurar credenciales (si no están ya configuradas)
export CLOUDINARY_CLOUD_NAME="dikb9wzup"
export CLOUDINARY_API_KEY="298397144263636"
export CLOUDINARY_API_SECRET="8JnHARLfkJCvvUyDAce73YBGYvw"

# Subir fotos
python subir_fotos_cloudinary.py "propiedades_template_propiedades_bbr_diciembre2025.json" \
  --carpeta-fotos ./fotos \
  --inmobiliaria bbr
```

**Resultado**: El JSON se actualiza con las URLs de Cloudinary:

```json
{
  "id": "PROP-001",
  "fotos": {
    "carpeta": "1",
    "urls": [
      "https://res.cloudinary.com/bbr/image/upload/v1/prop-001-01.jpg",
      "https://res.cloudinary.com/bbr/image/upload/v1/prop-001-02.jpg",
      "https://res.cloudinary.com/bbr/image/upload/v1/prop-001-03.jpg"
    ]
  }
}
```

#### Paso 4: Subir a GitHub

```bash
git add propiedades_bbr.json
git commit -m "Carga inicial catálogo BBR - Diciembre 2025"
git push
```

---

### Mes 2+: Actualización Mensual

#### Paso 1: Cliente Actualiza el Excel

El cliente abre el Excel del mes anterior y realiza los cambios:

**Acciones posibles**:
- ✅ **Eliminar filas** de propiedades vendidas/alquiladas
- ✅ **Modificar datos** de propiedades existentes (precio, descripción, etc.)
- ✅ **Agregar nuevas filas** al final con IDs secuenciales

**Ejemplo de cambios**:

```
Excel Diciembre 2025:
- PROP-001: Casa en Villa Urquiza ($295,000)
- PROP-002: Depto en Palermo ($180,000)
- PROP-003: Local en Belgrano ($3,500/mes)

Excel Enero 2026:
- PROP-001: Casa en Villa Urquiza ($285,000)  ← Precio modificado
- [PROP-002 ELIMINADO - vendido]
- PROP-003: Local en Belgrano ($3,500/mes)
- PROP-004: Depto en Recoleta ($220,000)      ← NUEVO
```

**IMPORTANTE**:
- ⚠️ **NO CAMBIAR** el ID de propiedades existentes
- ⚠️ Si cambió las fotos de una propiedad existente, **debe incluir las nuevas fotos en carpeta numerada**

#### Paso 2: Preparar Carpetas de Fotos (Solo Nuevas/Modificadas)

**NO es necesario enviar todas las fotos**, solo las de propiedades nuevas o con fotos modificadas:

```
fotos_enero/
└── 3/           # Solo PROP-004 (nueva propiedad = fila 4 del Excel = carpeta 3)
    ├── 01.jpg
    └── 02.jpg
```

#### Paso 3: Generar JSON con Merge

```bash
python excel_to_json.py "Template_Propiedades_BBR_Enero2026.xlsx" \
  --json-anterior "propiedades_bbr_diciembre2025.json"
```

**Output**:
```
Procesando archivo: Template_Propiedades_BBR_Enero2026.xlsx
Modo ACTUALIZACIÓN: 3 propiedades en JSON anterior
  OK Fila 2: PROP-001 - Casa... [Fotos: CONSERVADAS]
  OK Fila 3: PROP-003 - Local... [Fotos: CONSERVADAS]
  OK Fila 4: PROP-004 - Depto... [Fotos: PENDIENTES]

Estado de fotos:
  - Conservadas (URLs existentes): 2
  - Pendientes (nuevas/modificadas): 1
```

**Resultado**:
- ✅ PROP-001: Precio actualizado + URLs de fotos **conservadas**
- ✅ PROP-002: **No aparece** en el nuevo JSON (eliminado correctamente)
- ✅ PROP-003: Sin cambios + URLs de fotos **conservadas**
- ✅ PROP-004: Nueva propiedad + `fotos.urls: []` (pendiente)

#### Paso 4: Subir Solo Fotos Nuevas a Cloudinary

```bash
python subir_fotos_cloudinary.py "propiedades_template_propiedades_bbr_enero2026.json" \
  --carpeta-fotos ./fotos_enero \
  --inmobiliaria bbr
```

El script:
- ✅ Detecta que solo PROP-004 necesita fotos
- ✅ Sube las fotos de la carpeta `3/`
- ✅ Actualiza solo ese registro en el JSON

#### Paso 5: Subir a GitHub

```bash
git add propiedades_bbr.json
git commit -m "Actualización mensual BBR - Enero 2026"
git push
```

---

## 📊 Ejemplo Completo con Datos Reales

### Diciembre 2025 - Carga Inicial

**Excel**:
| ID | Tipo | Operación | Precio | Barrio |
|----|------|-----------|--------|---------|
| PROP-001 | Casa | Venta | $295,000 | Villa Urquiza |
| PROP-002 | Departamento | Venta | $180,000 | Palermo |
| PROP-003 | Local Comercial | Alquiler | $3,500 | Belgrano |

**Fotos**:
```
fotos/
├── 1/  → 3 fotos (PROP-001)
├── 2/  → 2 fotos (PROP-002)
└── 3/  → 4 fotos (PROP-003)
```

**Resultado JSON** (después de subir a Cloudinary):
```json
{
  "propiedades": [
    {
      "id": "PROP-001",
      "precio": { "valor": 295000.0 },
      "fotos": {
        "carpeta": "1",
        "urls": ["url1.jpg", "url2.jpg", "url3.jpg"]
      }
    },
    {
      "id": "PROP-002",
      "precio": { "valor": 180000.0 },
      "fotos": {
        "carpeta": "2",
        "urls": ["url1.jpg", "url2.jpg"]
      }
    },
    {
      "id": "PROP-003",
      "precio": { "valor": 3500.0, "periodo": "mes" },
      "fotos": {
        "carpeta": "3",
        "urls": ["url1.jpg", "url2.jpg", "url3.jpg", "url4.jpg"]
      }
    }
  ],
  "metadata": {
    "total": 3,
    "fecha_generacion": "2025-12-15T10:00:00"
  }
}
```

---

### Enero 2026 - Primera Actualización

**Cambios del cliente**:
1. PROP-001: Bajó el precio a $285,000
2. PROP-002: Se vendió (eliminar del Excel)
3. PROP-003: Sin cambios
4. PROP-004: Nuevo departamento en Recoleta

**Excel Enero**:
| ID | Tipo | Operación | Precio | Barrio |
|----|------|-----------|--------|---------|
| PROP-001 | Casa | Venta | $285,000 | Villa Urquiza |
| PROP-003 | Local Comercial | Alquiler | $3,500 | Belgrano |
| PROP-004 | Departamento | Venta | $220,000 | Recoleta |

**Fotos Enero** (solo nuevas):
```
fotos_enero/
└── 3/  → 2 fotos (PROP-004 está en fila 4, pero carpeta es 3)
```

**Comando**:
```bash
python excel_to_json.py "Template_Propiedades_BBR_Enero2026.xlsx" \
  --json-anterior "propiedades_bbr_diciembre2025.json"
```

**Resultado JSON** (después de merge + Cloudinary):
```json
{
  "propiedades": [
    {
      "id": "PROP-001",
      "precio": { "valor": 285000.0 },  ← ACTUALIZADO
      "fotos": {
        "carpeta": "1",
        "urls": ["url1.jpg", "url2.jpg", "url3.jpg"]  ← CONSERVADAS
      }
    },
    {
      "id": "PROP-003",
      "precio": { "valor": 3500.0, "periodo": "mes" },
      "fotos": {
        "carpeta": "3",
        "urls": ["url1.jpg", "url2.jpg", "url3.jpg", "url4.jpg"]  ← CONSERVADAS
      }
    },
    {
      "id": "PROP-004",  ← NUEVA
      "precio": { "valor": 220000.0 },
      "fotos": {
        "carpeta": "3",
        "urls": ["nueva-url1.jpg", "nueva-url2.jpg"]  ← SUBIDAS
      }
    }
  ],
  "metadata": {
    "total": 3,
    "fecha_generacion": "2026-01-15T10:00:00"
  }
}
```

---

## 🎯 Ventajas del Sistema

### Para el Cliente (Inmobiliaria)

✅ **Simple**: Solo mantiene un Excel actualizado
✅ **Eficiente**: No necesita re-enviar todas las fotos cada mes
✅ **Intuitivo**: Eliminar fila = eliminar propiedad

### Para el Desarrollador (Vos)

✅ **Mínimo trabajo manual**: Scripts automatizan todo
✅ **Sin duplicación de fotos**: Cloudinary conserva URLs existentes
✅ **Trazabilidad**: El ID mantiene la relación entre Excel y JSON
✅ **Escalable**: El mismo flujo funciona con 10 o 1000 propiedades

---

## 🔧 Scripts Disponibles

### 1. `crear_excel_template.py`

**Propósito**: Generar el template Excel vacío para inmobiliarias

**Uso**:
```bash
python crear_excel_template.py
```

**Output**: `Template_Propiedades_InmoBot_YYYYMMDD.xlsx`

---

### 2. `excel_to_json.py`

**Propósito**: Convertir Excel a JSON, con soporte para merge de URLs de fotos

**Uso**:
```bash
# Primera vez (sin merge)
python excel_to_json.py "Propiedades_BBR.xlsx"

# Actualización mensual (con merge)
python excel_to_json.py "Propiedades_BBR_Enero.xlsx" \
  --json-anterior "propiedades_bbr_diciembre.json"
```

**Parámetros**:
- `archivo.xlsx`: Excel con las propiedades (requerido)
- `--json-anterior`: JSON anterior para merge de URLs (opcional)

**Output**: `propiedades_[nombre].json`

---

### 3. `subir_fotos_cloudinary.py`

**Propósito**: Subir fotos a Cloudinary y actualizar JSON con URLs limpias (sin hash)

**Uso**:
```bash
# Configurar credenciales (una sola vez)
export CLOUDINARY_CLOUD_NAME="dikb9wzup"
export CLOUDINARY_API_KEY="298397144263636"
export CLOUDINARY_API_SECRET="8JnHARLfkJCvvUyDAce73YBGYvw"

# Subir fotos
python subir_fotos_cloudinary.py "propiedades_bbr.json" \
  --carpeta-fotos ./fotos \
  --inmobiliaria bbr

# Modo dry-run (prueba sin subir)
python subir_fotos_cloudinary.py "propiedades_bbr.json" \
  --carpeta-fotos ./fotos \
  --inmobiliaria bbr \
  --dry-run
```

**Parámetros**:
- `archivo.json`: JSON generado por excel_to_json.py
- `--carpeta-fotos`: Ruta a carpetas numeradas con fotos
- `--inmobiliaria`: Nombre de la inmobiliaria para organizar en Cloudinary (ej: bbr, demo)
- `--dry-run`: Modo prueba (opcional)

**Funcionalidad**:
1. Lee el JSON
2. Identifica propiedades con `fotos.urls: []` (pendientes)
3. Para cada propiedad pendiente:
   - Lee el número de carpeta (`fotos.carpeta`)
   - Sube fotos a Cloudinary con Public IDs limpios: `inmobiliaria/prop-id/fotoNN.jpg`
   - Actualiza `fotos.urls` con las URLs generadas
4. Conserva URLs existentes (no las vuelve a subir)
5. Guarda el JSON actualizado (con backup del original)

**Estructura en Cloudinary**:
```
bbr/
├── prop-001/
│   ├── foto01.jpg
│   ├── foto02.jpg
│   └── foto03.jpg
└── prop-002/
    ├── foto01.jpg
    └── foto02.jpg
```

**URLs resultantes** (sin hash):
```
https://res.cloudinary.com/dikb9wzup/image/upload/bbr/prop-001/foto01.jpg
https://res.cloudinary.com/dikb9wzup/image/upload/bbr/prop-001/foto02.jpg
```

---

## 📁 Estructura de Archivos Recomendada

```
proyecto/
├── Scripts-Templates/
│   ├── crear_excel_template.py
│   ├── excel_to_json.py
│   ├── subir_fotos_cloudinary.py (pendiente)
│   └── FLUJO_ACTUALIZACION_MENSUAL.md (este archivo)
│
├── Clientes/
│   ├── BBR/
│   │   ├── Excels/
│   │   │   ├── Template_BBR_Diciembre2025.xlsx
│   │   │   └── Template_BBR_Enero2026.xlsx
│   │   ├── Fotos/
│   │   │   ├── diciembre/
│   │   │   │   ├── 1/
│   │   │   │   ├── 2/
│   │   │   │   └── 3/
│   │   │   └── enero/
│   │   │       └── 3/
│   │   └── JSON/
│   │       ├── propiedades_bbr_diciembre2025.json
│   │       └── propiedades_bbr_enero2026.json
│   │
│   └── OtroCliente/
│       └── ...
│
└── GitHub-Repo/
    └── data/
        └── propiedades_bbr.json  ← Este es el que usa el widget
```

---

## ⚠️ Consideraciones Importantes

### IDs

- ✅ El ID es **permanente** y **único** para cada propiedad
- ⚠️ **NUNCA** cambiar el ID de una propiedad existente
- ⚠️ **NUNCA** reusar IDs de propiedades eliminadas
- ✅ IDs nuevos deben ser **secuenciales** (PROP-004, PROP-005, etc.)

### Fotos

- ✅ Si una propiedad **no cambió sus fotos**, NO incluir su carpeta
- ⚠️ Si una propiedad **cambió sus fotos**, incluir la carpeta y el script las reemplazará
- ✅ El número de carpeta corresponde a: `número_fila_excel - 1`
  - Fila 2 del Excel → Carpeta 1
  - Fila 3 del Excel → Carpeta 2
  - etc.

### Eliminación de Propiedades

- ✅ Simplemente **eliminar la fila** del Excel
- ✅ No aparecerá en el nuevo JSON
- ✅ Las fotos permanecen en Cloudinary (no se eliminan automáticamente)

### Modificación de Propiedades

- ✅ Cambiar cualquier campo **excepto el ID**
- ✅ Si cambió precio, descripción, etc.: las fotos se conservan automáticamente
- ⚠️ Si cambió las fotos: incluir carpeta con nuevas fotos

---

## 🚀 Próximos Pasos

1. ✅ Sistema de Excel con IDs y merge de JSON - **COMPLETADO**
2. ⏳ Desarrollar `subir_fotos_cloudinary.py`
3. ⏳ Probar flujo completo con cliente real (BBR)
4. ⏳ Documentar proceso en video/tutorial para clientes
5. ⏳ Crear dashboard web para que clientes vean su catálogo

---

## 📞 Soporte

Para dudas sobre este proceso:
- Documentación: Este archivo
- Scripts: Ver comentarios en cada archivo Python
- Issues: Reportar en el repositorio del proyecto
