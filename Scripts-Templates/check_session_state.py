import psycopg2
import json

CONN = "postgresql://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl"
SESSION = "test-cucurullo-final-20260511125955"

conn = psycopg2.connect(CONN)
cur = conn.cursor()

# Estado final de la conversación
cur.execute("""
    SELECT cc.estado_json
    FROM contextos_conversacion cc
    JOIN conversaciones c ON c.id_conversacion = cc.id_conversacion
    WHERE c.session_id = %s
    ORDER BY cc.updated_at DESC
    LIMIT 1
""", (SESSION,))
row = cur.fetchone()
if row:
    data = row[0] if isinstance(row[0], dict) else json.loads(row[0])
    ultimo = data.get("ultimo_item_referenciado", "")
    print(f"ultimo_item_referenciado: {str(ultimo)[:8]} (esperado: 44b092e1 = La Rioja)")
    print(f"item_seleccionado_explicitamente: {data.get('item_seleccionado_explicitamente')}")
else:
    print("Sesion no encontrada")

# Lead más reciente con "Damian Test"
cur.execute("""
    SELECT nombre, metadata
    FROM leads
    WHERE nombre ILIKE %s
    ORDER BY created_at DESC
    LIMIT 3
""", ("%Damian Test%",))
rows = cur.fetchall()
if rows:
    for r in rows:
        meta = r[1] if isinstance(r[1], dict) else (json.loads(r[1]) if r[1] else {})
        props = meta.get("propiedades_interes", [])
        print(f"\nLead: {r[0]}")
        print(f"  propiedades_interes: {props}")
else:
    print("No se encontraron leads con ese nombre")

conn.close()
