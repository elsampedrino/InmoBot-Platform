export interface Usuario {
  id_usuario: number;
  nombre: string | null;
  email: string;
  es_superadmin: boolean;
  activo: boolean;
  id_empresa: number | null;
  empresa_nombre: string | null;
  created_at: string | null;
}

export interface UsuarioListResponse {
  usuarios: Usuario[];
  total: number;
}

export interface UsuarioCreateRequest {
  nombre: string;
  email: string;
  password: string;
  es_superadmin: boolean;
  id_empresa: number | null;
}

export interface UsuarioUpdateRequest {
  nombre?: string;
  email?: string;
  es_superadmin?: boolean;
  id_empresa?: number | null;
  activo?: boolean;
}

export interface UsuarioResetPasswordRequest {
  nueva_password: string;
}