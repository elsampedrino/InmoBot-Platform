import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Copy, Check } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession, updateSessionEmpresa } from "../lib/auth";
import type {
  Empresa,
  EmpresaUpdateRequest,
  EmpresaServicios,
  EmpresaNotificaciones,
  CatalogoRepoConfig,
  CatalogoRepoUpdateRequest,
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
  const [catalogo, setCatalogo] = useState<CatalogoRepoConfig | null>(null);
  const [catalogoForm, setCatalogoForm] = useState<CatalogoRepoUpdateRequest>({});
  const [igConfig, setIgConfig] = useState<{ ig_user_id: string; page_id: string | null; token_configured: boolean; facebook_configurado: boolean; token_expires_at: string | null } | null>(null);
  const [igForm, setIgForm] = useState({ ig_user_id: "", page_id: "", access_token: "", token_expires_at: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [data, cat, ig] = await Promise.all([
          api.get<Empresa>(`/admin/empresas/${id}`),
          api.get<CatalogoRepoConfig | null>(`/admin/empresas/${id}/catalogo`).catch(() => null),
          api.get<{ ig_user_id: string; page_id: string | null; token_configured: boolean; facebook_configurado: boolean; token_expires_at: string | null }>(
            `/admin/instagram/config/${id}`
          ).catch(() => null),
        ]);
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
        if (cat) {
          setCatalogo(cat);
          setCatalogoForm({
            github_repo: cat.github_repo ?? "",
            github_branch: cat.github_branch ?? "main",
            github_path: cat.github_path ?? "",
            github_raw_url: cat.github_raw_url ?? "",
            catalog_source: cat.catalog_source ?? "github",
            export_format: cat.export_format ?? "inmo_v1",
          });
        }
        if (ig) {
          setIgConfig(ig);
          setIgForm({
            ig_user_id: ig.ig_user_id,
            page_id: ig.page_id ?? "",
            access_token: "",
            token_expires_at: ig.token_expires_at
              ? ig.token_expires_at.slice(0, 10)
              : "",
          });
        }
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
    if (form.servicios?.catalogo_repo) {
      if (!catalogoForm.github_repo?.trim()) {
        setError("El repositorio GitHub (owner/repo) es requerido cuando la publicación de catálogo está habilitada.");
        return;
      }
      if (!/^[\w.-]+\/[\w.-]+$/.test(catalogoForm.github_repo.trim())) {
        setError("El repositorio debe tener el formato owner/repo (ej: miusuario/mi-repo).");
        return;
      }
      if (!catalogoForm.github_path?.trim()) {
        setError("El archivo destino (path) es requerido para publicar el catálogo.");
        return;
      }
    }

    try {
      setSaving(true);
      const updated = await api.put<Empresa>(`/admin/empresas/${id}`, form);
      const session = getSession();
      if (session && Number(id) === session.empresa.id_empresa) {
        updateSessionEmpresa({
          id_empresa: updated.id_empresa,
          nombre: updated.nombre,
          slug: updated.slug ?? null,
          servicios: updated.servicios as unknown as Record<string, boolean>,
        });
      }
      if (form.servicios?.catalogo_repo) {
        await api.put<CatalogoRepoConfig>(`/admin/empresas/${id}/catalogo`, catalogoForm);
      }
      if ((form.servicios?.instagram || form.servicios?.facebook) && (igForm.ig_user_id.trim() || igForm.page_id.trim())) {
        await api.put(`/admin/instagram/config/${id}`, {
          ig_user_id: igForm.ig_user_id.trim(),
          page_id: igForm.page_id.trim() || null,
          access_token: igForm.access_token.trim() || null,
          token_expires_at: igForm.token_expires_at || null,
        });
      }
      setSaved(true);
      setTimeout(() => navigate("/empresas"), 1200);
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
              <FieldRow label="Landing page administrada">
                <Toggle
                  value={form.servicios?.landing ?? false}
                  onChange={(v) => setServicios({ landing: v })}
                />
              </FieldRow>
              <FieldRow label="Publicación de catálogo">
                <Toggle
                  value={form.servicios?.catalogo_repo ?? false}
                  onChange={(v) => setServicios({ catalogo_repo: v })}
                />
              </FieldRow>
              <FieldRow label="Panel cliente">
                <Toggle
                  value={form.servicios?.panel_cliente ?? false}
                  onChange={(v) => setServicios({ panel_cliente: v })}
                />
              </FieldRow>
              <FieldRow label="Publicación en Instagram">
                <Toggle
                  value={form.servicios?.instagram ?? false}
                  onChange={(v) => setServicios({ instagram: v })}
                />
              </FieldRow>
              <FieldRow label="Publicación en Facebook">
                <Toggle
                  value={form.servicios?.facebook ?? false}
                  onChange={(v) => setServicios({ facebook: v })}
                />
              </FieldRow>
            </Card>

            {/* Card: Configuración de repositorio (solo si catalogo_repo habilitado) */}
            {form.servicios?.catalogo_repo && (
              <Card title="Repositorio de catálogo">
                <p className="text-xs text-gray-400 -mt-2">
                  Destino GitHub donde se publica el catálogo (landing, bot, o ambos).
                </p>
                <Field label="Repositorio (owner/repo)">
                  <input
                    type="text"
                    value={catalogoForm.github_repo ?? ""}
                    onChange={(e) => setCatalogoForm((f) => ({ ...f, github_repo: e.target.value }))}
                    placeholder="ej: miusuario/mi-repo"
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </Field>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Branch">
                    <input
                      type="text"
                      value={catalogoForm.github_branch ?? ""}
                      onChange={(e) => setCatalogoForm((f) => ({ ...f, github_branch: e.target.value }))}
                      placeholder="main"
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </Field>
                  <Field label="Archivo destino">
                    <input
                      type="text"
                      value={catalogoForm.github_path ?? ""}
                      onChange={(e) => setCatalogoForm((f) => ({ ...f, github_path: e.target.value }))}
                      placeholder="propiedades.json"
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </Field>
                </div>
                <Field label="URL raw (para bot)">
                  <input
                    type="text"
                    value={catalogoForm.github_raw_url ?? ""}
                    onChange={(e) => setCatalogoForm((f) => ({ ...f, github_raw_url: e.target.value }))}
                    placeholder="https://raw.githubusercontent.com/..."
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                  <p className="text-xs text-gray-400">
                    Formato: raw.githubusercontent.com/{"{owner}/{repo}/{branch}/{path}"}
                  </p>
                </Field>
                {!catalogo && (
                  <p className="text-xs text-amber-600">
                    Esta empresa aún no tiene configuración de repositorio guardada.
                  </p>
                )}
              </Card>
            )}

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

            {/* Card: Instagram / Facebook (se muestra si alguno está habilitado) */}
            {(form.servicios?.instagram || form.servicios?.facebook) && (
              <Card title="Instagram / Facebook">
                <p className="text-xs text-gray-400 -mt-2">
                  Credenciales para publicar en redes sociales vía Meta Graph API.
                </p>

                {/* ── Sección Instagram ── */}
                {form.servicios?.instagram && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700 flex items-center gap-1.5">
                        <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-pink-500">
                          <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                          <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
                          <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
                        </svg>
                        Instagram
                      </span>
                      {igConfig?.ig_user_id ? (
                        <span className="text-xs font-medium px-2 py-0.5 bg-green-100 text-green-700 rounded-full">✓ Configurado</span>
                      ) : (
                        <span className="text-xs font-medium px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">No configurado</span>
                      )}
                    </div>
                    <Field label="IG User ID">
                      <input
                        type="text"
                        value={igForm.ig_user_id}
                        onChange={(e) => setIgForm((f) => ({ ...f, ig_user_id: e.target.value }))}
                        placeholder="ej: 17841400000000000"
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                      />
                      <p className="text-xs text-gray-400">ID numérico de la cuenta Business/Creator</p>
                    </Field>
                  </div>
                )}

                {/* ── Sección Facebook ── */}
                {form.servicios?.facebook && (
                  <div className={`space-y-3 ${form.servicios?.instagram ? "border-t border-gray-100 pt-3 mt-1" : ""}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-700 flex items-center gap-1.5">
                        <svg width={14} height={14} viewBox="0 0 24 24" fill="currentColor" className="text-blue-600">
                          <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.883v2.254h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
                        </svg>
                        Facebook
                      </span>
                      {igConfig?.facebook_configurado ? (
                        <span className="text-xs font-medium px-2 py-0.5 bg-green-100 text-green-700 rounded-full">✓ Configurado</span>
                      ) : (
                        <span className="text-xs font-medium px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">No configurado</span>
                      )}
                    </div>
                    <Field label="Page ID">
                      <input
                        type="text"
                        value={igForm.page_id}
                        onChange={(e) => setIgForm((f) => ({ ...f, page_id: e.target.value }))}
                        placeholder="ej: 1115827611611540"
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                      />
                      <p className="text-xs text-gray-400">ID numérico de la Página de Facebook</p>
                    </Field>
                  </div>
                )}

                {/* ── Token compartido ── */}
                <div className="border-t border-gray-100 pt-3 mt-1 space-y-3">
                  <Field label="Access Token">
                    <input
                      type="password"
                      value={igForm.access_token}
                      onChange={(e) => setIgForm((f) => ({ ...f, access_token: e.target.value }))}
                      placeholder={igConfig?.token_configured ? "••••••••  (token ya configurado)" : "Pegar Page Access Token de larga duración"}
                      autoComplete="new-password"
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                    <p className="text-xs text-gray-400">
                      Page Access Token — funciona para Instagram y Facebook. Dejar vacío para mantener el existente.
                    </p>
                  </Field>
                  <Field label="Vencimiento del token (opcional)">
                    <input
                      type="date"
                      value={igForm.token_expires_at}
                      onChange={(e) => setIgForm((f) => ({ ...f, token_expires_at: e.target.value }))}
                      className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </Field>
                </div>

                {!igConfig && (
                  <p className="text-xs text-amber-600">
                    Esta empresa aún no tiene redes sociales configuradas.
                  </p>
                )}
              </Card>
            )}

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
            {saving ? "Guardando..." : saved ? "✓ Guardado" : "Guardar cambios"}
          </button>
        </div>
      </form>
    </div>
  );
}