# Workflow Telegram con Estadísticas

## Flujo actualizado para registrar leads en conversion_logs

```
┌─────────────────────────┐
│  Webhook Contact        │ ← Recibe formulario "Agendar visita"
└───────────┬─────────────┘
            │
            ├──────────────────────────────────┐
            │                                  │
            v                                  v
┌─────────────────────────┐      ┌─────────────────────────────┐
│ Preparar Mensaje        │      │ Preparar INSERT Lead        │ ← NUEVO
│ Telegram                │      │ (conversion_logs)           │
└───────────┬─────────────┘      └──────────────┬──────────────┘
            │                                   │
            v                                   v
┌─────────────────────────┐      ┌─────────────────────────────┐
│ Enviar Mensaje          │      │ Postgres: Execute Query     │ ← NUEVO
│ Telegram                │      │ (INSERT conversion_logs)    │
└───────────┬─────────────┘      └──────────────┬──────────────┘
            │                                   │
            └──────────────┬────────────────────┘
                          │
                          v
            ┌─────────────────────────┐
            │ Responder al Webhook    │
            │ Contact                 │
            └─────────────────────────┘
```

## Nodos a agregar:

### 1. Nodo Code: "Preparar INSERT Lead"
- **Ubicación:** Después de "Webhook Contact", en paralelo con "Preparar Mensaje Telegram"
- **Código:** [nodo-insert-conversion-log.js](./nodo-insert-conversion-log.js)
- **Salida:** `{ query: "INSERT INTO...", nombre, telefono, disponibilidad, source }`

### 2. Nodo Postgres: "Insert Lead Stats"
- **Tipo:** Postgres → Execute Query
- **Credential:** Postgres account
- **Query:** `={{ $json.query }}`
- **Query Parameters:** (dejar vacío)

## Datos registrados:

Cada vez que un usuario complete el formulario "Agendar una visita", se guardará:
- ✅ **nombre** - Nombre del interesado
- ✅ **telefono** - Teléfono de contacto
- ✅ **disponibilidad** - Horario disponible
- ✅ **source** - Origen (widget, telegram, etc.)
- ✅ **timestamp** - Fecha y hora automática

## Próximos pasos:

1. Agregar nodo "Preparar INSERT Lead" en el workflow de Telegram
2. Agregar nodo "Insert Lead Stats" conectado al anterior
3. Probar el flujo completo
4. Verificar que los datos se guarden en `conversion_logs`

