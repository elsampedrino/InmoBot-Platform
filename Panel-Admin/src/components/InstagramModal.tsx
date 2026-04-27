import { useEffect, useState } from "react";
import { X, AlertTriangle, CheckCircle } from "lucide-react";
import { api, ApiError } from "../lib/api";

function IGIcon({ size = 15 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
    </svg>
  );
}

function FBIcon({ size = 15 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.883v2.254h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
    </svg>
  );
}

interface PreviewResponse {
  id_item: string;
  external_id: string;
  titulo: string;
  image_url: string | null;
  caption: string;
  item_activo: boolean;
  instagram_configurado: boolean;
  facebook_configurado: boolean;
  ultima_publicacion: {
    status: string;
    provider_post_id: string | null;
    published_at: string | null;
  } | null;
}

interface PublishResult {
  status: string;
  provider_post_id: string | null;
  published_at: string | null;
  error_message: string | null;
}

interface PlatformResult {
  result?: PublishResult;
  error?: string;
}

interface SocialResults {
  ig?: PlatformResult;
  fb?: PlatformResult;
}

export default function InstagramModal({
  idItem,
  onClose,
  igEnabled = true,
  fbEnabled = false,
}: {
  idItem: string;
  onClose: () => void;
  igEnabled?: boolean;
  fbEnabled?: boolean;
}) {
  const [preview, setPreview]       = useState<PreviewResponse | null>(null);
  const [titulo, setTitulo]         = useState("");
  const [caption, setCaption]       = useState("");
  const [loading, setLoading]       = useState(true);
  const [loadError, setLoadError]   = useState<string | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [results, setResults]       = useState<SocialResults | null>(null);
  const [publishToIG, setPublishToIG]   = useState(false);
  const [publishToFB, setPublishToFB]   = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<PreviewResponse>(`/admin/instagram/preview/${idItem}`);
        setPreview(data);
        setTitulo(data.titulo);
        setCaption(data.caption);
        setPublishToIG(igEnabled && data.instagram_configurado);
        setPublishToFB(fbEnabled && data.facebook_configurado);
      } catch (e) {
        setLoadError(e instanceof ApiError ? e.message : "Error al cargar preview");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [idItem]);

  async function handlePublish() {
    if (!preview) return;
    setPublishing(true);
    const partial: SocialResults = {};
    if (publishToIG) {
      try {
        partial.ig = { result: await api.post<PublishResult>("/admin/instagram/publish", { id_item: idItem, caption }) };
      } catch (e) {
        partial.ig = { error: e instanceof ApiError ? e.message : "Error al publicar en Instagram" };
      }
    }
    if (publishToFB) {
      try {
        partial.fb = { result: await api.post<PublishResult>("/admin/instagram/fb/publish", { id_item: idItem, caption }) };
      } catch (e) {
        partial.fb = { error: e instanceof ApiError ? e.message : "Error al publicar en Facebook" };
      }
    }
    setResults(partial);
    setPublishing(false);
  }

  const canPublish =
    (publishToIG || publishToFB) &&
    !!preview?.item_activo &&
    !!preview?.image_url &&
    !!caption.trim();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl max-h-[90vh] overflow-y-auto">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <span className="text-pink-500"><IGIcon size={18} /></span>
            <span className="text-blue-600"><FBIcon size={16} /></span>
            <h2 className="text-base font-semibold text-gray-900">Publicar en redes sociales</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">

          {loading && (
            <div className="text-center py-12 text-gray-400 text-sm">Cargando preview...</div>
          )}

          {loadError && (
            <div className="bg-red-50 text-red-700 text-sm rounded-lg p-4">{loadError}</div>
          )}

          {preview && !results && (
            <div className="space-y-5">

              {/* Título editable */}
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Título</label>
                <input
                  type="text"
                  value={titulo}
                  onChange={(e) => setTitulo(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {/* Imagen */}
              {preview.image_url ? (
                <div className="w-full aspect-square max-h-60 overflow-hidden rounded-xl bg-gray-100">
                  <img
                    src={preview.image_url}
                    alt={preview.titulo}
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-full aspect-square max-h-60 flex items-center justify-center bg-gray-100 rounded-xl">
                  <p className="text-sm text-gray-400">Sin imagen — no se puede publicar</p>
                </div>
              )}

              {/* Advertencias */}
              {!preview.item_activo && (
                <div className="flex items-center gap-2 bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3">
                  <AlertTriangle size={15} className="shrink-0" />
                  Esta propiedad está inactiva. Activala antes de publicar.
                </div>
              )}

              {/* Caption */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">
                  Texto de la publicación{" "}
                  <span className="text-xs text-gray-400 font-normal">
                    ({caption.length}/2200)
                  </span>
                </label>
                <textarea
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  rows={8}
                  maxLength={2200}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500 resize-y"
                />
              </div>

              {/* Selección de plataformas */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Publicar en:</label>
                <div className="flex gap-5">
                  {igEnabled && (
                    <label className={`flex items-center gap-2 text-sm select-none ${!preview.instagram_configurado ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}>
                      <input
                        type="checkbox"
                        checked={publishToIG}
                        onChange={(e) => setPublishToIG(e.target.checked)}
                        disabled={!preview.instagram_configurado}
                        className="rounded accent-pink-500"
                      />
                      <span className="text-pink-500"><IGIcon size={14} /></span>
                      Instagram
                      {!preview.instagram_configurado && (
                        <span className="text-xs text-gray-400">(no configurado)</span>
                      )}
                    </label>
                  )}
                  {fbEnabled && (
                    <label className={`flex items-center gap-2 text-sm select-none ${!preview.facebook_configurado ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}>
                      <input
                        type="checkbox"
                        checked={publishToFB}
                        onChange={(e) => setPublishToFB(e.target.checked)}
                        disabled={!preview.facebook_configurado}
                        className="rounded accent-blue-600"
                      />
                      <span className="text-blue-600"><FBIcon size={14} /></span>
                      Facebook
                      {!preview.facebook_configurado && (
                        <span className="text-xs text-gray-400">(no configurado)</span>
                      )}
                    </label>
                  )}
                </div>
              </div>

              {/* Última publicación */}
              {preview.ultima_publicacion && (
                <div className="text-xs text-gray-500 bg-gray-50 rounded-lg px-4 py-3">
                  <span className="font-medium">Última publicación (Instagram):</span>{" "}
                  {preview.ultima_publicacion.status === "published" && preview.ultima_publicacion.published_at
                    ? `publicada el ${new Date(preview.ultima_publicacion.published_at).toLocaleString("es-AR")}`
                    : `estado: ${preview.ultima_publicacion.status}`}
                </div>
              )}

              {/* Acciones */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handlePublish}
                  disabled={!canPublish || publishing}
                  className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-sm font-medium rounded-lg hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  {publishing ? "Publicando..." : "Publicar ahora"}
                </button>
              </div>
            </div>
          )}

          {/* Resultados */}
          {results && (() => {
            const allOk = (!results.ig || results.ig.result) && (!results.fb || results.fb.result);
            const anyOk = results.ig?.result || results.fb?.result;
            return (
              <div className="text-center py-8 space-y-4">
                {allOk
                  ? <CheckCircle size={40} className="text-green-500 mx-auto" />
                  : anyOk
                    ? <AlertTriangle size={40} className="text-yellow-500 mx-auto" />
                    : <AlertTriangle size={40} className="text-red-500 mx-auto" />
                }
                <p className="text-base font-semibold text-gray-900">
                  {allOk ? "¡Publicado con éxito!" : anyOk ? "Publicado parcialmente" : "Error al publicar"}
                </p>
                <div className="space-y-2 text-sm text-left max-w-xs mx-auto">
                  {results.ig && (
                    results.ig.result
                      ? <div className="flex items-center gap-2 text-green-700">
                          <CheckCircle size={14} className="shrink-0" />
                          <span className="text-pink-500"><IGIcon size={13} /></span>
                          Instagram — {results.ig.result.published_at
                            ? new Date(results.ig.result.published_at).toLocaleString("es-AR")
                            : "publicado"}
                        </div>
                      : <div className="flex items-start gap-2 text-red-600">
                          <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                          <span><span className="font-medium">Instagram:</span> {results.ig.error}</span>
                        </div>
                  )}
                  {results.fb && (
                    results.fb.result
                      ? <div className="flex items-center gap-2 text-green-700">
                          <CheckCircle size={14} className="shrink-0" />
                          <span className="text-blue-600"><FBIcon size={13} /></span>
                          Facebook — {results.fb.result.published_at
                            ? new Date(results.fb.result.published_at).toLocaleString("es-AR")
                            : "publicado"}
                        </div>
                      : <div className="flex items-start gap-2 text-red-600">
                          <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                          <span><span className="font-medium">Facebook:</span> {results.fb.error}</span>
                        </div>
                  )}
                </div>
                <button
                  onClick={onClose}
                  className="mt-2 px-5 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cerrar
                </button>
              </div>
            );
          })()}

        </div>
      </div>
    </div>
  );
}
