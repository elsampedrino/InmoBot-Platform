import configData from '../data/config_navines.json';

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
  amarillo: string;
  amarillo_oscuro: string;
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

let cachedConfig: SiteConfig | null = null;

export function getConfig(): SiteConfig {
  if (cachedConfig) return cachedConfig;
  cachedConfig = configData as unknown as SiteConfig;
  return cachedConfig;
}

export function getEmpresa(): ConfigEmpresa { return getConfig().empresa; }
export function getHero(): ConfigHero { return getConfig().hero; }
export function getStats(): ConfigStat[] { return getConfig().stats; }
export function getQuienesSomos(): ConfigQuienesSomos { return getConfig().quienes_somos; }
export function getServicios(): ConfigServicios { return getConfig().servicios; }
export function getContacto(): ConfigContacto { return getConfig().contacto; }
export function getRedesSociales(): ConfigRedesSociales { return getConfig().redes_sociales; }
export function getFooter(): ConfigFooter { return getConfig().footer; }
export function getWidgetBot(): ConfigWidgetBot { return getConfig().widget_bot; }
export function getTema(): ConfigTema { return getConfig().tema; }
export function getColores(): ConfigColores { return getConfig().tema.colores; }
export function getFuentes(): ConfigFuentes { return getConfig().tema.fuentes; }
export function getNavegacion(): ConfigNavegacion { return getConfig().navegacion; }

export function getWhatsAppUrl(): string {
  const contacto = getContacto();
  const mensaje = encodeURIComponent(contacto.whatsapp.mensaje_inicial);
  return `https://wa.me/${contacto.whatsapp.numero}?text=${mensaje}`;
}

export function getTelefonoUrl(): string {
  return `tel:${getContacto().telefono.link}`;
}

export function getEmailUrl(): string {
  return `mailto:${getContacto().email}`;
}
