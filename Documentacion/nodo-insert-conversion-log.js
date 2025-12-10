// ============================================
// NODO CODE: Preparar INSERT para conversion_logs
// Registra solicitudes de visita (leads)
// ============================================

// Obtener datos del webhook de contacto
const webhookData = $input.first().json;
const body = webhookData.body || webhookData;

// Extraer datos del formulario
const nombre = String(body.nombre || 'No especificado');
const telefono = String(body.telefono || 'No especificado');
const disponibilidad = String(body.disponibilidad || 'No especificada');
const source = 'widget'; // Por defecto es widget, cambiar si viene de telegram u otro origen

// Función para escapar comillas simples en strings SQL
function escapeSql(str) {
  if (str === null || str === undefined) return 'NULL';
  return "'" + String(str).replace(/'/g, "''") + "'";
}

// Construir query SQL completo
const query = `INSERT INTO conversion_logs (
  nombre,
  telefono,
  disponibilidad,
  source
) VALUES (
  ${escapeSql(nombre)},
  ${escapeSql(telefono)},
  ${escapeSql(disponibilidad)},
  ${escapeSql(source)}
)`;

return [{
  json: {
    query: query,
    // Pasar datos originales para el siguiente nodo
    nombre: nombre,
    telefono: telefono,
    disponibilidad: disponibilidad,
    source: source
  }
}];

// ============================================
// LUEGO CONECTAR A: Postgres → Execute Query
// Query: ={{ $json.query }}
// ============================================
