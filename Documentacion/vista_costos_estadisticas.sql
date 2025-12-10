-- ============================================
-- VISTA: Estadísticas con Costos en USD
-- Calcula dinámicamente el costo basado en tokens
-- ============================================

-- Precios de Anthropic (Enero 2025)
-- Haiku: $0.25 input / $1.25 output por 1M tokens
-- Sonnet: $3.00 input / $15.00 output por 1M tokens
-- Nota: Usamos promedio de 50% input / 50% output como estimación

CREATE OR REPLACE VIEW estadisticas_con_costos AS
SELECT
  id,
  timestamp,
  session_id,
  consulta,
  idioma,
  success,
  response_time_ms,
  tokens_haiku,
  tokens_sonnet,
  tokens_total,
  propiedades_mostradas,

  -- Costos Haiku (promedio $0.75 por 1M tokens = 50% input + 50% output)
  ROUND((tokens_haiku * 0.75) / 1000000.0, 6) as costo_haiku_usd,

  -- Costos Sonnet (promedio $9.00 por 1M tokens = 50% input + 50% output)
  ROUND((tokens_sonnet * 9.00) / 1000000.0, 6) as costo_sonnet_usd,

  -- Costo total
  ROUND(
    ((tokens_haiku * 0.75) + (tokens_sonnet * 9.00)) / 1000000.0,
    6
  ) as costo_total_usd

FROM chat_logs
WHERE success = 1
ORDER BY timestamp DESC;

COMMENT ON VIEW estadisticas_con_costos IS 'Estadísticas de chat con costos calculados en USD';

-- ============================================
-- VISTA: Resumen de Costos por Período
-- ============================================

CREATE OR REPLACE VIEW resumen_costos AS
SELECT
  DATE(timestamp) as fecha,
  COUNT(*) as total_consultas,
  SUM(tokens_haiku) as tokens_haiku_total,
  SUM(tokens_sonnet) as tokens_sonnet_total,
  SUM(tokens_total) as tokens_total,

  -- Costos del día
  ROUND(SUM((tokens_haiku * 0.75) / 1000000.0), 4) as costo_haiku_dia_usd,
  ROUND(SUM((tokens_sonnet * 9.00) / 1000000.0), 4) as costo_sonnet_dia_usd,
  ROUND(SUM(((tokens_haiku * 0.75) + (tokens_sonnet * 9.00)) / 1000000.0), 4) as costo_total_dia_usd,

  -- Costo promedio por consulta
  ROUND(AVG(((tokens_haiku * 0.75) + (tokens_sonnet * 9.00)) / 1000000.0), 6) as costo_promedio_consulta_usd

FROM chat_logs
WHERE success = 1
GROUP BY DATE(timestamp)
ORDER BY fecha DESC;

COMMENT ON VIEW resumen_costos IS 'Resumen diario de costos de API';

-- ============================================
-- VISTA: Dashboard con Costos
-- Actualiza la vista dashboard_summary para incluir costos
-- ============================================

CREATE OR REPLACE VIEW dashboard_summary_con_costos AS
SELECT
  -- Totales existentes
  (SELECT COUNT(*) FROM chat_logs) as total_consultas,
  (SELECT COUNT(*) FROM chat_logs WHERE success = 1) as consultas_exitosas,
  (SELECT COUNT(*) FROM chat_logs WHERE success = 0) as consultas_fallidas,
  (SELECT COUNT(*) FROM conversion_logs) as total_leads,

  -- Porcentajes
  ROUND(100.0 * (SELECT COUNT(*) FROM chat_logs WHERE success = 1) /
    NULLIF((SELECT COUNT(*) FROM chat_logs), 0), 2) as tasa_exito_pct,
  ROUND(100.0 * (SELECT COUNT(*) FROM conversion_logs) /
    NULLIF((SELECT COUNT(*) FROM chat_logs WHERE success = 1), 0), 2) as tasa_conversion_pct,

  -- Promedios
  (SELECT ROUND(AVG(response_time_ms)) FROM chat_logs WHERE success = 1) as tiempo_respuesta_promedio_ms,
  (SELECT ROUND(AVG(tokens_total)) FROM chat_logs WHERE success = 1) as tokens_promedio_por_consulta,

  -- Tokens totales
  (SELECT SUM(tokens_haiku) FROM chat_logs) as tokens_haiku_total,
  (SELECT SUM(tokens_sonnet) FROM chat_logs) as tokens_sonnet_total,
  (SELECT SUM(tokens_total) FROM chat_logs) as tokens_total_general,

  -- ⭐ COSTOS TOTALES
  ROUND((SELECT SUM((tokens_haiku * 0.75) / 1000000.0) FROM chat_logs WHERE success = 1), 4) as costo_total_haiku_usd,
  ROUND((SELECT SUM((tokens_sonnet * 9.00) / 1000000.0) FROM chat_logs WHERE success = 1), 4) as costo_total_sonnet_usd,
  ROUND((SELECT SUM(((tokens_haiku * 0.75) + (tokens_sonnet * 9.00)) / 1000000.0) FROM chat_logs WHERE success = 1), 4) as costo_total_general_usd,

  -- Costo promedio por consulta
  ROUND((SELECT AVG(((tokens_haiku * 0.75) + (tokens_sonnet * 9.00)) / 1000000.0) FROM chat_logs WHERE success = 1), 6) as costo_promedio_consulta_usd,

  -- Fecha del reporte
  NOW() as fecha_reporte;

COMMENT ON VIEW dashboard_summary_con_costos IS 'Dashboard ejecutivo con información de costos incluida';

-- ============================================
-- Queries de ejemplo
-- ============================================

-- Ver todas las consultas con costos
-- SELECT * FROM estadisticas_con_costos LIMIT 10;

-- Ver resumen de costos por día
-- SELECT * FROM resumen_costos LIMIT 7;

-- Ver dashboard completo con costos
-- SELECT * FROM dashboard_summary_con_costos;

-- Ver costo total acumulado
-- SELECT
--   costo_total_general_usd as costo_acumulado,
--   total_consultas,
--   costo_promedio_consulta_usd
-- FROM dashboard_summary_con_costos;

-- ============================================
-- FIN
-- ============================================
