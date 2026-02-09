// Configuración centralizada de la landing
// Por ahora carga desde archivo local, pero puede migrar a GitHub

import configData from '../data/config_bbr.json';

// Tipos para la configuración
export interface ConfigEmpresa {
  nombre: string;
  nombre_corto: string;
  slogan: string;
  logo: string;
  favicon: string;
  descripcion_meta: string;
}

export interface ConfigHero {
  titulo_linea1: string;
  titulo_linea2: string;
  subtitulo: string;
  imagen_fondo: string;
  cta_principal: { texto: string; link: string };
  cta_secundario: { texto: string; link: string };
}

export interface ConfigStat {
  valor: string;
  label: string;
}

export interface ConfigValor {
  titulo: string;
  descripcion: string;
  icono: string;
}

export interface ConfigQuienesSomos {
  titulo_seccion: string;
  subtitulo: string;
  parrafos: string[];
  imagen: string;
  años_experiencia: string;
  valores: ConfigValor[];
}

export interface ConfigServicio {
  titulo: string;
  descripcion: string;
  icono: string;
}

export interface ConfigServicios {
  titulo_seccion: string;
  subtitulo: string;
  descripcion: string;
  lista: ConfigServicio[];
}

export interface ConfigContacto {
  titulo_seccion: string;
  subtitulo: string;
  descripcion: string;
  telefono: { display: string; link: string };
  whatsapp: { numero: string; mensaje_inicial: string };
  email: string;
  direccion: string;
  horarios: { semana: string; sabado: string };
  formulario: { titulo: string; asunto_email: string; webhook_url: string; origen: string };
}

export interface ConfigRedesSociales {
  instagram?: string;
  facebook?: string;
  youtube?: string;
  twitter?: string;
  web_comercial?: string;
}

export interface ConfigFooter {
  descripcion: string;
  desarrollado_por: { nombre: string; link: string };
}

export interface ConfigWidgetBot {
  habilitado: boolean;
  apiUrl: string;
  contactUrl: string;
  repo: string;
  nombre: string;
  mensaje_bienvenida: string;
  placeholder: string;
  posicion: string;
  tamaño_boton: string;
  ancho_chat: string;
  alto_chat: string;
  mostrar_badge_innovacion: boolean;
  texto_badge: string;
  texto_destacado: string;
  subtexto_destacado: string;
  descripcion_destacado: string;
}

export interface ConfigColores {
  primario: string;
  primario_oscuro: string;
  primario_claro: string;
  secundario: string;
  secundario_claro: string;
  gris_oscuro: string;
  gris: string;
  gris_claro: string;
  fondo_gris: string;
  fondo_gris_logo: string;
  blanco: string;
  off_white: string;
}

export interface ConfigFuentes {
  principal: string;
  fallback: string;
  tamaño_base: {
    desktop: string;
    tablet: string;
    mobile: string;
  };
  google_fonts_url: string;
}

export interface ConfigTema {
  colores: ConfigColores;
  fuentes: ConfigFuentes;
}

export interface ConfigNavItem {
  label: string;
  href?: string;
  submenu?: { label: string; href: string }[];
}

export interface ConfigNavegacion {
  items: ConfigNavItem[];
}

export interface SiteConfig {
  empresa: ConfigEmpresa;
  hero: ConfigHero;
  stats: ConfigStat[];
  quienes_somos: ConfigQuienesSomos;
  servicios: ConfigServicios;
  contacto: ConfigContacto;
  redes_sociales: ConfigRedesSociales;
  footer: ConfigFooter;
  widget_bot: ConfigWidgetBot;
  tema: ConfigTema;
  navegacion: ConfigNavegacion;
}

// Configuración cacheada
let cachedConfig: SiteConfig | null = null;

/**
 * Obtiene la configuración del sitio
 * Por ahora carga desde archivo local, pero puede migrar a GitHub
 */
export function getConfig(): SiteConfig {
  if (cachedConfig) return cachedConfig;
  cachedConfig = configData as SiteConfig;
  return cachedConfig;
}

// Helpers para acceso rápido a secciones específicas
export function getEmpresa(): ConfigEmpresa {
  return getConfig().empresa;
}

export function getHero(): ConfigHero {
  return getConfig().hero;
}

export function getStats(): ConfigStat[] {
  return getConfig().stats;
}

export function getQuienesSomos(): ConfigQuienesSomos {
  return getConfig().quienes_somos;
}

export function getServicios(): ConfigServicios {
  return getConfig().servicios;
}

export function getContacto(): ConfigContacto {
  return getConfig().contacto;
}

export function getRedesSociales(): ConfigRedesSociales {
  return getConfig().redes_sociales;
}

export function getFooter(): ConfigFooter {
  return getConfig().footer;
}

export function getWidgetBot(): ConfigWidgetBot {
  return getConfig().widget_bot;
}

export function getTema(): ConfigTema {
  return getConfig().tema;
}

export function getColores(): ConfigColores {
  return getConfig().tema.colores;
}

export function getFuentes(): ConfigFuentes {
  return getConfig().tema.fuentes;
}

export function getNavegacion(): ConfigNavegacion {
  return getConfig().navegacion;
}

/**
 * Genera las variables CSS para los colores del tema
 */
export function generarVariablesCSS(): string {
  const colores = getColores();
  return `
    --color-primario: ${colores.primario};
    --color-primario-oscuro: ${colores.primario_oscuro};
    --color-primario-claro: ${colores.primario_claro};
    --color-secundario: ${colores.secundario};
    --color-secundario-claro: ${colores.secundario_claro};
    --color-gris-oscuro: ${colores.gris_oscuro};
    --color-gris: ${colores.gris};
    --color-gris-claro: ${colores.gris_claro};
    --color-fondo-gris: ${colores.fondo_gris};
    --color-fondo-gris-logo: ${colores.fondo_gris_logo};
    --color-blanco: ${colores.blanco};
    --color-off-white: ${colores.off_white};
  `;
}

/**
 * Genera la URL de WhatsApp con mensaje predefinido
 */
export function getWhatsAppUrl(): string {
  const contacto = getContacto();
  const mensaje = encodeURIComponent(contacto.whatsapp.mensaje_inicial);
  return `https://wa.me/${contacto.whatsapp.numero}?text=${mensaje}`;
}

/**
 * Genera la URL de teléfono
 */
export function getTelefonoUrl(): string {
  return `tel:${getContacto().telefono.link}`;
}

/**
 * Genera la URL de email
 */
export function getEmailUrl(): string {
  return `mailto:${getContacto().email}`;
}
