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
} from "lucide-react";
import { clearSession, getSession } from "../lib/auth";

const navItems = [
  { to: "/dashboard",   label: "Inicio",     icon: LayoutDashboard, superadmin: false, soloEmpresa: false },
  { to: "/propiedades", label: "Propiedades", icon: Building2,       superadmin: false, soloEmpresa: true  },
  { to: "/leads",       label: "Leads",       icon: Users,           superadmin: false, soloEmpresa: true  },
  { to: "/empresas",    label: "Empresas",    icon: Briefcase,       superadmin: true,  soloEmpresa: false },
  { to: "/usuarios",       label: "Usuarios",      icon: UserCog,   superadmin: true,  soloEmpresa: false },
  { to: "/importaciones",  label: "Importaciones", icon: FileInput, superadmin: true,  soloEmpresa: false },
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
      <aside className="w-64 bg-gray-900 flex flex-col">
        {/* Logo / empresa */}
        <div className="px-6 py-5 border-b border-gray-700">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">Panel Admin</p>
          <p className="text-sm font-semibold text-white truncate">
            {session?.empresa.nombre ?? "InmoBot"}
          </p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.filter(({ superadmin, soloEmpresa }) =>
            (!superadmin || session?.usuario.es_superadmin) &&
            (!soloEmpresa || !session?.usuario.es_superadmin)
          ).map(({ to, label, icon: Icon }) => (
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

        {/* Footer usuario */}
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
              onClick={handleLogout}
              title="Cerrar sesión"
              className="text-gray-400 hover:text-red-400 transition-colors"
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