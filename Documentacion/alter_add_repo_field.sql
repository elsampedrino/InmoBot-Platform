-- ============================================
-- ALTER TABLE: Agregar campo repo para multi-tenancy
-- Fecha: 28 de Diciembre 2025
-- ============================================

-- Agregar columna repo a chat_logs
ALTER TABLE chat_logs
ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo';

-- Agregar columna repo a conversion_logs
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo';

-- Crear índices para búsquedas por repo
CREATE INDEX IF NOT EXISTS idx_chat_logs_repo
ON chat_logs(repo);

CREATE INDEX IF NOT EXISTS idx_conversion_logs_repo
ON conversion_logs(repo);

-- Comentarios
COMMENT ON COLUMN chat_logs.repo IS 'Identificador del catálogo/cliente: demo, bbr, etc';
COMMENT ON COLUMN conversion_logs.repo IS 'Identificador del catálogo/cliente: demo, bbr, etc';

-- ============================================
-- VERIFICACIÓN POST-ALTERACIÓN
-- ============================================

-- Verificar que las columnas se hayan creado correctamente
SELECT
  table_name,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name IN ('chat_logs', 'conversion_logs')
  AND column_name = 'repo'
ORDER BY table_name, ordinal_position;

-- Ver índices creados
SELECT
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename IN ('chat_logs', 'conversion_logs')
  AND indexname LIKE '%repo%';

-- ============================================
-- QUERIES DE EJEMPLO CON FILTRO POR REPO
-- ============================================

-- Estadísticas solo de BBR (producción)
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms
FROM chat_logs
WHERE repo = 'bbr'
  AND timestamp >= NOW() - INTERVAL '7 days';

-- Estadísticas solo de DEMO
SELECT
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms
FROM chat_logs
WHERE repo = 'demo'
  AND timestamp >= NOW() - INTERVAL '7 days';

-- Comparación entre repos
SELECT
  repo,
  COUNT(*) as total_consultas,
  SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as consultas_exitosas,
  ROUND(100.0 * SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito_pct,
  ROUND(AVG(response_time_ms)::numeric, 0) as tiempo_promedio_ms,
  SUM(tokens_total) as tokens_totales
FROM chat_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY repo
ORDER BY total_consultas DESC;

-- Leads por repo
SELECT
  repo,
  COUNT(*) as total_leads,
  COUNT(DISTINCT session_id) as sesiones_convertidas
FROM conversion_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY repo
ORDER BY total_leads DESC;

-- ============================================
-- ACTUALIZAR REGISTROS EXISTENTES (OPCIONAL)
-- ============================================

-- Si querés marcar registros viejos como 'demo' o 'unknown'
-- Descomentar si es necesario:

-- UPDATE chat_logs
-- SET repo = 'demo'
-- WHERE repo IS NULL;

-- UPDATE conversion_logs
-- SET repo = 'demo'
-- WHERE repo IS NULL;

-- ============================================
-- FIN
-- ============================================
