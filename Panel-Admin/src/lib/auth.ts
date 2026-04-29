const TOKEN_KEY = "inmobot_admin_token";
const USER_KEY  = "inmobot_admin_user";

export interface AdminUser {
  id_usuario: number;
  nombre: string | null;
  email: string;
  es_superadmin: boolean;
}

export interface AdminEmpresa {
  id_empresa: number;
  nombre: string;
  slug: string | null;
  servicios: Record<string, boolean>;
}

export interface AuthSession {
  access_token: string;
  usuario: AdminUser;
  empresa: AdminEmpresa;
}

export function saveSession(session: AuthSession): void {
  sessionStorage.setItem(TOKEN_KEY, session.access_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify({ usuario: session.usuario, empresa: session.empresa }));
}

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getSession(): { usuario: AdminUser; empresa: AdminEmpresa } | null {
  const raw = sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function updateSessionEmpresa(empresa: AdminEmpresa): void {
  const session = getSession();
  if (!session) return;
  sessionStorage.setItem(USER_KEY, JSON.stringify({ ...session, empresa }));
}

export function clearSession(): void {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}