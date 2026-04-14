import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import type { Usuario, UsuarioUpdateRequest, UsuarioResetPasswordRequest } from "../types/usuarios";
import type { Empresa, EmpresaListResponse } from "../types/empresas";

// ─── Helpers UI ───────────────────────────────────────────────────────────────

function Toggle({
  value,
  onChange,
  disabled = false,
}: {
  value: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={() => !disabled && onChange(!value)}
      disabled={disabled}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${value ? "bg-brand-600" : "bg-gray-300"}`}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${value ? "translate-x-6" : "translate-x-1"}`} />
    </button>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
      <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      {children}
    </div>
  );
}

function FieldRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      {children}
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────

export default function UsuarioFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const session = getSession();
  const isOwn = session?.usuario.id_usuario === Number(id);

  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [form, setForm] = useState<UsuarioUpdateRequest>({});
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sección contraseña
  const [showPassword, setShowPassword] = useState(false);
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [confirmarPassword, setConfirmarPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordOk, setPasswordOk] = useState(false);

  // Aviso de cambio de rol
  const rolCambiaASuperadmin = !usuario?.es_superadmin && form.es_superadmin === true;
  const rolCambiaACliente = usuario?.es_superadmin && form.es_superadmin === false;

  useEffect(() => {
    async function load() {
      try {
        const [userData, empresasData] = await Promise.all([
          api.get<Usuario>(`/admin/usuarios/${id}`),
          api.get<EmpresaListResponse>("/admin/empresas?activa=true"),
        ]);
        setUsuario(userData);
        setForm({
          nombre: userData.nombre ?? "",
          email: userData.email,
          es_superadmin: userData.es_superadmin,
          id_empresa: userData.id_empresa,
          activo: userData.activo,
        });
        const ownEmpresaId = session?.empresa.id_empresa;
        setEmpresas(empresasData.empresas.filter((e) => e.id_empresa !== ownEmpresaId));
      } catch {
        setError("No se pudo cargar el usuario.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!form.nombre?.trim() || form.nombre.length < 2) {
      setError("El nombre debe tener al menos 2 caracteres.");
      return;
    }
    if (!form.email?.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      setError("El email no tiene un formato válido.");
      return;
    }
    if (!isOwn && form.es_superadmin === false && !form.id_empresa) {
      setError("La empresa es obligatoria para usuarios cliente.");
      return;
    }

    try {
      setSaving(true);
      await api.put<Usuario>(`/admin/usuarios/${id}`, form);
      navigate("/usuarios");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar.");
    } finally {
      setSaving(false);
    }
  }

  async function handleResetPassword(e: React.FormEvent) {
    e.preventDefault();
    setPasswordError(null);
    setPasswordOk(false);

    if (nuevaPassword.length < 8) {
      setPasswordError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (nuevaPassword !== confirmarPassword) {
      setPasswordError("Las contraseñas no coinciden.");
      return;
    }

    try {
      setSavingPassword(true);
      const body: UsuarioResetPasswordRequest = { nueva_password: nuevaPassword };
      await api.post<void>(`/admin/usuarios/${id}/reset-password`, body);
      setNuevaPassword("");
      setConfirmarPassword("");
      setShowPassword(false);
      setPasswordOk(true);
      setTimeout(() => setPasswordOk(false), 3000);
    } catch (err) {
      setPasswordError(err instanceof ApiError ? err.message : "Error al cambiar contraseña.");
    } finally {
      setSavingPassword(false);
    }
  }

  if (loading) return <div className="p-8 text-sm text-gray-400">Cargando...</div>;
  if (!usuario) return <div className="p-8 text-sm text-red-500">{error}</div>;

  const esClienteActual = form.es_superadmin === false;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => navigate("/usuarios")} className="text-xs text-gray-400 hover:text-gray-600 mb-2">
          ← Volver a usuarios
        </button>
        <h1 className="text-xl font-semibold text-gray-900">
          {usuario.nombre ?? usuario.email}
          {isOwn && <span className="ml-2 text-xs font-normal text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full">Tu cuenta</span>}
        </h1>
      </div>

      <form onSubmit={handleSave}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* ── Col izquierda ── */}
          <div className="space-y-5">
            <Card title="Información">
              <Field label="Nombre *">
                <input
                  type="text"
                  value={form.nombre ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </Field>

              <Field label="Email *">
                <input
                  type="email"
                  value={form.email ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </Field>

              {/* Rol — deshabilitado para propio usuario */}
              <Field label="Rol">
                <div className="flex gap-4">
                  {([false, true] as const).map((val) => (
                    <label
                      key={String(val)}
                      className={`flex items-center gap-2 ${isOwn ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
                    >
                      <input
                        type="radio"
                        checked={form.es_superadmin === val}
                        onChange={() => !isOwn && setForm((f) => ({
                          ...f,
                          es_superadmin: val,
                          id_empresa: val ? null : f.id_empresa,
                        }))}
                        disabled={isOwn}
                        className="accent-brand-600"
                      />
                      <span className="text-sm text-gray-700">{val ? "Superadmin" : "Cliente"}</span>
                    </label>
                  ))}
                </div>
                {rolCambiaASuperadmin && (
                  <p className="text-xs text-amber-600 mt-1">Al guardar, esta cuenta perderá la asociación con su empresa.</p>
                )}
                {rolCambiaACliente && (
                  <p className="text-xs text-amber-600 mt-1">Necesitás asignar una empresa para este usuario.</p>
                )}
                {isOwn && (
                  <p className="text-xs text-gray-400 mt-1">No podés cambiar tu propio rol.</p>
                )}
              </Field>

              {/* Empresa — solo si cliente, deshabilitada para propio usuario */}
              {esClienteActual && (
                <Field label="Empresa *">
                  <select
                    value={form.id_empresa ?? ""}
                    onChange={(e) => setForm((f) => ({ ...f, id_empresa: e.target.value ? Number(e.target.value) : null }))}
                    disabled={isOwn}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                  >
                    <option value="">Seleccioná una empresa</option>
                    {empresas.map((emp) => (
                      <option key={emp.id_empresa} value={emp.id_empresa}>{emp.nombre}</option>
                    ))}
                  </select>
                  {isOwn && <p className="text-xs text-gray-400">No podés cambiar tu empresa desde acá.</p>}
                </Field>
              )}

              {/* Activo — deshabilitado para propio usuario */}
              <FieldRow label="Activo">
                <div className="flex flex-col items-end gap-1">
                  <Toggle
                    value={form.activo ?? true}
                    onChange={(v) => setForm((f) => ({ ...f, activo: v }))}
                    disabled={isOwn}
                  />
                  {isOwn && <p className="text-xs text-gray-400">No podés desactivarte a vos mismo.</p>}
                </div>
              </FieldRow>
            </Card>
          </div>

          {/* ── Col derecha ── */}
          <div className="space-y-5">
            <Card title="Contraseña">
              {!showPassword ? (
                <div>
                  <p className="text-sm text-gray-500 mb-3">
                    Podés establecer una nueva contraseña para este usuario.
                  </p>
                  <button
                    type="button"
                    onClick={() => setShowPassword(true)}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Cambiar contraseña
                  </button>
                  {passwordOk && (
                    <p className="mt-2 text-sm text-green-600">Contraseña actualizada correctamente.</p>
                  )}
                </div>
              ) : (
                <form onSubmit={handleResetPassword} className="space-y-3">
                  <Field label="Nueva contraseña *">
                    <input
                      type="password"
                      value={nuevaPassword}
                      onChange={(e) => setNuevaPassword(e.target.value)}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                      placeholder="Mínimo 8 caracteres"
                      autoFocus
                    />
                  </Field>
                  <Field label="Confirmar *">
                    <input
                      type="password"
                      value={confirmarPassword}
                      onChange={(e) => setConfirmarPassword(e.target.value)}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                      placeholder="Repetir contraseña"
                    />
                  </Field>
                  {passwordError && <p className="text-sm text-red-600">{passwordError}</p>}
                  <div className="flex gap-2 pt-1">
                    <button
                      type="submit"
                      disabled={savingPassword}
                      className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
                    >
                      {savingPassword ? "Guardando..." : "Guardar contraseña"}
                    </button>
                    <button
                      type="button"
                      onClick={() => { setShowPassword(false); setNuevaPassword(""); setConfirmarPassword(""); setPasswordError(null); }}
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
                    >
                      Cancelar
                    </button>
                  </div>
                </form>
              )}
            </Card>
          </div>
        </div>

        {/* Error general */}
        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        {/* Acciones */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate("/usuarios")}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
          >
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>
      </form>
    </div>
  );
}