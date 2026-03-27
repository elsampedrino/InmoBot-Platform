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

// ── Helper ────────────────────────────────────────────────────────────────────

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
        {label}
      </label>
      {children}
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}

const inputCls =
  "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500";

// ── Cloudinary upload ─────────────────────────────────────────────────────────

async function uploadToCloudinary(file: File): Promise<string> {
  const sign = await api.post<CloudinarySignResponse>("/admin/items/cloudinary-sign", {});
  const form = new FormData();
  form.append("file", file);
  form.append("api_key", sign.api_key);
  form.append("timestamp", String(sign.timestamp));
  form.append("signature", sign.signature);
  form.append("folder", sign.folder);

  const res = await fetch(
    `https://api.cloudinary.com/v1_1/${sign.cloud_name}/image/upload`,
    { method: "POST", body: form },
  );
  if (!res.ok) throw new Error("Error al subir imagen a Cloudinary");
  const data = await res.json();
  return data.secure_url as string;
}

// ── Blank form state ──────────────────────────────────────────────────────────

function blankForm(): ItemCreateRequest {
  return {
    external_id: "",
    tipo: "casa",
    categoria: "venta",
    titulo: "",
    descripcion: null,
    descripcion_corta: null,
    precio: null,
    moneda: "USD",
    destacado: false,
    atributos: {
      calle: "",
      barrio: "",
      ciudad: "",
      lat: null,
      lng: null,
      dormitorios: null,
      banios: null,
      ambientes: null,
      superficie_total: "",
      superficie_cubierta: "",
      antiguedad: "",
      estado_construccion: "",
      detalles: [],
    },
    fotos: [],
  };
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function PropiedadFormPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [form, setForm]         = useState<ItemCreateRequest>(blankForm());
  const [activo, setActivo]     = useState(true);
  const [loading, setLoading]   = useState(isEdit);
  const [saving, setSaving]     = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [detalle, setDetalle]   = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  // Cargar datos si es edición
  useEffect(() => {
    if (!isEdit) return;
    api.get<ItemAdmin>(`/admin/items/${id}`)
      .then(item => {
        const fotos = item.media?.fotos ?? [];
        setActivo(item.activo);
        setForm({
          external_id: item.external_id,
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
          fotos,
        });
      })
      .catch(err => setError(err instanceof ApiError ? err.message : "Error al cargar"))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  // Setters helpers
  function setField<K extends keyof ItemCreateRequest>(k: K, v: ItemCreateRequest[K]) {
    setForm(f => ({ ...f, [k]: v }));
  }
  function setAttr(k: string, v: unknown) {
    setForm(f => ({ ...f, atributos: { ...f.atributos, [k]: v } }));
  }

  // Fotos
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

  function removePhoto(idx: number) {
    setField("fotos", form.fotos.filter((_, i) => i !== idx));
  }

  // Detalles
  function addDetalle() {
    const v = detalle.trim();
    if (!v) return;
    setAttr("detalles", [...(form.atributos.detalles ?? []), v]);
    setDetalle("");
  }
  function removeDetalle(idx: number) {
    setAttr("detalles", (form.atributos.detalles ?? []).filter((_, i) => i !== idx));
  }

  // Submit
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.titulo || !form.external_id || !form.tipo) {
      setError("Completá los campos obligatorios: ID externo, Tipo y Título.");
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

  if (loading) {
    return <div className="p-8 text-gray-400">Cargando...</div>;
  }

  return (
    <div className="p-8 max-w-3xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate("/propiedades")}
          className="text-gray-400 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          {isEdit ? "Editar propiedad" : "Nueva propiedad"}
        </h1>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 text-red-700 text-sm rounded-lg p-4">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">

        {/* ── Identificación ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Identificación</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="ID externo *" hint='Ej: "PROP-042"'>
              <input
                className={inputCls}
                value={form.external_id}
                onChange={e => setField("external_id", e.target.value)}
                placeholder="PROP-001"
                required
              />
            </Field>
            <Field label="Tipo *">
              <select
                className={inputCls}
                value={form.tipo}
                onChange={e => setField("tipo", e.target.value)}
              >
                {TIPOS_PROPIEDAD.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Operación">
              <select
                className={inputCls}
                value={form.categoria ?? ""}
                onChange={e => setField("categoria", e.target.value || null)}
              >
                <option value="">— Sin especificar —</option>
                {CATEGORIAS_PROPIEDAD.map(c => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Estado">
              <div className="flex flex-col gap-2 pt-1">
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.destacado}
                    onChange={e => setField("destacado", e.target.checked)}
                    className="w-4 h-4 rounded"
                  />
                  Destacada
                </label>
                {isEdit && (
                  <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={activo}
                      onChange={e => setActivo(e.target.checked)}
                      className="w-4 h-4 rounded"
                    />
                    Activa (publicada)
                  </label>
                )}
              </div>
            </Field>
          </div>
        </div>

        {/* ── Descripción ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Descripción</h2>
          <div className="space-y-4">
            <Field label="Título *">
              <input
                className={inputCls}
                value={form.titulo}
                onChange={e => setField("titulo", e.target.value)}
                placeholder="Casa Venta — Ramallo"
                required
              />
            </Field>
            <Field label="Descripción corta">
              <input
                className={inputCls}
                value={form.descripcion_corta ?? ""}
                onChange={e => setField("descripcion_corta", e.target.value || null)}
                placeholder="Breve descripción para listados"
              />
            </Field>
            <Field label="Descripción completa">
              <textarea
                className={`${inputCls} resize-none`}
                rows={4}
                value={form.descripcion ?? ""}
                onChange={e => setField("descripcion", e.target.value || null)}
                placeholder="Descripción detallada de la propiedad..."
              />
            </Field>
          </div>
        </div>

        {/* ── Precio ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Precio</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Valor">
              <input
                type="number"
                className={inputCls}
                value={form.precio ?? ""}
                onChange={e => setField("precio", e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="0"
                min={0}
              />
            </Field>
            <Field label="Moneda">
              <select
                className={inputCls}
                value={form.moneda ?? "USD"}
                onChange={e => setField("moneda", e.target.value)}
              >
                {MONEDAS.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
            </Field>
          </div>
        </div>

        {/* ── Ubicación ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Ubicación</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Calle">
              <input
                className={inputCls}
                value={(form.atributos.calle as string) ?? ""}
                onChange={e => setAttr("calle", e.target.value || undefined)}
                placeholder="San Martín al 500"
              />
            </Field>
            <Field label="Barrio">
              <input
                className={inputCls}
                value={(form.atributos.barrio as string) ?? ""}
                onChange={e => setAttr("barrio", e.target.value || undefined)}
                placeholder="Centro"
              />
            </Field>
            <Field label="Ciudad">
              <input
                className={inputCls}
                value={(form.atributos.ciudad as string) ?? ""}
                onChange={e => setAttr("ciudad", e.target.value || undefined)}
                placeholder="Ramallo"
              />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <Field label="Latitud" hint="Opcional — para el mapa">
              <input
                type="number"
                step="any"
                className={inputCls}
                value={(form.atributos.lat as number) ?? ""}
                onChange={e => setAttr("lat", e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="-33.4848"
              />
            </Field>
            <Field label="Longitud">
              <input
                type="number"
                step="any"
                className={inputCls}
                value={(form.atributos.lng as number) ?? ""}
                onChange={e => setAttr("lng", e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="-60.0080"
              />
            </Field>
          </div>
        </div>

        {/* ── Características ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Características</h2>
          <div className="grid grid-cols-3 gap-4">
            <Field label="Dormitorios">
              <input
                type="number"
                className={inputCls}
                value={(form.atributos.dormitorios as number) ?? ""}
                onChange={e => setAttr("dormitorios", e.target.value ? parseInt(e.target.value) : null)}
                placeholder="3"
                min={0}
              />
            </Field>
            <Field label="Baños">
              <input
                type="number"
                className={inputCls}
                value={(form.atributos.banios as number) ?? ""}
                onChange={e => setAttr("banios", e.target.value ? parseInt(e.target.value) : null)}
                placeholder="2"
                min={0}
              />
            </Field>
            <Field label="Ambientes">
              <input
                type="number"
                className={inputCls}
                value={(form.atributos.ambientes as number) ?? ""}
                onChange={e => setAttr("ambientes", e.target.value ? parseInt(e.target.value) : null)}
                placeholder="5"
                min={0}
              />
            </Field>
            <Field label="Sup. cubierta">
              <input
                className={inputCls}
                value={(form.atributos.superficie_cubierta as string) ?? ""}
                onChange={e => setAttr("superficie_cubierta", e.target.value || undefined)}
                placeholder="120 m²"
              />
            </Field>
            <Field label="Sup. total">
              <input
                className={inputCls}
                value={(form.atributos.superficie_total as string) ?? ""}
                onChange={e => setAttr("superficie_total", e.target.value || undefined)}
                placeholder="300 m²"
              />
            </Field>
            <Field label="Antigüedad">
              <input
                className={inputCls}
                value={(form.atributos.antiguedad as string) ?? ""}
                onChange={e => setAttr("antiguedad", e.target.value || undefined)}
                placeholder="10 años"
              />
            </Field>
            <Field label="Estado construcción">
              <select
                className={inputCls}
                value={(form.atributos.estado_construccion as string) ?? ""}
                onChange={e => setAttr("estado_construccion", e.target.value || undefined)}
              >
                <option value="">— Sin especificar —</option>
                {ESTADOS_CONSTRUCCION.map(e => (
                  <option key={e.value} value={e.value}>{e.label}</option>
                ))}
              </select>
            </Field>
          </div>

          {/* Detalles / amenidades */}
          <div className="mt-4">
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">
              Detalles / amenidades
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {(form.atributos.detalles ?? []).map((d, i) => (
                <span
                  key={i}
                  className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                >
                  {d as string}
                  <button
                    type="button"
                    onClick={() => removeDetalle(i)}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                className={`${inputCls} flex-1`}
                value={detalle}
                onChange={e => setDetalle(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); addDetalle(); }}}
                placeholder="pileta, parrilla, cochera..."
              />
              <button
                type="button"
                onClick={addDetalle}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
              >
                Agregar
              </button>
            </div>
          </div>
        </div>

        {/* ── Fotos ── */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Fotos</h2>

          {/* Grid de fotos */}
          {form.fotos.length > 0 && (
            <div className="grid grid-cols-4 gap-3 mb-4">
              {form.fotos.map((url, i) => (
                <div key={i} className="relative group">
                  <img
                    src={url}
                    alt=""
                    className="w-full h-24 object-cover rounded-lg border border-gray-200"
                  />
                  <button
                    type="button"
                    onClick={() => removePhoto(i)}
                    className="absolute top-1 right-1 p-0.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X size={12} />
                  </button>
                  {i === 0 && (
                    <span className="absolute bottom-1 left-1 bg-black/60 text-white text-xs px-1.5 py-0.5 rounded">
                      Principal
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Upload */}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            type="button"
            disabled={uploading}
            onClick={() => fileRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 border border-dashed border-gray-300 text-gray-500 text-sm rounded-lg hover:border-brand-400 hover:text-brand-600 transition-colors disabled:opacity-40"
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <ImagePlus size={16} />
                Subir foto
              </>
            )}
          </button>
          <p className="text-xs text-gray-400 mt-2">
            Las fotos se suben directamente a Cloudinary. La primera foto es la imagen principal.
          </p>
        </div>

        {/* ── Acciones ── */}
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