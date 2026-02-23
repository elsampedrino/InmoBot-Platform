#!/usr/bin/env python3
"""
Scraper para Navines Inmobiliaria - Terrenos en venta
Genera JSON con estructura estándar InmoBot
Sin dependencias externas - usa solo stdlib
"""

import urllib.request
import json
import re
from datetime import datetime
from html.parser import HTMLParser

BASE_URL = "https://navinesinmob.com.ar"
LISTING_URL = f"{BASE_URL}/resultados.php?tipo=Terreno&operacion=Venta"

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
        self.in_description = False
        self.text_buffer = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Capture images from gallery
        if tag == 'img':
            src = attrs_dict.get('src', '')
            if 'imagenes/galerias/' in src or 'imagenes/destacadas/' in src:
                if len(self.data['images']) < 3:
                    self.data['images'].append(f"{BASE_URL}/{src}")

        # Capture title (h2)
        if tag == 'h2':
            self.current_tag = 'title'
            self.capture_text = True

        # Capture price (h4, strong, or any tag with U$S/ARS)
        if tag in ['h4', 'strong', 'span']:
            self.current_tag = 'price'
            self.capture_text = True

        # Capture paragraphs (might be description)
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
                if not self.data['price']:  # Only capture first price
                    self.data['price'] = text

            elif self.current_tag == 'p' and len(text) > 100 and not self.data['description']:
                # Long paragraph is likely the description
                self.data['description'] = text

            # Capture any line with details
            if ':' in text and len(text) < 100:
                self.data['details'].append(text)

            self.text_buffer = ''
            self.capture_text = False

def get_property_ids():
    """Obtiene todos los IDs de terrenos en venta"""
    print(f"Fetching property list from {LISTING_URL}...")

    req = urllib.request.Request(LISTING_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', errors='ignore')

    parser = PropertyListParser()
    parser.feed(html)

    print(f"Found {len(parser.property_ids)} properties")
    return parser.property_ids

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

    # Extract address from raw HTML
    text_plain = re.sub(r'<[^>]+>', ' ', html)
    text_plain = re.sub(r'\s+', ' ', text_plain)

    address = ""
    barrio = ""
    ciudad = "San Pedro"

    # Pattern 1: structured field "Ubicación: Calle X al 123, SAN PEDRO"
    # Only accept if followed by a city name (confirms it's a structured field)
    match = re.search(
        r'Ubicaci[oó]n\s*:\s*([^<\n\r]{5,100}?)\s*,\s*(?:SAN PEDRO|RAMALLO|BUENOS AIRES|VILLA RAMALLO)',
        text_plain, re.IGNORECASE
    )
    if match:
        address = match.group(1).strip().rstrip('.,')

    # Pattern 2: description with emoji marker "✅ Ubicación: [address]."
    if not address and parser.data['description']:
        match = re.search(r'[✅📍]\s*Ubicaci[oó]n\s*:\s*([^\n\r.]{5,80})', parser.data['description'])
        if match:
            raw = match.group(1).strip().rstrip('.,')
            raw = re.split(r',\s*(?:SAN PEDRO|RAMALLO)', raw, flags=re.IGNORECASE)[0].strip()
            address = raw

    # Extract superficie
    superficie_total = 0
    superficie_cubierta = 0

    for detail in parser.data['details']:
        if 'Superficie total' in detail or 'Superficie Total' in detail:
            match = re.search(r'(\d+)\s*m', detail)
            if match:
                superficie_total = int(match.group(1))
        elif 'Superficie cubierta' in detail or 'Superficie Cubierta' in detail:
            match = re.search(r'(\d+)\s*m', detail)
            if match:
                superficie_cubierta = int(match.group(1))

    # Look for dimensions in title or description
    if superficie_total == 0:
        combined_text = parser.data['title'] + ' ' + parser.data['description']
        match = re.search(r'(\d+)\s*m[²2]', combined_text)
        if match:
            superficie_total = int(match.group(1))

    return {
        'id': f"NAVINES-TERRENO-{prop_id}",
        'titulo': parser.data['title'],
        'direccion': address,
        'barrio': barrio,
        'ciudad': ciudad,
        'precio': price_value,
        'moneda': currency,
        'superficie_total': superficie_total,
        'superficie_cubierta': superficie_cubierta,
        'descripcion': parser.data['description'],
        'fotos': parser.data['images']
    }

def generar_descripcion_corta(descripcion, titulo, superficie):
    """Genera un resumen corto con la info más relevante de la descripción"""
    if not descripcion:
        partes = []
        if titulo:
            partes.append(titulo)
        if superficie:
            partes.append(f"Superficie: {superficie} m²")
        return ". ".join(partes)

    # Limpiar texto: quitar emojis, saltos de línea múltiples y bullets
    texto = re.sub(r'[✅⭐🏡🔑💰📍]', '', descripcion)
    texto = re.sub(r'\r?\n+', ' ', texto)
    texto = re.sub(r'\s{2,}', ' ', texto).strip()

    # Tomar las primeras 2 oraciones significativas
    oraciones = re.split(r'(?<=[.!?])\s+', texto)
    resumen = ""
    for oracion in oraciones:
        oracion = oracion.strip()
        if len(oracion) < 20:
            continue
        if resumen:
            resumen += " " + oracion
        else:
            resumen = oracion
        if len(resumen) >= 150:
            break

    return resumen[:250].strip() if resumen else texto[:250]


def convert_to_inmobot_format(properties):
    """Convierte al formato JSON estándar de InmoBot"""
    propiedades = []

    for i, prop in enumerate(properties, start=1):
        propiedad = {
            "id": f"PROP-{i:03d}",
            "tipo": "lote",
            "operacion": "venta",
            "estado_construccion": "terreno",
            "titulo": prop['titulo'] or f"Terreno en {prop['ciudad']}",
            "direccion": {
                "calle": prop['direccion'] or "",
                "barrio": prop['barrio'] or prop['ciudad'],
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
                "dormitorios": None,
                "banos": None,
                "cocheras": None,
                "superficie_total": f"{prop['superficie_total']} m²" if prop['superficie_total'] > 0 else None,
                "superficie_cubierta": f"{prop['superficie_cubierta']} m²" if prop['superficie_cubierta'] > 0 else None
            },
            "descripcion": "",
            "descripcion_corta": generar_descripcion_corta(
                prop['descripcion'],
                prop['titulo'],
                prop['superficie_total']
            ),
            "fotos": prop['fotos'],
            "detalles": []
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
    print("=== Navines Inmobiliaria Scraper ===\n")

    # Get all property IDs
    property_ids = get_property_ids()

    # Scrape each property
    properties = []
    for prop_id in property_ids:
        try:
            prop_data = scrape_property_detail(prop_id)
            properties.append(prop_data)
        except Exception as e:
            print(f"Error scraping property {prop_id}: {e}")
            continue

    print(f"\nSuccessfully scraped {len(properties)} properties")

    # Convert to InmoBot format
    inmobot_json = convert_to_inmobot_format(properties)

    # Save to file
    output_file = "propiedades_navines.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inmobot_json, f, ensure_ascii=False, indent=2)

    print(f"\nJSON saved to: {output_file}")
    print(f"Total properties: {len(inmobot_json['propiedades'])}")

if __name__ == "__main__":
    main()
