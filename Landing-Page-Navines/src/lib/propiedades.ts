const GITHUB_JSON_URL = 'https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/main/propiedades_navines.json';

export interface Direccion {
  calle: string;
  barrio: string;
  ciudad: string;
  lat?: number;
  lng?: number;
}

export interface Precio {
  valor: number;
  moneda: string;
}

export interface Caracteristicas {
  ambientes?: number;
  dormitorios?: number;
  banios?: number;
  superficie_total?: string;
  superficie_cubierta?: string;
}

export interface Propiedad {
  id: string;
  tipo: string;
  operacion: string;
  titulo: string;
  destacado: boolean;
  activo: boolean;
  direccion: Direccion;
  precio: Precio;
  descripcion: string;
  descripcion_corta?: string;
  fotos: string[];
  caracteristicas: Caracteristicas;
  detalles?: string[];
}

interface PropiedadRaw {
  id: string;
  tipo: string;
  operacion: string;
  titulo: string;
  destacado?: boolean;
  activo?: boolean;
  direccion: Direccion;
  precio: Precio;
  descripcion: string;
  descripcion_corta?: string;
  fotos: { urls: string[] };
  caracteristicas: Caracteristicas;
  detalles?: string[];
}

interface JSONResponse {
  propiedades: PropiedadRaw[];
  metadata: {
    total: number;
    fecha_generacion?: string;
    ultima_actualizacion?: string;
  };
}

function transformarPropiedad(raw: PropiedadRaw): Propiedad {
  return {
    ...raw,
    activo: raw.activo !== false,
    destacado: raw.destacado === true,
    fotos: raw.fotos?.urls || []
  };
}

let cachedPropiedades: Propiedad[] | null = null;

export async function getPropiedades(): Promise<Propiedad[]> {
  if (cachedPropiedades) return cachedPropiedades;

  if (import.meta.env.DEV) {
    try {
      const { readFileSync } = await import('node:fs');
      const { join } = await import('node:path');
      const jsonPath = join(process.cwd(), '..', 'Navines Inmobiliaria', 'propiedades_navines.json');
      const data: JSONResponse = JSON.parse(readFileSync(jsonPath, 'utf-8'));
      cachedPropiedades = data.propiedades.map(transformarPropiedad);
      return cachedPropiedades;
    } catch (e) {
      console.warn('[DEV] No se pudo leer JSON local, usando GitHub como fallback');
    }
  }

  try {
    const response = await fetch(GITHUB_JSON_URL);
    if (!response.ok) throw new Error(`Error fetching propiedades: ${response.status}`);
    const data: JSONResponse = await response.json();
    cachedPropiedades = data.propiedades.map(transformarPropiedad);
    return cachedPropiedades;
  } catch (error) {
    console.error('Error cargando propiedades desde GitHub:', error);
    return [];
  }
}

function soloActivas(propiedades: Propiedad[]): Propiedad[] {
  return propiedades.filter(p => p.activo !== false);
}

export async function getCasasVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'casa' && p.operacion === 'venta');
}

export async function getLotesVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'lote' && p.operacion === 'venta');
}

export async function getPropiedadesDestacadas(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  const activas = soloActivas(propiedades);
  const destacadas = activas.filter(p => p.destacado === true);
  return destacadas.length > 0 ? destacadas.slice(0, 6) : activas.slice(0, 6);
}
