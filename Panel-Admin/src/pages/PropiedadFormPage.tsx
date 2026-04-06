import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, X, ImagePlus, Loader2 } from "lucide-react";
import { api, ApiError } from "../lib/api";
import {
  type ItemAdmin,
  type ItemCreateRequest,
  type CloudinarySignResponse,
  TIPOS_PROPIEDAD,
  CATEGORIAS_PROPIEDAD,
  MONEDAS,
  ESTADOS_CONSTRUCCION,
} from "../types/items";

// ── Helpers ───────────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-sm font-semibold text-gray-700 mb-4">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">{label}</label>
      {children}
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}

const inp = "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500";
const inpRO = "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-default";

// ── Cloudinary ────────────────────────────────────────────────────────────────

async function uploadToCloudinary(file: File): Promise<string> {
  const sign = await api.post<CloudinarySignResponse>("/admin/items/cloudinary-sign", {});
  const form = new FormData();
  form.append("file", file);
  form.append("api_key", sign.api_key);
  form.append("timestamp", String(sign.timestamp));
  form.append("signature", sign.signature);
  form.append("folder", sign.folder);
  if (sign.transformation) form.append("transformation", sign.transformation);

  const res = await fetch(
    `https://api.cloudinary.com/v1_1/${sign.cloud_name}/image/upload`,
    { method: "POST", body: form },
  );
  if (!res.ok) throw new Error("Error al subir imagen a Cloudinary");
  const data = await res.json();
  return data.secure_url as string;
}

// ── Estado inicial ────────────────────────────────────────────────────────────

function blankForm(): Omit<ItemCreateRequest, "external_id"> {
  return {
    tipo: "casa",
    categoria: "venta",
    titulo: "",
    descripcion: null,
    descripcion_corta: null,
    precio: null,
    moneda: "USD",
    destacado: false,
    atributos: {
      calle: "", barrio: "", ciudad: "",
      lat: null, lng: null,
      dormitorios: null, banios: null, ambientes: null,
      superficie_total: "", superficie_cubierta: "",
      antiguedad: "", estado_construccion: "",
      detalles: [],
    },
    fotos: [],
  };
}

// ── Componente ────────────────────────────────────────────────────────────────

export default function PropiedadFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [externalId, setExternalId] = useState<string>("");
  const [form, setForm]     = useState<Omit<ItemCreateRequest, "external_id">>(blankForm());
  const [activo, setActivo] = useState(true);
  const [loading, setLoading]   = useState(isEdit);
  const [saving, setSaving]     = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [detalle, setDetalle]   = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isEdit) return;
    api.get<ItemAdmin>(`/admin/items/${id}`)
      .then(item => {
        setExternalId(item.external_id);
        setActivo(item.activo);
        setForm({
          tipo: item.tipo,
          categoria: item.categoria,
          titulo: item.titulo,
          descripcion: item.descripcion,
          descripcion_corta: item.descripcion_corta,
          precio: item.precio,
          moneda: item.moneda ?? "USD",
          destacado: item.destacado,
          atributos: {
            calle: item.atributos?.calle ?? "",
            barrio: item.atributos?.barrio ?? "",
            ciudad: item.atributos?.ciudad ?? "",
            lat: item.atributos?.lat ?? null,
            lng: item.atributos?.lng ?? null,
            dormitorios: item.atributos?.dormitorios ?? null,
            banios: item.atributos?.banios ?? null,
            ambientes: item.atributos?.ambientes ?? null,
            superficie_total: item.atributos?.superficie_total ?? "",
            superficie_cubierta: item.atributos?.superficie_cubierta ?? "",
            antiguedad: item.atributos?.antiguedad ?? "",
            estado_construccion: item.atributos?.estado_construccion ?? "",
            detalles: item.atributos?.detalles ?? [],
          },
          fotos: item.media?.fotos ?? [],
        });
      })
      .catch(err => setError(err instanceof ApiError ? err.message : "Error al cargar"))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  function setField<K extends keyof typeof form>(k: K, v: (typeof form)[K]) {
    setForm(f => ({ ...f, [k]: v }));
  }
  function setAttr(k: string, v: unknown) {
    setForm(f => ({ ...f, atributos: { ...f.atributos, [k]: v } }));
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const url = await uploadToCloudinary(file);
      setField("fotos", [...form.fotos, url]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al subir foto");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  function addDetalle() {
    const v = detalle.trim();
    if (!v) return;
    setAttr("detalles", [...(form.atributos.detalles ?? []), v]);
    setDetalle("");
  }

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    if (!form.titulo || !form.tipo) {
      setError("Completá los campos obligatorios: Tipo y Título.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (isEdit) {
        await api.put(`/admin/items/${id}`, { ...form, activo });
      } else {
        await api.post("/admin/items", form);
      }
      navigate("/propiedades");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-8 text-gray-400">Cargando...</div>;

  const detalles = (form.atributos.detalles ?? []) as string[];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/propiedades")} className="text-gray-400 hover:text-gray-700 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEdit ? "Editar propiedad" : "Nueva propiedad"}
          </h1>
          {isEdit && externalId && (
            <p className="text-xs text-gray-400 mt-0.5 font-mono">{externalId}</p>
          )}
        </div>
      </div>

      {error && <div className="mb-4 bg-red-50 text-red-700 text-sm rounded-lg p-4">{error}</div>}

      <form onSubmit={handleSubmit}>
        {/* Layout 2 columnas en desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">

          {/* Columna izquierda */}
          <div className="space-y-4">

            {/* Identificación */}
            <Section title="Identificación">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Tipo *">
                  <select className={inp} value={form.tipo} onChange={e => setField("tipo", e.target.value)}>
                    {TIPOS_PROPIEDAD.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </Field>
                <Field label="Operación">
                  <select className={inp} value={form.categoria ?? ""} onChange={e => setField("categoria", e.target.value || null)}>
                    <option value="">— Sin especificar —</option>
                    {CATEGORIAS_PROPIEDAD.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                </Field>
              </div>
              <div className="flex gap-4 mt-4">
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input type="checkbox" checked={form.destacado} onChange={e => setField("destacado", e.target.checked)} className="w-4 h-4 rounded" />
                  Destacada
                </label>
                {isEdit && (
                  <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                    <input type="checkbox" checked={activo} onChange={e => setActivo(e.target.checked)} className="w-4 h-4 rounded" />
                    Activa (publicada)
                  </label>
                )}
              </div>
            </Section>

            {/* Descripción */}
            <Section title="Descripción">
              <div className="space-y-4">
                <Field label="Título *">
                  <input className={inp} value={form.titulo} onChange={e => setField("titulo", e.target.value)} placeholder="Casa Venta — Ramallo" required />
                </Field>
                <Field label="Descripción corta">
                  <input className={inp} value={form.descripcion_corta ?? ""} onChange={e => setField("descripcion_corta", e.target.value || null)} placeholder="Breve descripción para listados" />
                </Field>
                <Field label="Descripción completa">
                  <textarea className={`${inp} resize-none`} rows={4} value={form.descripcion ?? ""} onChange={e => setField("descripcion", e.target.value || null)} placeholder="Descripción detallada..." />
                </Field>
              </div>
            </Section>

            {/* Precio */}
            <Section title="Precio">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Valor">
                  <input
                    type="number"
                    className={inp}
                    value={form.precio ?? ""}
                    onChange={e => setField("precio", e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="Sin precio definido"
                    min={0}
                  />
                </Field>
                <Field label="Moneda">
                  <select className={inp} value={form.moneda ?? "USD"} onChange={e => setField("moneda", e.target.value)}>
                    {MONEDAS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </Field>
              </div>
            </Section>

            {/* Fotos */}
            <Section title="Fotos">
              {form.fotos.length > 0 && (
                <div className="grid grid-cols-4 gap-2 mb-3">
                  {form.fotos.map((url, i) => (
                    <div key={i} className="relative group">
                      <img src={url} alt="" className="w-full h-20 object-cover rounded-lg border border-gray-200" />
                      <button
                        type="button"
                        onClick={() => setField("fotos", form.fotos.filter((_, j) => j !== i))}
                        className="absolute top-1 right-1 p-0.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X size={11} />
                      </button>
                      {i === 0 && (
                        <span className="absolute bottom-1 left-1 bg-black/60 text-white text-xs px-1 py-0.5 rounded">Principal</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
              <button
                type="button"
                disabled={uploading}
                onClick={() => fileRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 border border-dashed border-gray-300 text-gray-500 text-sm rounded-lg hover:border-brand-400 hover:text-brand-600 transition-colors disabled:opacity-40"
              >
                {uploading ? <><Loader2 size={16} className="animate-spin" />Subiendo...</> : <><ImagePlus size={16} />Subir foto</>}
              </button>
            </Section>

          </div>

          {/* Columna derecha */}
          <div className="space-y-4">

            {/* Ubicación */}
            <Section title="Ubicación">
              <div className="grid grid-cols-2 gap-4">
                <Field label="Calle">
                  <input className={inp} value={(form.atributos.calle as string) ?? ""} onChange={e => setAttr("calle", e.target.value || undefined)} placeholder="San Martín al 500" />
                </Field>
                <Field label="Barrio">
                  <input className={inp} value={(form.atributos.barrio as string) ?? ""} onChange={e => setAttr("barrio", e.target.value || undefined)} placeholder="Centro" />
                </Field>
                <Field label="Ciudad">
                  <input className={inp} value={(form.atributos.ciudad as string) ?? ""} onChange={e => setAttr("ciudad", e.target.value || undefined)} placeholder="Ramallo" />
                </Field>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <Field label="Latitud" hint="Opcional — para el mapa">
                  <input type="number" step="any" className={inp} value={(form.atributos.lat as number) ?? ""} onChange={e => setAttr("lat", e.target.value ? parseFloat(e.target.value) : null)} placeholder="-33.4848" />
                </Field>
                <Field label="Longitud">
                  <input type="number" step="any" className={inp} value={(form.atributos.lng as number) ?? ""} onChange={e => setAttr("lng", e.target.value ? parseFloat(e.target.value) : null)} placeholder="-60.0080" />
                </Field>
              </div>
            </Section>

            {/* Características */}
            <Section title="Características">
              <div className="grid grid-cols-3 gap-4">
                <Field label="Dormitorios">
                  <input type="number" className={inp} value={(form.atributos.dormitorios as number) ?? ""} onChange={e => setAttr("dormitorios", e.target.value ? parseInt(e.target.value) : null)} placeholder="3" min={0} />
                </Field>
                <Field label="Baños">
                  <input type="number" className={inp} value={(form.atributos.banios as number) ?? ""} onChange={e => setAttr("banios", e.target.value ? parseInt(e.target.value) : null)} placeholder="2" min={0} />
                </Field>
                <Field label="Ambientes">
                  <input type="number" className={inp} value={(form.atributos.ambientes as number) ?? ""} onChange={e => setAttr("ambientes", e.target.value ? parseInt(e.target.value) : null)} placeholder="5" min={0} />
                </Field>
                <Field label="Sup. cubierta">
                  <input className={inp} value={(form.atributos.superficie_cubierta as string) ?? ""} onChange={e => setAttr("superficie_cubierta", e.target.value || undefined)} placeholder="120 m²" />
                </Field>
                <Field label="Sup. total">
                  <input className={inp} value={(form.atributos.superficie_total as string) ?? ""} onChange={e => setAttr("superficie_total", e.target.value || undefined)} placeholder="300 m²" />
                </Field>
                <Field label="Antigüedad">
                  <input className={inp} value={(form.atributos.antiguedad as string) ?? ""} onChange={e => setAttr("antiguedad", e.target.value || undefined)} placeholder="10 años" />
                </Field>
                <div className="col-span-3">
                  <Field label="Estado construcción">
                    <select className={inp} value={(form.atributos.estado_construccion as string) ?? ""} onChange={e => setAttr("estado_construccion", e.target.value || undefined)}>
                      <option value="">— Sin especificar —</option>
                      {ESTADOS_CONSTRUCCION.map(e => <option key={e.value} value={e.value}>{e.label}</option>)}
                    </select>
                  </Field>
                </div>
              </div>

              {/* Detalles / amenidades */}
              <div className="mt-4">
                <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">Detalles / amenidades</label>
                {detalles.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {detalles.map((d, i) => (
                      <span key={i} className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {d}
                        <button type="button" onClick={() => setAttr("detalles", detalles.filter((_, j) => j !== i))} className="text-gray-400 hover:text-red-500">
                          <X size={12} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex gap-2">
                  <input
                    className={`${inp} flex-1`}
                    value={detalle}
                    onChange={e => setDetalle(e.target.value)}
                    onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); addDetalle(); }}}
                    placeholder="pileta, parrilla, cochera..."
                  />
                  <button type="button" onClick={addDetalle} className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
                    Agregar
                  </button>
                </div>
              </div>
            </Section>

            {/* ID de solo lectura en edición */}
            {isEdit && (
              <Section title="Datos del sistema">
                <Field label="ID externo">
                  <input className={inpRO} value={externalId} readOnly />
                </Field>
              </Section>
            )}

          </div>
        </div>

        {/* Acciones */}
        <div className="flex items-center gap-3 pb-8">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-40 transition-colors"
          >
            {saving ? "Guardando..." : isEdit ? "Guardar cambios" : "Crear propiedad"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/propiedades")}
            className="px-6 py-2.5 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}