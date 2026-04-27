import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { type Lead, type LeadListResponse, ESTADOS_LEAD } from "../types/leads";

function EstadoBadge({ estado }: { estado: string }) {
  const def = ESTADOS_LEAD.find(e => e.value === estado);
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${def?.color ?? "bg-gray-100 text-gray-600"}`}>
      {def?.label ?? estado}
    </span>
  );
}

function formatFecha(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-AR", {
    day: "2-digit", month: "2-digit", year: "numeric",
  });
}

function propiedadInteres(lead: Lead): string {
  const props = (lead.metadata?.propiedades_interes as Array<{ titulo?: string }> | undefined) ?? [];
  if (!props.length) return "—";
  if (props.length === 1) return props[0].titulo ?? "—";
  return `${props[0].titulo ?? "—"} (+${props.length - 1})`;
}

export default function LeadsPage() {
  const navigate = useNavigate();
  const [leads, setLeads]       = useState<Lead[]>([]);
  const [total, setTotal]       = useState(0);
  const [page, setPage]         = useState(1);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);

  // Filtros
  const [filtroEstado, setFiltroEstado] = useState("");
  const [fechaDesde, setFechaDesde]     = useState("");
  const [fechaHasta, setFechaHasta]     = useState("");

  const PAGE_SIZE = 20;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  async function fetchLeads(p: number) {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(p), page_size: String(PAGE_SIZE) });
      if (filtroEstado) params.set("estado", filtroEstado);
      if (fechaDesde)   params.set("fecha_desde", new Date(fechaDesde).toISOString());
      if (fechaHasta)   params.set("fecha_hasta", new Date(fechaHasta + "T23:59:59").toISOString());

      const data = await api.get<LeadListResponse>(`/admin/leads?${params}`);
      setLeads(data.leads);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cargar leads");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchLeads(page); }, [page]);

  function handleFiltrar() {
    setPage(1);
    fetchLeads(1);
  }

  function handleLimpiar() {
    setFiltroEstado("");
    setFechaDesde("");
    setFechaHasta("");
    setPage(1);
    // Trigger fetch con filtros vacíos directamente
    setLoading(true);
    api.get<LeadListResponse>(`/admin/leads?page=1&page_size=${PAGE_SIZE}`)
      .then(data => { setLeads(data.leads); setTotal(data.total); })
      .catch(err => setError(err instanceof ApiError ? err.message : "Error"))
      .finally(() => setLoading(false));
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        <p className="text-gray-500 text-sm mt-1">{total} leads en total</p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Estado</label>
          <select
            value={filtroEstado}
            onChange={e => setFiltroEstado(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">Todos</option>
            {ESTADOS_LEAD.map(e => (
              <option key={e.value} value={e.value}>{e.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Desde</label>
          <input
            type="date"
            value={fechaDesde}
            onChange={e => setFechaDesde(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
          <input
            type="date"
            value={fechaHasta}
            onChange={e => setFechaHasta(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <button
          onClick={handleFiltrar}
          className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
        >
          Filtrar
        </button>
        <button
          onClick={handleLimpiar}
          className="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
        >
          Limpiar
        </button>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {error && (
          <div className="p-4 bg-red-50 text-red-700 text-sm border-b border-red-100">{error}</div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-brand-900 bg-brand-700">
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Nombre</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Teléfono</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Email</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Estado</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Fecha</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Propiedad de interés</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-400">Cargando...</td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-400">No hay leads que coincidan con los filtros.</td>
                </tr>
              ) : (
                leads.map(lead => (
                  <tr
                    key={lead.id_lead}
                    onClick={() => navigate(`/leads/${lead.id_lead}`)}
                    className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">{lead.nombre ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-600">{lead.telefono ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-600">{lead.email ?? "—"}</td>
                    <td className="px-4 py-3"><EstadoBadge estado={lead.estado} /></td>
                    <td className="px-4 py-3 text-gray-500">{formatFecha(lead.created_at)}</td>
                    <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{propiedadInteres(lead)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Página {page} de {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-1.5 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}