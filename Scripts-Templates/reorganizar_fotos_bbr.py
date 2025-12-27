#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REORGANIZAR FOTOS BBR
=====================
Reorganiza las fotos de BBR desde carpetas por dirección a carpetas numeradas
que corresponden con las filas del Excel estándar.

Input:
    - JSON: propiedades_bbr_propiedades_estandar_20251220.json
    - Fotos: ../BBR Grupo Inmobiliario/propiedades/ (organizadas por dirección)

Output:
    - Carpetas numeradas: ../BBR Grupo Inmobiliario/fotos_numeradas/1/, 2/, 3/, etc.

Uso:
    python reorganizar_fotos_bbr.py
"""

import json
import os
import shutil
from pathlib import Path
from difflib import get_close_matches

def normalizar_direccion(direccion):
    """
    Normaliza una dirección para comparación.
    "Av. Mitre al 1300" -> "av mitre 1300"
    """
    if not direccion:
        return ""

    # Convertir a lowercase y remover puntos, comas
    direccion = direccion.lower()
    direccion = direccion.replace(".", "")
    direccion = direccion.replace(",", "")
    direccion = direccion.replace("al ", "")
    direccion = direccion.replace("  ", " ")

    return direccion.strip()

def buscar_carpeta_fotos(direccion, tipo_prop, carpetas_disponibles):
    """
    Busca la carpeta de fotos que coincide con la dirección.

    Args:
        direccion: Dirección de la propiedad (ej: "Colón al 1100")
        tipo_prop: Tipo de propiedad para buscar en carpeta correcta
        carpetas_disponibles: Lista de carpetas disponibles

    Returns:
        str: Nombre de la carpeta encontrada o None
    """
    if not direccion:
        return None

    direccion_normalizada = normalizar_direccion(direccion)

    # Normalizar carpetas disponibles
    carpetas_normalizadas = {normalizar_direccion(c): c for c in carpetas_disponibles}

    # Buscar coincidencia exacta
    if direccion_normalizada in carpetas_normalizadas:
        return carpetas_normalizadas[direccion_normalizada]

    # Buscar coincidencia parcial
    matches = get_close_matches(direccion_normalizada, carpetas_normalizadas.keys(), n=1, cutoff=0.6)

    if matches:
        return carpetas_normalizadas[matches[0]]

    return None

def obtener_carpetas_tipo(tipo_prop, base_path):
    """
    Obtiene las carpetas de fotos según el tipo de propiedad.

    Args:
        tipo_prop: "Casa", "Departamento", "Terreno", "Campo", "Local Comercial"
        base_path: Path base de fotos

    Returns:
        tuple: (tipo_carpeta, lista_carpetas)
    """
    mapeo_tipos = {
        'Casa': 'Casas',
        'Departamento': 'Depto',
        'Terreno': 'Lotes',
        'Campo': 'Campos',
        'Local Comercial': 'Alquiler'  # Asumiendo que locales están en Alquiler
    }

    tipo_carpeta = mapeo_tipos.get(tipo_prop)

    if not tipo_carpeta:
        return (None, [])

    carpeta_tipo = base_path / tipo_carpeta

    if not carpeta_tipo.exists():
        return (tipo_carpeta, [])

    # Listar carpetas de direcciones
    carpetas = [d.name for d in carpeta_tipo.iterdir() if d.is_dir()]

    return (tipo_carpeta, carpetas)

def copiar_fotos(origen_path, destino_path):
    """
    Copia todas las fotos de origen a destino, renumerándolas.

    Args:
        origen_path: Path de carpeta origen con fotos
        destino_path: Path de carpeta destino
    """
    # Crear carpeta destino
    destino_path.mkdir(parents=True, exist_ok=True)

    # Extensiones de imagen válidas
    extensiones = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

    # Buscar fotos
    fotos = [
        f for f in origen_path.iterdir()
        if f.is_file() and f.suffix.lower() in extensiones
    ]

    # Ordenar por nombre
    fotos.sort(key=lambda f: f.name)

    # Copiar y renumerar
    for i, foto in enumerate(fotos, start=1):
        numero = str(i).zfill(2)
        extension = foto.suffix.lower()

        # Forzar .jpg para consistencia
        if extension in {'.jpeg', '.jpg'}:
            extension = '.jpg'

        destino_foto = destino_path / f"{numero}{extension}"

        shutil.copy2(foto, destino_foto)

    return len(fotos)

def main():
    """Función principal."""

    print("="*80)
    print("REORGANIZACIÓN DE FOTOS BBR")
    print("="*80)

    # Cargar JSON
    json_file = "propiedades_bbr_propiedades_estandar_20251220.json"
    print(f"\nCargando JSON: {json_file}")

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR al cargar JSON: {e}")
        return

    propiedades = data.get('propiedades', [])
    print(f"Total propiedades: {len(propiedades)}")

    # Paths
    fotos_base = Path("../BBR Grupo Inmobiliario/propiedades")
    fotos_destino_base = Path("../BBR Grupo Inmobiliario/fotos_numeradas")

    # Limpiar carpeta destino si existe
    if fotos_destino_base.exists():
        print(f"\nLimpiando carpeta destino existente...")
        shutil.rmtree(fotos_destino_base)

    fotos_destino_base.mkdir(parents=True, exist_ok=True)

    # Contadores
    procesadas = 0
    copiadas = 0
    no_encontradas = 0

    print(f"\n{'='*80}")
    print("PROCESANDO PROPIEDADES")
    print(f"{'='*80}")

    # Procesar cada propiedad
    for i, prop in enumerate(propiedades, start=1):
        prop_id = prop.get('id', '')
        tipo = prop.get('tipo', '')
        direccion = prop.get('direccion', {}).get('calle', '')

        print(f"\n[{i}] {prop_id} - {tipo}")
        print(f"    Dirección: {direccion}")

        # Obtener carpetas del tipo
        tipo_carpeta, carpetas_disponibles = obtener_carpetas_tipo(tipo, fotos_base)

        if not tipo_carpeta or not carpetas_disponibles:
            print(f"    ERROR: No hay carpeta de tipo '{tipo}'")
            no_encontradas += 1
            continue

        # Buscar carpeta de fotos
        carpeta_encontrada = buscar_carpeta_fotos(direccion, tipo, carpetas_disponibles)

        if not carpeta_encontrada:
            print(f"    ERROR: No se encontró carpeta de fotos")
            no_encontradas += 1
            continue

        print(f"    Carpeta origen: {tipo_carpeta}/{carpeta_encontrada}")

        # Copiar fotos
        origen = fotos_base / tipo_carpeta / carpeta_encontrada
        destino = fotos_destino_base / str(i)

        try:
            num_fotos = copiar_fotos(origen, destino)
            print(f"    OK: {num_fotos} fotos copiadas a carpeta {i}/")
            procesadas += 1
            copiadas += num_fotos
        except Exception as e:
            print(f"    ERROR al copiar fotos: {e}")
            no_encontradas += 1

    # Resumen
    print(f"\n{'='*80}")
    print("RESUMEN")
    print(f"{'='*80}")
    print(f"Total propiedades: {len(propiedades)}")
    print(f"  - Procesadas: {procesadas}")
    print(f"  - No encontradas: {no_encontradas}")
    print(f"Total fotos copiadas: {copiadas}")
    print(f"\nCarpeta generada: {fotos_destino_base}")

    if procesadas > 0:
        print(f"\nProximos pasos:")
        print(f"1. Verificar las carpetas numeradas generadas")
        print(f"2. Subir fotos a Cloudinary con:")
        print(f'   python subir_fotos_cloudinary.py "{json_file}" \\')
        print(f'     --carpeta-fotos "{fotos_destino_base}" \\')
        print(f'     --inmobiliaria bbr')

if __name__ == '__main__':
    main()
