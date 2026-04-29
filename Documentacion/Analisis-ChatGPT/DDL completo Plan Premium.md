Necesito que generes el DDL completo para PostgreSQL 15+ a partir del siguiente modelo ER (descrito abajo). 
Quiero un script único SQL que:
1) Cree las tablas con tipos correctos (UUID, JSONB, TEXT, TIMESTAMPTZ).
2) Agregue claves primarias, foráneas, NOT NULL donde corresponda.
3) Agregue índices recomendados (btree + GIN para JSONB + full-text si aplica).
4) Agregue constraints razonables (checks para enums simples, version >= 1, orden >= 0, etc.).
5) Use convención snake_case para nombres de tablas y columnas.
6) Use TIMESTAMPTZ para timestamps.
7) Incluya extensiones necesarias (CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; o gen_random_uuid() con pgcrypto).
8) Incluya ON DELETE apropiado:
   - Si se borra empresa => borrar items, kb_documents, overrides, leads, conversaciones, etc. (CASCADE).
   - Si se borra kb_document => borrar kb_chunks (CASCADE).
   - Si se borra conversacion => borrar mensajes, contextos_conversacion (CASCADE).
   - Para rubros/planes normalmente RESTRICT (o NO ACTION) para evitar borrar en cascada accidental (vos definilo razonablemente).
9) Deje comentarios SQL breves en tablas/columnas clave.

Modelo (tablas y campos):

- rubros:
  - id_rubro (int pk, identity)
  - nombre (text not null unique)
  - descripcion (text)
  - activo (boolean not null default true)
  - created_at, updated_at (timestamptz)

- planes:
  - id_plan (int pk, identity)
  - nombre (text not null unique)
  - followup_habilitado (boolean default false)
  - ia_habilitada (boolean default true)
  - max_leads_mes (int)
  - max_mensajes_mes (int)
  - max_items (int)
  - max_kb_docs (int)
  - created_at, updated_at (timestamptz)

- empresas:
  - id_empresa (int pk, identity)
  - nombre (text not null)
  - id_rubro (int fk rubros)
  - id_plan (int fk planes)
  - permite_followup (boolean default false)
  - activa (boolean default true)
  - timezone (text default 'America/Argentina/Buenos_Aires')
  - created_at, updated_at (timestamptz)
  - unique(nombre) NO es obligatorio (pueden repetirse), pero si proponés un slug o api_key lo podés agregar (opcional) y dejarlo unique.

- items:
  - id_item (uuid pk, default gen_random_uuid())
  - id_empresa (int fk empresas, not null)
  - id_rubro (int fk rubros, not null)
  - tipo (text not null)                 -- ej "inmueble", "auto", "servicio"
  - categoria (text)
  - titulo (text not null)
  - descripcion (text)
  - descripcion_corta (text)
  - precio (numeric)
  - moneda (text)
  - activo (boolean default true)
  - destacado (boolean default false)
  - atributos (jsonb not null default '{}'::jsonb)
  - media (jsonb not null default '{}'::jsonb)
  - created_at, updated_at (timestamptz)

  Índices:
  - (id_empresa, activo)
  - (id_empresa, id_rubro)
  - GIN(atributos)
  - opcional: full text sobre titulo+descripcion

- kb_documents:
  - id_documento (uuid pk, default gen_random_uuid())
  - id_empresa (int fk empresas, not null)
  - id_rubro (int fk rubros, not null)
  - titulo (text not null)
  - contenido_texto (text)     -- puede ser null si se usa storage_url
  - storage_url (text)         -- puede ser null si se usa contenido_texto
  - metadata (jsonb not null default '{}'::jsonb)
  - activo (boolean default true)
  - version (int not null default 1)
  - created_at, updated_at (timestamptz)
  Constraint: CHECK (contenido_texto IS NOT NULL OR storage_url IS NOT NULL)

  Índices:
  - (id_empresa, id_rubro, activo)
  - opcional full text sobre titulo + contenido_texto si no es null

- kb_chunks (opcional pero crearla):
  - id_chunk (uuid pk, default gen_random_uuid())
  - id_documento (uuid fk kb_documents not null)
  - orden (int not null)
  - chunk_texto (text not null)
  - metadata (jsonb not null default '{}'::jsonb)
  - created_at (timestamptz)
  Constraint: UNIQUE(id_documento, orden)
  Índice: (id_documento)

- rubro_schema:
  - id_rubro (int pk + fk rubros)
  - search_mode (text not null) -- 'items_structured' | 'kb_text' | 'mixed'
  - required_keys (jsonb default '[]'::jsonb)
  - facet_keys (jsonb default '[]'::jsonb)
  - validation_rules (jsonb default '{}'::jsonb)
  - updated_at (timestamptz)
  Constraint: CHECK(search_mode IN ('items_structured','kb_text','mixed'))

- rubro_prompts:
  - id_prompt (int pk, identity)
  - id_rubro (int fk rubros not null)
  - system_prompt (text not null)
  - style_prompt (text)
  - tooling_prompt (text)
  - version (int not null default 1)
  - activo (boolean default true)
  - created_at (timestamptz)
  Constraint: UNIQUE(id_rubro, version)
  Constraint: CHECK(version >= 1)

- empresa_prompt_overrides:
  - id_override (int pk, identity)
  - id_empresa (int fk empresas not null)
  - prompt_extra (text)
  - brand_voice (text)
  - activo (boolean default true)
  - created_at, updated_at (timestamptz)
  (si activo=true, idealmente solo 1 override activo por empresa: podés proponer partial unique index)

- leads:
  - id_lead (int pk, identity)
  - id_empresa (int fk empresas not null)
  - nombre (text)
  - telefono (text)
  - email (text)
  - canal (text)    -- 'web' | 'whatsapp' | etc
  - estado (text)   -- 'nuevo' | 'en_proceso' | 'cerrado' | etc
  - metadata (jsonb default '{}'::jsonb)
  - created_at, updated_at (timestamptz)
  Índices:
  - (id_empresa, created_at desc)
  - (id_empresa, estado)

- conversaciones:
  - id_conversacion (int pk, identity)
  - id_lead (int fk leads not null)
  - id_empresa (int fk empresas not null)
  - canal (text not null)
  - inicio (timestamptz)
  - fin (timestamptz)
  - created_at, updated_at (timestamptz)
  Índices:
  - (id_empresa, created_at desc)
  - (id_lead, created_at desc)

- mensajes:
  - id_mensaje (int pk, identity)
  - id_conversacion (int fk conversaciones not null)
  - emisor (text not null)  -- 'user' | 'bot' | 'system'
  - mensaje (text not null)
  - raw_payload (jsonb default '{}'::jsonb)
  - timestamp (timestamptz not null default now())
  Índices:
  - (id_conversacion, timestamp)
  Constraint: CHECK(emisor IN ('user','bot','system'))

- followups:
  - id_followup (int pk, identity)
  - id_lead (int fk leads not null)
  - id_conversacion (int fk conversaciones)
  - tipo (text not null)
  - estado (text not null) -- 'pendiente' | 'enviado' | 'cancelado' | 'fallido'
  - fecha_programada (timestamptz not null)
  - fecha_ejecucion (timestamptz)
  - payload (jsonb default '{}'::jsonb)
  - created_at, updated_at (timestamptz)
  Índices:
  - (fecha_programada) where estado='pendiente'
  - (id_lead, created_at desc)
  Constraint: CHECK(estado IN ('pendiente','enviado','cancelado','fallido'))

- contextos_conversacion:
  - id_contexto (int pk, identity)
  - id_conversacion (int fk conversaciones not null unique)
  - resumen_contexto (text)
  - updated_at (timestamptz)

Además:
- agregá triggers simples para updated_at (opcional) o dejá defaults y aclaralo.
- Generá todo en orden correcto (tablas referenciadas primero).
- El script debe ser ejecutable sin dependencias externas.

Entregable: un único bloque SQL.