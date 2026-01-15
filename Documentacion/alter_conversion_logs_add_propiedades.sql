-- ============================================
-- ALTER TABLE: Agregar campos de propiedades a conversion_logs
-- Fecha: 28 de Diciembre 2025
-- ============================================

-- Verificar estructura actual de la tabla
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'conversion_logs';

-- Agregar columna session_id si no existe
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

-- Agregar columna propiedades_ids si no existe
ALTER TABLE conversion_logs
ADD COLUMN IF NOT EXISTS propiedades_ids TEXT[];

-- Agregar índice para búsquedas por session_id
CREATE INDEX IF NOT EXISTS idx_conversion_logs_session_id
ON conversion_logs(session_id);

-- Comentarios
COMMENT ON COLUMN conversion_logs.session_id IS 'ID de sesión del chat para vincular con chat_logs';
COMMENT ON COLUMN conversion_logs.propiedades_ids IS 'Array con IDs de propiedades de interés del cliente';

-- ============================================
-- VERIFICACIÓN POST-ALTERACIÓN
-- ============================================

-- Verificar que las columnas se hayan creado correctamente
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversion_logs'
ORDER BY ordinal_position;

-- ============================================
-- FIN
-- ============================================
