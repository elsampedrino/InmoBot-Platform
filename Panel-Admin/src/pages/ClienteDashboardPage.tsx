import { useEffect, useState, type ReactNode } from "react";
import {
  Users, MessageCircle, Building2, RefreshCw,
  AlertTriangle, CheckCircle, TrendingUp, Eye,
  Smartphone, Globe, Radio,
} from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import { ESTADOS_LEAD } from "../types/leads";

// ─── Tipos ────────────────────────────────────────────────────────────────────
// Refleja la arquitectura omnicanal del backend: "channels" es una lista
// dinámica, cada canal trae su propia lista de métricas de largo variable.
// El frontend no asume qué canales existen ni cuántas métricas trae cada uno.

interface Summary {
  leads_periodo: number;
  leads_nuevos: number;
  consultas_periodo: number;
  propiedades_activas: number;
  canales_activos: number;
  canales_disponibles: number; // reservado para upsell futuro — no se muestra todavía
}

interface ChannelMetric {
  key: string;
  label: string;
  value: number;
  format: "int" | "percent" | "currency";
  sub?: string | null;
}

interface ChannelBlock {
  type: string;
  label: string;
  icon: string;
  metrics: ChannelMetric[];
}

interface LeadResumen {
  fecha: string;
  nombre: string | null;
  telefono: string | null;
  propiedad_titulo: string | null;
  estado: string;
  canal: string;
}

interface Actividad {
  conversaciones_periodo: number;
  promedio_diario: number;
}

interface PropConLeads {
  external_id: string;
  titulo: string;
  ubicacion: string | null;
  leads_periodo: number;
}

interface PropConsultada {
  external_id: string;
  titulo: string;
  ubicacion: string | null;
  consultas_periodo: number;
}

interface Rankings {
  props_con_leads: PropConLeads[];
  props_consultadas: PropConsultada[];
}

interface AlertaCliente {
  tipo: string;
  mensaje: string;
}

interface ClienteDashboardResponse {
  empresa_nombre: string;
  periodo: string;
  generado_en: string;
  summary: Summary;
  channels: ChannelBlock[];
  leads_recientes: LeadResumen[];
  actividad: Actividad;
  rankings: Rankings;
  alertas: AlertaCliente[];
}

// ─── Config períodos ──────────────────────────────────────────────────────────

const PERIODOS = [
  { value: "mes_actual", label: "Este mes" },
  { value: "7d",         label: "7 días"   },
  { value: "30d",        label: "30 días"  },
  { value: "90d",        label: "90 días"  },
] as const;

// ─── Mapas por canal (únicos puntos de acoplamiento visual a un canal) ────────
// Agregar un canal nuevo (Instagram DM, Messenger, Telegram...) = una entrada
// más acá. Si no está mapeado, cae al default — nunca rompe el render.

const CHANNEL_ICONS: Record<string, ReactNode> = {
  web:      <Globe size={15} />,
  whatsapp: <Smartphone size={15} />,
};
const DEFAULT_CHANNEL_ICON = <Radio size={15} />;

const CHANNEL_ACCENT: Record<string, string> = {
  web:      "border-violet-200 hover:border-violet-400",
  whatsapp: "border-green-200 hover:border-green-400",
};
const DEFAULT_CHANNEL_ACCENT = "border-gray-200 hover:border-gray-400";

const CANAL_BADGE: Record<string, { label: string; className: string }> = {
  web:      { label: "Web", className: "bg-violet-100 text-violet-700" },
  whatsapp: { label: "WA",  className: "bg-green-100 text-green-700" },
};
const DEFAULT_CANAL_BADGE = { label: "—", className: "bg-gray-100 text-gray-600" };

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtFecha(iso: string) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
}

function formatMetricValue(value: number, format: ChannelMetric["format"]): string {
  if (format === "percent")  return `${value}%`;
  if (format === "currency") return `US$ ${value.toFixed(2)}`;
  return String(value);
}

function EstadoBadge({ estado }: { estado: string }) {
  const def = ESTADOS_LEAD.find(e => e.value === estado);
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${def?.color ?? "bg-gray-100 text-gray-600"}`}>
      {def?.label ?? estado}
    </span>
  );
}

function CanalBadge({ canal }: { canal: string }) {
  const cfg = CANAL_BADGE[canal] ?? { ...DEFAULT_CANAL_BADGE, label: canal };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}

// ─── Componentes ──────────────────────────────────────────────────────────────

function KPICard({ icon, label, value, sub }: {
  icon: ReactNode; label: string; value: string | number; sub?: string;
}) {
  return (
    <div className="bg-gradient-to-br from-violet-50 to-cyan-50 rounded-xl border border-violet-100 p-4 flex flex-col gap-2 hover:border-violet-300 hover:shadow-xl hover:scale-105 transition-all duration-300">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide leading-tight">{label}</p>
      <div className="flex items-center gap-2">
        <div className="p-2 rounded-lg bg-gray-900 text-white shrink-0">{icon}</div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
      {sub && <p className="text-xs text-gray-400">{sub}</p>}
    </div>
  );
}

function MetricTile({ label, value, sub, accentClass }: {
  label: string; value: string; sub?: string | null; accentClass: string;
}) {
  return (
    <div className={`flex-1 min-w-[140px] bg-white rounded-xl border p-4 flex flex-col gap-2 transition-all duration-200 ${accentClass}`}>
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide leading-tight">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400">{sub}</p>}
    </div>
  );
}

function ChannelCard({ channel }: { channel: ChannelBlock }) {
  const icon   = CHANNEL_ICONS[channel.type] ?? DEFAULT_CHANNEL_ICON;
  const accent = CHANNEL_ACCENT[channel.type] ?? DEFAULT_CHANNEL_ACCENT;
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{channel.label}</h3>
      </div>
      <div className="flex flex-wrap gap-3">
        {channel.metrics.map(m => (
          <MetricTile
            key={m.key}
            label={m.label}
            value={formatMetricValue(m.value, m.format)}
            sub={m.sub}
            accentClass={accent}
          />
        ))}
      </div>
    </div>
  );
}

function PropRankItem({
  rank, externalId, titulo, ubicacion, count, countLabel, dark = false,
}: {
  rank: number;
  externalId: string;
  titulo: string;
  ubicacion: string | null;
  count: number;
  countLabel: string;
  dark?: boolean;
}) {
  return (
    <div className={`flex items-start gap-3 py-3 border-b ${dark ? "border-white/20" : "border-gray-100"} last:border-0`}>
      <span className={`text-xs font-bold ${dark ? "text-white/50" : "text-gray-300"} w-4 shrink-0 pt-0.5`}>{rank}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-xs font-mono font-semibold px-1.5 py-0.5 rounded ${dark ? "text-white bg-white/20" : "text-brand-600 bg-brand-50"}`}>
            {externalId}
          </span>
          <span className={`text-sm font-medium ${dark ? "text-white" : "text-gray-800"} truncate`}>{titulo}</span>
        </div>
        {ubicacion && (
          <p className={`text-xs ${dark ? "text-white/70" : "text-gray-400"} mt-0.5`}>{ubicacion}</p>
        )}
      </div>
      <div className="shrink-0 text-right">
        <span className={`text-lg font-bold ${dark ? "text-white" : "text-gray-900"}`}>{count}</span>
        <p className={`text-xs ${dark ? "text-white/70" : "text-gray-400"}`}>{countLabel}</p>
      </div>
    </div>
  );
}

// ─── Página ───────────────────────────────────────────────────────────────────

export default function ClienteDashboardPage() {
  const [data, setData]       = useState<ClienteDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);
  const [periodo, setPeriodo] = useState("mes_actual");

  const session = getSession();
  const nombreUsuario = session?.usuario.nombre ?? session?.empresa.nombre ?? "Bienvenido";

  async function load(p = periodo) {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ClienteDashboardResponse>(`/cliente/dashboard?periodo=${p}`);
      setData(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar el dashboard");
    } finally {
      setLoading(false);
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(periodo); }, [periodo]);

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

  const { summary, channels, leads_recientes, actividad, rankings, alertas, generado_en } = data;

  return (
    <div className="p-4 md:p-8 space-y-8">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hola, {nombreUsuario}</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            {data.empresa_nombre} · actualizado {fmtFecha(generado_en)}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Selector de período */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1 gap-0.5">
            {PERIODOS.map(p => (
              <button
                key={p.value}
                onClick={() => { setPeriodo(p.value); }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  periodo === p.value
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
          <button
            onClick={() => load(periodo)}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
          >
            <RefreshCw size={14} /> Actualizar
          </button>
        </div>
      </div>

      {/* KPIs globales — independientes de canal */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard icon={<Users         size={18}/>} label="Leads del período"    value={summary.leads_periodo} />
        <KPICard icon={<Users         size={18}/>} label="Leads nuevos"         value={summary.leads_nuevos} sub="Sin contactar" />
        <KPICard icon={<MessageCircle size={18}/>} label="Consultas totales"    value={summary.consultas_periodo} />
        <KPICard icon={<Building2     size={18}/>} label="Propiedades activas"  value={summary.propiedades_activas} />
        <KPICard icon={<Radio         size={18}/>} label="Canales activos"      value={summary.canales_activos} />
      </div>

      {/* Rendimiento por canal — lista dinámica, una tarjeta por canal habilitado */}
      {channels.length > 0 && (
        <div className="space-y-5">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Rendimiento por Canal</h2>
          {channels.map(ch => <ChannelCard key={ch.type} channel={ch} />)}
        </div>
      )}

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
          <CheckCircle size={16}/> Todo en orden este período
        </div>
      )}

      {/* Leads recientes + Actividad */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <div className="lg:col-span-2">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Leads del período</h2>

          {/* Mobile: cards */}
          <div className="md:hidden bg-white rounded-xl border-2 border-brand-700 divide-y divide-gray-100">
            {leads_recientes.length === 0 ? (
              <p className="px-4 py-8 text-center text-gray-400 text-sm">Sin leads registrados.</p>
            ) : leads_recientes.map((l, i) => (
              <div key={i} className="px-4 py-3 flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="text-sm font-medium text-gray-800 truncate">{l.nombre ?? l.telefono ?? "—"}</p>
                    <CanalBadge canal={l.canal} />
                  </div>
                  <p className="text-xs text-gray-400 truncate">{fmtFecha(l.fecha)}{l.propiedad_titulo ? ` · ${l.propiedad_titulo}` : ""}</p>
                </div>
                <EstadoBadge estado={l.estado} />
              </div>
            ))}
          </div>

          {/* Desktop: tabla */}
          <div className="hidden md:block bg-white rounded-xl border-2 border-brand-700 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-brand-700 border-b border-brand-900">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Fecha</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Nombre</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Teléfono</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Propiedad</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Canal</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {leads_recientes.map((l, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">{fmtFecha(l.fecha)}</td>
                    <td className="px-4 py-3 text-gray-800 font-medium">{l.nombre ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{l.telefono ?? "—"}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs max-w-[140px] truncate" title={l.propiedad_titulo ?? undefined}>
                      {l.propiedad_titulo ?? "—"}
                    </td>
                    <td className="px-4 py-3"><CanalBadge canal={l.canal} /></td>
                    <td className="px-4 py-3"><EstadoBadge estado={l.estado} /></td>
                  </tr>
                ))}
                {leads_recientes.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">
                      Sin leads registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Actividad</h2>
          <div className="bg-white rounded-xl border-2 border-brand-700 p-5 space-y-4">
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Conversaciones del período</p>
              <p className="text-3xl font-bold text-gray-900">{actividad.conversaciones_periodo}</p>
              <p className="text-xs text-gray-400 mt-0.5">Todos los canales</p>
            </div>
            <div className="border-t border-gray-100 pt-4">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Promedio diario</p>
              <p className="text-2xl font-bold text-gray-900">{actividad.promedio_diario}</p>
              <p className="text-xs text-gray-400 mt-0.5">conversaciones por día</p>
            </div>
            {actividad.conversaciones_periodo === 0 && (
              <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
                El bot aún no registró conversaciones en este período.
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
          <div className="bg-[#3037AB] rounded-xl px-4 py-2 ring-2 ring-cyan-400 shadow-lg shadow-cyan-500/30">
            {rankings.props_con_leads.length > 0 ? (
              rankings.props_con_leads.map((p, i) => (
                <PropRankItem
                  key={p.external_id + i}
                  rank={i + 1}
                  externalId={p.external_id}
                  titulo={p.titulo}
                  ubicacion={p.ubicacion}
                  count={p.leads_periodo}
                  countLabel="leads"
                  dark={true}
                />
              ))
            ) : (
              <p className="text-sm text-white/70 py-6 text-center">
                Todavía no hay propiedades vinculadas a leads en este período.
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
          <div className="bg-cyan-600 rounded-xl px-4 py-2 ring-2 ring-cyan-400 shadow-lg shadow-cyan-500/30">
            {rankings.props_consultadas.length > 0 ? (
              rankings.props_consultadas.map((p, i) => (
                <PropRankItem
                  key={p.external_id + i}
                  rank={i + 1}
                  externalId={p.external_id}
                  titulo={p.titulo}
                  ubicacion={p.ubicacion}
                  count={p.consultas_periodo}
                  countLabel="consultas"
                  dark={true}
                />
              ))
            ) : (
              <p className="text-sm text-white/70 py-6 text-center">
                Todavía no hay consultas sobre propiedades en este período.
              </p>
            )}
          </div>
        </div>
      </div>

    </div>
  );
}
