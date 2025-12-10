// ============================================
// NODO CODE: Preparar INSERT SQL Directo
// Reemplaza el nodo "Insert rows in a table"
// ============================================

const data = $input.all();

return data.map(item => {
  const d = item.json;

  // Construir query SQL con valores escapados
  const query = `
    INSERT INTO chat_logs (
      session_id,
      consulta,
      idioma,
      success,
      error_type,
      response_time_ms,
      tokens_haiku,
      tokens_sonnet,
      tokens_total,
      propiedades_mostradas,
      propiedades_ids
    ) VALUES (
      $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
    )
  `;

  // Parámetros con tipos correctos
  const params = [
    String(d.session_id),                    // $1 - VARCHAR
    String(d.consulta),                      // $2 - TEXT
    String(d.idioma),                        // $3 - VARCHAR
    parseInt(d.success, 10),                 // $4 - INTEGER
    d.error_type || null,                    // $5 - VARCHAR (nullable)
    parseInt(d.response_time_ms, 10),        // $6 - INTEGER
    parseInt(d.tokens_haiku, 10),            // $7 - INTEGER
    parseInt(d.tokens_sonnet, 10),           // $8 - INTEGER
    parseInt(d.tokens_total, 10),            // $9 - INTEGER
    parseInt(d.propiedades_mostradas, 10),   // $10 - INTEGER
    d.propiedades_ids || []                  // $11 - TEXT[] (array)
  ];

  return {
    json: {
      query: query,
      params: params
    }
  };
});

// ============================================
// LUEGO USAR NODO: Postgres → Execute Query
// ============================================
// En el nodo Postgres, usar:
// Query: {{ $json.query }}
// Query Parameters: {{ JSON.stringify($json.params) }}
// ============================================
