import { useState } from "react";

const DEFAULT_SETTINGS = {
  headlineSize: 22,
  headlineFont: "Syne",
  bulletSize: 12,
  bulletSpacing: 8,
  tagSize: 11,
  subSize: 13,
  statValueSize: 36,
  stepTextSize: 12,
  lineHeight: 1.15,
};

const FONT_OPTIONS = ["Syne", "DM Sans", "Space Grotesk", "Outfit", "Plus Jakarta Sans", "Manrope", "Raleway"];

const initialSlides = [
  {
    id: 1, type: "cover",
    tag: "🏠 Tecnología Inmobiliaria",
    headline: "¿Perdés clientes por no\nresponder a tiempo?",
    sub: "Tu inmobiliaria puede estar perdiendo ventas todos los días.",
    badge: "InmoBot", url: "Link en bio", accent: "#00D4FF",
  },
  {
    id: 2, type: "problem",
    tag: "⚠️ El problema",
    headline: "Cada minuto sin responder\nes un cliente que se va.",
    bullets: ["Si tardás, el lead se va a la competencia", "Consultas fuera de horario sin atender", "Respuestas repetitivas todo el día", "Leads que nunca vuelven"],
    url: "Link en bio", accent: "#FF6B35",
  },
  {
    id: 3, type: "solution",
    tag: "✅ La solución",
    headline: "InmoBot responde en\nsegundos. Siempre.",
    stats: [{ value: "24/7", label: "Atención sin pausa" }, { value: "<10s", label: "Tiempo de respuesta" }, { value: "100%", label: "Leads capturados" }, { value: "∞", label: "Consultas simultáneas" }],
    url: "Link en bio", accent: "#00D4FF",
  },
  {
    id: 4, type: "features",
    tag: "🧠 Cómo funciona",
    headline: "IA que entiende lo que\ntu cliente necesita.",
    steps: [{ n: "01", text: "El cliente consulta desde tu web" }, { n: "02", text: "La IA entiende lo que busca" }, { n: "03", text: "Filtra propiedades automáticamente" }, { n: "04", text: "Captura los datos del interesado" }],
    url: "Link en bio", accent: "#A78BFA",
  },
  {
    id: 5, type: "differentiator",
    tag: "📈 Beneficios",
    headline: "Más tiempo para vender.\nMenos tiempo respondiendo.",
    perks: ["Más consultas atendidas", "Menos tiempo operativo", "Más oportunidades de venta", "Tu equipo se enfoca en cerrar"],
    url: "Link en bio", accent: "#FFB800",
  },
  {
    id: 6, type: "cta",
    tag: "🚀 Empezá hoy",
    headline: "Probalo con tu propio\ncatálogo de propiedades.",
    sub: "Implementación rápida. Sin conocimientos técnicos.",
    cta: "👉 Link en bio", url: "Link en bio", accent: "#00D4FF",
  },
];

function Slider({ label, value, min, max, step = 1, onChange, unit = "" }) {
  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <span style={{ color: "#94A3B8", fontSize: 11, fontFamily: "'DM Sans', sans-serif" }}>{label}</span>
        <span style={{ color: "#E2E8F0", fontSize: 11, fontFamily: "monospace", background: "#1E293B", padding: "1px 6px", borderRadius: 4 }}>
          {value}{unit}
        </span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{ width: "100%", accentColor: "#00D4FF", cursor: "pointer", height: 4 }}
      />
    </div>
  );
}

function Select({ label, value, options, onChange }) {
  return (
    <div className="mb-4">
      <div className="mb-1">
        <span style={{ color: "#94A3B8", fontSize: 11, fontFamily: "'DM Sans', sans-serif" }}>{label}</span>
      </div>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: "100%", background: "#1E293B", border: "1px solid #334155",
          color: "#E2E8F0", borderRadius: 8, padding: "6px 10px",
          fontSize: 12, fontFamily: "'DM Sans', sans-serif", cursor: "pointer", outline: "none"
        }}
      >
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function SlidePreview({ slide, s }) {
  const { type, tag, headline, sub, bullets, stats, steps, perks, cta, url, accent, badge } = slide;
  const lines = headline.split("\n");

  return (
    <div style={{
      width: 380, height: 380, borderRadius: 18, overflow: "hidden", position: "relative",
      background: "linear-gradient(145deg, #0A0E1A 0%, #0D1526 50%, #0A0E1A 100%)",
      border: `1px solid ${accent}22`,
      boxShadow: `0 0 40px ${accent}25, 0 16px 48px #00000088`,
      fontFamily: "'DM Sans', sans-serif", flexShrink: 0,
    }}>
      {/* Grid */}
      <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05 }}>
        <defs><pattern id={`g${slide.id}`} width="36" height="36" patternUnits="userSpaceOnUse">
          <path d="M 36 0 L 0 0 0 36" fill="none" stroke={accent} strokeWidth="0.5" />
        </pattern></defs>
        <rect width="100%" height="100%" fill={`url(#g${slide.id})`} />
      </svg>
      {/* Orbs */}
      <div style={{ position: "absolute", left: "78%", top: "-8%", width: 220, height: 220, borderRadius: "50%", background: `radial-gradient(circle, ${accent}18 0%, transparent 70%)`, filter: "blur(18px)" }} />
      <div style={{ position: "absolute", left: "-5%", top: "72%", width: 160, height: 160, borderRadius: "50%", background: `radial-gradient(circle, ${accent}10 0%, transparent 70%)`, filter: "blur(16px)" }} />
      {/* Top line */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }} />

      <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", height: "100%", padding: 26 }}>
        {/* Top row */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <span style={{
            fontSize: s.tagSize, fontWeight: 600, letterSpacing: "0.04em",
            padding: "4px 12px", borderRadius: 999,
            background: `${accent}18`, color: accent, border: `1px solid ${accent}30`
          }}>{tag}</span>
          {badge && <span style={{ fontSize: s.tagSize, fontWeight: 700, color: accent, opacity: 0.7, letterSpacing: "0.12em" }}>{badge}</span>}
          <span style={{ fontSize: 10, color: "#ffffff25", fontFamily: "monospace" }}>{slide.id}/6</span>
        </div>

        {/* Headline */}
        <div style={{ marginBottom: 12 }}>
          {lines.map((line, i) => (
            <div key={i} style={{
              fontSize: s.headlineSize, fontWeight: 900, lineHeight: s.lineHeight,
              fontFamily: `'${s.headlineFont}', sans-serif`, letterSpacing: "-0.03em",
              color: i === 0 ? "#FFFFFF" : accent,
            }}>{line}</div>
          ))}
        </div>

        {/* Content */}
        {type === "cover" && (
          <p style={{ fontSize: s.subSize, color: "#94A3B8", lineHeight: 1.5 }}>{sub}</p>
        )}

        {type === "problem" && bullets && (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {bullets.map((b, i) => (
              <li key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: s.bulletSize, color: "#94A3B8", marginBottom: s.bulletSpacing, lineHeight: 1.35 }}>
                <span style={{ color: accent, flexShrink: 0, marginTop: 1 }}>✗</span>{b}
              </li>
            ))}
          </ul>
        )}

        {type === "solution" && stats && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 4 }}>
            {stats.map((st, i) => (
              <div key={i} style={{ borderRadius: 12, padding: "10px 12px", background: `${accent}0D`, border: `1px solid ${accent}20` }}>
                <div style={{ fontSize: s.statValueSize, fontWeight: 900, color: accent, fontFamily: `'${s.headlineFont}', sans-serif`, lineHeight: 1 }}>{st.value}</div>
                <div style={{ fontSize: 10, color: "#64748B", marginTop: 4 }}>{st.label}</div>
              </div>
            ))}
          </div>
        )}

        {type === "features" && steps && (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {steps.map((st, i) => (
              <li key={i} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: s.bulletSpacing + 4 }}>
                <span style={{ width: 28, height: 28, borderRadius: 8, background: `${accent}18`, color: accent, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 900, fontFamily: "monospace", flexShrink: 0 }}>{st.n}</span>
                <span style={{ fontSize: s.stepTextSize, color: "#94A3B8" }}>{st.text}</span>
              </li>
            ))}
          </ul>
        )}

        {type === "differentiator" && perks && (
          <ul style={{ listStyle: "none", padding: 0 }}>
            {perks.map((p, i) => (
              <li key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: s.bulletSize, color: "#94A3B8", marginBottom: s.bulletSpacing, lineHeight: 1.35 }}>
                <span style={{ color: accent, flexShrink: 0 }}>★</span>{p}
              </li>
            ))}
          </ul>
        )}

        {type === "cta" && (
          <div style={{ display: "flex", flexDirection: "column", flex: 1, justifyContent: "space-between" }}>
            <p style={{ fontSize: s.subSize, color: "#94A3B8", lineHeight: 1.5 }}>{sub}</p>
            <div style={{ borderRadius: 14, padding: "16px 20px", textAlign: "center", background: `linear-gradient(135deg, ${accent}22, ${accent}0D)`, border: `1px solid ${accent}40` }}>
              <p style={{ fontSize: 11, color: "#64748B", marginBottom: 4 }}>{cta}</p>
              <p style={{ fontSize: 14, fontWeight: 900, color: accent, fontFamily: `'${s.headlineFont}', sans-serif`, letterSpacing: "0.02em" }}>{url}</p>
            </div>
          </div>
        )}

        {/* Footer */}
        {type !== "cta" && (
          <div style={{ marginTop: "auto", paddingTop: 10, borderTop: "1px solid rgba(255,255,255,0.05)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 10, color: accent, opacity: 0.55, fontFamily: "monospace" }}>{url}</span>
            <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
              {[1,2,3,4,5,6].map(i => (
                <div key={i} style={{ height: 4, borderRadius: 9999, background: i === slide.id ? accent : "rgba(255,255,255,0.1)", width: i === slide.id ? 16 : 4, transition: "all 0.3s" }} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [current, setCurrent] = useState(0);
  const [s, setS] = useState(DEFAULT_SETTINGS);
  const [tab, setTab] = useState("typography");

  const set = (key, val) => setS(prev => ({ ...prev, [key]: val }));

  const tabs = [
    { id: "typography", label: "Tipografía" },
    { id: "spacing", label: "Espaciado" },
    { id: "sizes", label: "Tamaños" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#060810", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Sans:wght@400;500;600&family=Space+Grotesk:wght@700;800&family=Outfit:wght@700;800;900&family=Plus+Jakarta+Sans:wght@700;800;900&family=Manrope:wght@700;800&family=Raleway:wght@700;800;900&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ padding: "20px 28px 16px", borderBottom: "1px solid #1E293B", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ color: "#00D4FF", fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", marginBottom: 2 }}>EDITOR DE CARRUSEL</div>
          <div style={{ color: "#E2E8F0", fontSize: 18, fontWeight: 800, fontFamily: `'${s.headlineFont}', sans-serif` }}>InmoBot</div>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {initialSlides.map((_, i) => (
            <button key={i} onClick={() => setCurrent(i)} style={{
              width: 32, height: 32, borderRadius: 8, fontSize: 11, fontWeight: 700, cursor: "pointer",
              background: i === current ? initialSlides[i].accent + "22" : "#1E293B",
              border: `1px solid ${i === current ? initialSlides[i].accent + "66" : "#334155"}`,
              color: i === current ? initialSlides[i].accent : "#64748B",
              transition: "all 0.2s"
            }}>{i + 1}</button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* Control Panel */}
        <div style={{ width: 260, background: "#0A0E1A", borderRight: "1px solid #1E293B", padding: "20px 18px", overflowY: "auto", flexShrink: 0 }}>

          {/* Tabs */}
          <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#060810", borderRadius: 10, padding: 4 }}>
            {tabs.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} style={{
                flex: 1, padding: "6px 4px", borderRadius: 7, fontSize: 10, fontWeight: 600,
                cursor: "pointer", border: "none", transition: "all 0.2s",
                background: tab === t.id ? "#1E293B" : "transparent",
                color: tab === t.id ? "#E2E8F0" : "#475569",
              }}>{t.label}</button>
            ))}
          </div>

          {tab === "typography" && (
            <>
              <div style={{ color: "#475569", fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", marginBottom: 12 }}>FUENTES</div>
              <Select label="Fuente de títulos" value={s.headlineFont} options={FONT_OPTIONS} onChange={v => set("headlineFont", v)} />
              <div style={{ height: 1, background: "#1E293B", margin: "16px 0" }} />
              <div style={{ color: "#475569", fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", marginBottom: 12 }}>PREVIEW FUENTE</div>
              <div style={{ background: "#060810", borderRadius: 10, padding: "12px 14px", border: "1px solid #1E293B" }}>
                <div style={{ fontFamily: `'${s.headlineFont}', sans-serif`, fontWeight: 900, fontSize: 22, color: "#00D4FF", lineHeight: 1.1 }}>InmoBot</div>
                <div style={{ fontFamily: `'${s.headlineFont}', sans-serif`, fontWeight: 700, fontSize: 14, color: "#E2E8F0", marginTop: 4 }}>Tecnología Inmobiliaria</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: "#64748B", marginTop: 4 }}>Texto de cuerpo siempre en DM Sans</div>
              </div>
            </>
          )}

          {tab === "spacing" && (
            <>
              <div style={{ color: "#475569", fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", marginBottom: 12 }}>ESPACIADO</div>
              <Slider label="Espacio entre bullets" value={s.bulletSpacing} min={2} max={24} onChange={v => set("bulletSpacing", v)} unit="px" />
              <Slider label="Interlineado títulos" value={s.lineHeight} min={0.9} max={1.6} step={0.05} onChange={v => set("lineHeight", v)} />
            </>
          )}

          {tab === "sizes" && (
            <>
              <div style={{ color: "#475569", fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", marginBottom: 12 }}>TAMAÑOS</div>
              <Slider label="Título principal" value={s.headlineSize} min={14} max={32} onChange={v => set("headlineSize", v)} unit="px" />
              <Slider label="Texto bullets / perks" value={s.bulletSize} min={9} max={20} onChange={v => set("bulletSize", v)} unit="px" />
              <Slider label="Texto pasos (steps)" value={s.stepTextSize} min={9} max={20} onChange={v => set("stepTextSize", v)} unit="px" />
              <Slider label="Stats (números grandes)" value={s.statValueSize} min={20} max={60} onChange={v => set("statValueSize", v)} unit="px" />
              <Slider label="Tag / badge" value={s.tagSize} min={8} max={16} onChange={v => set("tagSize", v)} unit="px" />
              <Slider label="Subtítulo / sub" value={s.subSize} min={9} max={20} onChange={v => set("subSize", v)} unit="px" />
            </>
          )}

          {/* Reset button */}
          <div style={{ marginTop: 24 }}>
            <button
              onClick={() => setS(DEFAULT_SETTINGS)}
              style={{
                width: "100%", padding: "8px", borderRadius: 8, fontSize: 11, fontWeight: 600,
                cursor: "pointer", border: "1px solid #334155", background: "transparent",
                color: "#475569", transition: "all 0.2s"
              }}
              onMouseEnter={e => { e.target.style.borderColor = "#FF6B3566"; e.target.style.color = "#FF6B35"; }}
              onMouseLeave={e => { e.target.style.borderColor = "#334155"; e.target.style.color = "#475569"; }}
            >↺ Resetear valores</button>
          </div>
        </div>

        {/* Preview */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px 24px", gap: 20 }}>
          <SlidePreview slide={initialSlides[current]} s={s} />

          {/* Nav */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <button onClick={() => setCurrent(c => (c - 1 + 6) % 6)} style={{ width: 36, height: 36, borderRadius: "50%", background: "#0D1526", border: "1px solid #1E293B", color: "#64748B", cursor: "pointer", fontSize: 14 }}>←</button>
            <span style={{ color: "#334155", fontSize: 12, fontFamily: "monospace" }}>Slide {current + 1} / 6</span>
            <button onClick={() => setCurrent(c => (c + 1) % 6)} style={{ width: 36, height: 36, borderRadius: "50%", background: "#0D1526", border: "1px solid #1E293B", color: "#64748B", cursor: "pointer", fontSize: 14 }}>→</button>
          </div>

          {/* Export hint */}
          <div style={{ background: "#0D1526", border: "1px solid #1E293B", borderRadius: 12, padding: "12px 18px", textAlign: "center", maxWidth: 380 }}>
            <p style={{ color: "#475569", fontSize: 11, lineHeight: 1.5 }}>
              ✅ Cuando estés conforme con los ajustes, decime <span style={{ color: "#00D4FF" }}>"exportá"</span> y genero los 6 PNGs 1080×1080 listos para IG.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
