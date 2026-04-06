export interface ItemAtributos {
  calle?: string | null;
  barrio?: string | null;
  ciudad?: string | null;
  lat?: number | null;
  lng?: number | null;
  dormitorios?: number | null;
  banios?: number | null;
  ambientes?: number | null;
  superficie_total?: string | null;
  superficie_cubierta?: string | null;
  antiguedad?: string | null;
  estado_construccion?: string | null;
  detalles?: string[];
  expensas?: number | null;
  [key: string]: unknown;
}

export interface ItemAdmin {
  id_item: string;
  external_id: string;
  tipo: string;
  categoria: string | null;
  titulo: string;
  descripcion: string | null;
  descripcion_corta: string | null;
  precio: number | null;
  moneda: string | null;
  activo: boolean;
  destacado: boolean;
  atributos: ItemAtributos;
  media: { fotos: string[] };
  created_at: string | null;
}

export interface ItemAdminListResponse {
  items: ItemAdmin[];
  total: number;
  page: number;
  page_size: number;
}

export interface ItemCreateRequest {
  external_id: string;
  tipo: string;
  categoria: string | null;
  titulo: string;
  descripcion: string | null;
  descripcion_corta: string | null;
  precio: number | null;
  moneda: string | null;
  destacado: boolean;
  atributos: ItemAtributos;
  fotos: string[];
}

export interface ItemUpdateRequest extends Partial<ItemCreateRequest> {
  activo?: boolean;
}

export interface CloudinarySignResponse {
  cloud_name: string;
  api_key: string;
  timestamp: number;
  signature: string;
  folder: string;
  transformation: string;
}

export const TIPOS_PROPIEDAD = [
  { value: "casa",          label: "Casa" },
  { value: "departamento",  label: "Departamento" },
  { value: "local",         label: "Local comercial" },
  { value: "oficina",       label: "Oficina" },
  { value: "lote",          label: "Lote / Terreno" },
  { value: "campo",         label: "Campo" },
  { value: "galpon",        label: "Galpón" },
  { value: "cochera",       label: "Cochera" },
] as const;

export const CATEGORIAS_PROPIEDAD = [
  { value: "venta",   label: "Venta" },
  { value: "alquiler", label: "Alquiler" },
  { value: "alquiler_temporal", label: "Alquiler temporal" },
] as const;

export const MONEDAS = [
  { value: "USD", label: "USD (dólares)" },
  { value: "ARS", label: "ARS (pesos)" },
] as const;

export const ESTADOS_CONSTRUCCION = [
  { value: "nuevo",   label: "A estrenar" },
  { value: "usado",   label: "Usado" },
  { value: "reciclado", label: "Reciclado" },
  { value: "en_construccion", label: "En construcción" },
] as const;