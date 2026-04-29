** Top items mas mostrados ultimos 30 dias

SELECT i.external_id, i.titulo, COUNT(*) AS veces
FROM premium_chat_log_items cli
JOIN premium_chat_logs cl ON cl.id = cli.id_chat_log
JOIN items i ON i.id_item = cli.id_item
WHERE cl.id_empresa = 1
  AND cl.created_at >= now() - interval '30 days'
GROUP BY i.external_id, i.titulo
ORDER BY veces DESC
LIMIT 20;

** Top items con más conversiones

SELECT i.external_id, i.titulo, COUNT(*) AS conversiones
FROM premium_conversion_log_items coli
JOIN premium_conversion_logs col ON col.id = coli.id_conversion_log
JOIN items i ON i.id_item = coli.id_item
WHERE col.id_empresa = 1
GROUP BY i.external_id, i.titulo
ORDER BY conversiones DESC
LIMIT 20;

** Funnel simple: mostrados → interés → visita

SELECT
  SUM(CASE WHEN col.event_type='item_interest' THEN 1 ELSE 0 END) AS intereses,
  SUM(CASE WHEN col.event_type='visit_request'  THEN 1 ELSE 0 END) AS visitas
FROM premium_conversion_logs col
WHERE col.id_empresa = 1
  AND col.created_at >= now() - interval '30 days';