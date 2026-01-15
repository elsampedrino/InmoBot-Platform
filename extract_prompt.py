import json

# Leer workflow Haiku
with open('Flujos N8N/N8N_InmoBot - Haiku.json', 'r', encoding='utf-8') as f:
    wf_haiku = json.load(f)

# Leer workflow Haiku+Sonnet
with open('Flujos N8N/N8N_InmoBot - Haiku + Sonnet.json', 'r', encoding='utf-8') as f:
    wf_haiku_sonnet = json.load(f)

# Extraer nodo Haiku
node_haiku = [n for n in wf_haiku['nodes'] if n['name'] == 'Preparar Respuesta Haiku'][0]
with open('Documentacion/prompt_haiku_actual.txt', 'w', encoding='utf-8') as f:
    f.write(node_haiku['parameters']['jsCode'])
print("OK - Prompt Haiku guardado en Documentacion/prompt_haiku_actual.txt")

# Extraer nodos del workflow Haiku+Sonnet
for node in wf_haiku_sonnet['nodes']:
    if 'Haiku' in node['name'] or 'Sonnet' in node['name']:
        filename = f"Documentacion/prompt_{node['name'].replace(' ', '_').replace('-', '_').lower()}.txt"
        if 'jsCode' in node.get('parameters', {}):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(node['parameters']['jsCode'])
            print(f"OK - {node['name']} guardado en {filename}")

print("\nAnalisis de cambios completado")
