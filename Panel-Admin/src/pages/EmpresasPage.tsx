import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Pencil, Power, Bot, Globe, Send, Mail, Trash2 } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import type { Empresa, EmpresaListResponse, EmpresaCreateRequest } from "../types/empresas";
import { PLANES, TIMEZONES } from "../types/empresas";

// ─── Utilidades ───────────────────────────────────────────────────────────────

function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s-]/g, "")
    .trim()
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

function planLabel(id: number | null): string {
  return PLANES.find((p) => p.id === id)?.label ?? String(id ?? "—");
}

// ─── Modal Alta ───────────────────────────────────────────────────────────────

interface ModalAltaProps {
  onClose: () => void;
  onCreated: (e: Empresa) => void;
}

function ModalAlta({ onClose, onCreated }: ModalAltaProps) {
  const [form, setForm] = useState<EmpresaCreateRequest>({
    nombre: "",
    slug: "",
    id_plan: 1,
    timezone: "America/Argentina/Buenos_Aires",
    activa: true,
  });
  const [slugManual, setSlugManual] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function handleNombre(nombre: string) {
    setForm((f) => ({
      ...f,
      nombre,
      slug: slugManual ? f.slug : slugify(nombre),
    }));
  }

  function handleSlug(slug: string) {
    setSlugManual(true);
    setForm((f) => ({ ...f, slug }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!form.nombre.trim() || form.nombre.length < 3) {
      setError("El nombre debe tener al menos 3 caracteres.");
      return;
    }
    if (!form.slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(form.slug)) {
      setError("El slug solo puede contener letras minúsculas, números y guiones.");
      return;
    }
    try {
      setSaving(true);
      const empresa = await api.post<Empresa>("/admin/empresas", form);
      onCreated(empresa);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error inesperado.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900">Nueva empresa</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input
              type="text"
              value={form.nombre}
              onChange={(e) => handleNombre(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="BBR Brucellaria Bienes Raíces"
              autoFocus
            />
          </div>

          {/* Slug */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
            <input
              type="text"
              value={form.slug}
              onChange={(e) => handleSlug(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="bbr-brucellaria"
            />
            <p className="text-xs text-gray-400 mt-1">
              {slugManual ? "Editado manualmente" : "Generado automáticamente desde el nombre"}
            </p>
          </div>

          {/* Plan */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plan *</label>
            <select
              value={form.id_plan}
              onChange={(e) => setForm((f) => ({ ...f, id_plan: Number(e.target.value) }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {PLANES.map((p) => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
            <select
              value={form.timezone}
              onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>{tz}</option>
              ))}
            </select>
          </div>

          {/* Activa */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Activa</span>
            <button
              type="button"
              onClick={() => setForm((f) => ({ ...f, activa: !f.activa }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${form.activa ? "bg-brand-600" : "bg-gray-300"}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${form.activa ? "translate-x-6" : "translate-x-1"}`} />
            </button>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
            >
              {saving ? "Creando..." : "Crear empresa"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Listado ──────────────────────────────────────────────────────────────────

export default function EmpresasPage() {
  const navigate = useNavigate();
  const session = getSession();
  const ownEmpresaId = session?.empresa.id_empresa;

  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [total, setTotal] = useState(0);
  const [filtroActiva, setFiltroActiva] = useState<"todas" | "activas" | "inactivas">("todas");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [togglingId, setTogglingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const params = filtroActiva === "activas" ? "?activa=true" : filtroActiva === "inactivas" ? "?activa=false" : "";
      const data = await api.get<EmpresaListResponse>(`/admin/empresas${params}`);
      const visible = data.empresas.filter((e) => e.id_empresa !== ownEmpresaId);
      setEmpresas(visible);
      setTotal(visible.length);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [filtroActiva]);

  async function handleToggleActiva(empresa: Empresa) {
    setTogglingId(empresa.id_empresa);
    try {
      const updated = await api.patch<Empresa>(
        `/admin/empresas/${empresa.id_empresa}/activa?activa=${!empresa.activa}`,
        {}
      );
      setEmpresas((prev) => prev.map((e) => e.id_empresa === updated.id_empresa ? updated : e));
    } finally {
      setTogglingId(null);
    }
  }

  async function handleDelete(empresa: Empresa) {
    if (!window.confirm(`¿Eliminar "${empresa.nombre}"? Esta acción no se puede deshacer.`)) return;
    setDeleteError(null);
    setDeletingId(empresa.id_empresa);
    try {
      await api.del(`/admin/empresas/${empresa.id_empresa}`);
      setEmpresas((prev) => prev.filter((e) => e.id_empresa !== empresa.id_empresa));
      setTotal((t) => t - 1);
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Error al eliminar.");
    } finally {
      setDeletingId(null);
    }
  }

  function handleCreated(empresa: Empresa) {
    setShowModal(false);
    setEmpresas((prev) => [empresa, ...prev]);
    setTotal((t) => t + 1);
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Empresas</h1>
          <p className="text-sm text-gray-500 mt-0.5">{total} empresa{total !== 1 ? "s" : ""} en total</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
        >
          <Plus size={16} />
          Nueva empresa
        </button>
      </div>

      {/* Filtro */}
      <div className="flex gap-2 mb-4">
        {(["todas", "activas", "inactivas"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFiltroActiva(f)}
            className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors capitalize ${
              filtroActiva === f
                ? "bg-brand-600 text-white"
                : "bg-white border border-gray-300 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="py-16 text-center text-sm text-gray-400">Cargando...</div>
        ) : empresas.length === 0 ? (
          <div className="py-16 text-center text-sm text-gray-400">No hay empresas</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">Empresa</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Plan</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Servicios</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Notificaciones</th>
                <th className="text-center px-4 py-3 font-medium text-gray-600">Activa</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {empresas.map((empresa) => (
                <tr key={empresa.id_empresa} className="hover:bg-gray-50 transition-colors">
                  {/* Empresa */}
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{empresa.nombre}</p>
                    <p className="text-xs text-gray-400 font-mono">{empresa.slug ?? "—"}</p>
                  </td>

                  {/* Plan */}
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                      {planLabel(empresa.id_plan)}
                    </span>
                  </td>

                  {/* Servicios */}
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${empresa.servicios.bot ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-400"}`}>
                        <Bot size={11} /> Bot
                      </span>
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${empresa.servicios.landing ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-400"}`}>
                        <Globe size={11} /> Landing
                      </span>
                    </div>
                  </td>

                  {/* Notificaciones */}
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <span title="Telegram">
                        <Send size={15} className={empresa.notificaciones.telegram.enabled ? "text-blue-500" : "text-gray-300"} />
                      </span>
                      <span title="Email">
                        <Mail size={15} className={empresa.notificaciones.email.enabled ? "text-green-500" : "text-gray-300"} />
                      </span>
                    </div>
                  </td>

                  {/* Toggle activa */}
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => handleToggleActiva(empresa)}
                      disabled={togglingId === empresa.id_empresa}
                      className={`transition-colors disabled:opacity-40 ${empresa.activa ? "text-green-500 hover:text-red-400" : "text-gray-300 hover:text-green-500"}`}
                      title={empresa.activa ? "Desactivar" : "Activar"}
                    >
                      <Power size={16} />
                    </button>
                  </td>

                  {/* Acciones */}
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-3">
                      <button
                        onClick={() => navigate(`/empresas/${empresa.id_empresa}/editar`)}
                        className="text-gray-400 hover:text-brand-600 transition-colors"
                        title="Editar"
                      >
                        <Pencil size={15} />
                      </button>
                      <button
                        onClick={() => handleDelete(empresa)}
                        disabled={deletingId === empresa.id_empresa}
                        className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-40"
                        title="Eliminar"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {deleteError && (
        <p className="mt-3 text-sm text-red-600">{deleteError}</p>
      )}

      {showModal && <ModalAlta onClose={() => setShowModal(false)} onCreated={handleCreated} />}
    </div>
  );
}