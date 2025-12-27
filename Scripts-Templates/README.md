# Scripts y Templates - Sistema de Estandarización de Propiedades

Esta carpeta contiene todos los scripts y templates necesarios para el sistema de estandarización de catálogos de propiedades para inmobiliarias.

## 📁 Contenido

### Scripts Python

1. **[crear_excel_template.py](crear_excel_template.py)**
   - Genera el template Excel estandarizado para inmobiliarias
   - Incluye validaciones, dropdowns y formato profesional
   - Genera hoja de instrucciones completa

   ```bash
   python crear_excel_template.py
   # Output: Template_Propiedades_InmoBot_YYYYMMDD.xlsx
   ```

2. **[excel_to_json.py](excel_to_json.py)**
   - Convierte Excel completado a formato JSON
   - Soporta merge con JSON anterior (para actualizaciones mensuales)
   - Conserva URLs de fotos de Cloudinary automáticamente

   ```bash
   # Primera vez
   python excel_to_json.py "datos.xlsx"

   # Actualización mensual
   python excel_to_json.py "datos_enero.xlsx" --json-anterior "propiedades_diciembre.json"
   ```

3. **[subir_fotos_cloudinary.py](subir_fotos_cloudinary.py)**
   - Script para subir fotos a Cloudinary con URLs limpias (sin hash)
   - Organiza fotos por inmobiliaria: `inmobiliaria/prop-id/fotoNN.jpg`
   - Actualiza JSON con URLs generadas automáticamente
   - Conserva URLs existentes (solo sube fotos nuevas)

   ```bash
   # Configurar credenciales (solo una vez)
   export CLOUDINARY_CLOUD_NAME="dikb9wzup"
   export CLOUDINARY_API_KEY="298397144263636"
   export CLOUDINARY_API_SECRET="8JnHARLfkJCvvUyDAce73YBGYvw"

   # Subir fotos
   python subir_fotos_cloudinary.py "propiedades_bbr.json" \
     --carpeta-fotos ./fotos \
     --inmobiliaria bbr
   ```

### Documentación

- **[FLUJO_ACTUALIZACION_MENSUAL.md](FLUJO_ACTUALIZACION_MENSUAL.md)**
  - Documentación completa del flujo de actualización mensual
  - Ejemplos paso a paso
  - Casos de uso reales

### Templates y Archivos de Ejemplo

- `Template_Propiedades_InmoBot_YYYYMMDD.xlsx` - Templates Excel generados
- `propiedades_*.json` - Archivos JSON de ejemplo/prueba

## 🚀 Inicio Rápido

### Para Generar Template para un Nuevo Cliente

```bash
# 1. Generar template Excel
python crear_excel_template.py

# 2. Enviar el Excel generado al cliente
# 3. Cliente completa el Excel con sus propiedades
# 4. Cliente envía Excel + carpetas de fotos numeradas

# 5. Convertir a JSON
python excel_to_json.py "Propiedades_ClienteX.xlsx"

# 6. Subir fotos a Cloudinary
python subir_fotos_cloudinary.py "propiedades_clientex.json" \
  --carpeta-fotos ./fotos \
  --inmobiliaria clientex

# 7. Subir JSON final a GitHub
```

### Para Actualización Mensual

```bash
# 1. Cliente actualiza Excel (elimina vendidos, modifica precios, agrega nuevos)
# 2. Cliente envía Excel + fotos solo de propiedades nuevas/modificadas

# 3. Convertir con merge
python excel_to_json.py "Propiedades_ClienteX_Enero.xlsx" \
  --json-anterior "propiedades_clientex_diciembre.json"

# 4. Subir solo fotos nuevas a Cloudinary
python subir_fotos_cloudinary.py "propiedades_clientex_enero.json" \
  --carpeta-fotos ./fotos_enero \
  --inmobiliaria clientex

# 5. Subir JSON actualizado a GitHub
```

## 📋 Estructura del Excel Template

### Columnas (25 en total)

**Obligatorias** (encabezado rojo):
- `A`: ID (PROP-NNN)
- `B`: Tipo de Propiedad
- `C`: Operación
- `F`: Calle y Número
- `G`: Barrio/Localidad
- `H`: Ciudad
- `J`: Precio
- `K`: Moneda
- `X`: Descripción

**Opcionales** (encabezado azul):
- `D`: Estado Construcción
- `E`: Título (auto-generado si vacío)
- `I`: Código Postal
- `L`: Expensas
- `M-Q`: Características (ambientes, dormitorios, baños, superficies)
- `R-W`: Checkboxes (ascensor, balcón, cochera, baulera, pileta, mascotas)
- `Y`: Disponibilidad

## 📊 Estructura del JSON Generado

```json
{
  "propiedades": [
    {
      "id": "PROP-001",
      "tipo": "Casa",
      "operacion": "Venta",
      "estado_construccion": "Usado",
      "titulo": "Casa 3amb Venta - Villa Urquiza",
      "direccion": {
        "calle": "Bauness 2145",
        "barrio": "Villa Urquiza",
        "ciudad": "CABA",
        "cp": "C1431"
      },
      "precio": {
        "valor": 295000.0,
        "moneda": "USD",
        "periodo": null
      },
      "expensas": null,
      "caracteristicas": {
        "ambientes": 4,
        "dormitorios": 3,
        "banios": 2,
        "superficie_total": 180.0,
        "superficie_cubierta": 120.0
      },
      "detalles": {
        "estado_construccion": "Usado",
        "ascensor": false,
        "balcon": false,
        "cochera": true,
        "baulera": false,
        "pileta": false,
        "mascotas": true
      },
      "descripcion": "Hermosa casa reciclada...",
      "disponibilidad": "Inmediata",
      "fotos": {
        "carpeta": "1",
        "urls": [
          "https://res.cloudinary.com/.../foto1.jpg",
          "https://res.cloudinary.com/.../foto2.jpg"
        ]
      }
    }
  ],
  "metadata": {
    "total": 1,
    "fecha_generacion": "2025-12-20T13:00:00.000000",
    "archivo_origen": "Template_Propiedades_InmoBot_20251220.xlsx"
  }
}
```

## ⚠️ Reglas Importantes

### IDs
- ✅ Formato: `PROP-001`, `PROP-002`, `PROP-003`, etc.
- ✅ Secuencial y único
- ⚠️ **NUNCA** cambiar ID de propiedad existente
- ⚠️ **NUNCA** reusar IDs eliminados

### Fotos
- ✅ Carpetas numeradas: `1/`, `2/`, `3/`
- ✅ Fotos numeradas dentro: `01.jpg`, `02.jpg`, `03.jpg`
- ✅ Correspondencia: fila 2 Excel = carpeta 1, fila 3 = carpeta 2, etc.
- ✅ En actualizaciones: solo enviar fotos de propiedades nuevas/modificadas

### Actualizaciones
- ✅ Eliminar fila = eliminar propiedad
- ✅ Modificar datos = actualizar propiedad (conserva fotos)
- ✅ Agregar fila = nueva propiedad (requiere fotos)

## 🛠️ Dependencias

```bash
pip install openpyxl
# Para subir_fotos_cloudinary.py (cuando esté disponible):
# pip install cloudinary
```

## 📞 Soporte

- **Documentación completa**: Ver [FLUJO_ACTUALIZACION_MENSUAL.md](FLUJO_ACTUALIZACION_MENSUAL.md)
- **Código fuente**: Cada script tiene comentarios detallados
- **Issues**: Reportar problemas en el repositorio principal

---

**Última actualización**: 2025-12-20
