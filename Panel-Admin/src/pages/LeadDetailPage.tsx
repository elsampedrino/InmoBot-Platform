import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { type LeadDetalle, type PropiedadDetalle, ESTADOS_LEAD } from "../types/leads";

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-sm text-gray-800">{value || "—"}</p>
    </div>
  );
}

function formatFecha(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [lead, setLead]         = useState<LeadDetalle | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const [saving, setSaving]     = useState(false);
  const [estado, setEstado]     = useState("");

  useEffect(() => {
    api.get<LeadDetalle>(`/admin/leads/${id}`)
      .then(data => { setLead(data); setEstado(data.estado); })
      .catch(err => setError(err instanceof ApiError ? err.message : "Error al cargar el lead"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleGuardarEstado() {
    if (!lead || estado === lead.estado) return;
    setSaving(true);
    setError(null);
    try {
      const data = await api.patch<LeadDetalle>(`/admin/leads/${id}`, { estado });
      setLead(data);
      setEstado(data.estado);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar el estado.");
    } finally {
      setSaving(false);
    }
  }

  const propiedades: PropiedadDetalle[] = lead?.propiedades_detalle ?? [];

  if (loading) {
    return <div className="p-8 text-gray-400">Cargando...</div>;
  }

  if (error || !lead) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-700 text-sm rounded-lg p-4">{error ?? "Lead no encontrado"}</div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate("/leads")}
          className="text-gray-400 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{lead.nombre ?? "Lead sin nombre"}</h1>
          <p className="text-gray-400 text-xs mt-0.5">ID #{lead.id_lead} · {formatFecha(lead.created_at)}</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Datos del cliente */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Datos del cliente</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Nombre"  value={lead.nombre} />
            <Field label="Teléfono" value={lead.telefono} />
            <Field label="Email"   value={lead.email} />
            <Field label="Canal"   value={lead.canal} />
          </div>
        </div>

        {/* Estado */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Estado del lead</h2>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              <select
                value={estado}
                onChange={e => setEstado(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {ESTADOS_LEAD.map(e => (
                  <option key={e.value} value={e.value}>{e.label}</option>
                ))}
              </select>
              <button
                onClick={handleGuardarEstado}
                disabled={saving || estado === lead.estado}
                className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-40 transition-colors"
              >
                {saving ? "Guardando..." : "Guardar"}
              </button>
              {estado === lead.estado && (
                <span className="text-xs text-green-500">✓ Guardado</span>
              )}
            </div>
            <p className="text-xs text-gray-400">
              {ESTADOS_LEAD.find(e => e.value === estado)?.tooltip}
            </p>
          </div>
        </div>

        {/* Propiedades de interés */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Propiedades de interés</h2>
          {propiedades.length === 0 ? (
            <p className="text-sm text-gray-400">Sin propiedades registradas.</p>
          ) : (
            <div className="space-y-3">
              {propiedades.map((p, i) => (
                <div key={i} className="flex gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <span className="w-6 h-6 rounded-full bg-brand-600 text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800">{p.titulo}</p>
                    {(p.direccion || p.ciudad) && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {[p.direccion, p.barrio, p.ciudad].filter(Boolean).join(", ")}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
                      {p.tipo && (
                        <span className="text-xs text-gray-400 capitalize">{p.tipo} · {p.categoria}</span>
                      )}
                      {p.dormitorios != null && (
                        <span className="text-xs text-gray-400">{p.dormitorios} dorm.</span>
                      )}
                      {p.banios != null && (
                        <span className="text-xs text-gray-400">{p.banios} baño{p.banios !== 1 ? "s" : ""}</span>
                      )}
                      {p.superficie_cubierta && (
                        <span className="text-xs text-gray-400">{p.superficie_cubierta} cub.</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}