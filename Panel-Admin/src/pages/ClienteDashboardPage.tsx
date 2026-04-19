import { useEffect, useState, type ReactNode } from "react";
import {
  Users, MessageCircle, Building2, RefreshCw,
  AlertTriangle, CheckCircle, TrendingUp, Eye,
} from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import { ESTADOS_LEAD } from "../types/leads";

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface ClienteKPIs {
  leads_mes: number;
  leads_nuevos: number;
  conversaciones_mes: number;
  propiedades_activas: number;
  tokens_mes: number;
}

interface LeadResumen {
  fecha: string;
  nombre: string | null;
  telefono: string | null;
  propiedad_titulo: string | null;
  estado: string;
}

interface ActividadBot {
  conversaciones_mes: number;
  promedio_diario: number;
}

interface PropConLeads {
  external_id: string;
  titulo: string;
  ubicacion: string | null;
  leads_mes: number;
}

interface PropConsultada {
  external_id: string;
  titulo: string;
  ubicacion: string | null;
  consultas_mes: number;
}

interface AlertaCliente {
  tipo: string;
  mensaje: string;
}

interface ClienteDashboardResponse {
  empresa_nombre: string;
  kpis: ClienteKPIs;
  leads_recientes: LeadResumen[];
  actividad_bot: ActividadBot;
  props_con_leads: PropConLeads[];
  props_consultadas: PropConsultada[];
  alertas: AlertaCliente[];
  generado_en: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtFecha(iso: string) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
}

function EstadoBadge({ estado }: { estado: string }) {
  const def = ESTADOS_LEAD.find(e => e.value === estado);
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${def?.color ?? "bg-gray-100 text-gray-600"}`}>
      {def?.label ?? estado}
    </span>
  );
}

// ─── Componentes ──────────────────────────────────────────────────────────────

function KPICard({ icon, label, value, sub }: {
  icon: ReactNode; label: string; value: string | number; sub?: string;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-start gap-4">
      <div className="p-2.5 rounded-lg bg-brand-50 text-brand-600 shrink-0">{icon}</div>
      <div>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function PropRankItem({
  rank, externalId, titulo, ubicacion, count, countLabel, accent,
}: {
  rank: number;
  externalId: string;
  titulo: string;
  ubicacion: string | null;
  count: number;
  countLabel: string;
  accent: "green" | "blue";
}) {
  const badgeClass = accent === "green"
    ? "text-green-700 bg-green-50"
    : "text-brand-600 bg-brand-50";
  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
      <span className="text-xs font-bold text-gray-300 w-4 shrink-0 pt-0.5">{rank}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-xs font-mono font-semibold px-1.5 py-0.5 rounded ${badgeClass}`}>
            {externalId}
          </span>
          <span className="text-sm font-medium text-gray-800 truncate">{titulo}</span>
        </div>
        {ubicacion && (
          <p className="text-xs text-gray-400 mt-0.5">{ubicacion}</p>
        )}
      </div>
      <div className="shrink-0 text-right">
        <span className="text-lg font-bold text-gray-900">{count}</span>
        <p className="text-xs text-gray-400">{countLabel}</p>
      </div>
    </div>
  );
}

// ─── Página ───────────────────────────────────────────────────────────────────

export default function ClienteDashboardPage() {
  const [data, setData]       = useState<ClienteDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  const session = getSession();
  const nombreUsuario = session?.usuario.nombre ?? session?.empresa.nombre ?? "Bienvenido";

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ClienteDashboardResponse>("/cliente/dashboard");
      setData(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar el dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center text-gray-400 text-sm">
        Cargando dashboard...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-700 text-sm rounded-lg p-4">{error}</div>
      </div>
    );
  }

  const { kpis, leads_recientes, actividad_bot, props_con_leads, props_consultadas, alertas, generado_en } = data;

  return (
    <div className="p-8 space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hola, {nombreUsuario}</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            {data.empresa_nombre} · actualizado {fmtFecha(generado_en)}
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw size={14} /> Actualizar
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard icon={<Users         size={18}/>} label="Leads del mes"       value={kpis.leads_mes} />
        <KPICard icon={<Users         size={18}/>} label="Leads nuevos"        value={kpis.leads_nuevos} sub="Sin contactar" />
        <KPICard icon={<MessageCircle size={18}/>} label="Conversaciones"      value={kpis.conversaciones_mes} sub="(Mes actual)" />
        <KPICard icon={<Building2     size={18}/>} label="Propiedades activas" value={kpis.propiedades_activas} />
      </div>

      {/* Alertas */}
      {alertas.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {alertas.map((a, i) => (
            <div key={i} className="bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 flex items-center gap-3">
              <AlertTriangle size={15} className="text-yellow-500 shrink-0" />
              <p className="text-sm text-yellow-800">{a.mensaje}</p>
            </div>
          ))}
        </div>
      )}

      {alertas.length === 0 && (
        <div className="flex items-center gap-2 text-green-700 text-sm bg-green-50 rounded-xl px-4 py-3">
          <CheckCircle size={16}/> Todo en orden este mes
        </div>
      )}

      {/* Leads recientes + Actividad bot */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <div className="lg:col-span-2">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Leads recientes</h2>
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fecha</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Nombre</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Teléfono</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Propiedad</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {leads_recientes.map((l, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">{fmtFecha(l.fecha)}</td>
                    <td className="px-4 py-3 text-gray-800 font-medium">{l.nombre ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{l.telefono ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs max-w-[160px] truncate" title={l.propiedad_titulo ?? undefined}>
                      {l.propiedad_titulo ?? "—"}
                    </td>
                    <td className="px-4 py-3"><EstadoBadge estado={l.estado} /></td>
                  </tr>
                ))}
                {leads_recientes.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400 text-sm">
                      Sin leads registrados este mes.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Actividad del bot</h2>
          <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Conversaciones este mes</p>
              <p className="text-3xl font-bold text-gray-900">{actividad_bot.conversaciones_mes}</p>
            </div>
            <div className="border-t border-gray-100 pt-4">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Promedio diario</p>
              <p className="text-2xl font-bold text-gray-900">{actividad_bot.promedio_diario}</p>
              <p className="text-xs text-gray-400 mt-0.5">conversaciones por día</p>
            </div>
            {actividad_bot.conversaciones_mes === 0 && (
              <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
                El bot aún no registró conversaciones este mes.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Rendimiento de propiedades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Propiedades vinculadas a leads */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp size={15} className="text-green-600" />
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Propiedades vinculadas a leads</h2>
          </div>
          <p className="text-xs text-gray-400 mb-3">Propiedades asociadas a conversaciones que terminaron en contacto</p>
          <div className="bg-white rounded-xl border border-gray-200 px-4 py-2">
            {props_con_leads.length > 0 ? (
              props_con_leads.map((p, i) => (
                <PropRankItem
                  key={p.external_id + i}
                  rank={i + 1}
                  externalId={p.external_id}
                  titulo={p.titulo}
                  ubicacion={p.ubicacion}
                  count={p.leads_mes}
                  countLabel="leads"
                  accent="green"
                />
              ))
            ) : (
              <p className="text-sm text-gray-400 py-6 text-center">
                Todavía no hay propiedades vinculadas a leads este mes.
              </p>
            )}
          </div>
        </div>

        {/* Propiedades sin conversión */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Eye size={15} className="text-gray-500" />
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Propiedades sin conversión</h2>
          </div>
          <p className="text-xs text-gray-400 mb-3">Propiedades vistas en el Bot sin generar lead</p>
          <div className="bg-white rounded-xl border border-gray-200 px-4 py-2">
            {props_consultadas.length > 0 ? (
              props_consultadas.map((p, i) => (
                <PropRankItem
                  key={p.external_id + i}
                  rank={i + 1}
                  externalId={p.external_id}
                  titulo={p.titulo}
                  ubicacion={p.ubicacion}
                  count={p.consultas_mes}
                  countLabel="consultas"
                  accent="blue"
                />
              ))
            ) : (
              <p className="text-sm text-gray-400 py-6 text-center">
                Todavía no hay consultas sobre propiedades este mes.
              </p>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}
