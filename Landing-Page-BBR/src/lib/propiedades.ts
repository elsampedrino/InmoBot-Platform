// Helper para obtener propiedades desde el JSON centralizado de GitHub
// Esto permite que la landing se actualice automáticamente cuando se actualiza el JSON

const GITHUB_JSON_URL = 'https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/main/propiedades_bbr.json';

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
  fotos: string[]; // Transformado de {urls: string[]} a string[]
  caracteristicas: Caracteristicas;
  detalles?: string[];
}

interface PropiedadRaw {
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
  fotos: { carpeta: string; urls: string[] };
  caracteristicas: Caracteristicas;
  detalles?: string[];
}

interface JSONResponse {
  propiedades: PropiedadRaw[];
  metadata: {
    total: number;
    fecha_generacion: string;
  };
}

// Transforma el formato del JSON (fotos.urls) al formato esperado por los componentes (fotos)
function transformarPropiedad(raw: PropiedadRaw): Propiedad {
  return {
    ...raw,
    fotos: raw.fotos.urls || []
  };
}

// Cache para evitar múltiples fetches durante el build
let cachedPropiedades: Propiedad[] | null = null;

export async function getPropiedades(): Promise<Propiedad[]> {
  if (cachedPropiedades) {
    return cachedPropiedades;
  }

  // En dev: leer desde archivo local para probar features sin pushear (ej: mapa con lat/lng)
  if (import.meta.env.DEV) {
    try {
      const { readFileSync } = await import('node:fs');
      const { join } = await import('node:path');
      const jsonPath = join(process.cwd(), '..', 'BBR Grupo Inmobiliario', 'propiedades_bbr.json');
      const data: JSONResponse = JSON.parse(readFileSync(jsonPath, 'utf-8'));
      cachedPropiedades = data.propiedades.map(transformarPropiedad);
      return cachedPropiedades;
    } catch (e) {
      console.warn('[DEV] No se pudo leer JSON local, usando GitHub como fallback');
    }
  }

  try {
    const response = await fetch(GITHUB_JSON_URL);
    if (!response.ok) {
      throw new Error(`Error fetching propiedades: ${response.status}`);
    }
    const data: JSONResponse = await response.json();
    cachedPropiedades = data.propiedades.map(transformarPropiedad);
    return cachedPropiedades;
  } catch (error) {
    console.error('Error cargando propiedades desde GitHub:', error);
    return [];
  }
}

// Solo propiedades activas
function soloActivas(propiedades: Propiedad[]): Propiedad[] {
  return propiedades.filter(p => p.activo !== false);
}

// Helpers para filtrar por tipo y operación (solo activas)
export async function getCasasVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'casa' && p.operacion === 'venta');
}

export async function getDepartamentosVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'departamento' && p.operacion === 'venta');
}

export async function getLotesVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'terreno' && p.operacion === 'venta');
}

export async function getCamposVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.tipo === 'campo' && p.operacion === 'venta');
}

export async function getAlquileres(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.operacion === 'alquiler');
}

// Propiedades destacadas: usa el campo destacado=true del JSON (máx 6)
export async function getPropiedadesDestacadas(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return soloActivas(propiedades).filter(p => p.destacado === true).slice(0, 6);
}
