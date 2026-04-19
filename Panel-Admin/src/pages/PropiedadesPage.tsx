import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Upload, Pencil, Power, PowerOff, Star } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import {
  type ItemAdmin,
  type ItemAdminListResponse,
  TIPOS_PROPIEDAD,
  CATEGORIAS_PROPIEDAD,
} from "../types/items";

export default function PropiedadesPage() {
  const navigate = useNavigate();
  const session = getSession();
  const hasLanding = session?.empresa.servicios?.catalogo_repo === true;

  const [items, setItems]         = useState<ItemAdmin[]>([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState<string | null>(null);

  const [filterActivo, setFilterActivo] = useState<"" | "true" | "false">("");
  const [filterTipo, setFilterTipo]     = useState("");

  const PAGE_SIZE = 20;

  async function fetchItems(p: number) {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(p), page_size: String(PAGE_SIZE) });
      if (filterActivo) params.set("activo", filterActivo);
      if (filterTipo)   params.set("tipo", filterTipo);
      const data = await api.get<ItemAdminListResponse>(`/admin/items?${params}`);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cargar propiedades");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchItems(page); }, [page, filterActivo, filterTipo]);

  async function handleToggleActivo(item: ItemAdmin) {
    try {
      const updated = await api.patch<ItemAdmin>(
        `/admin/items/${item.id_item}/activo?activo=${!item.activo}`, {},
      );
      setItems(prev => prev.map(i => i.id_item === updated.id_item ? updated : i));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cambiar el estado.");
    }
  }

  async function handleToggleDestacado(item: ItemAdmin) {
    try {
      const updated = await api.patch<ItemAdmin>(
        `/admin/items/${item.id_item}/destacado?destacado=${!item.destacado}`, {},
      );
      setItems(prev => prev.map(i => i.id_item === updated.id_item ? updated : i));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cambiar destacado.");
    }
  }

  async function handleExportLanding() {
    setExporting(true);
    setExportMsg(null);
    try {
      const res = await api.post<{ ok: boolean; total: number; message: string; commit_sha: string | null }>(
        "/admin/items/export-landing", {},
      );
      setExportMsg(`✓ ${res.message}${res.commit_sha ? ` (commit ${res.commit_sha})` : ""}`);
    } catch (err) {
      setExportMsg(`Error: ${err instanceof ApiError ? err.message : "No se pudo exportar."}`);
    } finally {
      setExporting(false);
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const tipoLabel = (tipo: string) => TIPOS_PROPIEDAD.find(t => t.value === tipo)?.label ?? tipo;
  const catLabel  = (cat: string | null) => CATEGORIAS_PROPIEDAD.find(c => c.value === cat)?.label ?? cat ?? "—";

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Propiedades</h1>
          <p className="text-sm text-gray-400 mt-0.5">{total} propiedades en total</p>
        </div>
        <div className="flex items-center gap-3">
          {hasLanding && (
            <button
              onClick={handleExportLanding}
              disabled={exporting}
              className="flex items-center gap-2 px-4 py-2 border border-brand-600 text-brand-600 text-sm font-medium rounded-lg hover:bg-brand-50 disabled:opacity-40 transition-colors"
            >
              <Upload size={16} />
              {exporting ? "Publicando..." : "Publicar Catálogo"}
            </button>
          )}
          <button
            onClick={() => navigate("/propiedades/nueva")}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
          >
            <Plus size={16} />
            Nueva propiedad
          </button>
        </div>
      </div>

      {exportMsg && (
        <div className={`mb-4 text-sm rounded-lg p-3 ${exportMsg.startsWith("Error") ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"}`}>
          {exportMsg}
        </div>
      )}

      {/* Filtros */}
      <div className="flex gap-3 mb-4">
        <select
          value={filterActivo}
          onChange={e => { setFilterActivo(e.target.value as "" | "true" | "false"); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">Todas (activas e inactivas)</option>
          <option value="true">Solo activas</option>
          <option value="false">Solo inactivas</option>
        </select>
        <select
          value={filterTipo}
          onChange={e => { setFilterTipo(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">Todos los tipos</option>
          {TIPOS_PROPIEDAD.map(t => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      {error && <div className="mb-4 bg-red-50 text-red-700 text-sm rounded-lg p-4">{error}</div>}

      {/* Tabla */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400 text-sm">Cargando...</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">No hay propiedades.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Propiedad</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Tipo</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Operación</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Precio</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Activa</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Destacada</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Editar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map(item => {
                const fotos = item.media?.fotos ?? [];
                return (
                  <tr key={item.id_item} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-400 font-mono text-xs">{item.external_id}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {fotos[0] ? (
                          <img src={fotos[0]} alt="" className="w-10 h-10 object-cover rounded-lg shrink-0" />
                        ) : (
                          <div className="w-10 h-10 rounded-lg bg-gray-100 shrink-0" />
                        )}
                        <div>
                          <p className="font-medium text-gray-800 leading-tight">{item.titulo}</p>
                          {item.atributos?.ciudad && (
                            <p className="text-xs text-gray-400 mt-0.5">{item.atributos.ciudad as string}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{tipoLabel(item.tipo)}</td>
                    <td className="px-4 py-3 text-gray-600">{catLabel(item.categoria)}</td>
                    <td className="px-4 py-3 text-right text-gray-800 font-medium">
                      {item.precio ? `${item.moneda ?? ""} ${item.precio.toLocaleString("es-AR")}` : "—"}
                    </td>

                    {/* Toggle Activo */}
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleToggleActivo(item)}
                        title={item.activo ? "Desactivar" : "Activar"}
                        className={`inline-flex items-center justify-center w-8 h-8 rounded-lg transition-colors ${
                          item.activo
                            ? "bg-green-100 text-green-700 hover:bg-red-100 hover:text-red-600"
                            : "bg-gray-100 text-gray-400 hover:bg-green-100 hover:text-green-700"
                        }`}
                      >
                        {item.activo ? <Power size={14} /> : <PowerOff size={14} />}
                      </button>
                    </td>

                    {/* Toggle Destacado */}
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleToggleDestacado(item)}
                        title={item.destacado ? "Quitar destacado" : "Marcar como destacada"}
                        className={`inline-flex items-center justify-center w-8 h-8 rounded-lg transition-colors ${
                          item.destacado
                            ? "bg-yellow-100 text-yellow-600 hover:bg-gray-100 hover:text-gray-400"
                            : "bg-gray-100 text-gray-300 hover:bg-yellow-100 hover:text-yellow-600"
                        }`}
                      >
                        <Star size={14} />
                      </button>
                    </td>

                    {/* Editar */}
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => navigate(`/propiedades/${item.id_item}/editar`)}
                        title="Editar"
                        className="inline-flex items-center justify-center w-8 h-8 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors"
                      >
                        <Pencil size={15} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <p className="text-xs text-gray-400">Página {page} de {totalPages} ({total} propiedades)</p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-xs border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1.5 text-xs border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}