import { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
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
  const [showPassword, setShowPassword] = useState(false);

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
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#061631' }}>
      <div className="w-full max-w-sm">
        {/* Logo completo con texto integrado */}
        <div className="text-center mb-8">
          <img src="/inmobot-logo-completo.png" alt="InmoBot" className="w-48 mx-auto" />
          <p className="text-white font-bold text-sm mt-2">Panel Administrativo</p>
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
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
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

            <div className="text-center pt-1">
              <Link
                to="/forgot-password"
                className="text-xs text-gray-400 hover:text-brand-600 transition-colors"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}