-- Migración Fase 4 — Campo notificaciones en empresas
-- Almacena la configuración de canales de notificación por empresa.
-- Los canales actuales son telegram y email.

ALTER TABLE empresas
ADD COLUMN IF NOT EXISTS notificaciones JSONB NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN empresas.notificaciones IS
'Config de notificaciones por empresa. Estructura: {"telegram": {"enabled": bool, "chat_id": "..."}, "email": {"enabled": bool, "to": "..."}}';

-- Ejemplo BBR
-- UPDATE empresas
-- SET notificaciones = '{"telegram": {"enabled": true, "chat_id": "..."}, "email": {"enabled": true, "to": "..."}}'
-- WHERE id_empresa = 1;