"""
Seed de Knowledge Base para BBR Grupo Inmobiliario.

Inserta documentos institucionales en kb_documents + kb_chunks.

Uso:
    cd API-Premium
    python scripts/seed_kb_bbr.py                 # inserta/actualiza
    python scripts/seed_kb_bbr.py --dry-run       # solo muestra

Documentos incluidos:
    - comisiones_honorarios
    - documentacion_requerida
    - proceso_compra
    - proceso_alquiler
    - tasaciones_valuaciones
    - horarios_contacto
    - formas_de_pago
"""
import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg

from app.core.config import settings

# ─── Configuración del tenant BBR ─────────────────────────────────────────────
EMPRESA_SLUG = "cristian-inmob"

# ─── Contenido de la Knowledge Base ───────────────────────────────────────────
# Cada documento tiene: titulo, chunks (lista de textos)
# Los chunks se dividen para optimizar la búsqueda FTS.

KB_DOCUMENTS = [
    {
        "titulo": "Comisiones y Honorarios",
        "chunks": [
            (
                "BBR Grupo Inmobiliario cobra una comisión estándar del 3% del valor de la operación "
                "para ventas, pagado por cada parte (comprador y vendedor). En operaciones de alquiler, "
                "la comisión equivale a un mes de alquiler más IVA, a cargo del inquilino."
            ),
            (
                "Para desarrollos y lotes, la comisión puede variar entre el 3% y el 5% según el tipo "
                "de operación y acuerdo previo. En todos los casos la comisión se abona al momento de "
                "la firma de la escritura o contrato definitivo. No hay costos ocultos ni cargos adicionales "
                "por gestión o asesoramiento."
            ),
            (
                "En operaciones de alquiler comercial, la comisión es de dos meses de alquiler más IVA. "
                "Los honorarios por tasación de propiedades son gratuitos para clientes que operan con BBR. "
                "Para tasaciones sin operación posterior, consultar valor vigente."
            ),
        ],
    },
    {
        "titulo": "Documentación Requerida para Compraventa",
        "chunks": [
            (
                "Para iniciar el proceso de compraventa, el vendedor debe presentar: título de propiedad "
                "original, DNI del/los titulares, boleta de servicios al día (luz, gas, agua), "
                "libre deuda de expensas (si aplica) y libre deuda municipal."
            ),
            (
                "El comprador debe presentar: DNI vigente, CUIL/CUIT, constancia de ingresos o fuente de fondos "
                "según el monto de la operación. Para montos superiores a USD 100.000 puede requerirse "
                "declaración jurada de origen de fondos según normativa AFIP."
            ),
            (
                "En caso de sucesión, herencia o inmueble con múltiples titulares, se requiere documentación "
                "adicional: declaratoria de herederos o poder notarial según corresponda. "
                "El escribano interviniente guiará el proceso caso a caso."
            ),
        ],
    },
    {
        "titulo": "Documentación Requerida para Alquiler",
        "chunks": [
            (
                "Para alquilar una propiedad, el inquilino debe presentar: DNI vigente, recibos de sueldo "
                "de los últimos 3 meses o constancia de ingresos si es monotributista/autónomo, "
                "y referencias laborales o comerciales."
            ),
            (
                "Se requieren dos garantes con propiedades en la provincia, que deben presentar: DNI, "
                "título de propiedad o certificado de dominio, y libre deuda de impuestos. "
                "Como alternativa al garante propietario se acepta seguro de caución, "
                "sujeto a aprobación de la aseguradora."
            ),
        ],
    },
    {
        "titulo": "Proceso de Compra paso a paso",
        "chunks": [
            (
                "El proceso de compra en BBR consta de 5 etapas: "
                "1) Búsqueda y selección de la propiedad con asesoramiento de nuestro equipo. "
                "2) Reserva con seña del 10% del valor acordado. "
                "3) Revisión y firma del boleto de compraventa. "
                "4) Trámite de escritura con el escribano designado. "
                "5) Firma de escritura pública y entrega de llaves."
            ),
            (
                "La seña se abona al momento de hacer la reserva y se imputa al precio total. "
                "El plazo para firmar el boleto de compraventa es generalmente de 30 días desde la reserva. "
                "La escritura se firma en los plazos acordados en el boleto, habitualmente entre 30 y 90 días."
            ),
            (
                "Los gastos de escritura corren por cuenta del comprador (escribano, sellado, inscripción). "
                "El vendedor abona el impuesto a la transferencia o el ITI según corresponda. "
                "BBR acompaña a ambas partes en todo el proceso sin costo adicional."
            ),
        ],
    },
    {
        "titulo": "Proceso de Alquiler paso a paso",
        "chunks": [
            (
                "El proceso de alquiler en BBR incluye: "
                "1) Visita y selección del inmueble. "
                "2) Presentación de documentación y garantes. "
                "3) Aprobación por parte del propietario. "
                "4) Firma del contrato de alquiler ante escribano o en nuestra oficina. "
                "5) Pago de depósito, primer mes y comisión. Entrega de llaves."
            ),
            (
                "El contrato de alquiler tiene una duración mínima de 2 años según la Ley de Alquileres vigente. "
                "El depósito equivale a un mes de alquiler y se devuelve al finalizar el contrato "
                "descontando daños si los hubiera. Los ajustes de precio se realizan según el índice ICL "
                "publicado por el BCRA."
            ),
        ],
    },
    {
        "titulo": "Tasaciones y Valuaciones",
        "chunks": [
            (
                "BBR ofrece tasaciones gratuitas para propietarios que deseen vender o alquilar con nosotros. "
                "El proceso de tasación incluye visita al inmueble, análisis comparativo de mercado "
                "y entrega de informe de valor estimado en un plazo de 48 a 72 horas hábiles."
            ),
            (
                "Los factores que inciden en la tasación son: ubicación, superficie, estado de conservación, "
                "antigüedad, amenities, orientación y comparables de mercado en la zona. "
                "La tasación es una estimación profesional y no un valor garantizado de venta."
            ),
        ],
    },
    {
        "titulo": "Horarios y Contacto",
        "chunks": [
            (
                "BBR Grupo Inmobiliario atiende de lunes a viernes de 9:00 a 13:00 y de 16:00 a 20:00 horas. "
                "Los sábados atendemos de 9:00 a 13:00. "
                "Domingos y feriados no hay atención presencial, pero podés enviarnos un mensaje "
                "por WhatsApp y te respondemos a la brevedad."
            ),
            (
                "Podés contactarnos a través de WhatsApp, teléfono o formulario web. "
                "Nuestros asesores también coordinan visitas fuera del horario de oficina "
                "con cita previa. Para urgencias o consultas fuera de horario, "
                "enviar mensaje por WhatsApp al número de la inmobiliaria."
            ),
        ],
    },
    {
        "titulo": "Formas de Pago",
        "chunks": [
            (
                "En BBR aceptamos múltiples formas de pago para la compra de propiedades: "
                "efectivo en pesos argentinos, dólares billete, transferencia bancaria, "
                "y financiación hipotecaria a través de bancos con los que trabajamos. "
                "No aceptamos criptomonedas como forma de pago directa."
            ),
            (
                "Para alquileres, el pago mensual se realiza por transferencia bancaria o depósito. "
                "Los pagos en efectivo deben realizarse en nuestra oficina con emisión de recibo oficial. "
                "No se aceptan pagos en mano sin recibo. "
                "Trabajamos con créditos hipotecarios del Banco Provincia, Banco Nación y otros bancos privados."
            ),
        ],
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_doc_uuid(empresa_slug: str, titulo: str) -> str:
    """UUID determinístico para el documento, basado en empresa + titulo."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{empresa_slug}::{titulo}"))


def make_chunk_uuid(doc_id: str, orden: int) -> str:
    """UUID determinístico para el chunk."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_id}::chunk::{orden}"))


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main(dry_run: bool = False) -> None:
    print(f"Modo: {'DRY-RUN (sin DB)' if dry_run else 'INSERTAR/ACTUALIZAR'}")
    print("-" * 60)

    if dry_run:
        for doc_data in KB_DOCUMENTS:
            titulo = doc_data["titulo"]
            chunks = doc_data["chunks"]
            doc_id = make_doc_uuid(EMPRESA_SLUG, titulo)
            contenido_completo = "\n\n".join(chunks)
            print(f"\n[doc] [{doc_id[:8]}...] {titulo}")
            print(f"   {len(chunks)} chunks — {len(contenido_completo)} chars")
            for i, chunk_texto in enumerate(chunks):
                chunk_id = make_chunk_uuid(doc_id, i)
                print(f"   Chunk {i}: [{chunk_id[:8]}...] {chunk_texto[:80]}...")
        print("\n" + "=" * 60)
        print(f"OK DRY-RUN completado — {len(KB_DOCUMENTS)} documentos")
        return

    # Obtener id_empresa e id_rubro desde la DB
    conn = await asyncpg.connect(settings.DATABASE_URL.replace("+asyncpg", ""))
    try:
        empresa = await conn.fetchrow(
            "SELECT id_empresa FROM empresas WHERE slug = $1", EMPRESA_SLUG
        )
        if not empresa:
            print(f"ERROR: No se encontró empresa con slug='{EMPRESA_SLUG}'")
            return
        id_empresa = empresa["id_empresa"]

        # Obtener el primer rubro activo de la empresa
        rubro = await conn.fetchrow(
            "SELECT id_rubro FROM empresa_rubros WHERE id_empresa = $1 ORDER BY id_rubro LIMIT 1",
            id_empresa,
        )
        if not rubro:
            print(f"ERROR: No hay rubros para id_empresa={id_empresa}")
            return
        id_rubro = rubro["id_rubro"]

        print(f"Empresa: {EMPRESA_SLUG} (id={id_empresa}), Rubro: id={id_rubro}")

        for doc_data in KB_DOCUMENTS:
            titulo = doc_data["titulo"]
            chunks = doc_data["chunks"]
            doc_id = make_doc_uuid(EMPRESA_SLUG, titulo)
            contenido_completo = "\n\n".join(chunks)

            print(f"\n[doc] [{doc_id[:8]}...] {titulo}")
            print(f"   {len(chunks)} chunks — {len(contenido_completo)} chars")

            # Upsert documento
            await conn.execute(
                """
                INSERT INTO kb_documents
                    (id_documento, id_empresa, id_rubro, titulo, contenido_texto, activo, version)
                VALUES
                    ($1::uuid, $2, $3, $4, $5, TRUE, 1)
                ON CONFLICT (id_documento) DO UPDATE SET
                    titulo          = EXCLUDED.titulo,
                    contenido_texto = EXCLUDED.contenido_texto,
                    activo          = TRUE,
                    version         = kb_documents.version + 1
                """,
                doc_id, id_empresa, id_rubro, titulo, contenido_completo,
            )

            # Eliminar chunks previos del documento (re-seed limpio)
            await conn.execute(
                "DELETE FROM kb_chunks WHERE id_documento = $1::uuid", doc_id
            )

            # Insertar chunks
            for orden, chunk_texto in enumerate(chunks):
                chunk_id = make_chunk_uuid(doc_id, orden)
                await conn.execute(
                    """
                    INSERT INTO kb_chunks (id_chunk, id_documento, chunk_texto, orden)
                    VALUES ($1::uuid, $2::uuid, $3, $4)
                    """,
                    chunk_id, doc_id, chunk_texto, orden,
                )
                print(f"   + Chunk {orden}: {chunk_texto[:60]}...")

        print("\n" + "=" * 60)
        print(f"OK Seed KB completado — {len(KB_DOCUMENTS)} documentos")

    finally:
        await conn.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(dry_run=dry_run))
