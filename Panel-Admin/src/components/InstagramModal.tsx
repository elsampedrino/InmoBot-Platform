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

interface PreviewResponse {
  id_item: string;
  external_id: string;
  titulo: string;
  image_url: string | null;
  caption: string;
  item_activo: boolean;
  instagram_configurado: boolean;
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

export default function InstagramModal({
  idItem,
  onClose,
}: {
  idItem: string;
  onClose: () => void;
}) {
  const [preview, setPreview]       = useState<PreviewResponse | null>(null);
  const [caption, setCaption]       = useState("");
  const [loading, setLoading]       = useState(true);
  const [loadError, setLoadError]   = useState<string | null>(null);
  const [publishing, setPublishing] = useState(false);
  const [result, setResult]         = useState<PublishResult | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<PreviewResponse>(`/admin/instagram/preview/${idItem}`);
        setPreview(data);
        setCaption(data.caption);
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
    setPublishError(null);
    try {
      const res = await api.post<PublishResult>("/admin/instagram/publish", {
        id_item: idItem,
        caption,
      });
      setResult(res);
    } catch (e) {
      setPublishError(e instanceof ApiError ? e.message : "Error al publicar");
    } finally {
      setPublishing(false);
    }
  }

  const canPublish =
    preview?.item_activo && preview?.instagram_configurado && !!preview?.image_url;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl max-h-[90vh] overflow-y-auto">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2 text-pink-600">
            <IGIcon size={18} />
            <h2 className="text-base font-semibold text-gray-900">Publicar en Instagram</h2>
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

          {preview && !result && (
            <div className="space-y-5">

              {/* Propiedad */}
              <div>
                <p className="text-xs text-gray-400 font-mono">{preview.external_id}</p>
                <p className="text-sm font-medium text-gray-800">{preview.titulo}</p>
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
              {!preview.instagram_configurado && (
                <div className="flex items-center gap-2 bg-yellow-50 text-yellow-800 text-sm rounded-lg px-4 py-3">
                  <AlertTriangle size={15} className="shrink-0" />
                  Instagram no está configurado para esta empresa.
                </div>
              )}

              {/* Caption */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">
                  Caption{" "}
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

              {/* Última publicación */}
              {preview.ultima_publicacion && (
                <div className="text-xs text-gray-500 bg-gray-50 rounded-lg px-4 py-3">
                  <span className="font-medium">Última publicación:</span>{" "}
                  {preview.ultima_publicacion.status === "published" && preview.ultima_publicacion.published_at
                    ? `publicada el ${new Date(preview.ultima_publicacion.published_at).toLocaleString("es-AR")}`
                    : `estado: ${preview.ultima_publicacion.status}`}
                </div>
              )}

              {/* Error publicación */}
              {publishError && (
                <div className="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3">
                  {publishError}
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
                  disabled={!canPublish || publishing || !caption.trim()}
                  className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-sm font-medium rounded-lg hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  <IGIcon size={15} />
                  {publishing ? "Publicando..." : "Publicar ahora"}
                </button>
              </div>
            </div>
          )}

          {/* Success */}
          {result && (
            <div className="text-center py-8 space-y-3">
              <CheckCircle size={40} className="text-green-500 mx-auto" />
              <p className="text-base font-semibold text-gray-900">¡Publicado con éxito!</p>
              {result.published_at && (
                <p className="text-sm text-gray-400">
                  {new Date(result.published_at).toLocaleString("es-AR")}
                </p>
              )}
              {result.provider_post_id && (
                <p className="text-xs text-gray-300 font-mono">{result.provider_post_id}</p>
              )}
              <button
                onClick={onClose}
                className="mt-2 px-5 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cerrar
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
