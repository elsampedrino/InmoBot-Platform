// ============================================
// PREPARAR ESTADÍSTICAS DE CHAT - VERSIÓN HAIKU + SONNET
// ============================================

// Obtener datos del nodo anterior (Formatear Respuesta)
const formatData = $input.first().json;

// Obtener datos del webhook original
const webhookData = $('Webhook Chat').first().json;
const body = webhookData.body || webhookData;

// Inicializar variables
let tokensHaiku = 0;
let tokensSonnet = 0;
let propIds = [];
let propiedadesMostradas = 0;

// Solo obtener datos de APIs si fue exitoso
if (!formatData.error) {
  try {
    // 1. OBTENER TOKENS DE HAIKU
    const haikuData = $('Haiku - Filtrar Propiedades').first().json;
    if (haikuData?.usage) {
      tokensHaiku = (haikuData.usage.input_tokens || 0) + (haikuData.usage.output_tokens || 0);
    }

    // 2. OBTENER TOKENS DE SONNET
    const sonnetData = $('Sonnet - Respuesta Final').first().json;
    if (sonnetData?.usage) {
      tokensSonnet = (sonnetData.usage.input_tokens || 0) + (sonnetData.usage.output_tokens || 0);
    }

    // 3. OBTENER CANTIDAD DE PROPIEDADES MOSTRADAS (desde formatData que ya lo calculó)
    propiedadesMostradas = formatData.propiedadesMostradas || 0;

    // 4. EXTRAER IDs DE PROPIEDADES desde el nodo Preparar Respuesta Sonnet
    const sonnetPrep = $('Preparar Respuesta Sonnet').first().json;

    // Opción A: Si tiene el array de propiedadesFiltradas, extraer IDs desde ahí
    if (sonnetPrep?.propiedadesFiltradas && Array.isArray(sonnetPrep.propiedadesFiltradas)) {
      propIds = sonnetPrep.propiedadesFiltradas
        .map(p => p.id)
        .filter(id => id);
    }

    // Opción B (fallback): Si no hay propiedades filtradas, intentar extraer desde la respuesta de Haiku
    if (propIds.length === 0 && sonnetPrep?.haikuResponse) {
      const haikuResponse = sonnetPrep.haikuResponse;

      // Si Haiku devolvió IDs (no keywords como GREETING, NO_MATCH, etc.)
      if (haikuResponse &&
          haikuResponse !== 'GREETING' &&
          haikuResponse !== 'NO_MATCH' &&
          haikuResponse !== 'TOO_GENERIC') {

        // Extraer IDs del formato "PROP-001,PROP-004,PROP-007"
        const idsFromHaiku = haikuResponse.split(',').map(id => id.trim());
        propIds = idsFromHaiku;
      }
    }

  } catch (e) {
    // Si hay error obteniendo datos, continuar con valores por defecto
    console.log('Error obteniendo datos de APIs:', e.message);
  }
}

const tokensTotal = tokensHaiku + tokensSonnet;

// Calcular tiempo de respuesta
const startTime = new Date(body.timestamp || Date.now() - 3000);
const endTime = new Date();
const responseTimeMs = Math.round(endTime.getTime() - startTime.getTime());

// Detectar idioma simple
const consulta = body.message || body.consulta || body.query || '';
let idioma = 'es';

if (/\b(apartment|house|property|rent|buy|bedroom|bathroom|looking for)\b/i.test(consulta)) {
  idioma = 'en';
} else if (/\b(apartamento|propriedade|quartos|alugar|comprar|procuro)\b/i.test(consulta)) {
  idioma = consulta.toLowerCase().includes('quarto') ? 'pt' : 'es';
}

// Preparar datos para PostgreSQL
const sessionId = String(body.sessionId || 'unknown');
const consultaLimitada = String(consulta.substring(0, 500));
const idiomaStr = String(idioma);
const successInt = !formatData.error ? 1 : 0;
const errorTypeStr = formatData.errorType ? String(formatData.errorType) : null;
const responseTimeMsInt = parseInt(responseTimeMs, 10);
const tokensHaikuInt = parseInt(tokensHaiku, 10);
const tokensSonnetInt = parseInt(tokensSonnet, 10);
const tokensTotalInt = parseInt(tokensTotal, 10);
const propiedadesMostradasInt = parseInt(propiedadesMostradas, 10);

// Función para escapar comillas simples en strings SQL
function escapeSql(str) {
  if (str === null || str === undefined) return 'NULL';
  return "'" + String(str).replace(/'/g, "''") + "'";
}

// Construir array de propiedades para PostgreSQL
let propiedadesIdsSQL = 'NULL';
if (propIds.length > 0) {
  const escapedProps = propIds.map(p => escapeSql(p)).join(',');
  propiedadesIdsSQL = 'ARRAY[' + escapedProps + ']';
}

// Construir query SQL completo
const query = `INSERT INTO chat_logs (
  session_id, consulta, idioma, success, error_type, response_time_ms,
  tokens_haiku, tokens_sonnet, tokens_total, propiedades_mostradas, propiedades_ids
) VALUES (
  ${escapeSql(sessionId)},
  ${escapeSql(consultaLimitada)},
  ${escapeSql(idiomaStr)},
  ${successInt},
  ${errorTypeStr === null ? 'NULL' : escapeSql(errorTypeStr)},
  ${responseTimeMsInt},
  ${tokensHaikuInt},
  ${tokensSonnetInt},
  ${tokensTotalInt},
  ${propiedadesMostradasInt},
  ${propiedadesIdsSQL}
)`;

return [{
  json: {
    query: query,
    ...formatData,
    // Debug info (opcional, para verificar en N8N)
    _debug: {
      tokensHaiku: tokensHaikuInt,
      tokensSonnet: tokensSonnetInt,
      tokensTotal: tokensTotalInt,
      propiedadesMostradas: propiedadesMostradasInt,
      propIds: propIds
    }
  }
}];
