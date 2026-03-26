export interface PropiedadDetalle {
  id: string;
  titulo: string;
  tipo: string | null;
  categoria: string | null;
  direccion: string | null;
  ciudad: string | null;
  barrio: string | null;
  dormitorios: number | null;
  banios: number | null;
  superficie_cubierta: string | null;
}

export interface LeadDetalle extends Lead {
  propiedades_detalle: PropiedadDetalle[];
}

export interface Lead {
  id_lead: number;
  id_empresa: number;
  nombre: string | null;
  telefono: string | null;
  email: string | null;
  canal: string | null;
  estado: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
}

export interface LeadListResponse {
  leads: Lead[];
  total: number;
  page: number;
  page_size: number;
}

export const ESTADOS_LEAD = [
  { value: "nuevo",      label: "Nuevo",      color: "bg-blue-100 text-blue-800",    tooltip: "Lead recibido, sin contactar" },
  { value: "contactado", label: "Contactado", color: "bg-yellow-100 text-yellow-800", tooltip: "Se intentó contacto" },
  { value: "calificado", label: "Calificado", color: "bg-green-100 text-green-800",   tooltip: "Interés real confirmado" },
  { value: "descartado", label: "Descartado", color: "bg-gray-100 text-gray-500",     tooltip: "Sin interés o no viable" },
] as const;

export type EstadoLead = (typeof ESTADOS_LEAD)[number]["value"];