#!/usr/bin/env python3
"""
Scraper para Navines Inmobiliaria - Casas en venta (primeras 20)
Genera JSON con estructura estándar InmoBot
Sin dependencias externas - usa solo stdlib
"""

import urllib.request
import json
import re
from datetime import datetime
from html.parser import HTMLParser

BASE_URL = "https://navinesinmob.com.ar"
LISTING_URL = f"{BASE_URL}/resultados.php?tipo=Casa&operacion=Venta"
MAX_PROPERTIES = 20

# Servicios e instalaciones conocidos a capturar en "detalles"
SERVICIOS_CONOCIDOS = [
    'Agua Corriente', 'Agua corriente', 'Cloacas', 'Electricidad', 'Gas Natural',
    'Gas natural', 'Pavimento', 'Internet', 'Teléfono', 'Cable'
]

CARACTERISTICAS_CONOCIDAS = [
    'Parque', 'Parrilla', 'Patio', 'Jardín', 'Jardin', 'Cochera cubierta',
    'Cochera', 'Pileta', 'Quincho', 'Balcón', 'Balcon', 'Terraza',
    'Lavadero', 'Baulera', 'Playroom', 'Estudio', 'Living comedor',
    'Cocina funcional', 'Galería', 'Galeria', 'Ático', 'Atico',
    'Calefacción', 'Calefaccion', 'Aire acondicionado', 'Seguridad',
    'Portón eléctrico', 'Porton electrico', 'Alarma'
]


class PropertyListParser(HTMLParser):
    """Parser para extraer IDs de propiedades del listado"""
    def __init__(self):
        super().__init__()
        self.property_ids = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and 'propiedad.php?id=' in value:
                    match = re.search(r'id=(\d+)', value)
                    if match:
                        prop_id = match.group(1)
                        if prop_id not in self.property_ids:
                            self.property_ids.append(prop_id)


class PropertyDetailParser(HTMLParser):
    """Parser para extraer detalles de una propiedad"""
    def __init__(self):
        super().__init__()
        self.data = {
            'title': '',
            'price': '',
            'images': [],
            'description': '',
            'details': []
        }
        self.current_tag = None
        self.capture_text = False
        self.text_buffer = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Capture images from gallery (max 3)
        if tag == 'img':
            src = attrs_dict.get('src', '')
            if 'imagenes/galerias/' in src or 'imagenes/destacadas/' in src:
                if len(self.data['images']) < 3:
                    self.data['images'].append(f"{BASE_URL}/{src}")

        if tag == 'h2':
            self.current_tag = 'title'
            self.capture_text = True

        if tag in ['h4', 'strong', 'span']:
            self.current_tag = 'price'
            self.capture_text = True

        if tag == 'p':
            self.current_tag = 'p'
            self.capture_text = True

    def handle_data(self, data):
        if self.capture_text:
            self.text_buffer += data

    def handle_endtag(self, tag):
        if self.capture_text and tag in ['h2', 'h4', 'strong', 'span', 'p', 'div']:
            text = self.text_buffer.strip()

            if self.current_tag == 'title' and text and not self.data['title']:
                self.data['title'] = text

            elif self.current_tag == 'price' and ('U$S' in text or 'ARS' in text or '$' in text):
                if not self.data['price']:
                    self.data['price'] = text

            elif self.current_tag == 'p' and len(text) > 100 and not self.data['description']:
                self.data['description'] = text

            if ':' in text and len(text) < 100:
                self.data['details'].append(text)

            self.text_buffer = ''
            self.capture_text = False


def get_property_ids():
    """Obtiene los primeros MAX_PROPERTIES IDs de casas en venta"""
    print(f"Fetching property list from {LISTING_URL}...")

    req = urllib.request.Request(LISTING_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')

    parser = PropertyListParser()
    parser.feed(html)

    ids = parser.property_ids[:MAX_PROPERTIES]
    print(f"Found {len(ids)} properties (capped at {MAX_PROPERTIES})")
    return ids


def extract_detalles(html, description):
    """Extrae servicios y características adicionales del HTML"""
    text_plain = re.sub(r'<[^>]+>', ' ', html)
    text_plain = re.sub(r'\s+', ' ', text_plain)

    # Canonical names (deduped, title case)
    canonical = {
        'agua corriente': 'Agua corriente',
        'cloacas': 'Cloacas',
        'electricidad': 'Electricidad',
        'gas natural': 'Gas natural',
        'pavimento': 'Pavimento',
        'internet': 'Internet',
        'teléfono': 'Teléfono',
        'telefono': 'Teléfono',
        'cable': 'Cable',
        'parque': 'Parque',
        'parrilla': 'Parrilla',
        'patio': 'Patio',
        'jardín': 'Jardín',
        'jardin': 'Jardín',
        'cochera cubierta': 'Cochera cubierta',
        'pileta': 'Pileta',
        'quincho': 'Quincho',
        'balcón': 'Balcón',
        'balcon': 'Balcón',
        'terraza': 'Terraza',
        'lavadero': 'Lavadero',
        'baulera': 'Baulera',
        'playroom': 'Playroom',
        'estudio': 'Estudio',
        'living comedor': 'Living comedor',
        'cocina funcional': 'Cocina funcional',
        'galería': 'Galería',
        'galeria': 'Galería',
        'calefacción': 'Calefacción',
        'calefaccion': 'Calefacción',
        'aire acondicionado': 'Aire acondicionado',
        'seguridad': 'Seguridad',
        'portón eléctrico': 'Portón eléctrico',
        'porton electrico': 'Portón eléctrico',
        'alarma': 'Alarma',
    }

    found = set()
    text_lower = text_plain.lower()

    for key, display in canonical.items():
        if key in text_lower:
            found.add(display)

    return sorted(found)


def scrape_property_detail(prop_id):
    """Scrapea el detalle de una propiedad"""
    url = f"{BASE_URL}/propiedad.php?id={prop_id}"
    print(f"Scraping property {prop_id}...")

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')

    parser = PropertyDetailParser()
    parser.feed(html)

    # Parse price
    price_value = 0
    currency = "USD"
    if parser.data['price']:
        match = re.search(r'([\d.,]+)', parser.data['price'].replace('.', ''))
        if match:
            price_value = int(match.group(1).replace(',', ''))
        if 'ARS' in parser.data['price']:
            currency = "ARS"

    # Extract address from raw HTML plain text
    text_plain = re.sub(r'<[^>]+>', ' ', html)
    text_plain = re.sub(r'\s+', ' ', text_plain)

    address = ""
    ciudad = "San Pedro"

    # Pattern 1: structured field followed by city name
    match = re.search(
        r'Ubicaci[oó]n\s*:\s*([^<\n\r]{5,100}?)\s*,\s*(?:SAN PEDRO|RAMALLO|BUENOS AIRES|VILLA RAMALLO)',
        text_plain, re.IGNORECASE
    )
    if match:
        address = match.group(1).strip().rstrip('.,')

    # Pattern 2: emoji marker in description
    if not address and parser.data['description']:
        match = re.search(r'[✅📍]\s*Ubicaci[oó]n\s*:\s*([^\n\r.]{5,80})', parser.data['description'])
        if match:
            raw = match.group(1).strip().rstrip('.,')
            raw = re.split(r',\s*(?:SAN PEDRO|RAMALLO)', raw, flags=re.IGNORECASE)[0].strip()
            address = raw

    # Extract structured fields from raw HTML plain text
    # (label and value are in separate HTML tags, so we search in plain text)
    def extract_int_field(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            return val if val > 0 else None
        return None

    dormitorios = extract_int_field(r'Dormitorios?\s*:?\s*(\d+)', text_plain)
    banos = extract_int_field(r'Ba[ñn]os?\s*:?\s*(\d+)', text_plain)
    cocheras = extract_int_field(r'Cocheras?\s*:?\s*(\d+)', text_plain)
    antiguedad_raw = extract_int_field(r'Antig[üu]edad\s*:?\s*(\d+)', text_plain)
    antiguedad = antiguedad_raw if antiguedad_raw and antiguedad_raw > 0 else None

    # Superficies
    superficie_total = 0
    superficie_cubierta = 0

    def safe_superficie(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(',', '.')
            try:
                val = int(float(raw))
                return val if val > 0 else 0
            except ValueError:
                pass
        return 0

    superficie_total = safe_superficie(r'(?:Totales|Superficie\s+total)\s*:?\s*(\d[\d.,]*)\s*m', text_plain)
    superficie_cubierta = safe_superficie(r'(?:Cubierta|Superficie\s+cubierta)\s*:?\s*(\d[\d.,]*)\s*m', text_plain)

    # Fallback: extract superficie from title/description
    if superficie_total == 0:
        combined = parser.data['title'] + ' ' + parser.data['description']
        superficie_total = safe_superficie(r'(\d[\d.,]*)\s*m[²2]', combined)

    # Extract detalles (servicios + características)
    detalles = extract_detalles(html, parser.data['description'])

    return {
        'web_id': prop_id,
        'titulo': parser.data['title'],
        'direccion': address,
        'ciudad': ciudad,
        'precio': price_value,
        'moneda': currency,
        'dormitorios': dormitorios,
        'banos': banos,
        'cocheras': cocheras,
        'superficie_total': superficie_total,
        'superficie_cubierta': superficie_cubierta,
        'antiguedad': antiguedad,
        'descripcion': parser.data['description'],
        'detalles': detalles,
        'fotos': parser.data['images']
    }


def generar_descripcion_corta(descripcion, titulo, superficie):
    """Genera un resumen corto con la info más relevante"""
    if not descripcion:
        partes = []
        if titulo:
            partes.append(titulo)
        if superficie:
            partes.append(f"Superficie: {superficie} m²")
        return ". ".join(partes)

    # Limpiar emojis y saltos de línea
    texto = re.sub(r'[✅⭐🏡🔑💰📍⚡️]', '', descripcion)
    texto = re.sub(r'\r?\n+', ' ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto).strip()

    # Tomar las primeras 2 oraciones significativas
    oraciones = re.split(r'(?<=[.!?])\s+', texto)
    resumen = ""
    for oracion in oraciones:
        oracion = oracion.strip()
        if len(oracion) < 20:
            continue
        resumen = (resumen + " " + oracion).strip() if resumen else oracion
        if len(resumen) >= 150:
            break

    return resumen[:250].strip() if resumen else texto[:250]


def convert_to_inmobot_format(properties):
    """Convierte al formato JSON estándar de InmoBot"""
    propiedades = []

    for i, prop in enumerate(properties, start=1):
        propiedad = {
            "id": f"PROP-{i:03d}",
            "tipo": "casa",
            "operacion": "venta",
            "estado_construccion": "usado",
            "titulo": prop['titulo'] or f"Casa en venta - {prop['ciudad']}",
            "direccion": {
                "calle": prop['direccion'] or "",
                "barrio": prop['ciudad'],
                "ciudad": prop['ciudad'],
                "cp": "2930"
            },
            "precio": {
                "valor": prop['precio'],
                "moneda": prop['moneda'],
                "expensas": None
            },
            "caracteristicas": {
                "ambientes": None,
                "dormitorios": prop['dormitorios'] if prop['dormitorios'] and prop['dormitorios'] > 0 else None,
                "banos": prop['banos'] if prop['banos'] and prop['banos'] > 0 else None,
                "cocheras": prop['cocheras'] if prop['cocheras'] and prop['cocheras'] > 0 else None,
                "superficie_total": f"{prop['superficie_total']} m²" if prop['superficie_total'] > 0 else None,
                "superficie_cubierta": f"{prop['superficie_cubierta']} m²" if prop['superficie_cubierta'] > 0 else None,
                "antiguedad": f"{prop['antiguedad']} años" if prop['antiguedad'] else None
            },
            "descripcion": "",
            "descripcion_corta": generar_descripcion_corta(
                prop['descripcion'],
                prop['titulo'],
                prop['superficie_total']
            ),
            "fotos": prop['fotos'],
            "detalles": prop['detalles']
        }
        propiedades.append(propiedad)

    return {
        "metadata": {
            "total_propiedades": len(propiedades),
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
            "inmobiliaria": "Navines Inmobiliaria",
            "fuente": "Scraping web"
        },
        "propiedades": propiedades
    }


def main():
    print("=== Navines Inmobiliaria - Casas en Venta (primeras 20) ===\n")

    property_ids = get_property_ids()

    properties = []
    for prop_id in property_ids:
        try:
            prop_data = scrape_property_detail(prop_id)
            properties.append(prop_data)
        except Exception as e:
            print(f"Error scraping property {prop_id}: {e}")
            continue

    print(f"\nSuccessfully scraped {len(properties)} properties")

    inmobot_json = convert_to_inmobot_format(properties)

    output_file = "propiedades_navines_casas.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inmobot_json, f, ensure_ascii=False, indent=2)

    print(f"JSON saved to: {output_file}")
    print(f"Total properties: {len(inmobot_json['propiedades'])}")


if __name__ == "__main__":
    main()
