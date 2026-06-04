import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  Users,
  LogOut,
  ChevronRight,
  Briefcase,
  UserCog,
  FileInput,
  KeyRound,
  Eye,
  EyeOff,
  X,
} from "lucide-react";
import { clearSession, getSession } from "../lib/auth";
import { api, ApiError } from "../lib/api";

const navItems = [
  { to: "/dashboard",    label: "Inicio",       icon: LayoutDashboard, superadmin: false, soloEmpresa: false },
  { to: "/propiedades",  label: "Propiedades",  icon: Building2,       superadmin: false, soloEmpresa: true  },
  { to: "/leads",        label: "Leads",        icon: Users,           superadmin: false, soloEmpresa: true  },
  { to: "/empresas",     label: "Empresas",     icon: Briefcase,       superadmin: true,  soloEmpresa: false },
  { to: "/usuarios",     label: "Usuarios",     icon: UserCog,         superadmin: true,  soloEmpresa: false },
  { to: "/importaciones",label: "Importaciones",icon: FileInput,       superadmin: true,  soloEmpresa: false },
];

export default function Shell() {
  const navigate = useNavigate();
  const session = getSession();

  const [showModal, setShowModal]         = useState(false);
  const [passActual, setPassActual]       = useState("");
  const [passNueva, setPassNueva]         = useState("");
  const [passConfirm, setPassConfirm]     = useState("");
  const [showPass, setShowPass]           = useState(false);
  const [saving, setSaving]               = useState(false);
  const [passError, setPassError]         = useState<string | null>(null);
  const [passOk, setPassOk]              = useState(false);

  function handleLogout() {
    clearSession();
    navigate("/login", { replace: true });
  }

  function openModal() {
    setPassActual(""); setPassNueva(""); setPassConfirm("");
    setPassError(null); setPassOk(false); setShowModal(true);
  }

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPassError(null);
    if (passNueva !== passConfirm) { setPassError("Las contraseñas nuevas no coinciden."); return; }
    if (passNueva.length < 8) { setPassError("La nueva contraseña debe tener al menos 8 caracteres."); return; }
    setSaving(true);
    try {
      await api.post("/admin/auth/change-password", { password_actual: passActual, password_nueva: passNueva });
      setPassOk(true);
      setTimeout(() => setShowModal(false), 1500);
    } catch (err) {
      if (err instanceof ApiError) setPassError(err.message);
      else setPassError("No se pudo conectar con el servidor.");
    } finally {
      setSaving(false);
    }
  }

  const visibleItems = navItems.filter(({ superadmin, soloEmpresa }) =>
    (!superadmin || session?.usuario.es_superadmin) &&
    (!soloEmpresa || !session?.usuario.es_superadmin)
  );

  return (
    <div className="flex h-screen bg-gray-50">

      {/* ── Sidebar — solo desktop ─────────────────────────────────────── */}
      <aside className="hidden md:flex w-64 bg-gray-900 flex-col">
        <div className="px-6 py-5 border-b border-gray-700">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Panel Admin</p>
          <p className="text-sm font-semibold text-white truncate">
            {session?.empresa.nombre ?? "InmoBot"}
          </p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {visibleItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-white text-brand-700 shadow"
                    : "text-gray-300 hover:bg-white hover:text-gray-900"
                }`
              }
            >
              <Icon size={18} />
              <span className="flex-1">{label}</span>
              <ChevronRight size={14} className="opacity-40" />
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold">
              {session?.usuario.nombre?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {session?.usuario.nombre ?? session?.usuario.email}
              </p>
              <p className="text-xs text-gray-400 truncate">{session?.usuario.email}</p>
            </div>
            <button
              onClick={openModal}
              title="Cambiar contraseña"
              className="text-gray-400 hover:text-brand-400 transition-colors"
            >
              <KeyRound size={15} />
            </button>
            <button
              onClick={handleLogout}
              title="Cerrar sesión"
              className="text-gray-400 hover:text-red-400 transition-colors"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Top bar — solo mobile ──────────────────────────────────────── */}
      <header className="md:hidden fixed top-0 inset-x-0 z-30 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-4 h-14">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest leading-none mb-0.5">
            Panel Admin
          </p>
          <p className="text-sm font-semibold text-white truncate">
            {session?.empresa.nombre ?? "InmoBot"}
          </p>
        </div>
        <div className="flex items-center gap-3 ml-3">
          <div className="w-7 h-7 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
            {session?.usuario.nombre?.[0]?.toUpperCase() ?? "?"}
          </div>
          <button
            onClick={openModal}
            title="Cambiar contraseña"
            className="text-gray-400 hover:text-brand-400 transition-colors p-1"
          >
            <KeyRound size={17} />
          </button>
          <button
            onClick={handleLogout}
            title="Cerrar sesión"
            className="text-gray-400 hover:text-red-400 transition-colors p-1"
          >
            <LogOut size={18} />
          </button>
        </div>
      </header>

      {/* ── Main content ───────────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto pt-14 md:pt-0 pb-16 md:pb-0">
        <Outlet />
      </main>

      {/* ── Bottom nav — solo mobile ───────────────────────────────────── */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-30 bg-gray-900 border-t border-gray-700 flex">
        {visibleItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] font-medium transition-colors ${
                isActive ? "text-white" : "text-gray-500"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className={`p-1 rounded-lg transition-colors ${isActive ? "bg-brand-600" : ""}`}>
                  <Icon size={18} />
                </span>
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

    </div>

    {/* ── Modal cambiar contraseña ───────────────────────────────────── */}
    {showModal && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-semibold text-gray-800">Cambiar contraseña</h2>
            <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
              <X size={18} />
            </button>
          </div>

          {passOk ? (
            <div className="text-center py-4 space-y-2">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-700">¡Contraseña actualizada!</p>
            </div>
          ) : (
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña actual</label>
                <div className="relative">
                  <input
                    type={showPass ? "text" : "password"}
                    required
                    value={passActual}
                    onChange={e => setPassActual(e.target.value)}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                    placeholder="••••••••"
                  />
                  <button type="button" onClick={() => setShowPass(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" tabIndex={-1}>
                    {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña</label>
                <input
                  type={showPass ? "text" : "password"}
                  required
                  minLength={8}
                  value={passNueva}
                  onChange={e => setPassNueva(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                  placeholder="Mínimo 8 caracteres"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar nueva contraseña</label>
                <input
                  type={showPass ? "text" : "password"}
                  required
                  minLength={8}
                  value={passConfirm}
                  onChange={e => setPassConfirm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
                  placeholder="Repetí la contraseña"
                />
              </div>

              {passError && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
                  {passError}
                </div>
              )}

              <div className="flex gap-3 pt-1">
                <button type="button" onClick={() => setShowModal(false)}
                  className="flex-1 border border-gray-300 text-gray-700 font-medium py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                  Cancelar
                </button>
                <button type="submit" disabled={saving}
                  className="flex-1 bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-medium py-2 rounded-lg text-sm transition-colors">
                  {saving ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    )}
  );
}
