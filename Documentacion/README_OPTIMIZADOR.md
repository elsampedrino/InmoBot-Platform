# 🏠 Optimizador de Imágenes para Propiedades Inmobiliarias

Script automatizado para optimizar fotos de propiedades reduciendo peso sin perder calidad visible.

## 🎯 ¿Qué hace?

- ✅ Redimensiona imágenes a tamaños estándar web
- ✅ Genera 3 versiones: thumbnail, normal y HD
- ✅ Comprime sin pérdida visible de calidad
- ✅ Convierte a WebP (30% menos peso) + JPG (fallback)
- ✅ Procesa fotos de iPhone (HEIC) automáticamente
- ✅ Organiza todo por carpetas de propiedades
- ✅ Muestra estadísticas de ahorro de espacio

## 📦 Instalación

### Paso 1: Instalar Python
Asegurate de tener Python 3.8 o superior instalado.

```bash
python --version
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Estructura de carpetas esperada:

```
fotos_propiedades/
├── PROP-001/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.jpg
├── PROP-002/
│   ├── foto1.jpg
│   └── foto2.jpg
└── PROP-003/
    └── ...
```

### Ejecutar el script:

```bash
python optimizar_imagenes_propiedades.py fotos_propiedades/
```

### Resultado:

Se creará una carpeta `fotos_propiedades_optimizado/` con esta estructura:

```
fotos_propiedades_optimizado/
├── PROP-001/
│   ├── foto01_thumbnail.webp  (50-100 KB)
│   ├── foto01_thumbnail.jpg
│   ├── foto01_normal.webp     (150-250 KB)
│   ├── foto01_normal.jpg
│   ├── foto01_hd.webp         (400-600 KB)
│   ├── foto01_hd.jpg
│   ├── foto02_thumbnail.webp
│   └── ...
└── PROP-002/
    └── ...
```

## ⚙️ Configuración

Podés ajustar estos parámetros en el script:

```python
TAMAÑOS = {
    'thumbnail': (400, 300),    # Thumbnails pequeños
    'normal': (1200, 900),      # Vista principal
    'hd': (1920, 1440)          # Zoom opcional
}

CALIDAD_JPG = 85   # 80-90 recomendado
CALIDAD_WEBP = 85  # 80-90 recomendado
```

## 📊 Ejemplo de salida:

```
================================================================================
🏠 OPTIMIZADOR DE IMÁGENES PARA PROPIEDADES INMOBILIARIAS
================================================================================

📂 Carpeta de entrada: fotos_propiedades
📂 Carpeta de salida: fotos_propiedades_optimizado

🏢 Encontradas 3 propiedades

📁 Procesando: PROP-001
================================================================================
   🖼️  Encontradas 5 imágenes

   Imagen 1/5: DSC_1234.jpg
   ✅ thumbnail   → WebP:   78.3 KB | JPG:   92.1 KB
   ✅ normal      → WebP:  187.5 KB | JPG:  234.2 KB
   ✅ hd          → WebP:  423.8 KB | JPG:  567.3 KB

   [...]

   ✅ Procesadas exitosamente: 5/5

   💾 Tamaño original: 45.30 MB
   💾 Tamaño optimizado: 12.45 MB
   🎉 Ahorro: 72.5%
```

## 🎯 Formatos soportados

- ✅ JPG/JPEG
- ✅ PNG
- ✅ WebP
- ✅ HEIC/HEIF (fotos de iPhone)

## 💡 Consejos

### Para el bot inmobiliario:

1. **Usar versión "normal"** (1200x900px) para mostrar en el chat
2. **Usar "thumbnail"** para previews en listas
3. **Usar WebP** cuando el navegador lo soporte (menor peso)
4. **Fallback a JPG** para navegadores viejos

### Subir a hosting:

**Opción 1: Cloudinary (RECOMENDADO)**
```bash
# Gratis hasta 25GB
# URLs automáticas
# CDN global
```

**Opción 2: Google Drive**
```bash
# Compartir carpeta pública
# Obtener links directos
```

**Opción 3: Amazon S3**
```bash
# Para mayor escala
# CDN con CloudFront
```

## 🔧 Troubleshooting

### Error: "No module named 'PIL'"
```bash
pip install Pillow
```

### Error con fotos HEIC de iPhone
```bash
pip install pillow-heif
```

### Las imágenes se ven borrosas
- Aumentá CALIDAD_JPG o CALIDAD_WEBP (máx 95)
- Ajustá los tamaños en TAMAÑOS

### El script es muy lento
- Las fotos muy pesadas tardan más
- Normal: ~1-2 segundos por foto
- Considerá procesar en lotes pequeños

## 📝 Notas

- El script **NO modifica** las imágenes originales
- Crea una carpeta nueva con las versiones optimizadas
- Mantiene el aspect ratio original
- Convierte transparencias a fondo blanco

## 🆘 Soporte

Si tenés problemas, revisá:
1. Que Python esté instalado correctamente
2. Que las dependencias estén instaladas
3. Que la estructura de carpetas sea correcta
4. Los permisos de lectura/escritura

## 📄 Licencia

MIT - Uso libre para proyectos comerciales y personales
