#!/usr/bin/env python3
"""
Script optimizado para preparar imágenes para Cloudinary
- Genera UNA SOLA versión optimizada por foto
- Tamaño: 1200x900px (ideal para web)
- Formato: JPG (Cloudinary convierte a WebP automático)
- Peso objetivo: 150-250 KB
"""

import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif  # Para soporte de HEIC (fotos iPhone)

# CONFIGURACIÓN SIMPLIFICADA
TAMAÑO_OBJETIVO = (1200, 900)  # Ancho x Alto máximo
CALIDAD_JPG = 85  # 0-100, sweet spot para calidad/peso
PESO_MAXIMO_KB = 250  # Objetivo de peso máximo


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


def optimizar_imagen(ruta_entrada, carpeta_salida, nombre_salida):
    """
    Optimiza una imagen para Cloudinary
    
    Args:
        ruta_entrada: Path de la imagen original
        carpeta_salida: Carpeta donde guardar la versión optimizada
        nombre_salida: Nombre del archivo de salida (sin extensión)
    """
    
    try:
        # Cargar imagen
        extension = ruta_entrada.suffix.lower()
        
        if extension in ['.heic', '.heif']:
            print(f"   🔄 Convirtiendo HEIC a JPG...")
            img = convertir_heic_a_jpg(str(ruta_entrada))
            if img is None:
                return False
        else:
            img = Image.open(ruta_entrada)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco para imágenes con transparencia
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar manteniendo aspect ratio
        img.thumbnail(TAMAÑO_OBJETIVO, Image.Resampling.LANCZOS)
        
        # Guardar optimizado
        nombre_archivo = f"{nombre_salida}.jpg"
        ruta_salida = carpeta_salida / nombre_archivo
        
        # Guardar con compresión optimizada
        img.save(
            ruta_salida,
            'JPEG',
            quality=CALIDAD_JPG,
            optimize=True,
            progressive=True  # Para carga progresiva
        )
        
        # Verificar tamaño
        tamaño_kb = ruta_salida.stat().st_size / 1024
        
        # Si es muy pesado, reducir calidad iterativamente
        calidad_actual = CALIDAD_JPG
        while tamaño_kb > PESO_MAXIMO_KB and calidad_actual > 60:
            calidad_actual -= 5
            img.save(
                ruta_salida,
                'JPEG',
                quality=calidad_actual,
                optimize=True,
                progressive=True
            )
            tamaño_kb = ruta_salida.stat().st_size / 1024
        
        # Mostrar resultado
        dimensiones = img.size
        print(f"   ✅ {nombre_archivo}")
        print(f"      Dimensiones: {dimensiones[0]}x{dimensiones[1]}px")
        print(f"      Peso: {tamaño_kb:.1f} KB")
        
        if tamaño_kb > PESO_MAXIMO_KB:
            print(f"      ⚠️  Supera {PESO_MAXIMO_KB} KB (calidad reducida a {calidad_actual}%)")
        
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
        print(f"   [{idx}/{len(imagenes)}] {imagen.name}")
        nombre_salida = f"foto{idx:02d}"
        
        if optimizar_imagen(imagen, carpeta_salida, nombre_salida):
            exitosas += 1
        print()
    
    print(f"   ✅ Procesadas exitosamente: {exitosas}/{len(imagenes)}")
    
    # Calcular estadísticas
    tamaño_original = sum(f.stat().st_size for f in imagenes) / (1024 * 1024)
    archivos_optimizados = list(carpeta_salida.glob('*.jpg'))
    tamaño_optimizado = sum(f.stat().st_size for f in archivos_optimizados) / (1024 * 1024)
    
    if tamaño_original > 0:
        ahorro = ((tamaño_original - tamaño_optimizado) / tamaño_original) * 100
        print(f"\n   💾 Tamaño original: {tamaño_original:.2f} MB")
        print(f"   💾 Tamaño optimizado: {tamaño_optimizado:.2f} MB")
        print(f"   🎉 Ahorro: {ahorro:.1f}%")


def generar_lista_cloudinary(carpeta_salida):
    """Genera un archivo con la lista de archivos para subir a Cloudinary"""
    
    lista_archivo = carpeta_salida.parent / "cloudinary_upload_list.txt"
    
    with open(lista_archivo, 'w', encoding='utf-8') as f:
        f.write("# LISTA DE ARCHIVOS PARA SUBIR A CLOUDINARY\n")
        f.write("# Copiá esta estructura a Cloudinary manteniendo las carpetas\n\n")
        
        for carpeta in sorted(carpeta_salida.iterdir()):
            if carpeta.is_dir():
                f.write(f"\n## {carpeta.name}/\n")
                archivos = sorted(carpeta.glob('*.jpg'))
                for archivo in archivos:
                    tamaño_kb = archivo.stat().st_size / 1024
                    f.write(f"   - {archivo.name} ({tamaño_kb:.1f} KB)\n")
    
    print(f"\n📄 Lista generada: {lista_archivo}")


def main():
    """Función principal"""
    
    print("="*80)
    print("🏠 OPTIMIZADOR SIMPLE DE IMÁGENES PARA CLOUDINARY")
    print("="*80)
    print("\nGenerando UNA versión optimizada por foto:")
    print(f"   • Tamaño máximo: {TAMAÑO_OBJETIVO[0]}x{TAMAÑO_OBJETIVO[1]}px")
    print(f"   • Calidad: {CALIDAD_JPG}% (ajustable automáticamente)")
    print(f"   • Peso objetivo: ~{PESO_MAXIMO_KB} KB por foto")
    print(f"   • Formato: JPG (Cloudinary convertirá a WebP automático)")
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("\n❌ Uso: python optimizar_simple.py <carpeta_con_propiedades>")
        print("\nEstructura esperada:")
        print("  fotos_propiedades/")
        print("    ├── depto-palermo-001/")
        print("    │   ├── foto1.jpg")
        print("    │   ├── foto2.jpg")
        print("    │   └── ...")
        print("    ├── depto-belgrano-002/")
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
    
    # Generar lista para Cloudinary
    generar_lista_cloudinary(carpeta_salida)
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)
    print(f"\n📁 Archivos optimizados en: {carpeta_salida}")
    print("\n💡 Próximos pasos:")
    print("   1. Revisá las imágenes optimizadas")
    print("   2. Subí a Cloudinary (carpeta por carpeta o en lote)")
    print("   3. Usá las URLs base en tu bot")
    print("\n🔗 URL base en Cloudinary:")
    print("   https://res.cloudinary.com/TU-CUENTA/image/upload/propiedades/NOMBRE-CARPETA/foto01.jpg")
    print("\n🎨 Transformaciones on-the-fly:")
    print("   Thumbnail: /w_200,h_150,c_fill/propiedades/...")
    print("   Mobile: /w_600/propiedades/...")
    print("   Desktop: /w_1200/propiedades/...")
    print("   WebP: /f_webp/propiedades/...")
    print("   Auto-optimizado: /f_auto,q_auto/propiedades/...")


if __name__ == "__main__":
    main()