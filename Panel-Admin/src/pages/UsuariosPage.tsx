import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Pencil, Power, ShieldCheck, User, Trash2 } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import type { Usuario, UsuarioListResponse, UsuarioCreateRequest } from "../types/usuarios";
import type { Empresa, EmpresaListResponse } from "../types/empresas";

// ─── Modal Alta ───────────────────────────────────────────────────────────────

interface ModalAltaProps {
  onClose: () => void;
  onCreated: (u: Usuario) => void;
}

function ModalAlta({ onClose, onCreated }: ModalAltaProps) {
  const ownEmpresaId = getSession()?.empresa.id_empresa;

  const [form, setForm] = useState<UsuarioCreateRequest>({
    nombre: "",
    email: "",
    password: "",
    es_superadmin: false,
    id_empresa: null,
  });
  const [confirmar, setConfirmar] = useState("");
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<EmpresaListResponse>("/admin/empresas?activa=true").then((d) =>
      setEmpresas(d.empresas.filter((e) => e.id_empresa !== ownEmpresaId))
    );
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!form.nombre.trim() || form.nombre.length < 2) {
      setError("El nombre debe tener al menos 2 caracteres.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      setError("El email no tiene un formato válido.");
      return;
    }
    if (form.password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (form.password !== confirmar) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    if (!form.es_superadmin && !form.id_empresa) {
      setError("La empresa es obligatoria para usuarios cliente.");
      return;
    }

    try {
      setSaving(true);
      const usuario = await api.post<Usuario>("/admin/usuarios", form);
      onCreated(usuario);
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
          <h2 className="text-base font-semibold text-gray-900">Nuevo usuario</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input
              type="text"
              value={form.nombre}
              onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Juan García"
              autoFocus
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="juan@empresa.com"
            />
          </div>

          {/* Contraseña */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Mínimo 8 caracteres"
            />
          </div>

          {/* Confirmar */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña *</label>
            <input
              type="password"
              value={confirmar}
              onChange={(e) => setConfirmar(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Repetir contraseña"
            />
          </div>

          {/* Rol */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Rol *</label>
            <div className="flex gap-4">
              {([false, true] as const).map((val) => (
                <label key={String(val)} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={form.es_superadmin === val}
                    onChange={() => setForm((f) => ({ ...f, es_superadmin: val, id_empresa: null }))}
                    className="accent-brand-600"
                  />
                  <span className="text-sm text-gray-700">{val ? "Superadmin" : "Cliente"}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Empresa (solo si cliente) */}
          {!form.es_superadmin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empresa *</label>
              <select
                value={form.id_empresa ?? ""}
                onChange={(e) => setForm((f) => ({ ...f, id_empresa: e.target.value ? Number(e.target.value) : null }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Seleccioná una empresa</option>
                {empresas.map((emp) => (
                  <option key={emp.id_empresa} value={emp.id_empresa}>{emp.nombre}</option>
                ))}
              </select>
            </div>
          )}

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
              {saving ? "Creando..." : "Crear usuario"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Listado ──────────────────────────────────────────────────────────────────

export default function UsuariosPage() {
  const navigate = useNavigate();
  const session = getSession();
  const ownUserId = session?.usuario.id_usuario;

  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [total, setTotal] = useState(0);
  const [filtroActivo, setFiltroActivo] = useState<"todos" | "activos" | "inactivos">("todos");
  const [filtroRol, setFiltroRol] = useState<"todos" | "superadmin" | "cliente">("todos");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [togglingId, setTogglingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filtroActivo === "activos") params.set("activo", "true");
      if (filtroActivo === "inactivos") params.set("activo", "false");
      if (filtroRol === "superadmin") params.set("es_superadmin", "true");
      if (filtroRol === "cliente") params.set("es_superadmin", "false");
      const qs = params.toString() ? `?${params}` : "";
      const data = await api.get<UsuarioListResponse>(`/admin/usuarios${qs}`);
      setUsuarios(data.usuarios);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [filtroActivo, filtroRol]);

  async function handleToggleActivo(usuario: Usuario) {
    if (usuario.id_usuario === ownUserId) return;
    setTogglingId(usuario.id_usuario);
    try {
      const updated = await api.patch<Usuario>(
        `/admin/usuarios/${usuario.id_usuario}/activo?activo=${!usuario.activo}`,
        {}
      );
      setUsuarios((prev) => prev.map((u) => u.id_usuario === updated.id_usuario ? updated : u));
    } finally {
      setTogglingId(null);
    }
  }

  async function handleDelete(usuario: Usuario) {
    if (!window.confirm(`¿Eliminar al usuario "${usuario.nombre ?? usuario.email}"? Esta acción no se puede deshacer.`)) return;
    setDeleteError(null);
    setDeletingId(usuario.id_usuario);
    try {
      await api.del(`/admin/usuarios/${usuario.id_usuario}`);
      setUsuarios((prev) => prev.filter((u) => u.id_usuario !== usuario.id_usuario));
      setTotal((t) => t - 1);
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Error al eliminar.");
    } finally {
      setDeletingId(null);
    }
  }

  function handleCreated(usuario: Usuario) {
    setShowModal(false);
    setUsuarios((prev) => [usuario, ...prev]);
    setTotal((t) => t + 1);
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Usuarios</h1>
          <p className="text-sm text-gray-500 mt-0.5">{total} usuario{total !== 1 ? "s" : ""} en total</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
        >
          <Plus size={16} />
          Nuevo usuario
        </button>
      </div>

      {/* Filtros */}
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        {(["todos", "activos", "inactivos"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFiltroActivo(f)}
            className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors capitalize ${
              filtroActivo === f
                ? "bg-brand-600 text-white"
                : "bg-white border border-gray-300 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <div className="w-px h-5 bg-gray-300 mx-1" />
        {(["todos", "superadmin", "cliente"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFiltroRol(f)}
            className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors capitalize ${
              filtroRol === f
                ? "bg-gray-800 text-white"
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
        ) : usuarios.length === 0 ? (
          <div className="py-16 text-center text-sm text-gray-400">No hay usuarios</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-brand-900 bg-brand-700">
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Usuario</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Empresa</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Rol</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-white uppercase tracking-wide">Activo</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {usuarios.map((usuario) => {
                const isOwn = usuario.id_usuario === ownUserId;
                return (
                  <tr key={usuario.id_usuario} className="hover:bg-gray-50 transition-colors">
                    {/* Usuario */}
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900">{usuario.nombre ?? "—"}</p>
                      <p className="text-xs text-gray-400 font-mono">{usuario.email}</p>
                    </td>

                    {/* Empresa */}
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {usuario.es_superadmin ? "—" : (usuario.empresa_nombre ?? "—")}
                    </td>

                    {/* Rol */}
                    <td className="px-4 py-3">
                      {usuario.es_superadmin ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-violet-100 text-violet-700">
                          <ShieldCheck size={11} /> Superadmin
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                          <User size={11} /> Cliente
                        </span>
                      )}
                    </td>

                    {/* Toggle activo */}
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleToggleActivo(usuario)}
                        disabled={isOwn || togglingId === usuario.id_usuario}
                        title={isOwn ? "No podés desactivarte a vos mismo" : (usuario.activo ? "Desactivar" : "Activar")}
                        className={`transition-colors disabled:opacity-30 ${
                          isOwn ? "cursor-not-allowed" :
                          usuario.activo ? "text-green-500 hover:text-red-400" : "text-gray-300 hover:text-green-500"
                        }`}
                      >
                        <Power size={16} />
                      </button>
                    </td>

                    {/* Acciones */}
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => navigate(`/usuarios/${usuario.id_usuario}/editar`)}
                          className="text-gray-400 hover:text-brand-600 transition-colors"
                          title="Editar"
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(usuario)}
                          disabled={isOwn || deletingId === usuario.id_usuario}
                          title={isOwn ? "No podés eliminar tu propio usuario" : "Eliminar"}
                          className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {deleteError && <p className="mt-3 text-sm text-red-600">{deleteError}</p>}

      {showModal && <ModalAlta onClose={() => setShowModal(false)} onCreated={handleCreated} />}
    </div>
  );
}