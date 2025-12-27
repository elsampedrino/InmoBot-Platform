#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUBIR FOTOS A CLOUDINARY - INMOBILIARIAS
=========================================
Script para subir fotos de propiedades a Cloudinary y actualizar el JSON
con las URLs generadas. Solo procesa propiedades con fotos pendientes.

Uso:
    python subir_fotos_cloudinary.py archivo.json --carpeta-fotos ./fotos --inmobiliaria NOMBRE [opciones]

Parámetros:
    archivo.json       : JSON generado por excel_to_json.py (requerido)
    --carpeta-fotos    : Ruta a carpetas numeradas con fotos (requerido)
    --inmobiliaria     : Nombre de la inmobiliaria para carpeta en Cloudinary (requerido)
                         Ejemplos: "bbr", "demo", "propiedades_inmob1"
    --cloud-name       : Nombre del cloud de Cloudinary (opcional, usa env var)
    --api-key          : API Key de Cloudinary (opcional, usa env var)
    --api-secret       : API Secret de Cloudinary (opcional, usa env var)
    --dry-run          : Modo prueba, no sube fotos realmente

Variables de Entorno (recomendado):
    CLOUDINARY_CLOUD_NAME    : Nombre del cloud
    CLOUDINARY_API_KEY       : API Key
    CLOUDINARY_API_SECRET    : API Secret

Ejemplos:
    # Usando variables de entorno (recomendado)
    export CLOUDINARY_CLOUD_NAME="dikb9wzup"
    export CLOUDINARY_API_KEY="298397144263636"
    export CLOUDINARY_API_SECRET="8JnHARLfkJCvvUyDAce73YBGYvw"
    python subir_fotos_cloudinary.py "propiedades_bbr.json" \
        --carpeta-fotos ./fotos \
        --inmobiliaria bbr

    # Con parámetros
    python subir_fotos_cloudinary.py "propiedades_bbr.json" \
        --carpeta-fotos ./fotos \
        --inmobiliaria bbr \
        --cloud-name "dikb9wzup" \
        --api-key "298397144263636" \
        --api-secret "8JnHARLfkJCvvUyDAce73YBGYvw"

    # Modo dry-run (prueba sin subir)
    python subir_fotos_cloudinary.py "propiedades_bbr.json" \
        --carpeta-fotos ./fotos \
        --inmobiliaria bbr \
        --dry-run

Estructura en Cloudinary:
    bbr/prop-001/foto01.jpg
    bbr/prop-001/foto02.jpg
    bbr/prop-002/foto01.jpg
    demo/prop-001/foto01.jpg

URLs resultantes (sin hash, limpias):
    https://res.cloudinary.com/dikb9wzup/image/upload/bbr/prop-001/foto01.jpg
    https://res.cloudinary.com/dikb9wzup/image/upload/bbr/prop-001/foto02.jpg
"""

import sys
import json
import os
import argparse
from pathlib import Path
from datetime import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api

def configurar_cloudinary(cloud_name=None, api_key=None, api_secret=None):
    """
    Configura credenciales de Cloudinary desde parámetros o variables de entorno.

    Args:
        cloud_name: Nombre del cloud (opcional)
        api_key: API Key (opcional)
        api_secret: API Secret (opcional)

    Returns:
        bool: True si la configuración fue exitosa
    """
    # Obtener desde parámetros o variables de entorno
    cloud_name = cloud_name or os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = api_key or os.getenv('CLOUDINARY_API_KEY')
    api_secret = api_secret or os.getenv('CLOUDINARY_API_SECRET')

    # Validar que todas las credenciales estén disponibles
    if not all([cloud_name, api_key, api_secret]):
        print("ERROR: Faltan credenciales de Cloudinary")
        print("\nOpciones:")
        print("1. Usar variables de entorno:")
        print("   export CLOUDINARY_CLOUD_NAME='tu-cloud'")
        print("   export CLOUDINARY_API_KEY='tu-api-key'")
        print("   export CLOUDINARY_API_SECRET='tu-api-secret'")
        print("\n2. Pasar como parámetros:")
        print("   --cloud-name --api-key --api-secret")
        return False

    # Configurar Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )

    print(f"Cloudinary configurado: {cloud_name}")
    return True

def obtener_extensiones_imagen():
    """Retorna extensiones de imagen válidas."""
    return {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}

def buscar_fotos_en_carpeta(carpeta_path):
    """
    Busca todas las imágenes en una carpeta y las ordena numéricamente.

    Args:
        carpeta_path: Path a la carpeta con fotos

    Returns:
        list: Lista de Paths a archivos de imagen ordenados
    """
    if not carpeta_path.exists():
        return []

    extensiones = obtener_extensiones_imagen()

    # Buscar archivos de imagen
    fotos = [
        f for f in carpeta_path.iterdir()
        if f.is_file() and f.suffix.lower() in extensiones
    ]

    # Ordenar por nombre (asume formato: 01.jpg, 02.jpg, etc.)
    fotos.sort(key=lambda f: f.name)

    return fotos

def generar_public_id(propiedad_id, indice_foto, carpeta_inmobiliaria):
    """
    Genera el public_id para Cloudinary (sin hash, URL limpia).

    Args:
        propiedad_id: ID de la propiedad (ej: PROP-001)
        indice_foto: Índice de la foto (0, 1, 2, ...)
        carpeta_inmobiliaria: Nombre de la carpeta de la inmobiliaria (ej: "bbr", "propiedades_demo")

    Returns:
        str: public_id en formato: inmobiliaria/prop-001/foto01
        Ejemplo: "bbr/prop-001/foto01"
    """
    # Convertir ID a lowercase
    id_limpio = propiedad_id.lower()

    # Número de foto (01, 02, 03, ...)
    numero_foto = str(indice_foto + 1).zfill(2)

    # Formato: inmobiliaria/prop-id/fotoNN
    return f"{carpeta_inmobiliaria}/{id_limpio}/foto{numero_foto}"

def subir_foto_cloudinary(foto_path, public_id, dry_run=False):
    """
    Sube una foto a Cloudinary.

    Args:
        foto_path: Path al archivo de foto
        public_id: ID público en Cloudinary
        dry_run: Si es True, simula la subida sin ejecutarla

    Returns:
        dict: Respuesta de Cloudinary con URL, o None si falló
    """
    if dry_run:
        print(f"    [DRY-RUN] Subiendo: {foto_path.name} -> {public_id}")
        return {
            'secure_url': f'https://res.cloudinary.com/demo/image/upload/{public_id}.jpg',
            'public_id': public_id
        }

    try:
        # Subir con Public ID limpio (sin hash) y transformaciones optimizadas
        response = cloudinary.uploader.upload(
            str(foto_path),
            public_id=public_id,
            overwrite=True,      # Reemplazar si ya existe
            invalidate=True,     # Invalidar cache del CDN
            resource_type="image",
            format="jpg",        # Convertir todo a JPG para consistencia
            transformation=[
                {'quality': 'auto:good'},  # Calidad automática optimizada
                {'fetch_format': 'auto'}   # Formato automático según navegador
            ]
        )

        print(f"    Subida exitosa: {foto_path.name} -> {response['secure_url']}")
        return response

    except Exception as e:
        print(f"    ERROR subiendo {foto_path.name}: {str(e)}")
        return None

def procesar_json_propiedades(json_path, carpeta_fotos_path, carpeta_inmobiliaria, dry_run=False):
    """
    Procesa el JSON de propiedades, sube fotos pendientes y actualiza URLs.

    Args:
        json_path: Path al archivo JSON
        carpeta_fotos_path: Path a carpeta raíz con fotos numeradas
        carpeta_inmobiliaria: Nombre de carpeta en Cloudinary (ej: "bbr", "demo")
        dry_run: Modo prueba

    Returns:
        dict: JSON actualizado con URLs de Cloudinary
    """
    # Cargar JSON
    print(f"\nProcesando: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR al leer JSON: {e}")
        return None

    propiedades = data.get('propiedades', [])
    total = len(propiedades)

    print(f"Total propiedades: {total}")

    # Contadores
    procesadas = 0
    con_fotos = 0
    sin_fotos = 0
    errores = 0

    # Procesar cada propiedad
    for prop in propiedades:
        prop_id = prop.get('id')
        fotos_info = prop.get('fotos', {})
        urls_existentes = fotos_info.get('urls', [])

        # Si ya tiene URLs, conservarlas
        if urls_existentes:
            con_fotos += 1
            print(f"\n[{prop_id}] Ya tiene {len(urls_existentes)} fotos - CONSERVANDO")
            continue

        # Propiedad sin fotos - buscar carpeta
        carpeta_numero = fotos_info.get('carpeta')

        if not carpeta_numero:
            sin_fotos += 1
            print(f"\n[{prop_id}] Sin número de carpeta - SALTANDO")
            continue

        # Buscar carpeta de fotos
        carpeta_prop = carpeta_fotos_path / str(carpeta_numero)

        if not carpeta_prop.exists():
            sin_fotos += 1
            print(f"\n[{prop_id}] Carpeta {carpeta_numero}/ no encontrada - SALTANDO")
            continue

        # Buscar fotos en la carpeta
        fotos = buscar_fotos_en_carpeta(carpeta_prop)

        if not fotos:
            sin_fotos += 1
            print(f"\n[{prop_id}] Carpeta {carpeta_numero}/ vacía - SALTANDO")
            continue

        print(f"\n[{prop_id}] Procesando {len(fotos)} fotos desde carpeta {carpeta_numero}/")

        # Subir cada foto
        urls_nuevas = []

        for i, foto_path in enumerate(fotos):
            public_id = generar_public_id(prop_id, i, carpeta_inmobiliaria)

            response = subir_foto_cloudinary(foto_path, public_id, dry_run)

            if response and 'secure_url' in response:
                urls_nuevas.append(response['secure_url'])
            else:
                errores += 1

        # Actualizar JSON con URLs
        if urls_nuevas:
            prop['fotos']['urls'] = urls_nuevas
            procesadas += 1
            print(f"  Resultado: {len(urls_nuevas)} fotos subidas exitosamente")
        else:
            print(f"  ERROR: No se pudo subir ninguna foto")
            errores += 1

    # Resumen
    print(f"\n{'='*60}")
    print(f"RESUMEN DE PROCESAMIENTO")
    print(f"{'='*60}")
    print(f"Total propiedades: {total}")
    print(f"  - Con fotos conservadas: {con_fotos}")
    print(f"  - Procesadas (nuevas): {procesadas}")
    print(f"  - Sin fotos disponibles: {sin_fotos}")
    print(f"  - Con errores: {errores}")

    # Actualizar metadata
    data['metadata']['fecha_actualizacion_fotos'] = datetime.now().isoformat()
    data['metadata']['carpeta_cloudinary'] = carpeta_inmobiliaria

    return data

def main():
    """Función principal."""

    parser = argparse.ArgumentParser(
        description='Sube fotos de propiedades a Cloudinary y actualiza JSON'
    )

    parser.add_argument(
        'archivo_json',
        help='Archivo JSON con las propiedades'
    )

    parser.add_argument(
        '--carpeta-fotos',
        required=True,
        help='Ruta a carpeta raíz con fotos numeradas (1/, 2/, 3/, etc.)'
    )

    parser.add_argument(
        '--cloud-name',
        help='Nombre del cloud de Cloudinary (o usar CLOUDINARY_CLOUD_NAME env var)'
    )

    parser.add_argument(
        '--api-key',
        help='API Key de Cloudinary (o usar CLOUDINARY_API_KEY env var)'
    )

    parser.add_argument(
        '--api-secret',
        help='API Secret de Cloudinary (o usar CLOUDINARY_API_SECRET env var)'
    )

    parser.add_argument(
        '--inmobiliaria',
        required=True,
        help='Nombre de la inmobiliaria para carpeta en Cloudinary (ej: bbr, demo, propiedades_xxx)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Modo prueba - simula subida sin ejecutarla'
    )

    args = parser.parse_args()

    # Validar que el JSON existe
    json_path = Path(args.archivo_json)
    if not json_path.exists():
        print(f"ERROR: Archivo JSON no encontrado: {args.archivo_json}")
        sys.exit(1)

    # Validar que la carpeta de fotos existe
    carpeta_fotos_path = Path(args.carpeta_fotos)
    if not carpeta_fotos_path.exists():
        print(f"ERROR: Carpeta de fotos no encontrada: {args.carpeta_fotos}")
        sys.exit(1)

    # Configurar Cloudinary (solo si no es dry-run)
    if not args.dry_run:
        if not configurar_cloudinary(args.cloud_name, args.api_key, args.api_secret):
            sys.exit(1)
    else:
        print("MODO DRY-RUN: Las fotos NO se subirán realmente")

    # Procesar propiedades
    resultado = procesar_json_propiedades(
        json_path,
        carpeta_fotos_path,
        args.inmobiliaria,
        args.dry_run
    )

    if not resultado:
        print("ERROR: No se pudo procesar el JSON")
        sys.exit(1)

    # Guardar JSON actualizado
    try:
        # Crear backup del JSON original
        backup_path = json_path.with_suffix('.backup.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
        print(f"\nBackup creado: {backup_path}")

        # Guardar JSON actualizado
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"JSON actualizado exitosamente: {json_path}")
        print(f"{'='*60}")

        if not args.dry_run:
            print(f"\nProximos pasos:")
            print(f"1. Verificar el JSON actualizado")
            print(f"2. Subir a GitHub:")
            print(f"   git add {json_path.name}")
            print(f"   git commit -m 'Actualizar catálogo con fotos de Cloudinary'")
            print(f"   git push")
        else:
            print(f"\nEsto fue un DRY-RUN. Para subir realmente, ejecuta sin --dry-run")

    except Exception as e:
        print(f"ERROR al guardar JSON: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
