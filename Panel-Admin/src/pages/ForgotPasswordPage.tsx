import { useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail]     = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent]       = useState(false);
  const [error, setError]     = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/admin/auth/forgot-password", { email });
      setSent(true);
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
          {sent ? (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-800">Revisá tu correo</h2>
              <p className="text-sm text-gray-500">
                Si el email está registrado, vas a recibir un link para restablecer tu contraseña. El link es válido por 30 minutos.
              </p>
              <Link to="/login" className="block text-sm text-brand-600 hover:underline mt-2">
                Volver al login
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-lg font-semibold text-gray-800 mb-2">Restablecer contraseña</h2>
              <p className="text-sm text-gray-500 mb-6">
                Ingresá tu email y te enviamos un link para crear una nueva contraseña.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                    placeholder="tu@email.com"
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
                  {loading ? "Enviando..." : "Enviar link"}
                </button>

                <div className="text-center pt-1">
                  <Link to="/login" className="text-xs text-gray-400 hover:text-brand-600 transition-colors">
                    Volver al login
                  </Link>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}