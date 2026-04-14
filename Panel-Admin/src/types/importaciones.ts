export interface ImportacionPreviewItem {
  external_id: string;
  titulo: string;
  tipo: string;
  categoria: string | null;
}

export interface ImportacionItemModificado extends ImportacionPreviewItem {
  cambios: string[];
}

export interface ImportacionPreviewResponse {
  id_empresa: number;
  total_json: number;
  total_db: number;
  nuevos: ImportacionPreviewItem[];
  modificados: ImportacionItemModificado[];
  sin_cambios: number;
  a_desactivar: ImportacionPreviewItem[];
}

export interface ImportacionAplicarResponse {
  ok: boolean;
  insertados: number;
  actualizados: number;
  desactivados: number;
  id_log: number;
  message: string;
}

export interface ImportacionPublicarResponse {
  ok: boolean;
  total: number;
  commit_sha: string | null;
  id_log: number;
  message: string;
}

export interface ImportacionLog {
  id: number;
  id_empresa: number;
  empresa_nombre: string | null;
  accion: string;
  resultado: string;
  detalle: Record<string, unknown>;
  nombre_usuario: string | null;
  created_at: string | null;
}

export interface ImportacionLogListResponse {
  logs: ImportacionLog[];
  total: number;
}