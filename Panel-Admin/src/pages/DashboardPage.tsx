import { useEffect, useState } from "react";
import {
  Building2, Users, Upload, GitBranch, Zap,
  AlertTriangle, CheckCircle, XCircle, RefreshCw,
} from "lucide-react";
import { api, ApiError } from "../lib/api";

// ─── Tipos ────────────────────────────────────────────────────────────────────

interface DashboardKPIs {
  empresas_activas: number;
  usuarios_activos: number;
  importaciones_mes: number;
  publicaciones_mes: number;
  tokens_mes: number;
}

interface EmpresaUso {
  id_empresa: number;
  nombre: string;
  plan: string | null;
  importaciones_mes: number;
  publicaciones_mes: number;
  leads_mes: number;
  tokens_mes: number;
  tokens_input: number;
  tokens_output: number;
  costo_usd: number;
  estado_consumo: "normal" | "alto" | "critico";
}

interface ActividadItem {
  fecha: string;
  empresa: string;
  accion: string;
  resultado: string;
  usuario: string | null;
  detalle: Record<string, unknown> | null;
}

interface Alerta {
  tipo: string;
  empresa: string;
  detalle: string;
}

interface DashboardResponse {
  kpis: DashboardKPIs;
  uso_por_empresa: EmpresaUso[];
  actividad_reciente: ActividadItem[];
  alertas: Alerta[];
  generado_en: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtTokens(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

function fmtFecha(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString("es-AR", {
    day: "2-digit", month: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
}

function accionLabel(accion: string) {
  if (accion === "aplicar_db")      return "Importación";
  if (accion === "publicar_github") return "Publicación";
  return accion;
}

const CONSUMO_STYLES = {
  normal:  "bg-green-100 text-green-700",
  alto:    "bg-yellow-100 text-yellow-700",
  critico: "bg-red-100 text-red-700",
};

const ALERTA_ICON: Record<string, JSX.Element> = {
  sin_notificaciones: <AlertTriangle size={14} className="text-yellow-500" />,
  sin_repo:           <AlertTriangle size={14} className="text-orange-500" />,
  alto:               <AlertTriangle size={14} className="text-yellow-500" />,
  critico:            <XCircle       size={14} className="text-red-500"    />,
};

// ─── Componentes pequeños ─────────────────────────────────────────────────────

function KPICard({ icon, label, value, sub }: {
  icon: JSX.Element; label: string; value: string | number; sub?: string;
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

// ─── Página principal ─────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [data, setData]       = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<DashboardResponse>("/admin/dashboard");
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

  const { kpis, uso_por_empresa, actividad_reciente, alertas, generado_en } = data;

  return (
    <div className="p-8 space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Datos del mes en curso · actualizado {fmtFecha(generado_en)}
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
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard icon={<Building2 size={18}/>} label="Empresas activas"    value={kpis.empresas_activas} />
        <KPICard icon={<Users      size={18}/>} label="Usuarios activos"    value={kpis.usuarios_activos} />
        <KPICard icon={<Upload     size={18}/>} label="Importaciones mes"   value={kpis.importaciones_mes} />
        <KPICard icon={<GitBranch  size={18}/>} label="Publicaciones mes"   value={kpis.publicaciones_mes} />
        <KPICard icon={<Zap        size={18}/>} label="Tokens consumidos"   value={fmtTokens(kpis.tokens_mes)} sub="este mes (global)" />
      </div>

      {/* Alertas */}
      {alertas.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Alertas operativas</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {alertas.map((a, i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-xl p-4 flex items-start gap-3">
                <div className="mt-0.5 shrink-0">{ALERTA_ICON[a.tipo] ?? <AlertTriangle size={14} className="text-gray-400"/>}</div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{a.empresa}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{a.detalle}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {alertas.length === 0 && (
        <div className="flex items-center gap-2 text-green-700 text-sm bg-green-50 rounded-xl px-4 py-3">
          <CheckCircle size={16}/> Sin alertas operativas este mes
        </div>
      )}

      {/* Uso por empresa */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Uso por empresa — mes en curso</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Empresa</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Plan</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Importaciones</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Publicaciones</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Leads</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tokens</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Costo est.</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Consumo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {uso_por_empresa.map(emp => (
                <tr key={emp.id_empresa} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">{emp.nombre}</td>
                  <td className="px-4 py-3 text-gray-500">{emp.plan ?? "—"}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{emp.importaciones_mes}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{emp.publicaciones_mes}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{emp.leads_mes}</td>
                  <td className="px-4 py-3 text-right text-gray-700 font-mono text-xs">
                    {fmtTokens(emp.tokens_mes)}
                    <span className="text-gray-400 ml-1">({fmtTokens(emp.tokens_input)}↑ {fmtTokens(emp.tokens_output)}↓)</span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-700">
                    {emp.costo_usd > 0 ? `$${emp.costo_usd.toFixed(3)}` : "—"}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${CONSUMO_STYLES[emp.estado_consumo]}`}>
                      {emp.estado_consumo}
                    </span>
                  </td>
                </tr>
              ))}
              {uso_por_empresa.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-400 text-sm">
                    Sin datos de uso este mes.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actividad reciente */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Actividad reciente</h2>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fecha</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Empresa</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Acción</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Resultado</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Usuario</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Detalle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {actividad_reciente.map((a, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-400 text-xs whitespace-nowrap">{fmtFecha(a.fecha)}</td>
                  <td className="px-4 py-3 text-gray-700 font-medium">{a.empresa}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                      a.accion === "publicar_github"
                        ? "bg-purple-100 text-purple-700"
                        : "bg-blue-100 text-blue-700"
                    }`}>
                      {accionLabel(a.accion)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                      a.resultado === "ok" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                    }`}>
                      {a.resultado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{a.usuario ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {a.detalle
                      ? Object.entries(a.detalle)
                          .filter(([, v]) => v !== null && v !== undefined)
                          .map(([k, v]) => `${k}: ${v}`)
                          .join(" · ")
                      : "—"}
                  </td>
                </tr>
              ))}
              {actividad_reciente.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-400 text-sm">
                    Sin actividad registrada.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
