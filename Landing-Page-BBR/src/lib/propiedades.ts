// Helper para obtener propiedades desde el JSON centralizado de GitHub
// Esto permite que la landing se actualice automáticamente cuando se actualiza el JSON

const GITHUB_JSON_URL = 'https://raw.githubusercontent.com/elsampedrino/bot-inmobiliaria-data/main/propiedades_bbr.json';

export interface Direccion {
  calle: string;
  barrio: string;
  ciudad: string;
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
  estado_construccion?: string;
  titulo: string;
  direccion: Direccion;
  precio: Precio;
  descripcion: string;
  fotos: string[]; // Transformado de {urls: string[]} a string[]
  caracteristicas: Caracteristicas;
  detalles?: string[];
}

interface PropiedadRaw {
  id: string;
  tipo: string;
  operacion: string;
  estado_construccion?: string;
  titulo: string;
  direccion: Direccion;
  precio: Precio;
  descripcion: string;
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

// Helpers para filtrar por tipo y operación
export async function getCasasVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return propiedades.filter(p => p.tipo === 'casa' && p.operacion === 'venta');
}

export async function getDepartamentosVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return propiedades.filter(p => p.tipo === 'departamento' && p.operacion === 'venta');
}

export async function getLotesVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return propiedades.filter(p => p.tipo === 'terreno' && p.operacion === 'venta');
}

export async function getCamposVenta(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return propiedades.filter(p => p.tipo === 'campo' && p.operacion === 'venta');
}

export async function getAlquileres(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  return propiedades.filter(p => p.operacion === 'alquiler');
}

// Propiedades destacadas (las primeras 3 de cada tipo para la sección principal)
export async function getPropiedadesDestacadas(): Promise<Propiedad[]> {
  const propiedades = await getPropiedades();
  // Seleccionar algunas propiedades variadas para mostrar
  const casas = propiedades.filter(p => p.tipo === 'casa' && p.operacion === 'venta').slice(0, 2);
  const deptos = propiedades.filter(p => p.tipo === 'departamento').slice(0, 1);
  const lotes = propiedades.filter(p => p.tipo === 'terreno').slice(0, 1);
  const campos = propiedades.filter(p => p.tipo === 'campo').slice(0, 1);
  const alquileres = propiedades.filter(p => p.operacion === 'alquiler').slice(0, 1);

  return [...casas, ...deptos, ...lotes, ...campos, ...alquileres].slice(0, 6);
}
