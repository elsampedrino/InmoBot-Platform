import { getSession } from "../lib/auth";

export default function DashboardPage() {
  const session = getSession();

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Bienvenido, {session?.usuario.nombre ?? "Admin"}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Panel de administración — {session?.empresa.nombre}
        </p>
      </div>

      {/* Placeholder cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Propiedades activas", value: "—" },
          { label: "Leads este mes",      value: "—" },
          { label: "Conversaciones hoy",  value: "—" },
          { label: "Tasa de contacto",    value: "—" },
        ].map(card => (
          <div key={card.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              {card.label}
            </p>
            <p className="text-3xl font-bold text-gray-800">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
        <p className="text-sm text-gray-400 text-center py-8">
          Las estadísticas y gráficas se implementarán en la próxima fase.
        </p>
      </div>
    </div>
  );
}