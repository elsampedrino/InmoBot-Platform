"""
seed_saas_inmobot.py — Seed completo del rubro saas_inmobot para InmoBot Platform.

Crea:
  1. Rubro 'saas_inmobot' en la tabla rubros
  2. Asociación empresa_rubros (id_empresa=2, es_default=False)
  3. RubroSchema (search_mode='kb_text', sin facets de catálogo)
  4. RubroPrompt (asistente comercial InmoBot)
  5. KB: 10 documentos temáticos, ~50 chunks

Uso:
  cd API-Premium
  python -m Scripts-Templates.seed_saas_inmobot
  # o desde raíz del repo:
  python Scripts-Templates/seed_saas_inmobot.py

Variables de entorno necesarias:
  DATABASE_URL=postgresql+asyncpg://...
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Asegurar que el módulo app sea importable
sys.path.insert(0, str(Path(__file__).parent.parent / "API-Premium"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://inmobot_db_6c3z_user:uBoJyXtnzgjvH8cDxHIDjCM8N3Jxzwbo@dpg-d0i9e4buibrs73a7l7og-a.oregon-postgres.render.com/inmobot_db_6c3z",
)

ID_EMPRESA_INMOBOT_PLATFORM = 2


# ─── PROMPT ESPECIALIZADO ────────────────────────────────────────────────────

SYSTEM_PROMPT = """Sos el asistente comercial digital de InmoBot, una plataforma que automatiza la atención al cliente para inmobiliarias y negocios con catálogos digitales.

Tu rol es el de un asesor consultivo, no un vendedor. No presionás, no insistís, no hacés promesas que no podés cumplir. Ayudás al visitante a entender si InmoBot es la solución correcta para su negocio.

TONO: profesional, claro, cercano. Hablás de vos a vos (voseo rioplatense). Conciso: respuestas de 2-4 párrafos máximo, sin listas innecesarias.

ROL:
- Explicás funcionalidades y planes con claridad
- Comparás planes según el caso puntual del visitante
- Resolvés objeciones con argumentos concretos y casos reales
- Detectás interés comercial genuino
- Promovés demos cuando hay señales de interés (pero solo una vez por conversación)
- Derivás a WhatsApp cuando el visitante quiere seguir la conversación con alguien del equipo

CAPTURA DE INTERÉS:
Si el visitante hace preguntas sobre precios, implementación, integraciones o casos de uso, ese es interés real. En ese contexto, luego de responder su pregunta, podés sugerir una demo o continuar por WhatsApp, pero solo cuando sea natural — nunca de forma forzada.

LÍMITES:
- No inventés precios, fechas ni funcionalidades que no estén en tu base de conocimiento
- Si no tenés un dato, decís: "No tengo ese detalle en este momento, pero lo podemos resolver directamente con el equipo por WhatsApp"
- Nunca prometés descuentos, acuerdos especiales ni tiempos exactos de implementación sin confirmación

BASE DE CONOCIMIENTO:
Cuando respondas preguntas sobre planes, precios, funcionalidades, implementación u objeciones, basate en los documentos de tu base de conocimiento. Si no encontrás información relevante, respondé con lo que sabés y ofrecé continuar la conversación por WhatsApp."""

STYLE_PROMPT = """Estilo de comunicación:
- Voseo rioplatense en todos los mensajes
- Sin emojis ni signos de exclamación excesivos
- Respuestas directas, sin introducción innecesaria
- Cuando hay una lista de puntos, usá guiones, no numeración
- Terminá cada respuesta sustancial con una pregunta o CTA natural, nunca con "¿Hay algo más en lo que pueda ayudarte?"
- Si el visitante muestra interés, mencioná la posibilidad de demo UNA sola vez"""


# ─── BASE DE CONOCIMIENTO ────────────────────────────────────────────────────

KB_DOCUMENTS = [

    # ── PLANES Y PRECIOS ──────────────────────────────────────────────────────
    {
        "titulo": "PLANES_Y_PRECIOS",
        "chunks": [
            {
                "orden": 1,
                "texto": """InmoBot tiene tres planes: Básico, Pro y Premium.

El plan Básico incluye el chatbot web embebido en la landing de la inmobiliaria, respuesta automática 24/7 a consultas sobre propiedades, y notificaciones por email cuando se genera un lead. Es el punto de entrada ideal para inmobiliarias que quieren empezar a automatizar sin complejidad.

El plan Pro agrega integraciones más avanzadas y mayor capacidad de personalización del bot. Incluye todo lo del Básico más opciones de configuración de tono y flujos de conversación.

El plan Premium es la solución completa: incluye el panel de administración online para gestionar propiedades, dashboard de métricas, integración con WhatsApp para derivación a asesores, publicación automática en Instagram y Facebook, y el sistema de captura de leads más avanzado. Es el plan recomendado para inmobiliarias que quieren digitalizar toda la operación comercial.""",
                "metadata": {"categoria": "planes", "subtema": "resumen_planes"},
            },
            {
                "orden": 2,
                "texto": """InmoBot no tiene precios fijos publicados. Cada propuesta se arma en base a un análisis preliminar de la inmobiliaria: cantidad de propiedades, volumen estimado de consultas, integraciones necesarias y nivel de automatización deseado.

Para recibir una propuesta personalizada, la mejor forma es agendar una demo breve donde el equipo evalúa el caso y presenta una propuesta a medida sin compromiso.

No hay contratos de largo plazo — la suscripción es mes a mes y se puede cancelar en cualquier momento.""",
                "metadata": {"categoria": "planes", "subtema": "precios"},
            },
            {
                "orden": 3,
                "texto": """Comparativa rápida de planes:

Plan Básico:
- Chatbot web en tu landing
- Respuesta automática 24/7
- Notificaciones por email de leads
- Sin panel de administración

Plan Pro:
- Todo lo del Básico
- Personalización avanzada del bot
- Mayor capacidad de configuración

Plan Premium:
- Todo lo del Pro
- Panel de administración online de propiedades
- Dashboard con métricas y conversiones
- Derivación automática a WhatsApp con asesores
- Publicación en Instagram y Facebook (próximamente disponible)
- Captura inteligente de leads con contexto conversacional
- Soporte prioritario""",
                "metadata": {"categoria": "planes", "subtema": "comparativa"},
            },
        ],
    },

    # ── FUNCIONALIDADES CORE ──────────────────────────────────────────────────
    {
        "titulo": "FUNCIONALIDADES_CORE",
        "chunks": [
            {
                "orden": 1,
                "texto": """El chatbot de InmoBot responde consultas de forma automática las 24 horas, los 7 días de la semana. No importa si el visitante llega a las 3 de la mañana o un domingo feriado: recibe respuestas precisas sobre propiedades disponibles, precios, características y ubicación.

El bot utiliza inteligencia artificial para entender el lenguaje natural. No es un menú de opciones ni un árbol de decisión: el visitante escribe como hablaría con una persona y el bot interpreta su consulta, refina la búsqueda y muestra las propiedades más relevantes.""",
                "metadata": {"categoria": "funcionalidades", "subtema": "chatbot_ia"},
            },
            {
                "orden": 2,
                "texto": """El widget de InmoBot se instala en cualquier sitio web con un solo snippet de código. No requiere cambiar el diseño del sitio ni contratar un desarrollador.

Es compatible con Wix, WordPress, sitios HTML personalizados, y cualquier plataforma que permita agregar código JavaScript. La instalación típica tarda menos de 10 minutos.""",
                "metadata": {"categoria": "funcionalidades", "subtema": "instalacion_widget"},
            },
            {
                "orden": 3,
                "texto": """InmoBot captura leads de forma automática durante la conversación. Cuando el visitante muestra interés real (pide un asesor, deja sus datos, consulta sobre una propiedad específica), el sistema registra un lead con nombre, teléfono, email y las propiedades que consultó.

Todos los leads quedan disponibles en el panel de administración con historial completo de la conversación. El equipo de ventas puede hacer seguimiento sin perder contexto.""",
                "metadata": {"categoria": "funcionalidades", "subtema": "captura_leads"},
            },
        ],
    },

    # ── FUNCIONALIDADES PREMIUM ───────────────────────────────────────────────
    {
        "titulo": "FUNCIONALIDADES_PREMIUM",
        "chunks": [
            {
                "orden": 1,
                "texto": """El panel de administración online (Plan Premium) permite gestionar todo el catálogo de propiedades desde el navegador, sin necesidad de acceder a archivos o código.

Desde el panel se puede:
- Agregar, editar o desactivar propiedades
- Subir fotos (se guardan en Cloudinary automáticamente)
- Marcar propiedades como destacadas
- Publicar cambios en la landing con un solo clic
- Ver el catálogo completo con filtros

Los cambios se reflejan en la landing en menos de 2 minutos gracias al sistema de deploy automático.""",
                "metadata": {"categoria": "funcionalidades_premium", "subtema": "panel_admin"},
            },
            {
                "orden": 2,
                "texto": """El dashboard de métricas (Plan Premium) muestra en tiempo real el rendimiento del bot y la generación de leads.

Se puede ver:
- Cantidad de conversaciones iniciadas
- Tasa de captura de leads
- Propiedades más consultadas
- Horarios de mayor actividad
- Conversiones por canal (web, WhatsApp)

Esta información permite tomar decisiones sobre qué propiedades destacar, en qué horarios activar campañas y qué consultas están quedando sin respuesta adecuada.""",
                "metadata": {"categoria": "funcionalidades_premium", "subtema": "dashboard"},
            },
            {
                "orden": 3,
                "texto": """El contexto conversacional (Plan Premium) hace que el bot recuerde lo que el visitante buscó antes dentro de la misma sesión.

Si el visitante primero buscó "departamento en Palermo 2 dormitorios" y luego pregunta "¿tiene cochera?", el bot entiende que está preguntando sobre la propiedad que ya estaba viendo — no empieza de cero.

Esto genera una experiencia de búsqueda mucho más natural y reduce la frustración del visitante.""",
                "metadata": {"categoria": "funcionalidades_premium", "subtema": "contexto_conversacional"},
            },
        ],
    },

    # ── WHATSAPP ──────────────────────────────────────────────────────────────
    {
        "titulo": "WHATSAPP_HANDOFF",
        "chunks": [
            {
                "orden": 1,
                "texto": """La derivación a WhatsApp (Plan Premium) permite que el bot pase la conversación a un asesor humano cuando el visitante está listo para hablar con alguien del equipo.

El flujo es automático: cuando el bot detecta una señal de interés alta (el visitante pide hablar con un asesor, deja sus datos o hace una pregunta que requiere atención personalizada), muestra un botón directo a WhatsApp del número de la inmobiliaria.

El asesor recibe el mensaje con el nombre del contacto y las propiedades que consultó, para poder dar seguimiento sin pedir que repita todo desde cero.""",
                "metadata": {"categoria": "whatsapp", "subtema": "handoff"},
            },
            {
                "orden": 2,
                "texto": """El número de WhatsApp para derivación se configura en el panel de administración. Se puede tener un solo número para toda la inmobiliaria o configurar números distintos por asesor.

El agente recibe el mensaje en formato: "Hola [nombre del asesor], soy [nombre del visitante]. Estuve consultando sobre [propiedad X] en InmoBot y me interesa saber más."

No requiere WhatsApp Business API ni ninguna integración externa — funciona directamente con links wa.me.""",
                "metadata": {"categoria": "whatsapp", "subtema": "configuracion"},
            },
        ],
    },

    # ── INTEGRACIONES ─────────────────────────────────────────────────────────
    {
        "titulo": "INTEGRACIONES",
        "chunks": [
            {
                "orden": 1,
                "texto": """InmoBot se integra con Instagram y Facebook para publicar propiedades automáticamente desde el panel de administración (disponible en Plan Premium).

Con un solo clic desde la ficha de una propiedad, se genera y publica una imagen con los datos principales en el perfil de Instagram y/o la página de Facebook de la inmobiliaria.

Se usa la API oficial de Meta (Instagram Graph API y Facebook Graph API). No requiere terceros ni herramientas adicionales. Solo se necesita conectar una vez la cuenta de Instagram/Facebook en el panel.""",
                "metadata": {"categoria": "integraciones", "subtema": "instagram_facebook"},
            },
            {
                "orden": 2,
                "texto": """Las fotos de propiedades en InmoBot se almacenan en Cloudinary, un servicio de CDN especializado en imágenes.

Esto significa que las fotos se optimizan automáticamente (formato, resolución, peso), se sirven rápido en cualquier dispositivo y no consumen espacio en el servidor del cliente.

El upload de fotos se hace directamente desde el panel de administración, sin necesidad de un servicio externo.""",
                "metadata": {"categoria": "integraciones", "subtema": "cloudinary"},
            },
            {
                "orden": 3,
                "texto": """El catálogo de propiedades de InmoBot se publica en la landing vía GitHub y Vercel.

Cuando se hace clic en "Publicar catálogo" desde el panel, los datos se envían a un repositorio en GitHub. Vercel detecta el cambio automáticamente y hace el redeploy de la landing en menos de 2 minutos.

Este flujo garantiza que la landing siempre esté actualizada sin intervención manual y sin costos de hosting por actualizaciones frecuentes.""",
                "metadata": {"categoria": "integraciones", "subtema": "github_vercel"},
            },
        ],
    },

    # ── IMPLEMENTACIÓN ────────────────────────────────────────────────────────
    {
        "titulo": "IMPLEMENTACION",
        "chunks": [
            {
                "orden": 1,
                "texto": """La implementación de InmoBot tiene dos partes: la configuración inicial y la puesta en producción.

La configuración inicial incluye:
- Carga del catálogo de propiedades (desde Excel o manual)
- Configuración del bot (tono, presentación, respuestas clave)
- Instalación del widget en el sitio web del cliente
- Configuración de notificaciones (email, WhatsApp)

El tiempo estimado es de 3 a 7 días hábiles desde que se entregan los materiales necesarios.""",
                "metadata": {"categoria": "implementacion", "subtema": "proceso"},
            },
            {
                "orden": 2,
                "texto": """Para implementar InmoBot no es necesario cambiar el sitio web ni contratar un desarrollador.

El widget se instala copiando un snippet de código en el HTML del sitio. Si el cliente no tiene acceso técnico al sitio, el equipo de InmoBot puede coordinarlo con el proveedor web.

Tampoco se necesita un servidor propio: toda la infraestructura (API, base de datos, almacenamiento de fotos, CDN) es de InmoBot.""",
                "metadata": {"categoria": "implementacion", "subtema": "requisitos"},
            },
            {
                "orden": 3,
                "texto": """El catálogo inicial de propiedades se puede cargar de dos formas:
1. Desde un archivo Excel con el formato estándar de InmoBot
2. Manual, desde el panel de administración

Si la inmobiliaria ya tiene un portal web (Argenprop, Zonaprop, etc.) con su catálogo publicado, el equipo de InmoBot puede analizar si hay una forma de importarlo automáticamente.

Una vez configurado, la gestión del catálogo la hace el propio cliente desde el panel, sin depender del equipo técnico de InmoBot.""",
                "metadata": {"categoria": "implementacion", "subtema": "catalogo"},
            },
        ],
    },

    # ── DIFERENCIADORES ───────────────────────────────────────────────────────
    {
        "titulo": "DIFERENCIADORES",
        "chunks": [
            {
                "orden": 1,
                "texto": """¿En qué se diferencia InmoBot de un chatbot genérico?

Un chatbot genérico (como los que vienen con ManyChat, Tidio o ChatGPT plugins) responde preguntas con texto libre pero no entiende un catálogo de propiedades.

InmoBot está diseñado específicamente para inmobiliarias: entiende tipos de propiedades, zonas, precios, rangos, y puede buscar en el catálogo real del cliente y mostrar los resultados con fotos, precio y características. No es un FAQ automático — es un buscador inteligente integrado al inventario.""",
                "metadata": {"categoria": "diferenciadores", "subtema": "vs_chatbot_generico"},
            },
            {
                "orden": 2,
                "texto": """¿Por qué InmoBot vs atender WhatsApp manualmente?

Atender WhatsApp manualmente tiene un techo: no se puede responder a las 3am, no se puede atender 10 personas al mismo tiempo, y la calidad de respuesta depende de quién esté disponible.

InmoBot responde en segundos a cualquier hora, siempre con la misma calidad, y solo deriva a un humano cuando hay interés real. El asesor recibe leads ya calificados, no personas que simplemente quieren saber si "hay algo en Palermo".""",
                "metadata": {"categoria": "diferenciadores", "subtema": "vs_whatsapp_manual"},
            },
            {
                "orden": 3,
                "texto": """InmoBot fue construido para el mercado inmobiliario argentino.

Esto significa que el bot habla en voseo rioplatense, entiende términos locales (ambientes, cochera, PH, monoambiente), maneja precios en pesos y dólares, y está adaptado a la forma en que los argentinos buscan propiedades.

No es una herramienta genérica traducida: es una plataforma construida desde cero para este contexto.""",
                "metadata": {"categoria": "diferenciadores", "subtema": "mercado_local"},
            },
        ],
    },

    # ── OBJECIONES ────────────────────────────────────────────────────────────
    {
        "titulo": "OBJECIONES",
        "chunks": [
            {
                "orden": 1,
                "texto": """Objeción: "Es caro para lo que tenemos"

El costo de InmoBot hay que compararlo con el costo de atender consultas manualmente. Una inmobiliaria con 50 consultas mensuales por WhatsApp gasta en promedio 8-10 horas del tiempo de un asesor solo en responder preguntas básicas.

InmoBot automatiza esas respuestas básicas y deja al asesor libre para cerrar operaciones. La inversión típica se recupera en el primer mes si se cierra aunque sea una operación adicional gracias a un lead capturado fuera de horario.""",
                "metadata": {"categoria": "objeciones", "subtema": "precio"},
            },
            {
                "orden": 2,
                "texto": """Objeción: "No sé si mis clientes van a usar un bot"

El bot no se presenta como un robot: tiene nombre, responde en lenguaje natural y el visitante muchas veces no sabe si está hablando con una persona o un sistema automatizado.

Además, el bot está disponible cuando el asesor no lo está. Muchas consultas inmobiliarias se generan de noche o en fin de semana. Sin un sistema automático, esas consultas se pierden o se responden tarde.""",
                "metadata": {"categoria": "objeciones", "subtema": "adopcion_clientes"},
            },
            {
                "orden": 3,
                "texto": """Objeción: "Mi web es vieja / no tengo sitio web"

InmoBot incluye la opción de armar una landing page específica para la inmobiliaria. Si el cliente no tiene sitio web o tiene uno desactualizado, el equipo puede crear una landing moderna, rápida y optimizada para buscadores como parte del servicio.

El widget también se puede instalar en sitios muy simples, sin necesidad de un CMS moderno.""",
                "metadata": {"categoria": "objeciones", "subtema": "web_vieja"},
            },
            {
                "orden": 4,
                "texto": """Objeción: "Necesito contratar un técnico o programador"

No. La implementación la hace el equipo de InmoBot. El cliente no necesita conocimientos técnicos para usar el panel de administración, agregar propiedades, publicar en redes sociales o revisar las métricas.

Si en algún momento hay que tocar algo técnico (como instalar el widget en un CMS particular), el equipo lo coordina directamente.""",
                "metadata": {"categoria": "objeciones", "subtema": "barrera_tecnica"},
            },
            {
                "orden": 5,
                "texto": """Objeción: "Ya tengo WhatsApp Business, no necesito esto"

WhatsApp Business es una herramienta de comunicación, no un sistema de automatización de consultas. Con WhatsApp Business todavía necesitás que alguien lea los mensajes y responda.

InmoBot no reemplaza WhatsApp: se integra con él. El bot captura la consulta, identifica si hay interés real, y ahí sí deriva la conversación a WhatsApp para que el asesor cierre la operación.""",
                "metadata": {"categoria": "objeciones", "subtema": "whatsapp_business"},
            },
            {
                "orden": 6,
                "texto": """Objeción: "¿Sirve para inmobiliarias chicas?"

InmoBot es especialmente útil para inmobiliarias pequeñas y unipersonales. Una persona sola no puede responder consultas las 24 horas ni atender 5 conversaciones al mismo tiempo.

Varias inmobiliarias de 1 a 3 personas usan InmoBot para responder fuera de horario, capturar leads mientras duermen y publicar en redes sin esfuerzo manual. El tiempo que se libera se invierte en cerrar operaciones.""",
                "metadata": {"categoria": "objeciones", "subtema": "inmobiliaria_chica"},
            },
        ],
    },

    # ── CASOS DE USO ──────────────────────────────────────────────────────────
    {
        "titulo": "CASOS_DE_USO",
        "chunks": [
            {
                "orden": 1,
                "texto": """BBR Grupo Inmobiliario (Mendoza) utiliza InmoBot en su landing para responder consultas sobre su catálogo de propiedades. El bot está configurado con el catálogo completo de la inmobiliaria y responde preguntas sobre disponibilidad, precios y características.

El flujo de captura de leads está activo: cuando un visitante muestra interés concreto, el sistema registra sus datos y los notifica al asesor via email y WhatsApp en tiempo real.""",
                "metadata": {"categoria": "casos_de_uso", "subtema": "bbr"},
            },
            {
                "orden": 2,
                "texto": """Casos de uso frecuentes de InmoBot en inmobiliarias:

- Responder preguntas fuera de horario (noche, fin de semana, feriados)
- Filtrar propiedades por zona, tipo y precio sin intervención del asesor
- Capturar datos de contacto de visitantes interesados
- Publicar automáticamente en Instagram cuando se suma una propiedad nueva
- Notificar al asesor cuando hay un lead calificado listo para seguimiento
- Mantener el catálogo actualizado desde el panel sin tocar el sitio web""",
                "metadata": {"categoria": "casos_de_uso", "subtema": "usos_frecuentes"},
            },
        ],
    },

    # ── DEMO Y CONTACTO ───────────────────────────────────────────────────────
    {
        "titulo": "DEMO_Y_CONTACTO",
        "chunks": [
            {
                "orden": 1,
                "texto": """La demo de InmoBot es una reunión breve (30-45 min) por videollamada donde el equipo muestra el producto en funcionamiento y puede responder preguntas específicas del negocio.

En la demo se puede ver:
- El bot respondiendo consultas en vivo con el catálogo del cliente (si lo envía antes)
- El panel de administración completo
- El flujo de captura de leads
- Las integraciones disponibles

No hay compromiso ni costo asociado a la demo.""",
                "metadata": {"categoria": "demo", "subtema": "que_incluye"},
            },
            {
                "orden": 2,
                "texto": """Para agendar una demo o hacer consultas comerciales, la forma más rápida es escribir directamente por WhatsApp al equipo de InmoBot.

También se puede completar el formulario de contacto en automatizacionia.com.ar.

El equipo suele responder en el mismo día hábil.""",
                "metadata": {"categoria": "demo", "subtema": "como_contactar"},
            },
        ],
    },

    # ── FAQ ───────────────────────────────────────────────────────────────────
    {
        "titulo": "FAQ",
        "chunks": [
            {
                "orden": 1,
                "texto": """Preguntas frecuentes sobre InmoBot:

¿Necesito cambiar mi sitio web?
No. El widget se instala en cualquier sitio web existente con un snippet de código.

¿Cuánto tarda la implementación?
Entre 3 y 7 días hábiles, dependiendo de la complejidad del catálogo.

¿El bot habla en español argentino?
Sí. Está configurado con voseo rioplatense y entiende términos locales del mercado inmobiliario.

¿Puedo cambiar las propiedades yo mismo?
Sí, desde el panel de administración (Plan Premium) podés agregar, editar y desactivar propiedades sin intervención técnica.

¿Funciona en celular?
Sí. El widget está optimizado para dispositivos móviles. También el panel de administración es responsive.""",
                "metadata": {"categoria": "faq", "subtema": "general"},
            },
            {
                "orden": 2,
                "texto": """Más preguntas frecuentes:

¿InmoBot solo sirve para inmobiliarias?
La plataforma está especializada en inmobiliarias, pero la arquitectura multi-rubro permite adaptarla a automotoras, turismo y otros negocios con catálogos. Consultá disponibilidad.

¿Qué pasa si el visitante hace una pregunta que el bot no sabe responder?
El bot está diseñado para reconocer cuando no tiene la información y sugerir continuar la conversación con un asesor, sin inventar respuestas.

¿Puedo probar InmoBot antes de contratar?
Sí. La demo incluye una prueba en vivo del sistema. También podés ver el bot funcionando en automatizacionia.com.ar.

¿Hay contratos anuales?
No. La suscripción es mensual y se puede cancelar en cualquier momento.""",
                "metadata": {"categoria": "faq", "subtema": "producto_contrato"},
            },
        ],
    },
]


# ─── SEED ────────────────────────────────────────────────────────────────────

async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():

            # 1. Crear rubro saas_inmobot
            result = await session.execute(
                text("SELECT id_rubro FROM rubros WHERE slug = 'saas_inmobot'")
            )
            existing = result.scalar_one_or_none()

            if existing:
                id_rubro = existing
                print(f"[OK] Rubro saas_inmobot ya existe (id={id_rubro})")
            else:
                result = await session.execute(
                    text("""
                        INSERT INTO rubros (nombre, slug, descripcion, activo)
                        VALUES ('SaaS InmoBot', 'saas_inmobot', 'Asistente comercial de InmoBot Platform', true)
                        RETURNING id_rubro
                    """)
                )
                id_rubro = result.scalar_one()
                print(f"[OK] Rubro saas_inmobot creado (id={id_rubro})")

            # 2. Asociar a empresa id=2
            result = await session.execute(
                text("""
                    SELECT 1 FROM empresa_rubros
                    WHERE id_empresa = :emp AND id_rubro = :rub
                """),
                {"emp": ID_EMPRESA_INMOBOT_PLATFORM, "rub": id_rubro},
            )
            if not result.scalar_one_or_none():
                await session.execute(
                    text("""
                        INSERT INTO empresa_rubros (id_empresa, id_rubro, activo, es_default)
                        VALUES (:emp, :rub, true, false)
                    """),
                    {"emp": ID_EMPRESA_INMOBOT_PLATFORM, "rub": id_rubro},
                )
                print(f"[OK] empresa_rubros: empresa 2 <-> rubro {id_rubro}")
            else:
                print(f"[OK] empresa_rubros ya existía")

            # 3. RubroSchema (kb_text: sin catálogo de items)
            result = await session.execute(
                text("SELECT 1 FROM rubro_schema WHERE id_rubro = :rub"),
                {"rub": id_rubro},
            )
            if not result.scalar_one_or_none():
                await session.execute(
                    text("""
                        INSERT INTO rubro_schema (id_rubro, search_mode, required_keys, facet_keys, validation_rules)
                        VALUES (:rub, 'kb_text', '[]'::jsonb, '[]'::jsonb, '{}'::jsonb)
                    """),
                    {"rub": id_rubro},
                )
                print("[OK] RubroSchema creado (search_mode=kb_text)")
            else:
                print("[OK] RubroSchema ya existía")

            # 4. RubroPrompt
            result = await session.execute(
                text("SELECT 1 FROM rubro_prompts WHERE id_rubro = :rub AND activo = true"),
                {"rub": id_rubro},
            )
            if not result.scalar_one_or_none():
                await session.execute(
                    text("""
                        INSERT INTO rubro_prompts (id_rubro, system_prompt, style_prompt, version, activo)
                        VALUES (:rub, :sys, :sty, 1, true)
                    """),
                    {"rub": id_rubro, "sys": SYSTEM_PROMPT, "sty": STYLE_PROMPT},
                )
                print("[OK] RubroPrompt creado")
            else:
                print("[OK] RubroPrompt ya existía (no reemplazado)")

            # 5. Slug para rubro existente inmobiliaria (id=1) si no tiene slug
            await session.execute(
                text("""
                    UPDATE rubros SET slug = 'inmobiliaria_demo'
                    WHERE id_rubro = 1 AND slug IS NULL
                """)
            )
            print("[OK] slug 'inmobiliaria_demo' asignado a rubro id=1 (si no tenía)")

            # 6. KB Documents + Chunks
            total_chunks = 0
            for doc in KB_DOCUMENTS:
                # Verificar si ya existe
                result = await session.execute(
                    text("""
                        SELECT id_documento FROM kb_documents
                        WHERE id_empresa = :emp AND id_rubro = :rub AND titulo = :titulo
                    """),
                    {"emp": ID_EMPRESA_INMOBOT_PLATFORM, "rub": id_rubro, "titulo": doc["titulo"]},
                )
                existing_doc = result.scalar_one_or_none()

                if existing_doc:
                    print(f"  [SKIP] Documento '{doc['titulo']}' ya existe, omitido")
                    continue

                doc_result = await session.execute(
                    text("""
                        INSERT INTO kb_documents (id_empresa, id_rubro, titulo, contenido_texto, metadata, activo)
                        VALUES (:emp, :rub, :titulo, '', '{}'::jsonb, true)
                        RETURNING id_documento
                    """),
                    {"emp": ID_EMPRESA_INMOBOT_PLATFORM, "rub": id_rubro, "titulo": doc["titulo"]},
                )
                id_documento = doc_result.scalar_one()

                for chunk in doc["chunks"]:
                    await session.execute(
                        text("""
                            INSERT INTO kb_chunks (id_documento, orden, chunk_texto, metadata)
                            VALUES (:doc, :orden, :texto, CAST(:meta AS jsonb))
                        """),
                        {
                            "doc": id_documento,
                            "orden": chunk["orden"],
                            "texto": chunk["texto"],
                            "meta": json.dumps(chunk["metadata"]),
                        },
                    )
                    total_chunks += 1

                print(f"  [OK] '{doc['titulo']}': {len(doc['chunks'])} chunks")

            print(f"\n[DONE] Seed completado. {total_chunks} chunks de KB insertados.")
            print(f"   id_rubro saas_inmobot = {id_rubro}")
            print(f"   Para usar el asistente comercial, el widget debe enviar:")
            print(f'   {{ "rubroSlug": "saas_inmobot", "message": "...", "sessionId": "..." }}')

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
