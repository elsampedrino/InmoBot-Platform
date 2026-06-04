import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { api, ApiError } from "../lib/api";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword]       = useState("");
  const [confirmPassword, setConfirm] = useState("");
  const [showPass, setShowPass]       = useState(false);
  const [loading, setLoading]         = useState(false);
  const [done, setDone]               = useState(false);
  const [error, setError]             = useState<string | null>(null);

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "#061631" }}>
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-sm text-center space-y-4">
          <p className="text-red-600 font-medium">Link inválido o expirado.</p>
          <Link to="/forgot-password" className="text-sm text-brand-600 hover:underline">
            Solicitar un nuevo link
          </Link>
        </div>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setLoading(true);
    try {
      await api.post("/admin/auth/reset-password", { token, password_nueva: password });
      setDone(true);
      setTimeout(() => navigate("/login", { replace: true }), 2500);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("No se pudo conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "#061631" }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <img src="/inmobot-logo-completo.png" alt="InmoBot" className="w-48 mx-auto" />
          <p className="text-white font-bold text-sm mt-2">Panel Administrativo</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {done ? (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-800">¡Contraseña actualizada!</h2>
              <p className="text-sm text-gray-500">Redirigiendo al login...</p>
            </div>
          ) : (
            <>
              <h2 className="text-lg font-semibold text-gray-800 mb-6">Nueva contraseña</h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña</label>
                  <div className="relative">
                    <input
                      type={showPass ? "text" : "password"}
                      required
                      minLength={8}
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                      placeholder="Mínimo 8 caracteres"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPass(v => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                      tabIndex={-1}
                    >
                      {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña</label>
                  <input
                    type={showPass ? "text" : "password"}
                    required
                    minLength={8}
                    value={confirmPassword}
                    onChange={e => setConfirm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                    placeholder="Repetí la contraseña"
                  />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
                >
                  {loading ? "Guardando..." : "Guardar contraseña"}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}