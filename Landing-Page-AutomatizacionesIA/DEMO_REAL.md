# Demo Real - Widget de Testing

El widget de demo en la landing page se conecta al workflow **real** de N8N Haiku + Sonnet con limitación de consultas.

## Arquitectura

```
Usuario en Landing Page
         ↓
   Demo Widget (TypeScript)
         ↓
   POST https://n8n-bot-inmobiliario.onrender.com/webhook/chat
         ↓
   N8N Workflow (Haiku + Sonnet)
         ↓
   GitHub Repo "demo"
         ↓
   Respuesta al usuario
```

## Flujo de Datos

### 1. Request al Webhook

**Endpoint**: `https://n8n-bot-inmobiliario.onrender.com/webhook/chat`

**Método**: POST

**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "message": "Busco un departamento de 2 ambientes en Palermo",
  "sessionId": "demo-1704985200000-abc123xyz",
  "repo": "demo"
}
```

### 2. Procesamiento en N8N

El workflow ejecuta:

1. **Webhook Chat** - Recibe el request
2. **HTTP Request GitHub** - Obtiene propiedades del repo `demo`
3. **Preparar Filtrado Haiku** - Formatea propiedades y consulta
4. **Haiku - Filtrar Propiedades** - Claude Haiku selecciona propiedades relevantes
5. **Preparar Respuesta Sonnet** - Construye payload con propiedades filtradas
6. **Sonnet - Generar Respuesta** - Claude Sonnet genera respuesta natural
7. **Logging PostgreSQL** - Guarda en `chat_logs`
8. **Response Webhook** - Devuelve respuesta

### 3. Response

**Status**: 200 OK

**Body**:
```json
{
  "response": "🏠 **Depto 2 amb - Palermo Soho**\nHermoso departamento de 45m² con cochera y balcón...\n**$180.000**\n📸 https://...",
  "sessionId": "demo-1704985200000-abc123xyz",
  "timestamp": "2026-01-11T12:30:00.000Z"
}
```

## Limitación de Consultas

### Implementación

El widget usa **sessionStorage** del navegador para trackear consultas:

```typescript
// Estado almacenado en sessionStorage
sessionStorage.setItem('demo-session-id', 'demo-1704985200000-abc123xyz');
sessionStorage.setItem('demo-query-count', '2');
```

### Lógica de Límite

```typescript
const MAX_QUERIES = 3;
let queryCount = parseInt(sessionStorage.getItem('demo-query-count') || '0');

if (queryCount >= MAX_QUERIES) {
  // Mostrar mensaje de límite alcanzado
  // Deshabilitar input
  // Sugerir contacto o reload
}
```

### Mensajes al Usuario

**Después de cada consulta**:
```
ℹ️ Te quedan 2 consultas de prueba.
```

**Al alcanzar el límite**:
```
⚠️ Límite de consultas alcanzado

Has alcanzado el límite de 3 consultas de prueba.

Para continuar probando el asistente, contactanos y te damos
acceso completo o recargá la página para reiniciar el demo.
```

## Reset del Demo

El usuario puede resetear el contador de 3 formas:

1. **Recargar la página** - sessionStorage se mantiene, pero puede limpiar cookies
2. **Abrir en ventana incógnita** - Nueva sesión limpia
3. **Limpiar sessionStorage manualmente**:
   ```javascript
   sessionStorage.removeItem('demo-session-id');
   sessionStorage.removeItem('demo-query-count');
   ```

## Configuración del Repo Demo

El repo `demo` debe existir en tu GitHub con la estructura:

```
github.com/tu-usuario/inmobot-propiedades-demo/
└── propiedades_demo.json
```

**Contenido esperado**:
```json
{
  "propiedades": [
    {
      "id": "DEMO-001",
      "tipo": "Departamento",
      "operacion": "Venta",
      "titulo": "Depto 2 amb - Palermo Soho",
      "precio": {
        "valor": 180000,
        "moneda": "USD"
      },
      "direccion": {
        "barrio": "Palermo",
        "ciudad": "Buenos Aires"
      },
      "caracteristicas": {
        "dormitorios": 1,
        "superficie_total": 45
      },
      "detalles": ["cochera", "balcon"],
      "fotos": {
        "urls": [
          "https://ejemplo.com/foto1.jpg",
          "https://ejemplo.com/foto2.jpg"
        ]
      }
    }
    // ... más propiedades
  ]
}
```

Ver [JSON_ESTANDAR.md](../Documentacion/JSON_ESTANDAR.md) para el esquema completo.

## Costos de Testing

Cada consulta consume:

- **Haiku (filtrado)**: ~500 tokens = ~$0.0004 USD
- **Sonnet (respuesta)**: ~600 tokens = ~$0.018 USD
- **Total por consulta**: ~$0.0184 USD

3 consultas por sesión = ~$0.055 USD

## Monitoreo

Todas las consultas del demo se logguean en PostgreSQL:

**Tabla**: `chat_logs`

**Campos relevantes**:
- `session_id`: Contiene "demo-" para identificar consultas de testing
- `repo`: Siempre "demo"
- `timestamp`: Fecha/hora de la consulta
- `tokens_haiku`, `tokens_sonnet`: Consumo de tokens
- `costo_total`: Costo en USD

### Query para ver consultas del demo:

```sql
SELECT
  session_id,
  mensaje_usuario,
  timestamp,
  tokens_haiku,
  tokens_sonnet,
  costo_total
FROM chat_logs
WHERE session_id LIKE 'demo-%'
ORDER BY timestamp DESC
LIMIT 50;
```

## Mantenimiento

### Cambiar límite de consultas

Editar en [`src/components/Demo.astro`](src/components/Demo.astro:82):

```typescript
const MAX_QUERIES = 5; // Cambiar de 3 a 5
```

### Cambiar repo de testing

```typescript
body: JSON.stringify({
  message: message,
  sessionId: sessionId,
  repo: 'testing-premium' // Cambiar repo
})
```

### Deshabilitar límite (no recomendado)

Comentar la verificación:

```typescript
// if (queryCount >= MAX_QUERIES) {
//   // ... código de límite
// }
```

## Seguridad

### Protecciones Implementadas

1. **Límite de consultas**: Evita abuso del demo
2. **SessionStorage**: No se puede manipular desde otro sitio
3. **CORS**: N8N webhook configurado con CORS apropiado
4. **Rate limiting**: N8N tiene throttling incorporado
5. **Repo aislado**: El repo "demo" no contiene datos reales

### Riesgos Potenciales

⚠️ **Session storage puede resetearse**: El usuario puede limpiar sessionStorage y hacer más consultas

⚠️ **Sin autenticación**: Cualquiera con la URL del webhook puede hacer consultas

⚠️ **Costos**: Si muchos usuarios testean simultáneamente, puede aumentar costos de API

### Mitigaciones Recomendadas (Futuras)

1. **Backend rate limiting**: Limitar por IP en lugar de sessionStorage
2. **Captcha**: Agregar reCAPTCHA antes de permitir testing
3. **Analytics**: Trackear abuso con Google Analytics o Plausible
4. **Webhook privado**: Mover webhook a endpoint autenticado

## Troubleshooting

### Error: "Problemas técnicos"

**Causa**: Webhook de N8N no responde o está caído

**Solución**:
1. Verificar que Render no esté en sleep mode
2. Check N8N workflow está activo
3. Verificar logs de N8N

### Respuestas vacías o genéricas

**Causa**: Repo "demo" vacío o sin propiedades

**Solución**:
1. Verificar que existe `github.com/.../inmobot-propiedades-demo`
2. Verificar archivo `propiedades_demo.json` válido
3. Check permisos de GitHub (public repo)

### Contador no funciona

**Causa**: sessionStorage deshabilitado en el navegador

**Solución**:
- Informar al usuario que debe habilitar cookies/storage
- Considerar fallback a variable en memoria (se pierde al reload)

---

**Última actualización**: 2026-01-11
