# 🗄️ Diseño de Base de Datos — Agente Comercial Inteligente Multirubro (SaaS)

## 🎯 Objetivo
Este documento define el **modelo de datos completo** para un SaaS de agentes comerciales inteligentes:
- Multirubro
- Multiempresa
- Multiplan
- Omnicanal
- Con IA contextual (Claude / LLM)

---

## 🏢 Tabla: empresas
```sql
CREATE TABLE empresas (
    id UUID PRIMARY KEY,
    nombre VARCHAR(100),
    rubro_id UUID,
    plan_id UUID,
    prompt_empresa TEXT,
    activa BOOLEAN DEFAULT true,
    fecha_alta TIMESTAMP,
    fecha_baja TIMESTAMP
);
```

---

## 🏷️ Tabla: rubros
```sql
CREATE TABLE rubros (
    id UUID PRIMARY KEY,
    nombre VARCHAR(50),
    descripcion TEXT,
    prompt_rubro TEXT,
    prompt_restricciones TEXT,
    prompt_ejemplos TEXT,
    activo BOOLEAN DEFAULT true
);
```

---

## 💳 Tabla: planes
```sql
CREATE TABLE planes (
    id UUID PRIMARY KEY,
    nombre VARCHAR(50),
    nivel_followup INT,
    max_tokens_mensuales INT,
    modelo_ia VARCHAR(50),
    permite_historial BOOLEAN,
    canales_habilitados JSONB,
    activo BOOLEAN
);
```

---

## 👤 Tabla: usuarios_finales
```sql
CREATE TABLE usuarios_finales (
    id UUID PRIMARY KEY,
    empresa_id UUID,
    canal VARCHAR(30),
    identificador_externo VARCHAR(100),
    fecha_alta TIMESTAMP
);
```

---

## 💬 Tabla: conversaciones
```sql
CREATE TABLE conversaciones (
    id UUID PRIMARY KEY,
    usuario_id UUID,
    empresa_id UUID,
    canal VARCHAR(30),
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP
);
```

---

## ✉️ Tabla: mensajes
```sql
CREATE TABLE mensajes (
    id UUID PRIMARY KEY,
    conversacion_id UUID,
    rol VARCHAR(20),
    contenido TEXT,
    tokens_usados INT,
    fecha TIMESTAMP
);
```

---

## 🧠 Tabla: prompts
```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY,
    tipo VARCHAR(30),
    referencia_id UUID,
    contenido TEXT,
    version INT,
    activo BOOLEAN,
    fecha_creacion TIMESTAMP
);
```

---

## 📦 Tabla: items_rubro
```sql
CREATE TABLE items_rubro (
    id UUID PRIMARY KEY,
    empresa_id UUID,
    tipo VARCHAR(30),
    datos JSONB,
    activo BOOLEAN
);
```

---

## 📊 Tabla: metricas
```sql
CREATE TABLE metricas (
    id UUID PRIMARY KEY,
    empresa_id UUID,
    fecha DATE,
    tokens_usados INT,
    consultas INT
);
```

---

## 🎯 Conclusión
Diseño preparado para escalar, versionar prompts y controlar costos.
