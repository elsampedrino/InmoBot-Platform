#!/usr/bin/env python3
"""
Script para subir imágenes de BBR a Cloudinary
Carpeta destino: Inmob-BBR

Autor: Claude Code
Fecha: 2025-01-13
"""

import os
import sys
import io
from pathlib import Path
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import json

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================
# CONFIGURACIÓN CLOUDINARY
# ============================================

CLOUD_NAME = "dikb9wzup"
API_KEY = "298397144263636"
API_SECRET = "8JnHARLfkJCvvUyDAce73YBGYvw"

# Carpeta base en Cloudinary para las fotos de BBR
CARPETA_BASE = "Inmob-BBR"

# Carpeta local con imágenes optimizadas
CARPETA_LOCAL = "PROPIEDADES_OPTIMIZADAS"

# ============================================
# FUNCIONES
# ============================================

def configurar_cloudinary():
    """Configura la conexión con Cloudinary"""
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET
    )


def normalizar_nombre_para_public_id(nombre):
    """
    Normaliza nombre para usar como Public ID
    Ej: "La Rioja al 600" -> "la-rioja-al-600"
    """
    # Quitar tildes
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'
    }

    nombre_norm = nombre
    for viejo, nuevo in reemplazos.items():
        nombre_norm = nombre_norm.replace(viejo, nuevo)

    # Convertir a minúsculas y reemplazar espacios por guiones
    nombre_norm = nombre_norm.lower()
    nombre_norm = nombre_norm.replace(' ', '-')
    nombre_norm = nombre_norm.replace('.', '')
    nombre_norm = nombre_norm.replace('/', '-')
    nombre_norm = nombre_norm.replace(',', '')
    nombre_norm = nombre_norm.replace('(', '')
    nombre_norm = nombre_norm.replace(')', '')

    return nombre_norm


def subir_imagen(ruta_archivo, public_id):
    """
    Sube una imagen a Cloudinary con Public ID específico

    Args:
        ruta_archivo: Path del archivo local
        public_id: Public ID deseado (ej: "Inmob-BBR/Casas/la-rioja-al-600/foto01")
    """
    try:
        result = cloudinary.uploader.upload(
            str(ruta_archivo),
            public_id=public_id,
            overwrite=True,  # Sobrescribe si ya existe
            invalidate=True,  # Invalida cache del CDN
            resource_type="image"
        )

        return {
            'success': True,
            'public_id': result['public_id'],
            'url': result['secure_url'],
            'formato': result['format'],
            'tamaño_kb': result['bytes'] / 1024
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def procesar_tipo_propiedad(tipo_carpeta):
    """
    Procesa todas las propiedades de un tipo (Casas, Alquiler, Lotes, Campos)

    Args:
        tipo_carpeta: Nombre de la carpeta del tipo (ej: "Casas")

    Returns:
        Dict con resultados {nombre_propiedad: [resultados]}
    """
    carpeta_tipo = Path(CARPETA_LOCAL) / tipo_carpeta

    if not carpeta_tipo.exists():
        print(f"⚠️  Carpeta no encontrada: {carpeta_tipo}")
        return {}

    print(f"\n{'='*80}")
    print(f"📁 PROCESANDO: {tipo_carpeta}/")
    print(f"{'='*80}")

    resultados_tipo = {}

    # Procesar cada propiedad (subcarpeta)
    propiedades = [d for d in sorted(carpeta_tipo.iterdir()) if d.is_dir()]

    if not propiedades:
        print(f"   ⚠️  No hay propiedades en esta carpeta")
        return {}

    print(f"   🏠 {len(propiedades)} propiedades encontradas\n")

    for prop_folder in propiedades:
        nombre_original = prop_folder.name
        nombre_normalizado = normalizar_nombre_para_public_id(nombre_original)

        print(f"\n   📷 {nombre_original}")
        print(f"      → Public ID: {nombre_normalizado}")

        # Buscar imágenes
        extensiones = ['.jpg', '.jpeg', '.png', '.webp']
        imagenes = [
            f for f in prop_folder.iterdir()
            if f.is_file() and f.suffix.lower() in extensiones
        ]

        if not imagenes:
            print(f"      ⚠️  Sin imágenes")
            continue

        imagenes_ordenadas = sorted(imagenes)
        print(f"      🖼️  {len(imagenes_ordenadas)} imágenes")

        resultados_prop = []

        for idx, imagen in enumerate(imagenes_ordenadas, 1):
            # Construir Public ID: Inmob-BBR/{tipo}/{nombre-propiedad}/foto{idx}
            public_id = f"{CARPETA_BASE}/{tipo_carpeta}/{nombre_normalizado}/foto{idx:02d}"

            print(f"         [{idx}/{len(imagenes_ordenadas)}] {imagen.name} → foto{idx:02d}", end='')

            # Subir
            resultado = subir_imagen(imagen, public_id)

            if resultado['success']:
                print(f" ✅ ({resultado['tamaño_kb']:.1f} KB)")
                resultados_prop.append(resultado)
            else:
                print(f" ❌ {resultado['error']}")

        if resultados_prop:
            resultados_tipo[nombre_original] = resultados_prop
            print(f"      ✅ {len(resultados_prop)} fotos subidas")

    return resultados_tipo


def generar_json_urls(todos_resultados):
    """
    Genera JSON con todas las URLs organizadas por tipo y propiedad
    """
    output_file = "cloudinary_urls_bbr.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(todos_resultados, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Archivo generado: {output_file}")
    return output_file


# ============================================
# MAIN
# ============================================

def main():
    """Función principal"""

    print("="*80)
    print("☁️  BBR GRUPO INMOBILIARIO - UPLOAD A CLOUDINARY")
    print("="*80)
    print(f"\nCloud Name: {CLOUD_NAME}")
    print(f"Carpeta Cloudinary: {CARPETA_BASE}/")
    print(f"Carpeta local: {CARPETA_LOCAL}/")

    # Verificar que existe la carpeta de imágenes optimizadas
    if not Path(CARPETA_LOCAL).exists():
        print(f"\n❌ Error: No existe la carpeta '{CARPETA_LOCAL}'")
        print("\n💡 Ejecutá primero: python optimizar_imagenes.py")
        sys.exit(1)

    # Configurar Cloudinary
    print("\n🔧 Configurando conexión con Cloudinary...")
    configurar_cloudinary()
    print("   ✅ Conectado")

    # Confirmar
    print("\n⚠️  ADVERTENCIA:")
    print("   • Se subirán las imágenes a la carpeta 'Inmob-BBR' en Cloudinary")
    print("   • Se sobrescribirán archivos existentes con el mismo Public ID")
    print("   • Se invalidará el cache del CDN")
    print()
    confirmar = input("¿Continuar? (s/n): ").strip().lower()

    if confirmar != 's':
        print("Operación cancelada")
        sys.exit(0)

    # Procesar cada tipo de propiedad
    tipos = ["Casas", "Alquiler", "Lotes", "Campos"]
    todos_resultados = {}

    for tipo in tipos:
        resultados_tipo = procesar_tipo_propiedad(tipo)
        if resultados_tipo:
            todos_resultados[tipo] = resultados_tipo

    # Generar JSON con URLs
    if todos_resultados:
        archivo_json = generar_json_urls(todos_resultados)
    else:
        print("\n❌ No se subieron imágenes")
        sys.exit(1)

    # Estadísticas finales
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)

    total_propiedades = sum(len(props) for props in todos_resultados.values())
    total_fotos = sum(
        len(fotos)
        for tipo_props in todos_resultados.values()
        for fotos in tipo_props.values()
    )

    print(f"\n📊 Estadísticas:")
    print(f"   • Tipos procesados: {len(todos_resultados)}")
    print(f"   • Propiedades con fotos: {total_propiedades}")
    print(f"   • Fotos subidas: {total_fotos}")

    print(f"\n📄 URLs guardadas en: {archivo_json}")

    print("\n🔗 Formato de URLs:")
    print(f"   https://res.cloudinary.com/{CLOUD_NAME}/image/upload/{CARPETA_BASE}/[TIPO]/[PROPIEDAD]/foto01.jpg")

    print("\n💡 Próximos pasos:")
    print("   1. Revisar cloudinary_urls_bbr.json")
    print("   2. Ejecutar script para actualizar propiedades_bbr.json con las URLs de Cloudinary")
    print("   3. Subir propiedades_bbr.json a GitHub")
    print("   4. Actualizar URL en N8N workflow")


if __name__ == "__main__":
    main()
