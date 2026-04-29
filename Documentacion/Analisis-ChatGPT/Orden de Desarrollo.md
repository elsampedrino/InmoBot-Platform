*** Propuesta de orden de desarrollo

# Fase 1 — Esqueleto + Core (main.py, config.py, database.py, modelos Pydantic) ✅
# Fase 2 — Chat endpoint (el pipeline completo mínimo funcional) ✅
# Fase 3 — Router + Context Manager ✅
# Fase 4 — Query Parser + Search Engine ✅
# Fase 5 — AI Service (Haiku + Sonnet) ✅
# Fase 6 — KB ✅
# Fase 6b — Leads + Analytics ✅
# Fase 7a — Contrato Backend-Widget ✅
#   - Adapter layer (app/adapters/widget_legacy.py): traducción bidireccional
#     entre contrato interno Premium y contrato legacy del widget
#   - Endpoint: POST /webhook/{empresa_slug}/chat
#     Request:  { message, sessionId, timestamp, repo }
#     Response: { success, response, sessionId, propiedades_detalladas[],
#                 propiedadesMostradas, leads, timestamp, metricas }
#   - Sin tocar el widget; sin duplicar inteligencia en N8N
# Fase 7b — Validación E2E Widget ✅
#   - 9 escenarios, 78/78 checks pasados (100%)
#   - N8N queda fuera del loop conversacional principal
# Fase 7c — Integración Operativa Final + Deploy en Render ✅
#   - Arquitectura final: Widget → API Premium directa (sin N8N en el loop)
#   - render.yaml + runtime.txt: configuración declarativa para Render
#   - config_bbr.json: apiUrl actualizado a /webhook/cristian-inmob/chat
#   - .env.example corregido (CORS_ORIGINS formato string, no JSON)
#   - scripts/smoke_test_render.py: validación post-deploy (5 pruebas)
#   - Checklist de salida a piloto web documentado en el entregable
# Fase 8 — Webhooks WhatsApp (pendiente)