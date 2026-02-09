** Estructura Json Propiedades estándar : **


{
  "propiedades": [
    {
      "id": "PROP-XXX",
      "tipo": "casa|departamento|lote|local|terreno",
      "operacion": "venta|alquiler",
      "estado_construccion": "usado|nuevo|en construcción|terreno",
      "titulo": "string",
      "direccion": {
        "calle": "string",
        "barrio": "string",
        "ciudad": "string"
      },
      "precio": {
        "valor": number,
        "moneda": "USD|ARS",
        "nota": "string (opcional)"
      },
      "descripcion": "string",
      "fotos": {
        "urls": ["array de strings"]
      },
      "caracteristicas": {
        "dormitorios": number,
        "banios": number,
        "superficie_total": "string",
        "superficie_cubierta": "string"
      },
      "detalles": ["array de strings"]
    }
  ]
}