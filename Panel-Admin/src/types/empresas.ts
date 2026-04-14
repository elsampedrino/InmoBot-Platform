export interface EmpresaServicios {
  bot: boolean;
  landing: boolean;
}

export interface EmpresaTelegram {
  enabled: boolean;
  chat_id: string;
}

export interface EmpresaEmail {
  enabled: boolean;
  to: string;
}

export interface EmpresaNotificaciones {
  telegram: EmpresaTelegram;
  email: EmpresaEmail;
}

export interface Empresa {
  id_empresa: number;
  nombre: string;
  slug: string | null;
  id_plan: number | null;
  activa: boolean;
  permite_followup: boolean;
  timezone: string;
  servicios: EmpresaServicios;
  notificaciones: EmpresaNotificaciones;
  created_at: string | null;
}

export interface EmpresaListResponse {
  empresas: Empresa[];
  total: number;
}

export interface EmpresaCreateRequest {
  nombre: string;
  slug: string;
  id_plan: number;
  timezone: string;
  activa: boolean;
}

export interface EmpresaUpdateRequest {
  nombre?: string;
  id_plan?: number;
  activa?: boolean;
  permite_followup?: boolean;
  timezone?: string;
  servicios?: EmpresaServicios;
  notificaciones?: EmpresaNotificaciones;
}

export const PLANES: { id: number; label: string }[] = [
  { id: 1, label: "Premium" },
  { id: 2, label: "PRO" },
  { id: 3, label: "Básico" },
];

export const TIMEZONES = [
  "America/Argentina/Buenos_Aires",
  "America/Argentina/Cordoba",
  "America/Argentina/Mendoza",
  "America/Argentina/Salta",
  "America/Montevideo",
  "America/Santiago",
  "America/Bogota",
  "America/Lima",
  "America/Mexico_City",
  "America/New_York",
  "Europe/Madrid",
];