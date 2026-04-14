import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Copy, Check } from "lucide-react";
import { api, ApiError } from "../lib/api";
import type {
  Empresa,
  EmpresaUpdateRequest,
  EmpresaServicios,
  EmpresaNotificaciones,
} from "../types/empresas";
import { PLANES, TIMEZONES } from "../types/empresas";

// ─── Toggle helper ────────────────────────────────────────────────────────────

function Toggle({ value, onChange }: { value: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!value)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${value ? "bg-brand-600" : "bg-gray-300"}`}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${value ? "translate-x-6" : "translate-x-1"}`} />
    </button>
  );
}

// ─── Sección card ─────────────────────────────────────────────────────────────

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

export default function EmpresaFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [empresa, setEmpresa] = useState<Empresa | null>(null);
  const [form, setForm] = useState<EmpresaUpdateRequest>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<Empresa>(`/admin/empresas/${id}`);
        setEmpresa(data);
        setForm({
          nombre: data.nombre,
          id_plan: data.id_plan ?? 1,
          activa: data.activa,
          permite_followup: data.permite_followup,
          timezone: data.timezone,
          servicios: { ...data.servicios },
          notificaciones: {
            telegram: { ...data.notificaciones.telegram },
            email: { ...data.notificaciones.email },
          },
        });
      } catch {
        setError("No se pudo cargar la empresa.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  function setServicios(partial: Partial<EmpresaServicios>) {
    setForm((f) => ({ ...f, servicios: { ...f.servicios!, ...partial } }));
  }

  function setNotif(partial: Partial<EmpresaNotificaciones>) {
    setForm((f) => ({ ...f, notificaciones: { ...f.notificaciones!, ...partial } }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    // Validaciones
    if (!form.nombre?.trim() || form.nombre.length < 3) {
      setError("El nombre debe tener al menos 3 caracteres.");
      return;
    }
    const tg = form.notificaciones?.telegram;
    if (tg?.enabled && !tg.chat_id.trim()) {
      setError("El Chat ID de Telegram es requerido cuando está habilitado.");
      return;
    }
    const em = form.notificaciones?.email;
    if (em?.enabled && !em.to.trim()) {
      setError("El email destino es requerido cuando está habilitado.");
      return;
    }
    if (em?.enabled && em.to && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em.to)) {
      setError("El email destino no tiene un formato válido.");
      return;
    }

    try {
      setSaving(true);
      await api.put<Empresa>(`/admin/empresas/${id}`, form);
      navigate("/empresas");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar.");
    } finally {
      setSaving(false);
    }
  }

  async function copySlug() {
    if (empresa?.slug) {
      await navigator.clipboard.writeText(empresa.slug);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  if (loading) return <div className="p-8 text-sm text-gray-400">Cargando...</div>;
  if (!empresa) return <div className="p-8 text-sm text-red-500">{error}</div>;

  const tgEnabled = form.notificaciones?.telegram.enabled ?? false;
  const emailEnabled = form.notificaciones?.email.enabled ?? false;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => navigate("/empresas")} className="text-xs text-gray-400 hover:text-gray-600 mb-2">
          ← Volver a empresas
        </button>
        <h1 className="text-xl font-semibold text-gray-900">{empresa.nombre}</h1>
      </div>

      <form onSubmit={handleSave}>
        {/* Layout dos columnas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* ── Col izquierda ── */}
          <div className="space-y-5">

            {/* Card: Info general */}
            <Card title="Información general">
              <Field label="Nombre *">
                <input
                  type="text"
                  value={form.nombre ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </Field>

              <Field label="Slug">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={empresa.slug ?? ""}
                    readOnly
                    className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono bg-gray-50 text-gray-500 cursor-not-allowed"
                  />
                  <button
                    type="button"
                    onClick={copySlug}
                    title="Copiar slug"
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {copied ? <Check size={15} className="text-green-500" /> : <Copy size={15} />}
                  </button>
                </div>
                <p className="text-xs text-gray-400">Solo lectura — cambiar puede romper endpoints y el widget</p>
              </Field>

              <Field label="Timezone">
                <select
                  value={form.timezone ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  {TIMEZONES.map((tz) => (
                    <option key={tz} value={tz}>{tz}</option>
                  ))}
                </select>
              </Field>

              <FieldRow label="Activa">
                <Toggle value={form.activa ?? true} onChange={(v) => setForm((f) => ({ ...f, activa: v }))} />
              </FieldRow>
            </Card>

            {/* Card: Servicios */}
            <Card title="Servicios habilitados">
              <FieldRow label="Bot conversacional">
                <Toggle
                  value={form.servicios?.bot ?? true}
                  onChange={(v) => setServicios({ bot: v })}
                />
              </FieldRow>
              <FieldRow label="Landing page">
                <Toggle
                  value={form.servicios?.landing ?? false}
                  onChange={(v) => setServicios({ landing: v })}
                />
              </FieldRow>
            </Card>

          </div>

          {/* ── Col derecha ── */}
          <div className="space-y-5">

            {/* Card: Notificaciones */}
            <Card title="Notificaciones">
              {/* Telegram */}
              <div className="space-y-3">
                <FieldRow label="Telegram">
                  <Toggle
                    value={tgEnabled}
                    onChange={(v) => setNotif({ telegram: { ...form.notificaciones!.telegram, enabled: v } })}
                  />
                </FieldRow>
                {tgEnabled && (
                  <Field label="Chat ID">
                    <input
                      type="text"
                      value={form.notificaciones?.telegram.chat_id ?? ""}
                      onChange={(e) =>
                        setNotif({ telegram: { ...form.notificaciones!.telegram, chat_id: e.target.value } })
                      }
                      placeholder="ej: 8169006203"
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </Field>
                )}
              </div>

              <div className="border-t border-gray-100 pt-3 space-y-3">
                {/* Email */}
                <FieldRow label="Email">
                  <Toggle
                    value={emailEnabled}
                    onChange={(v) => setNotif({ email: { ...form.notificaciones!.email, enabled: v } })}
                  />
                </FieldRow>
                {emailEnabled && (
                  <Field label="Email destino">
                    <input
                      type="email"
                      value={form.notificaciones?.email.to ?? ""}
                      onChange={(e) =>
                        setNotif({ email: { ...form.notificaciones!.email, to: e.target.value } })
                      }
                      placeholder="ventas@empresa.com"
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </Field>
                )}
              </div>
            </Card>

            {/* Card: Operativa */}
            <Card title="Configuración operativa">
              <Field label="Plan">
                <select
                  value={form.id_plan ?? 1}
                  onChange={(e) => setForm((f) => ({ ...f, id_plan: Number(e.target.value) }))}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  {PLANES.map((p) => (
                    <option key={p.id} value={p.id}>{p.label}</option>
                  ))}
                </select>
              </Field>

              <FieldRow label="Follow-up automático">
                <Toggle
                  value={form.permite_followup ?? false}
                  onChange={(v) => setForm((f) => ({ ...f, permite_followup: v }))}
                />
              </FieldRow>
            </Card>

          </div>
        </div>

        {/* Error */}
        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        {/* Acciones */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate("/empresas")}
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