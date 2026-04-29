
# InmoBot Premium – Modelo de Configuración Multi‑Tenant
Versión: 0.1

Este documento define cómo InmoBot maneja **múltiples empresas (tenants)** dentro del mismo sistema.

---

# 1. Objetivo

Permitir que múltiples empresas utilicen el sistema compartiendo infraestructura
pero manteniendo aislamiento de:

- datos
- catálogo
- prompts
- analítica

---

# 2. Entidad principal: Empresa

Tabla: `empresas`

Cada empresa representa un cliente del SaaS.

Datos clave:

- nombre
- plan
- timezone
- slug
- configuración general

---

# 3. Planes

Tabla: `planes`

Define capacidades:

- límite de leads
- límite de mensajes
- followups habilitados
- IA habilitada
- cantidad máxima de items

Esto permite diferenciar planes:

- Starter
- Pro
- Premium

---

# 4. Rubros habilitados

Tabla: `empresa_rubros`

Una empresa puede operar en distintos rubros.

Ejemplo:

Inmobiliaria
Autos
Hoteles

---

# 5. Personalización de prompts

Tablas:

- rubro_prompts
- empresa_prompt_overrides

Esto permite que cada empresa tenga:

- voz de marca
- instrucciones específicas
- reglas comerciales

---

# 6. Configuración específica de empresa

Ejemplo:

```json
{
  "brand_voice": "formal",
  "cta_mode": "soft",
  "max_items_per_response": 3,
  "timezone": "America/Argentina/Buenos_Aires"
}
```

---

# 7. Aislamiento de datos

Todas las tablas deben filtrar por:

id_empresa

Esto garantiza que:

- una empresa no vea datos de otra
- analítica esté separada
- catálogos estén aislados

---

# 8. Analítica por tenant

Las métricas deben poder calcularse por:

empresa
rubro
canal

Esto permite dashboards individuales para cada cliente.

---

# 9. Escalabilidad multi‑tenant

El diseño actual permite:

- miles de empresas
- millones de conversaciones
- catálogos independientes

Sin necesidad de bases separadas.

---

# 10. Futuras extensiones

Configuración avanzada por empresa:

- reglas de negocio
- límites personalizados
- integraciones externas
- CRM

---

# 11. Objetivo final

El modelo multi‑tenant permite que InmoBot sea un verdadero **SaaS escalable**,
donde cada empresa tiene su propia experiencia personalizada
sin duplicar infraestructura.

---

Fin del documento.
