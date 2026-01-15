#!/usr/bin/env python3
"""
Script para generar JSON de benchmark con 102 propiedades (34 x 3)
Modifica solo los IDs de las propiedades para testing de rendimiento
"""

import json
import copy
from datetime import datetime

# Leer JSON original
input_file = r"BBR Grupo Inmobiliario\propiedades_bbr.json"
output_file = r"BBR Grupo Inmobiliario\propiedades_bbr_benchmark_102.json"

print("Generador de JSON de Benchmark")
print("=" * 60)

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

original_props = data['propiedades']
total_original = len(original_props)

print(f"JSON original cargado: {total_original} propiedades")

# Crear lista para las nuevas propiedades
nuevas_propiedades = []

# Triplicar las propiedades modificando solo el ID
for multiplicador in range(1, 4):  # 1, 2, 3
    for prop in original_props:
        # Crear copia profunda de la propiedad
        nueva_prop = copy.deepcopy(prop)

        # Modificar solo el ID
        id_original = prop['id']  # ej: "PROP-001"
        numero_original = int(id_original.split('-')[1])  # ej: 1

        # Calcular nuevo ID:
        # Lote 1: PROP-001 a PROP-034 (multiplicador 1)
        # Lote 2: PROP-035 a PROP-068 (multiplicador 2)
        # Lote 3: PROP-069 a PROP-102 (multiplicador 3)
        nuevo_numero = numero_original + (total_original * (multiplicador - 1))
        nuevo_id = f"PROP-{nuevo_numero:03d}"

        nueva_prop['id'] = nuevo_id

        nuevas_propiedades.append(nueva_prop)

        if multiplicador == 1:
            status = "Original"
        elif multiplicador == 2:
            status = f"Copia {multiplicador} (ID modificado)"
        else:
            status = f"Copia {multiplicador} (ID modificado)"

        print(f"{status}: {id_original} -> {nuevo_id}")

# Actualizar metadata
data['propiedades'] = nuevas_propiedades
data['metadata']['total'] = len(nuevas_propiedades)
data['metadata']['ultima_actualizacion'] = datetime.now().isoformat()
data['metadata']['version'] = "1.0.0-benchmark"
data['metadata']['notas'].append({
    "fecha": datetime.now().isoformat(),
    "accion": "Generación de JSON de benchmark",
    "descripcion": f"Triplicado de {total_original} propiedades a {len(nuevas_propiedades)} para testing de rendimiento",
    "cambios": len(nuevas_propiedades) - total_original
})

# Guardar nuevo JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("=" * 60)
print(f"JSON de benchmark generado exitosamente!")
print(f"Archivo: {output_file}")
print(f"Total propiedades: {len(nuevas_propiedades)}")
print(f"Rango IDs: PROP-001 -> PROP-{len(nuevas_propiedades):03d}")
print(f"Listo para testing de rendimiento y costos")
print("=" * 60)
