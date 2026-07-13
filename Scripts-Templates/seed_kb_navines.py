# -*- coding: utf-8 -*-
"""
Seed KB para Navines Inmobiliaria (id_empresa=5, id_rubro=1).
Borra docs anteriores y re-inserta con acentos y contenido enriquecido.
"""
import asyncio
import uuid
import asyncpg

ID_EMPRESA = 5
ID_RUBRO   = 1

DOCS = [
    {
        "titulo": "Comisiones y Honorarios",
        "chunks": [
            "Navines Inmobiliaria cobra una comisión estándar del 3% del valor de la operación "
            "para ventas y compraventas, pagado por cada parte (comprador y vendedor). "
            "En operaciones de alquiler, la comisión equivale a un mes de alquiler más IVA, a cargo del inquilino.",

            "Para desarrollos y lotes, la comisión puede variar entre el 3% y el 5% según el tipo de "
            "operación y acuerdo previo. En todos los casos la comisión se abona al momento de la firma "
            "de la escritura o contrato definitivo. No hay costos ocultos ni cargos adicionales por "
            "gestión o asesoramiento.",

            "En operaciones de alquiler comercial, la comisión es de dos meses de alquiler más IVA. "
            "Los honorarios por tasación de propiedades son gratuitos para clientes que operan con Navines. "
            "Para tasaciones sin operación posterior, consultar valor vigente.",
        ],
    },
    {
        "titulo": "Documentación Requerida para Compraventa",
        "chunks": [
            "Para iniciar el proceso de compraventa, el vendedor debe presentar: título de propiedad "
            "original, DNI del/los titulares, boleta de servicios al día (luz, gas, agua), libre deuda "
            "de expensas (si aplica) y libre deuda municipal.",

            "El comprador debe presentar: DNI vigente, CUIL/CUIT, constancia de ingresos o fuente de "
            "fondos según el monto de la operación. Para montos superiores a USD 100.000 puede requerirse "
            "declaración jurada de origen de fondos según normativa AFIP.",

            "En caso de sucesión, herencia o inmueble con múltiples titulares, se requiere documentación "
            "adicional: declaratoria de herederos o poder notarial según corresponda. El escribano "
            "interviniente guiará el proceso caso a caso.",
        ],
    },
    {
        "titulo": "Documentación Requerida para Alquiler",
        "chunks": [
            "Para alquilar una propiedad, el inquilino debe presentar: DNI vigente, recibos de sueldo "
            "de los últimos 3 meses o constancia de ingresos si es monotributista/autónomo, y referencias "
            "laborales o comerciales.",

            "Se requieren dos garantes con propiedades en la provincia, que deben presentar: DNI, título "
            "de propiedad o certificado de dominio, y libre deuda de impuestos. Como alternativa al "
            "garante propietario se acepta seguro de caución, sujeto a aprobación de la aseguradora.",
        ],
    },
    {
        "titulo": "Proceso de Compra paso a paso",
        "chunks": [
            "El proceso de compra en Navines consta de 5 etapas: 1) Búsqueda y selección de la propiedad "
            "con asesoramiento de nuestro equipo. 2) Reserva con seña del 10% del valor acordado. "
            "3) Revisión y firma del boleto de compraventa. 4) Trámite de escritura con el escribano "
            "designado. 5) Firma de escritura pública y entrega de llaves.",

            "La seña se abona al momento de hacer la reserva y se imputa al precio total. El plazo para "
            "firmar el boleto de compraventa es generalmente de 30 días desde la reserva. La escritura "
            "se firma en los plazos acordados en el boleto, habitualmente entre 30 y 90 días.",

            "Los gastos de escritura corren por cuenta del comprador (escribano, sellado, inscripción). "
            "El vendedor abona el impuesto a la transferencia o el ITI según corresponda. Navines "
            "acompaña a ambas partes en todo el proceso sin costo adicional.",
        ],
    },
    {
        "titulo": "Proceso de Alquiler paso a paso",
        "chunks": [
            "El proceso de alquiler en Navines incluye: 1) Visita y selección del inmueble. "
            "2) Presentación de documentación y garantes. 3) Aprobación por parte del propietario. "
            "4) Firma del contrato de alquiler ante escribano o en nuestra oficina. "
            "5) Pago de depósito, primer mes y comisión. Entrega de llaves.",

            "El contrato de alquiler tiene una duración mínima de 2 años según la Ley de Alquileres "
            "vigente. El depósito equivale a un mes de alquiler y se devuelve al finalizar el contrato "
            "descontando daños si los hubiera. Los ajustes de precio se realizan según el índice ICL "
            "publicado por el BCRA.",
        ],
    },
    {
        "titulo": "Tasaciones y Valuaciones",
        "chunks": [
            "Navines Inmobiliaria ofrece tasaciones gratuitas para propietarios que deseen vender o "
            "alquilar con nosotros. El proceso de tasación incluye visita al inmueble, análisis "
            "comparativo de mercado y entrega de informe de valor estimado en un plazo de 48 a 72 "
            "horas hábiles.",

            "Los factores que inciden en la tasación son: ubicación, superficie, estado de conservación, "
            "antigüedad, amenities, orientación y comparables de mercado en la zona. La tasación es una "
            "estimación profesional y no un valor garantizado de venta.",
        ],
    },
    {
        "titulo": "Horarios y Contacto",
        "chunks": [
            "Navines Inmobiliaria atiende de lunes a viernes de 9:00 a 13:00 y de 16:00 a 20:00 horas. "
            "Los sábados atendemos de 9:00 a 13:00. Domingos y feriados no hay atención presencial, "
            "pero podés enviarnos un mensaje por WhatsApp y te respondemos a la brevedad.",

            "Podés contactarnos a través de WhatsApp, teléfono o formulario web. Nuestros asesores "
            "también coordinan visitas fuera del horario de oficina con cita previa. Para urgencias o "
            "consultas fuera de horario, enviá un mensaje por WhatsApp al número de la inmobiliaria.",
        ],
    },
    {
        "titulo": "Formas de Pago",
        "chunks": [
            "En Navines aceptamos múltiples formas de pago para la compra de propiedades: efectivo en "
            "pesos argentinos, dólares billete, transferencia bancaria, y financiación hipotecaria a "
            "través de bancos con los que trabajamos. No aceptamos criptomonedas como forma de pago directa.",

            "Para alquileres, el pago mensual se realiza por transferencia bancaria o depósito. Los pagos "
            "en efectivo deben realizarse en nuestra oficina con emisión de recibo oficial. No se aceptan "
            "pagos en mano sin recibo. Trabajamos con créditos hipotecarios del Banco Provincia, Banco "
            "Nación y otros bancos privados.",
        ],
    },
]


async def main():
    conn = await asyncpg.connect(
        "postgresql://n8n_b4cl_user:grrYrWL7KFLO7xF6uy1F1lJVDmSG0uCI"
        "@dpg-d4llmj8dl3ps7388nfeg-a.oregon-postgres.render.com/n8n_b4cl",
        ssl="require",
    )

    # Borrar docs anteriores de Navines (chunks se borran por ON DELETE CASCADE)
    prev = await conn.fetchval("SELECT count(*) FROM kb_documents WHERE id_empresa=$1", ID_EMPRESA)
    await conn.execute("DELETE FROM kb_documents WHERE id_empresa=$1", ID_EMPRESA)
    print(f"Borrados: {prev} documentos previos de Navines")

    inserted_docs = 0
    inserted_chunks = 0

    for doc in DOCS:
        contenido = "\n\n".join(doc["chunks"])
        doc_id = uuid.uuid4()
        await conn.execute(
            "INSERT INTO kb_documents (id_documento, id_empresa, id_rubro, titulo, contenido_texto, activo, version) "
            "VALUES ($1, $2, $3, $4, $5, TRUE, 1)",
            doc_id, ID_EMPRESA, ID_RUBRO, doc["titulo"], contenido,
        )
        for i, chunk_texto in enumerate(doc["chunks"]):
            chunk_id = uuid.uuid4()
            await conn.execute(
                "INSERT INTO kb_chunks (id_chunk, id_documento, orden, chunk_texto) VALUES ($1, $2, $3, $4)",
                chunk_id, doc_id, i + 1, chunk_texto,
            )
            inserted_chunks += 1
        inserted_docs += 1
        print(f"  [{inserted_docs}] {doc['titulo']} ({len(doc['chunks'])} chunks)")

    print(f"\nTotal: {inserted_docs} docs, {inserted_chunks} chunks insertados para Navines")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
