#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar el JSON normalizado al repositorio bot-inmobiliaria-data en GitHub
Usa la API de GitHub para actualizar el archivo directamente
"""

import json
import base64
import os
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: Necesitas instalar requests: pip install requests")
    exit(1)

# Configuración
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Token de GitHub desde variable de entorno
REPO_OWNER = "elsampedrino"
REPO_NAME = "bot-inmobiliaria-data"
FILE_PATH = "propiedades_bbr.json"
BRANCH = "main"

# Rutas locales
JSON_LOCAL = Path("BBR Grupo Inmobiliario/propiedades_bbr.json")

def obtener_sha_archivo(token, owner, repo, path, branch):
    """Obtiene el SHA del archivo actual en GitHub (necesario para actualizar)"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"ref": branch}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['sha']
    elif response.status_code == 404:
        return None  # Archivo no existe
    else:
        raise Exception(f"Error obteniendo SHA: {response.status_code} - {response.text}")

def actualizar_archivo_github(token, owner, repo, path, content, message, sha=None, branch="main"):
    """Actualiza un archivo en GitHub usando la API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    # Codificar contenido en base64
    content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "message": message,
        "content": content_encoded,
        "branch": branch
    }

    # Si el archivo existe, necesitamos el SHA
    if sha:
        data["sha"] = sha

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Error actualizando archivo: {response.status_code} - {response.text}")

def main():
    print("=" * 70)
    print("SINCRONIZACION DE JSON A GITHUB")
    print("=" * 70)
    print()

    # Verificar token
    if not GITHUB_TOKEN:
        print("ERROR: No se encontro GITHUB_TOKEN en las variables de entorno")
        print()
        print("Para configurar el token:")
        print("  1. Ve a GitHub -> Settings -> Developer settings -> Personal access tokens")
        print("  2. Genera un token con permiso 'repo'")
        print("  3. Configura la variable de entorno:")
        print("     Windows: set GITHUB_TOKEN=tu_token")
        print("     Linux/Mac: export GITHUB_TOKEN=tu_token")
        print()
        return

    # 1. Leer JSON local
    print(f"1. Leyendo JSON local: {JSON_LOCAL}")
    if not JSON_LOCAL.exists():
        print(f"   ERROR: No se encuentra el archivo {JSON_LOCAL}")
        return

    with open(JSON_LOCAL, 'r', encoding='utf-8') as f:
        data = json.load(f)

    propiedades = data.get('propiedades', [])
    print(f"   -> {len(propiedades)} propiedades")
    print(f"   -> Ultima actualizacion: {data['metadata']['ultima_actualizacion']}")
    print()

    # 2. Verificar normalización
    print("2. Verificando normalizacion...")
    tipos_normalizados = all(
        p.get('tipo', '').islower() for p in propiedades if p.get('tipo')
    )
    operaciones_normalizadas = all(
        p.get('operacion', '').islower() for p in propiedades if p.get('operacion')
    )

    if tipos_normalizados and operaciones_normalizadas:
        print("   OK - JSON esta normalizado (tipo y operacion en minusculas)")
    else:
        print("   ADVERTENCIA: JSON no esta completamente normalizado")
        print("   Ejecuta 'normalizar_json_minusculas.py' primero")
    print()

    # 3. Preparar contenido
    print("3. Preparando contenido para GitHub...")
    content = json.dumps(data, indent=2, ensure_ascii=False)
    print(f"   -> Tamaño: {len(content)} caracteres")
    print()

    # 4. Obtener SHA del archivo actual
    print(f"4. Obteniendo SHA del archivo en GitHub ({REPO_OWNER}/{REPO_NAME})...")
    try:
        sha = obtener_sha_archivo(GITHUB_TOKEN, REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH)
        if sha:
            print(f"   -> SHA encontrado: {sha[:7]}...")
        else:
            print("   -> Archivo no existe, se creara uno nuevo")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    print()

    # 5. Actualizar archivo en GitHub
    print("5. Actualizando archivo en GitHub...")
    commit_message = f"""Actualizar catálogo BBR con normalización a minúsculas

- Normalizar tipo, operacion, estado_construccion a minúsculas
- Total: {len(propiedades)} propiedades
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Esto mejora el matching con consultas de usuarios normalizadas en el prompt.
"""

    try:
        result = actualizar_archivo_github(
            GITHUB_TOKEN,
            REPO_OWNER,
            REPO_NAME,
            FILE_PATH,
            content,
            commit_message,
            sha,
            BRANCH
        )
        print(f"   OK - Archivo actualizado exitosamente")
        print(f"   -> Commit: {result['commit']['sha'][:7]}")
        print(f"   -> URL: {result['content']['html_url']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    print()

    # 6. Verificar que GitHub Raw se actualice
    print("6. Verificacion...")
    print(f"   -> URL Raw: https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{FILE_PATH}")
    print("   -> IMPORTANTE: GitHub Raw puede tardar 1-2 minutos en actualizar el cache")
    print()

    print("=" * 70)
    print("SINCRONIZACION COMPLETADA")
    print("=" * 70)
    print()
    print(f"El JSON normalizado se subio correctamente a:")
    print(f"  https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/{BRANCH}/{FILE_PATH}")
    print()
    print("N8N ya puede leer el JSON normalizado!")

if __name__ == "__main__":
    main()
