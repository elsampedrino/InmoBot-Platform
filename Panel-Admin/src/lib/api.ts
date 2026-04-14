import { getToken, clearSession } from "./auth";

const BASE_URL = import.meta.env.VITE_API_URL ?? "https://api-premium-hyha.onrender.com";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (getToken()) {
      // Había sesión activa → expiró o fue revocada
      clearSession();
      window.location.href = "/login";
      throw new ApiError(401, "Sesión expirada");
    }
    // Sin sesión (ej: intento de login) → mostrar error real de la API
    const body = await res.json().catch(() => ({}));
    throw new ApiError(401, body.detail ?? "Credenciales inválidas");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? "Error inesperado");
  }

  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export const api = {
  get:  <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put:   <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT",   body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del:   <T>(path: string) => request<T>(path, { method: "DELETE" }),
};