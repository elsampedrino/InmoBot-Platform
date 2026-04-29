import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { saveSession, type AuthSession } from "../lib/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [error, setError]         = useState<string | null>(null);
  const [errorType, setErrorType] = useState<"error" | "info">("error");
  const [loading, setLoading]     = useState(false);

  useEffect(() => {
    if (searchParams.get("razon") === "panel_deshabilitado") {
      setError("El panel de cliente no está habilitado para esta empresa.");
      setErrorType("info");
    }
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setErrorType("error");
    setLoading(true);
    try {
      const session = await api.post<AuthSession>("/admin/auth/login", { email, password });
      saveSession(session);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
        setErrorType(err.status === 403 ? "info" : "error");
      } else {
        setError("No se pudo conectar con el servidor.");
        setErrorType("error");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-900 to-brand-700 px-4">
      <div className="w-full max-w-sm">
        {/* Logo/título */}
        <div className="text-center mb-8">
          <div className="mb-4">
            <img src="/inmobot-logo.jpg" alt="InmoBot" className="w-20 h-20 rounded-2xl mx-auto object-cover" />
          </div>
          <h1 className="text-2xl font-bold text-white">InmoBot Panel</h1>
          <p className="text-brand-100 text-sm mt-1">Panel Administrativo</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-6">Iniciar sesión</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className={errorType === "info"
                ? "bg-amber-50 border border-amber-200 text-amber-800 text-sm rounded-lg px-3 py-2"
                : "bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2"
              }>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
            >
              {loading ? "Ingresando..." : "Ingresar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}