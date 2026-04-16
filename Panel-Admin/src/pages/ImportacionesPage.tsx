import { useEffect, useRef, useState } from "react";
import {
  Upload,
  Eye,
  Database,
  GitBranch,
  CheckCircle2,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  RefreshCw,
} from "lucide-react";
import { api, ApiError } from "../lib/api";
import { getSession } from "../lib/auth";
import type { Empresa, EmpresaListResponse } from "../types/empresas";
import type {
  ImportacionPreviewResponse,
  ImportacionAplicarResponse,
  ImportacionPublicarResponse,
  ImportacionLog,
  ImportacionLogListResponse,
} from "../types/importaciones";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function badgeAccion(accion: string) {
  if (accion === "aplicar_db")
    return (
      <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
        Actualizar DB
      </span>
    );
  if (accion === "publicar_github")
    return (
      <span className="px-2 py-0.5 rounded text-xs font-medium bg-violet-100 text-violet-700">
        Publicar GitHub
      </span>
    );
  return <span className="text-xs text-gray-500">{accion}</span>;
}

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ─── Stat card ────────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className={`rounded-xl border px-5 py-4 flex flex-col gap-1 ${color}`}>
      <span className="text-2xl font-bold">{value}</span>
      <span className="text-xs font-medium">{label}</span>
    </div>
  );
}

// ─── Collapsible list ─────────────────────────────────────────────────────────

function CollapsibleList({
  title,
  items,
  color,
}: {
  title: string;
  items: { external_id: string; titulo: string; cambios?: string[] }[];
  color: string;
}) {
  const [open, setOpen] = useState(false);
  if (items.length === 0) return null;
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <span className={color}>
          {title} ({items.length})
        </span>
        {open ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
      </button>
      {open && (
        <ul className="divide-y divide-gray-100">
          {items.map((item) => (
            <li key={item.external_id} className="px-4 py-2 text-sm">
              <span className="font-mono text-xs text-gray-400 mr-2">
                {item.external_id}
              </span>
              <span className="text-gray-700">{item.titulo}</span>
              {item.cambios && item.cambios.length > 0 && (
                <span className="ml-2 text-xs text-amber-600">
                  ({item.cambios.join(", ")})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function ImportacionesPage() {
  const ownEmpresaId = getSession()?.empresa.id_empresa;

  // Selector de empresa
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [selectedEmpresaId, setSelectedEmpresaId] = useState<number | null>(null);
  const selectedEmpresa = empresas.find((e) => e.id_empresa === selectedEmpresaId) ?? null;
  const hasCatalogoRepo = selectedEmpresa?.servicios?.catalogo_repo === true;

  // Archivo
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [catalogoJson, setCatalogoJson] = useState<object | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);

  // Preview
  const [preview, setPreview] = useState<ImportacionPreviewResponse | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  // Aplicar
  const [applying, setApplying] = useState(false);
  const [applyResult, setApplyResult] = useState<ImportacionAplicarResponse | null>(null);
  const [applyError, setApplyError] = useState<string | null>(null);

  // Publicar
  const [publishing, setPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<ImportacionPublicarResponse | null>(null);
  const [publishError, setPublishError] = useState<string | null>(null);

  // Logs
  const [logs, setLogs] = useState<ImportacionLog[]>([]);
  const [logsTotal, setLogsTotal] = useState(0);
  const [logsLoading, setLogsLoading] = useState(false);

  // Cargar empresas
  useEffect(() => {
    api
      .get<EmpresaListResponse>("/admin/empresas?activa=true")
      .then((d) =>
        setEmpresas(d.empresas.filter((e) => e.id_empresa !== ownEmpresaId))
      );
  }, []);

  // Cargar logs cuando cambia empresa
  useEffect(() => {
    if (!selectedEmpresaId) return;
    loadLogs(selectedEmpresaId);
  }, [selectedEmpresaId]);

  async function loadLogs(id: number) {
    setLogsLoading(true);
    try {
      const d = await api.get<ImportacionLogListResponse>(
        `/admin/importaciones/logs?id_empresa=${id}&limit=20`
      );
      setLogs(d.logs);
      setLogsTotal(d.total);
    } finally {
      setLogsLoading(false);
    }
  }

  // Limpiar resultados al cambiar empresa o archivo
  function resetResults() {
    setPreview(null);
    setPreviewError(null);
    setApplyResult(null);
    setApplyError(null);
    setPublishResult(null);
    setPublishError(null);
  }

  function handleEmpresaChange(id: number | null) {
    setSelectedEmpresaId(id);
    resetResults();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileError(null);
    resetResults();
    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const parsed = JSON.parse(ev.target?.result as string);
        setCatalogoJson(parsed);
        setFileName(file.name);
      } catch {
        setFileError("El archivo no es un JSON válido.");
        setCatalogoJson(null);
        setFileName(null);
      }
    };
    reader.readAsText(file);
  }

  async function handlePreview() {
    if (!selectedEmpresaId || !catalogoJson) return;
    setPreviewError(null);
    setPreview(null);
    setPreviewing(true);
    try {
      const result = await api.post<ImportacionPreviewResponse>(
        "/admin/importaciones/preview",
        { id_empresa: selectedEmpresaId, catalogo: catalogoJson }
      );
      setPreview(result);
    } catch (err) {
      setPreviewError(err instanceof ApiError ? err.message : "Error al previsualizar.");
    } finally {
      setPreviewing(false);
    }
  }

  async function handleAplicarDb() {
    if (!selectedEmpresaId || !catalogoJson) return;
    setApplyError(null);
    setApplyResult(null);
    setApplying(true);
    try {
      const result = await api.post<ImportacionAplicarResponse>(
        "/admin/importaciones/aplicar-db",
        { id_empresa: selectedEmpresaId, catalogo: catalogoJson }
      );
      setApplyResult(result);
      // Refrescar logs y preview
      loadLogs(selectedEmpresaId);
      handlePreview();
    } catch (err) {
      setApplyError(err instanceof ApiError ? err.message : "Error al aplicar.");
    } finally {
      setApplying(false);
    }
  }

  async function handlePublicarGithub() {
    if (!selectedEmpresaId) return;
    setPublishError(null);
    setPublishResult(null);
    setPublishing(true);
    try {
      const result = await api.post<ImportacionPublicarResponse>(
        "/admin/importaciones/publicar-github",
        { id_empresa: selectedEmpresaId }
      );
      setPublishResult(result);
      loadLogs(selectedEmpresaId);
    } catch (err) {
      setPublishError(err instanceof ApiError ? err.message : "Error al publicar.");
    } finally {
      setPublishing(false);
    }
  }

  const canPreview = !!selectedEmpresaId && !!catalogoJson && !previewing;
  const canApply = !!preview && !!catalogoJson && !applying;
  const canPublish = !!selectedEmpresaId && hasCatalogoRepo && !publishing;

  return (
    <div className="p-6 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Importaciones de Catálogo</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Cargá un JSON estándar, previsualizá los cambios y actualizá la base de datos o publicá el catálogo al repositorio.
        </p>
      </div>

      {/* Step 1: Empresa + Archivo */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">1. Seleccioná empresa y archivo</h2>
        <div className="grid grid-cols-2 gap-4">
          {/* Empresa */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Empresa *</label>
            <select
              value={selectedEmpresaId ?? ""}
              onChange={(e) =>
                handleEmpresaChange(e.target.value ? Number(e.target.value) : null)
              }
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Seleccioná una empresa</option>
              {empresas.map((emp) => (
                <option key={emp.id_empresa} value={emp.id_empresa}>
                  {emp.nombre}
                </option>
              ))}
            </select>
            {selectedEmpresa && (
              <p className="mt-1 text-xs text-gray-400">
                Catálogo repo: {hasCatalogoRepo ? "✓ habilitado" : "✗ no habilitado"}
              </p>
            )}
          </div>

          {/* Archivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Archivo JSON *
            </label>
            <div
              className="w-full border border-dashed border-gray-300 rounded-lg px-3 py-2 text-sm cursor-pointer hover:border-brand-400 hover:bg-brand-50 transition-colors flex items-center gap-2"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={15} className="text-gray-400 shrink-0" />
              <span className={fileName ? "text-gray-800" : "text-gray-400"}>
                {fileName ?? "Hacé click para seleccionar"}
              </span>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,application/json"
              className="hidden"
              onChange={handleFileChange}
            />
            {fileError && <p className="mt-1 text-xs text-red-600">{fileError}</p>}
          </div>
        </div>

        {/* Botón previsualizar */}
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={handlePreview}
            disabled={!canPreview}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-900 disabled:opacity-40 transition-colors"
          >
            {previewing ? (
              <RefreshCw size={15} className="animate-spin" />
            ) : (
              <Eye size={15} />
            )}
            {previewing ? "Procesando..." : "Previsualizar cambios"}
          </button>
          {previewError && (
            <p className="text-sm text-red-600">{previewError}</p>
          )}
        </div>
      </div>

      {/* Step 2: Preview */}
      {preview && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">
            2. Resultado del análisis — {preview.total_json} items en JSON, {preview.total_db} en DB
          </h2>

          <div className="grid grid-cols-4 gap-3 mb-4">
            <StatCard
              label="Nuevos"
              value={preview.nuevos.length}
              color="border-green-200 text-green-700 bg-green-50"
            />
            <StatCard
              label="Modificados"
              value={preview.modificados.length}
              color="border-amber-200 text-amber-700 bg-amber-50"
            />
            <StatCard
              label="Sin cambios"
              value={preview.sin_cambios}
              color="border-gray-200 text-gray-600 bg-gray-50"
            />
            <StatCard
              label="A desactivar"
              value={preview.a_desactivar.length}
              color="border-red-200 text-red-700 bg-red-50"
            />
          </div>

          <div className="space-y-2">
            <CollapsibleList
              title="Nuevos"
              items={preview.nuevos}
              color="text-green-700"
            />
            <CollapsibleList
              title="Modificados"
              items={preview.modificados}
              color="text-amber-700"
            />
            <CollapsibleList
              title="A desactivar"
              items={preview.a_desactivar}
              color="text-red-700"
            />
          </div>
        </div>
      )}

      {/* Step 3: Acciones */}
      {preview && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">3. Acciones</h2>
          <div className="flex items-start gap-4">
            {/* Actualizar DB */}
            <div className="flex-1">
              <button
                onClick={handleAplicarDb}
                disabled={!canApply}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-40 transition-colors"
              >
                {applying ? (
                  <RefreshCw size={15} className="animate-spin" />
                ) : (
                  <Database size={15} />
                )}
                {applying ? "Aplicando..." : "Actualizar DB"}
              </button>
              <p className="mt-1.5 text-xs text-gray-400 text-center">
                Inserta, modifica y desactiva items en la base de datos.
              </p>
              {applyError && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                  <AlertCircle size={13} /> {applyError}
                </p>
              )}
              {applyResult && (
                <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
                  <CheckCircle2 size={13} /> {applyResult.message}
                </p>
              )}
            </div>

            <div className="pt-2 text-gray-300 text-sm font-medium self-start mt-1">o</div>

            {/* Publicar GitHub */}
            <div className="flex-1">
              <div title={!hasCatalogoRepo ? "Esta empresa no tiene habilitada la publicación de catálogo" : ""}>
                <button
                  onClick={handlePublicarGithub}
                  disabled={!canPublish}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-900 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {publishing ? (
                    <RefreshCw size={15} className="animate-spin" />
                  ) : (
                    <GitBranch size={15} />
                  )}
                  {publishing ? "Publicando..." : "Publicar en GitHub"}
                </button>
              </div>
              <p className="mt-1.5 text-xs text-gray-400 text-center">
                {hasCatalogoRepo
                  ? "Exporta los items activos de la DB al repositorio GitHub."
                  : "Requiere que la empresa tenga habilitada la publicación de catálogo."}
              </p>
              {publishError && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                  <AlertCircle size={13} /> {publishError}
                </p>
              )}
              {publishResult && (
                <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
                  <CheckCircle2 size={13} /> {publishResult.message}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Publicar sin preview (cuando ya hay items en DB) */}
      {!preview && selectedEmpresaId && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">
            Publicar catálogo actual en GitHub
          </h2>
          <p className="text-sm text-gray-500 mb-3">
            Podés publicar los items activos actuales de la DB sin necesidad de cargar un JSON.
          </p>
          <div
            title={
              !hasCatalogoRepo
                ? "Esta empresa no tiene habilitada la publicación de catálogo"
                : ""
            }
            className="inline-block"
          >
            <button
              onClick={handlePublicarGithub}
              disabled={!canPublish}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-900 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {publishing ? (
                <RefreshCw size={15} className="animate-spin" />
              ) : (
                <GitBranch size={15} />
              )}
              {publishing ? "Publicando..." : "Publicar en GitHub"}
            </button>
          </div>
          {publishError && (
            <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
              <AlertCircle size={13} /> {publishError}
            </p>
          )}
          {publishResult && (
            <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
              <CheckCircle2 size={13} /> {publishResult.message}
            </p>
          )}
        </div>
      )}

      {/* Historial de logs */}
      {selectedEmpresaId && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">
              Historial ({logsTotal})
            </h2>
            <button
              onClick={() => loadLogs(selectedEmpresaId)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Actualizar"
            >
              <RefreshCw size={14} className={logsLoading ? "animate-spin" : ""} />
            </button>
          </div>
          {logsLoading ? (
            <div className="py-10 text-center text-sm text-gray-400">Cargando...</div>
          ) : logs.length === 0 ? (
            <div className="py-10 text-center text-sm text-gray-400">
              No hay registros de importación
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">
                    Acción
                  </th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">
                    Empresa
                  </th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">
                    Detalle
                  </th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">
                    Usuario
                  </th>
                  <th className="text-left px-4 py-2.5 font-medium text-gray-600">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2.5">{badgeAccion(log.accion)}</td>
                    <td className="px-4 py-2.5 text-sm text-gray-700">
                      {log.empresa_nombre ?? "—"}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-gray-500">
                      {log.accion === "aplicar_db" && (
                        <>
                          +{String(log.detalle.insertados ?? 0)} &nbsp;
                          ~{String(log.detalle.actualizados ?? 0)} &nbsp;
                          -{String(log.detalle.desactivados ?? 0)}
                        </>
                      )}
                      {log.accion === "publicar_github" && (
                        <>
                          {String(log.detalle.total_propiedades ?? 0)} props
                          {log.detalle.commit_sha && (
                            <span className="ml-1 font-mono text-gray-400">
                              #{String(log.detalle.commit_sha)}
                            </span>
                          )}
                        </>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-gray-600">
                      {log.nombre_usuario ?? "—"}
                    </td>
                    <td className="px-4 py-2.5 text-gray-400 text-xs">
                      {formatDate(log.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}