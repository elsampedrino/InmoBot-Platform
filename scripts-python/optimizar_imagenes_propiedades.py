#!/usr/bin/env python3
"""
Script para optimizar imágenes de propiedades inmobiliarias
- Redimensiona a tamaños estándar
- Comprime sin perder calidad visible
- Genera thumbnails automáticamente
- Convierte a formato WebP y JPG
"""

import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif  # Para soporte de HEIC (fotos iPhone)

# CONFIGURACIÓN
TAMAÑOS = {
    'thumbnail': (400, 300),    # Para previews pequeños
    'normal': (1200, 900),      # Para vista principal
    'hd': (1920, 1440)          # Para zoom (opcional)
}

CALIDAD_JPG = 85  # 0-100, recomendado 80-85
CALIDAD_WEBP = 85  # 0-100, recomendado 80-90

TAMAÑO_MAXIMO = {
    'thumbnail': 100,   # KB
    'normal': 250,      # KB
    'hd': 600          # KB
}


def convertir_heic_a_jpg(ruta_imagen):
    """Convierte imágenes HEIC (iPhone) a JPG"""
    try:
        heif_file = pillow_heif.read_heif(ruta_imagen)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        return image
    except Exception as e:
        print(f"   ⚠️  Error convirtiendo HEIC: {e}")
        return None


def optimizar_imagen(ruta_entrada, carpeta_salida, nombre_base):
    """
    Optimiza una imagen generando múltiples versiones
    
    Args:
        ruta_entrada: Path de la imagen original
        carpeta_salida: Carpeta donde guardar las versiones optimizadas
        nombre_base: Nombre base para los archivos de salida
    """
    
    try:
        # Cargar imagen
        extension = ruta_entrada.suffix.lower()
        
        if extension in ['.heic', '.heif']:
            print(f"   🔄 Convirtiendo HEIC a JPG: {ruta_entrada.name}")
            img = convertir_heic_a_jpg(str(ruta_entrada))
            if img is None:
                return False
        else:
            img = Image.open(ruta_entrada)
        
        # Convertir a RGB si es necesario (para WebP/JPG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco para imágenes con transparencia
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        resultados = []
        
        # Generar cada versión
        for tipo, dimensiones in TAMAÑOS.items():
            # Redimensionar manteniendo aspect ratio
            img_redimensionada = img.copy()
            img_redimensionada.thumbnail(dimensiones, Image.Resampling.LANCZOS)
            
            # Guardar en WebP (mejor compresión)
            nombre_webp = f"{nombre_base}_{tipo}.webp"
            ruta_webp = carpeta_salida / nombre_webp
            img_redimensionada.save(
                ruta_webp,
                'WEBP',
                quality=CALIDAD_WEBP,
                method=6  # Mejor compresión
            )
            
            # Guardar en JPG (fallback)
            nombre_jpg = f"{nombre_base}_{tipo}.jpg"
            ruta_jpg = carpeta_salida / nombre_jpg
            img_redimensionada.save(
                ruta_jpg,
                'JPEG',
                quality=CALIDAD_JPG,
                optimize=True
            )
            
            # Verificar tamaños
            tamaño_webp_kb = ruta_webp.stat().st_size / 1024
            tamaño_jpg_kb = ruta_jpg.stat().st_size / 1024
            
            resultados.append({
                'tipo': tipo,
                'webp': {'ruta': ruta_webp, 'tamaño': tamaño_webp_kb},
                'jpg': {'ruta': ruta_jpg, 'tamaño': tamaño_jpg_kb}
            })
            
            # Mostrar info
            print(f"   ✅ {tipo:10s} → WebP: {tamaño_webp_kb:6.1f} KB | JPG: {tamaño_jpg_kb:6.1f} KB")
            
            # Advertencia si excede el tamaño máximo
            if tamaño_webp_kb > TAMAÑO_MAXIMO[tipo]:
                print(f"      ⚠️  WebP excede tamaño recomendado ({TAMAÑO_MAXIMO[tipo]} KB)")
            if tamaño_jpg_kb > TAMAÑO_MAXIMO[tipo]:
                print(f"      ⚠️  JPG excede tamaño recomendado ({TAMAÑO_MAXIMO[tipo]} KB)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error procesando imagen: {e}")
        return False


def procesar_carpeta_propiedad(carpeta_propiedad, carpeta_salida_base):
    """
    Procesa todas las imágenes de una propiedad
    
    Args:
        carpeta_propiedad: Path de la carpeta con fotos originales
        carpeta_salida_base: Path base para carpetas optimizadas
    """
    
    nombre_propiedad = carpeta_propiedad.name
    print(f"\n📁 Procesando: {nombre_propiedad}")
    print("="*80)
    
    # Crear carpeta de salida para esta propiedad
    carpeta_salida = carpeta_salida_base / nombre_propiedad
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    # Buscar todas las imágenes
    extensiones_validas = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif'}
    imagenes = [
        f for f in carpeta_propiedad.iterdir()
        if f.is_file() and f.suffix.lower() in extensiones_validas
    ]
    
    if not imagenes:
        print("   ⚠️  No se encontraron imágenes")
        return
    
    print(f"   🖼️  Encontradas {len(imagenes)} imágenes\n")
    
    # Procesar cada imagen
    exitosas = 0
    for idx, imagen in enumerate(sorted(imagenes), 1):
        print(f"   Imagen {idx}/{len(imagenes)}: {imagen.name}")
        nombre_base = f"foto{idx:02d}"
        
        if optimizar_imagen(imagen, carpeta_salida, nombre_base):
            exitosas += 1
        print()
    
    print(f"   ✅ Procesadas exitosamente: {exitosas}/{len(imagenes)}")
    
    # Calcular ahorro de espacio
    tamaño_original = sum(f.stat().st_size for f in imagenes) / (1024 * 1024)
    tamaño_optimizado = sum(
        f.stat().st_size for f in carpeta_salida.rglob('*')
        if f.is_file()
    ) / (1024 * 1024)
    ahorro = ((tamaño_original - tamaño_optimizado) / tamaño_original) * 100
    
    print(f"\n   💾 Tamaño original: {tamaño_original:.2f} MB")
    print(f"   💾 Tamaño optimizado: {tamaño_optimizado:.2f} MB")
    print(f"   🎉 Ahorro: {ahorro:.1f}%")


def main():
    """Función principal"""
    
    print("="*80)
    print("🏠 OPTIMIZADOR DE IMÁGENES PARA PROPIEDADES INMOBILIARIAS")
    print("="*80)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("\n❌ Uso: python optimizar_imagenes_propiedades.py <carpeta_con_propiedades>")
        print("\nEstructura esperada:")
        print("  carpeta_propiedades/")
        print("    ├── PROP-001/")
        print("    │   ├── foto1.jpg")
        print("    │   ├── foto2.jpg")
        print("    │   └── ...")
        print("    ├── PROP-002/")
        print("    │   └── ...")
        print("    └── ...")
        sys.exit(1)
    
    carpeta_entrada = Path(sys.argv[1])
    
    if not carpeta_entrada.exists():
        print(f"\n❌ Error: La carpeta '{carpeta_entrada}' no existe")
        sys.exit(1)
    
    # Crear carpeta de salida
    carpeta_salida = carpeta_entrada.parent / f"{carpeta_entrada.name}_optimizado"
    carpeta_salida.mkdir(exist_ok=True)
    
    print(f"\n📂 Carpeta de entrada: {carpeta_entrada}")
    print(f"📂 Carpeta de salida: {carpeta_salida}")
    print(f"\n⚙️  Configuración:")
    print(f"   • Calidad JPG: {CALIDAD_JPG}%")
    print(f"   • Calidad WebP: {CALIDAD_WEBP}%")
    print(f"   • Formatos: WebP + JPG")
    
    # Buscar carpetas de propiedades
    carpetas_propiedades = [
        d for d in carpeta_entrada.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]
    
    if not carpetas_propiedades:
        print("\n❌ No se encontraron carpetas de propiedades")
        sys.exit(1)
    
    print(f"\n🏢 Encontradas {len(carpetas_propiedades)} propiedades")
    
    # Procesar cada propiedad
    for carpeta_prop in sorted(carpetas_propiedades):
        procesar_carpeta_propiedad(carpeta_prop, carpeta_salida)
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)
    print(f"\n📁 Las imágenes optimizadas están en: {carpeta_salida}")
    print("\n💡 Próximos pasos:")
    print("   1. Revisar las imágenes optimizadas")
    print("   2. Subir a Cloudinary/Google Drive")
    print("   3. Actualizar rutas en la base de datos")


if __name__ == "__main__":
    main()
