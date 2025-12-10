#!/usr/bin/env python3
"""
Script para subir imágenes a Cloudinary con Public IDs limpios (sin hash)
"""

import os
import sys
from pathlib import Path
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# CONFIGURACIÓN
CLOUD_NAME = "dikb9wzup"
API_KEY = "298397144263636"        # Reemplazar con tu API Key
API_SECRET = "8JnHARLfkJCvvUyDAce73YBGYvw"  # Reemplazar con tu API Secret

# Prefijo para todas las fotos (opcional)
CARPETA_BASE = "fotos_demo"


def configurar_cloudinary():
    """Configura la conexión con Cloudinary"""
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET
    )


def subir_imagen(ruta_archivo, public_id):
    """
    Sube una imagen a Cloudinary con Public ID específico (sin hash)
    
    Args:
        ruta_archivo: Path del archivo local
        public_id: Public ID deseado (ej: "fotos_demo/depto-palermo-001/foto01")
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


def procesar_carpeta(carpeta_local, nombre_propiedad):
    """
    Procesa todas las imágenes de una carpeta
    
    Args:
        carpeta_local: Path de la carpeta local con fotos
        nombre_propiedad: Nombre de la propiedad (ej: "depto-palermo-001")
    """
    print(f"\n📁 Procesando: {nombre_propiedad}")
    print("="*80)
    
    # Buscar imágenes
    extensiones = ['.jpg', '.jpeg', '.png', '.webp']
    imagenes = [
        f for f in carpeta_local.iterdir()
        if f.is_file() and f.suffix.lower() in extensiones
    ]
    
    if not imagenes:
        print("   ⚠️  No se encontraron imágenes")
        return []
    
    imagenes_ordenadas = sorted(imagenes)
    print(f"   🖼️  Encontradas {len(imagenes_ordenadas)} imágenes\n")
    
    resultados = []
    
    for idx, imagen in enumerate(imagenes_ordenadas, 1):
        # Construir Public ID sin extensión
        public_id = f"{CARPETA_BASE}/{nombre_propiedad}/foto{idx:02d}"
        
        print(f"   [{idx}/{len(imagenes_ordenadas)}] {imagen.name}")
        print(f"      → {public_id}")
        
        # Subir
        resultado = subir_imagen(imagen, public_id)
        
        if resultado['success']:
            print(f"      ✅ Subido: {resultado['tamaño_kb']:.1f} KB")
            print(f"      🔗 {resultado['url']}")
            resultados.append(resultado)
        else:
            print(f"      ❌ Error: {resultado['error']}")
        
        print()
    
    exitosas = len([r for r in resultados if r['success']])
    print(f"   ✅ Subidas exitosamente: {exitosas}/{len(imagenes_ordenadas)}")
    
    return resultados


def generar_urls_json(resultados_totales):
    """Genera JSON con todas las URLs organizadas"""
    import json
    
    output_file = "cloudinary_urls_finales.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados_totales, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Archivo generado: {output_file}")


def main():
    """Función principal"""
    
    print("="*80)
    print("☁️  UPLOADER A CLOUDINARY - URLs LIMPIAS (sin hash)")
    print("="*80)
    print(f"\nCloud Name: {CLOUD_NAME}")
    print(f"Carpeta base: {CARPETA_BASE}")
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("\n❌ Uso: python subir_cloudinary.py <carpeta_con_propiedades>")
        print("\nEstructura esperada:")
        print("  fotos_propiedades/")
        print("    ├── depto-palermo-001/")
        print("    │   ├── foto01.jpg")
        print("    │   ├── foto02.jpg")
        print("    │   └── ...")
        print("    ├── depto-belgrano-004/")
        print("    └── ...")
        print("\nResultado en Cloudinary:")
        print("  fotos_demo/depto-palermo-001/foto01.jpg")
        print("  fotos_demo/depto-palermo-001/foto02.jpg")
        print("  ...")
        sys.exit(1)
    
    carpeta_entrada = Path(sys.argv[1])
    
    if not carpeta_entrada.exists():
        print(f"\n❌ Error: La carpeta '{carpeta_entrada}' no existe")
        sys.exit(1)
    
    # Verificar configuración
    if API_KEY == "TU_API_KEY" or API_SECRET == "TU_API_SECRET":
        print("\n❌ Error: Configurá tu API_KEY y API_SECRET en el script")
        print("\nLos encontrás en:")
        print("Cloudinary Dashboard → Settings → Access Keys")
        sys.exit(1)
    
    # Configurar Cloudinary
    print("\n🔧 Configurando conexión con Cloudinary...")
    configurar_cloudinary()
    print("   ✅ Conectado")
    
    # Buscar carpetas de propiedades
    carpetas_propiedades = [
        d for d in carpeta_entrada.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]
    
    if not carpetas_propiedades:
        print("\n❌ No se encontraron carpetas de propiedades")
        sys.exit(1)
    
    print(f"\n🏢 Encontradas {len(carpetas_propiedades)} propiedades")
    
    # Confirmar
    print("\n⚠️  ADVERTENCIA:")
    print("   • Se sobrescribirán archivos existentes con el mismo Public ID")
    print("   • Se invalidará el cache del CDN")
    print()
    confirmar = input("¿Continuar? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("Operación cancelada")
        sys.exit(0)
    
    # Procesar cada propiedad
    resultados_totales = {}
    
    for carpeta_prop in sorted(carpetas_propiedades):
        nombre_propiedad = carpeta_prop.name
        resultados = procesar_carpeta(carpeta_prop, nombre_propiedad)
        
        if resultados:
            resultados_totales[nombre_propiedad] = resultados
    
    # Generar JSON con URLs
    if resultados_totales:
        generar_urls_json(resultados_totales)
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)
    
    # Estadísticas
    total_subidas = sum(len(r) for r in resultados_totales.values())
    total_exitosas = sum(
        len([x for x in r if x['success']])
        for r in resultados_totales.values()
    )
    
    print(f"\n📊 Estadísticas:")
    print(f"   • Propiedades procesadas: {len(resultados_totales)}")
    print(f"   • Fotos subidas: {total_exitosas}/{total_subidas}")
    
    print("\n🔗 URLs resultantes:")
    print(f"   Base: https://res.cloudinary.com/{CLOUD_NAME}/image/upload/{CARPETA_BASE}/PROPIEDAD/foto01.jpg")
    
    print("\n🎨 Ejemplos de transformación:")
    if resultados_totales:
        primera_prop = list(resultados_totales.keys())[0]
        primera_foto = resultados_totales[primera_prop][0]
        public_id = primera_foto['public_id']
        
        print(f"\n   Thumbnail:")
        print(f"   https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_200,h_150,c_fill,f_auto/{public_id}.jpg")
        
        print(f"\n   Mobile:")
        print(f"   https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_600,f_auto/{public_id}.jpg")
        
        print(f"\n   Desktop:")
        print(f"   https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_1200,f_auto/{public_id}.jpg")
    
    print("\n💡 Próximos pasos:")
    print("   1. Verificá las URLs en el JSON generado")
    print("   2. Probá una URL en el navegador")
    print("   3. Actualizá tu base de datos con las carpetas correctas")
    print("   4. ¡Listo para usar en el bot!")


if __name__ == "__main__":
    main()