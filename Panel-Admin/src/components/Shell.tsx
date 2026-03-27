import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Building2,
  Users,
  LogOut,
  ChevronRight,
} from "lucide-react";
import { clearSession, getSession } from "../lib/auth";

const navItems = [
  { to: "/dashboard",   label: "Inicio",     icon: LayoutDashboard },
  { to: "/propiedades", label: "Propiedades", icon: Building2 },
  { to: "/leads",       label: "Leads",       icon: Users },
];

export default function Shell() {
  const navigate = useNavigate();
  const session = getSession();

  function handleLogout() {
    clearSession();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo / empresa */}
        <div className="px-6 py-5 border-b border-gray-200">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Panel Admin</p>
          <p className="text-sm font-semibold text-gray-800 truncate">
            {session?.empresa.nombre ?? "InmoBot"}
          </p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`
              }
            >
              <Icon size={18} />
              <span className="flex-1">{label}</span>
              <ChevronRight size={14} className="text-gray-300" />
            </NavLink>
          ))}
        </nav>

        {/* Footer usuario */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold">
              {session?.usuario.nombre?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">
                {session?.usuario.nombre ?? session?.usuario.email}
              </p>
              <p className="text-xs text-gray-400 truncate">{session?.usuario.email}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Cerrar sesión"
              className="text-gray-400 hover:text-red-500 transition-colors"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}