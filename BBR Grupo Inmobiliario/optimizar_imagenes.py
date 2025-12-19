"""
Script para optimizar imágenes de BBR Grupo Inmobiliario
Similar al script de demo pero adaptado para las carpetas de BBR

Autor: Claude Code
Fecha: 2025-01-13
"""

from PIL import Image
import os
from pathlib import Path
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================
# CONFIGURACIÓN
# ============================================

INPUT_DIR = "PROPIEDADES"
OUTPUT_DIR = "PROPIEDADES_OPTIMIZADAS"

# Configuración de optimización
MAX_WIDTH = 1200  # Ancho máximo para imágenes
QUALITY = 85  # Calidad JPEG (0-100)
WEBP_QUALITY = 80  # Calidad WebP

# Extensiones válidas
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# ============================================
# FUNCIONES
# ============================================

def crear_directorio_salida(ruta_relativa):
    """
    Crea estructura de carpetas en OUTPUT_DIR
    """
    output_path = Path(OUTPUT_DIR) / ruta_relativa
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def optimizar_imagen(input_path, output_path):
    """
    Optimiza una imagen: redimensiona si es necesario y comprime
    """
    try:
        # Abrir imagen
        img = Image.open(input_path)

        # Convertir RGBA a RGB si es necesario
        if img.mode == 'RGBA':
            # Crear fondo blanco
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Usa canal alpha como máscara
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Redimensionar si es muy grande
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

        # Guardar optimizada
        # Cambiar extensión a .jpg
        output_path = output_path.with_suffix('.jpg')
        img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)

        return True, output_path

    except Exception as e:
        return False, str(e)

def procesar_carpeta(carpeta_base):
    """
    Procesa todas las imágenes en una carpeta y sus subcarpetas
    """
    input_base = Path(INPUT_DIR) / carpeta_base

    if not input_base.exists():
        print(f"⚠️  Carpeta no encontrada: {input_base}")
        return 0

    contador = 0
    errores = 0

    print(f"\n📁 Procesando: {carpeta_base}/")
    print("-" * 80)

    # Recorrer todas las subcarpetas (direcciones)
    for direccion_folder in sorted(input_base.iterdir()):
        if not direccion_folder.is_dir():
            continue

        # Crear carpeta de salida
        ruta_relativa = direccion_folder.relative_to(INPUT_DIR)
        output_folder = crear_directorio_salida(ruta_relativa)

        # Procesar cada imagen en la carpeta
        imagenes = [f for f in direccion_folder.iterdir()
                   if f.suffix.lower() in VALID_EXTENSIONS]

        if not imagenes:
            continue

        print(f"  📷 {direccion_folder.name} ({len(imagenes)} fotos)")

        for img_file in imagenes:
            output_file = output_folder / img_file.name

            success, result = optimizar_imagen(img_file, output_file)

            if success:
                # Calcular reducción de tamaño
                size_original = img_file.stat().st_size
                size_optimizada = result.stat().st_size
                reduccion = ((size_original - size_optimizada) / size_original) * 100

                print(f"    ✅ {img_file.name} → {result.name} "
                      f"({size_original//1024}KB → {size_optimizada//1024}KB, "
                      f"-{reduccion:.1f}%)")
                contador += 1
            else:
                print(f"    ❌ Error en {img_file.name}: {result}")
                errores += 1

    return contador

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("🖼️  BBR Grupo Inmobiliario - Optimizador de Imágenes\n")
    print("=" * 80)
    print(f"📁 Carpeta entrada: {INPUT_DIR}/")
    print(f"📁 Carpeta salida: {OUTPUT_DIR}/")
    print(f"⚙️  Configuración: {MAX_WIDTH}px máx, JPEG calidad {QUALITY}")
    print("=" * 80)

    # Crear carpeta de salida principal
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # Procesar cada tipo de propiedad
    carpetas = ["Casas", "Alquiler", "Lotes", "Campos"]

    total_procesadas = 0

    for carpeta in carpetas:
        procesadas = procesar_carpeta(carpeta)
        total_procesadas += procesadas

    print("\n" + "=" * 80)
    print(f"✅ Proceso completado!")
    print(f"📊 Total de imágenes optimizadas: {total_procesadas}")
    print(f"📁 Imágenes guardadas en: {OUTPUT_DIR}/")
    print("\n📝 Próximo paso:")
    print("   Ejecutar script de subida a Cloudinary (carpeta: Inmob-BBR)")
