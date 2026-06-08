import { useState, useEffect } from "react";
import { api, ApiError } from "../lib/api";

const DAYS = [
  { key: "monday",    label: "Lunes"     },
  { key: "tuesday",   label: "Martes"    },
  { key: "wednesday", label: "Miércoles" },
  { key: "thursday",  label: "Jueves"    },
  { key: "friday",    label: "Viernes"   },
  { key: "saturday",  label: "Sábado"    },
  { key: "sunday",    label: "Domingo"   },
];

type DayConfig = { enabled: boolean; from?: string; to?: string };
type HorarioConfig = Record<string, DayConfig>;

const DEFAULT_HORARIO: HorarioConfig = {
  monday:    { enabled: true,  from: "09:30", to: "18:30" },
  tuesday:   { enabled: true,  from: "09:30", to: "18:30" },
  wednesday: { enabled: true,  from: "09:30", to: "18:30" },
  thursday:  { enabled: true,  from: "09:30", to: "18:30" },
  friday:    { enabled: true,  from: "09:30", to: "18:30" },
  saturday:  { enabled: false },
  sunday:    { enabled: false },
};

export default function BotConfigPage() {
  const [mode, setMode]               = useState<"always_on" | "after_hours">("always_on");
  const [horario, setHorario]         = useState<HorarioConfig>(DEFAULT_HORARIO);
  const [loading, setLoading]         = useState(true);
  const [saving, setSaving]           = useState(false);
  const [error, setError]             = useState<string | null>(null);
  const [saved, setSaved]             = useState(false);

  useEffect(() => {
    api.get<{ bot_mode: string; horario_config: HorarioConfig }>("/admin/bot-config")
      .then(data => {
        setMode(data.bot_mode as "always_on" | "after_hours");
        setHorario(data.horario_config ?? DEFAULT_HORARIO);
      })
      .catch(() => setError("No se pudo cargar la configuración."))
      .finally(() => setLoading(false));
  }, []);

  function toggleDay(key: string) {
    setHorario(h => ({
      ...h,
      [key]: { ...h[key], enabled: !h[key]?.enabled },
    }));
  }

  function setTime(key: string, field: "from" | "to", val: string) {
    setHorario(h => ({
      ...h,
      [key]: { ...h[key], [field]: val },
    }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSaved(false);
    setSaving(true);
    try {
      await api.put("/admin/bot-config", {
        bot_mode: mode,
        horario_config: mode === "after_hours" ? horario : undefined,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("No se pudo guardar la configuración.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return (
    <div className="p-6 text-sm text-gray-500">Cargando configuración...</div>
  );

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 mb-1">Modo de atención del bot</h1>
      <p className="text-sm text-gray-500 mb-6">
        Configurá cuándo responde el bot automáticamente por WhatsApp.
      </p>

      <form onSubmit={handleSave} className="space-y-6">

        {/* ── Selector de modo ─────────────────────────────────────────── */}
        <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
          {[
            {
              value: "always_on",
              label: "Siempre activo",
              desc: "El bot responde las 24 hs, todos los días.",
            },
            {
              value: "after_hours",
              label: "Fuera de horario",
              desc: "El bot responde solo cuando la oficina está cerrada.",
            },
          ].map(opt => (
            <label
              key={opt.value}
              className="flex items-start gap-4 px-5 py-4 cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <input
                type="radio"
                name="mode"
                value={opt.value}
                checked={mode === opt.value}
                onChange={() => setMode(opt.value as "always_on" | "after_hours")}
                className="mt-1 accent-brand-600"
              />
              <div>
                <p className="text-sm font-medium text-gray-800">{opt.label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{opt.desc}</p>
              </div>
            </label>
          ))}
        </div>

        {/* ── Grilla de horarios (solo after_hours) ────────────────────── */}
        {mode === "after_hours" && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">Horario de oficina</h2>
            <p className="text-xs text-gray-500 mb-4">
              Días y franjas en que la oficina está abierta. Fuera de estos horarios el bot responderá.
              Zona horaria: <span className="font-medium">America/Argentina/Buenos_Aires</span>.
            </p>

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {DAYS.map(({ key, label }) => {
                const day = horario[key] ?? { enabled: false };
                return (
                  <div
                    key={key}
                    className="flex items-center gap-4 px-5 py-3 border-b border-gray-100 last:border-0"
                  >
                    {/* Toggle activo/cerrado */}
                    <button
                      type="button"
                      onClick={() => toggleDay(key)}
                      className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors focus:outline-none ${
                        day.enabled ? "bg-brand-600" : "bg-gray-300"
                      }`}
                      aria-label={`${label} ${day.enabled ? "habilitado" : "cerrado"}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 translate-y-0.5 rounded-full bg-white shadow transition-transform ${
                          day.enabled ? "translate-x-4" : "translate-x-0.5"
                        }`}
                      />
                    </button>

                    {/* Nombre del día */}
                    <span className={`w-24 text-sm ${day.enabled ? "text-gray-800 font-medium" : "text-gray-400"}`}>
                      {label}
                    </span>

                    {/* Inputs de hora */}
                    {day.enabled ? (
                      <div className="flex items-center gap-2 flex-1">
                        <input
                          type="time"
                          value={day.from ?? "09:00"}
                          onChange={e => setTime(key, "from", e.target.value)}
                          className="border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 w-28"
                        />
                        <span className="text-gray-400 text-xs">a</span>
                        <input
                          type="time"
                          value={day.to ?? "18:00"}
                          onChange={e => setTime(key, "to", e.target.value)}
                          className="border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 w-28"
                        />
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400 italic">Cerrado — bot activo todo el día</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Feedback y botón guardar ─────────────────────────────────── */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}
        {saved && (
          <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg px-4 py-3">
            Configuración guardada correctamente.
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-medium px-6 py-2 rounded-lg text-sm transition-colors"
          >
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>
        </div>

      </form>
    </div>
  );
}
