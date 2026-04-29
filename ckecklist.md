🧭 Roadmap actualizado (priorizado)
🔧 Fase 0 — Cierre técnico inmediato (en curso)
Fix guardado de repositorio (sin hardcodeo)
Ajustes finales de Empresas (servicios + UI)
Validación completa de Importaciones (preview + apply + publish)
Consistencia de textos (“Publicar catálogo”, etc.)

🚀 Fase 1 — Valor inmediato (PRIORIDAD ALTA)
1. Dashboard Admin (simple)
👉 Para vos (control operativo)
empresas activas
importaciones del mes
publicaciones GitHub
actividad reciente
uso por empresa (clave para límites)

2. Dashboard Cliente (MVP)
👉 Para Cristian (percepción de valor)
leads del mes
leads por estado
actividad del bot (conversaciones)
resumen simple (sin analytics complejos)

3. Instagram (🔥 NUEVA PRIORIDAD)
👉 Para impacto comercial directo
Primera versión (simple):
botón “Publicar en Instagram”
usar imágenes + texto de propiedad
publicar manualmente desde panel

Después (si funciona):
templates
multi-post
automatización parcial

🧠 Fase 2 — Robustez del sistema
límites de importaciones por empresa (1–2 por mes)
validaciones de servicios (catalogo_repo, panel_cliente, etc.)
mejoras en logs (más detalle)
errores controlados en publicación/importación

🧪 Fase 3 — Validación real
uso real por Cristian
feedback:
qué usa
qué no entiende
qué le falta
ajustes de UX

📈 Fase 4 — Escalabilidad

4. Onboarding de nuevas inmobiliarias
flujo claro:
crear empresa
configurar repo
crear usuario
habilitar panel

🧠 Fase 5 — Inteligencia (más adelante)
5. KB (Knowledge Base)
ABM de contenido
integración con bot
mejora de respuestas

** CHECKLIST **
BLOQUE 1 — Cierre actual
 Fix guardado config repositorio (sin hardcodeo)
 Validar lectura desde empresas_rubro_catalogos
 Ajustar UI Empresas (servicios + badges)
 Renombrar textos (“Publicar catálogo”)
 Test completo importación:
 preview OK
 apply DB OK
 publish GitHub OK
 log OK

 📊 BLOQUE 2 — Dashboard Admin
 Crear endpoint resumen admin
 Mostrar:
 empresas activas
 importaciones del mes
 publicaciones GitHub
 actividad reciente
 Tabla simple “uso por empresa”

👤 BLOQUE 3 — Dashboard Cliente
 Endpoint métricas cliente
 UI simple con:
 leads del mes
 leads por estado
 conversaciones
 Sin gráficos complejos (solo claridad)

📸 BLOQUE 4 — Instagram (clave)
 Definir formato de post (texto + fotos)
 Endpoint backend publicar IG
 Botón en panel cliente:
 “Publicar en Instagram”
 Usar fotos de Cloudinary
 Test con 1 propiedad real

🧠 BLOQUE 5 — Reglas de negocio
 Contador importaciones por empresa
 Mostrar uso mensual
 (Opcional) warning si supera límite

🧪 BLOQUE 6 — Validación con Cristian
 Le pasa panel completo
 Observás uso real
 Ajustás UX


Creacion de App developer para IG
La arquitectura queda así:


Tu cuenta Meta Developer
└── App "InmoBot" (tuya, una sola vez)
    ├── Cliente BBR → te da permiso → vos obtenés su token
    ├── Cliente Navines → te da permiso → vos obtenés su token
    └── Cliente nuevo → te da permiso → vos obtenés su token
Lo que hace cada cliente: simplemente conectar su Instagram a una Página de Facebook (si no lo tiene) y darte acceso de administrador a esa página por 5 minutos — o directamente mandarte el token si usás el flujo manual.

El flujo real para un cliente nuevo:

Vos tenés la app creada en tu cuenta
El cliente te da acceso admin a su Página de FB (o lo hacés via OAuth en el futuro)
Vos generás el token desde tu Graph API Explorer con los permisos del cliente
Lo cargás en el panel → ficha de empresa → campo Access Token
Listo — el cliente nunca sabe que existe una API
Para arrancar hoy:

Necesitás cuenta en developers.facebook.com con tu usuario de Facebook
Crear la app "InmoBot" una sola vez
¿Querés que te guíe paso a paso por la creación de la app ahora?

