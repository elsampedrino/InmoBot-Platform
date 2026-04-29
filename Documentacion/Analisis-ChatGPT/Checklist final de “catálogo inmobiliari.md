Checklist final de “catálogo inmobiliario”

Te recomiendo dejar documentado (y listo) esto:

1) Constraints/índices imprescindibles

items.external_id NOT NULL ✅

UNIQUE (id_empresa, external_id) como constraint ✅

FK compuesta items(id_empresa,id_rubro) -> empresa_rubros ✅

2) Funciones listas

import_catalogo_inmobiliaria(p_id_empresa, p_id_rubro, p_catalogo jsonb) ✅

export_catalogo_inmobiliaria(p_id_empresa, p_id_rubro) (RETURNS JSON) ✅