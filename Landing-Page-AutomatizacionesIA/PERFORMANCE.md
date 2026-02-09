# Performance & Optimization Guide

## Hero Background Animations

El fondo animado del Hero está optimizado para máximo rendimiento y mínimo uso de CPU/GPU.

### Tecnologías Utilizadas

- **100% CSS3 & SVG** - Sin JavaScript para las animaciones
- **GPU Acceleration** - Uso de `transform3d()` en lugar de `transform()`
- **Will-change** - Hints al navegador para optimización
- **Filtros SVG** - Efectos de glow nativos del navegador

### Elementos Animados

| Elemento | Cantidad | Animación | Duración | Técnica |
|----------|----------|-----------|----------|---------|
| Gradient Blobs | 3 | Movimiento suave + escala | 20s | CSS transform3d |
| Nodos (circles) | 13 | Pulse + escala | 3s | CSS opacity + scale |
| Líneas (lines) | 9 | Flujo de datos | 8s | SVG stroke-dashoffset |
| Partículas | 6 | Flotación | 12s | CSS transform3d |

### Optimizaciones Implementadas

#### 1. GPU Acceleration
```css
transform: translate3d(30px, -50px, 0) scale(1.1);
/* En lugar de: transform: translate(30px, -50px) scale(1.1); */
```

El uso de `translate3d()` fuerza al navegador a usar aceleración GPU incluso en transformaciones 2D.

#### 2. Will-change Property
```css
.animate-blob {
  will-change: transform;
}
```

Informa al navegador qué propiedades van a cambiar, permitiendo pre-optimización.

#### 3. SVG Stroke Animations
```css
stroke-dasharray: 500;
stroke-dashoffset: 1000;
animation: lineFlow 8s linear infinite;
```

Las animaciones de `stroke-dashoffset` son muy eficientes en SVG y crean el efecto de "flujo de datos".

#### 4. Staggered Delays
```css
.node-1 { animation-delay: 0s; }
.node-2 { animation-delay: 0.2s; }
.node-3 { animation-delay: 0.4s; }
```

Los delays escalonados distribuyen el trabajo del navegador en el tiempo, evitando picos de CPU.

#### 5. Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  .animate-blob,
  .node,
  .ai-lines line,
  .particle {
    animation: none !important;
  }
}
```

Respeta las preferencias de accesibilidad del usuario.

### Performance Metrics

**Target**:
- Lighthouse Performance: 95+
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Cumulative Layout Shift: < 0.1
- CPU Usage: < 5% en idle

**Técnicas**:
- Sin JavaScript para animaciones de fondo
- SVG inline (0 HTTP requests)
- CSS animations (browser-optimized)
- GPU-accelerated transforms

### Troubleshooting

#### Si las animaciones se ven entrecortadas:

1. **Reducir cantidad de elementos**:
   - Menos nodos (actualmente 13)
   - Menos partículas (actualmente 6)
   - Menos líneas (actualmente 9)

2. **Aumentar duración de animaciones**:
   - Blobs: de 20s a 30s
   - Nodos: de 3s a 5s
   - Líneas: de 8s a 12s

3. **Simplificar blur effects**:
   - Reducir `blur-3xl` a `blur-2xl` en los blobs
   - Reducir `stdDeviation` en el filtro SVG glow

4. **Deshabilitar en móvil**:
```css
@media (max-width: 768px) {
  .ai-lines,
  .ai-particles {
    display: none;
  }
}
```

### Browser Compatibility

✅ Chrome/Edge (Chromium): Excelente
✅ Firefox: Excelente
✅ Safari: Bueno (algunos efectos pueden variar)
⚠️ IE11: No soportado (usar fallback estático)

### Testing

Para verificar performance en desarrollo:

```bash
# Build de producción
npm run build

# Preview local
npm run preview

# Abrir Chrome DevTools
# Performance tab → Record → Reload page
```

Métricas a verificar:
- FPS durante scroll (debe mantenerse en 60fps)
- CPU usage (debe ser < 10% en idle)
- GPU memory (< 50MB para las animaciones)

### Alternativas

Si el performance no es satisfactorio:

1. **Versión simplificada**: Solo gradient blobs, sin SVG
2. **Versión estática**: Imagen de fondo fija con gradiente
3. **Lazy load**: Cargar animaciones solo después del hero

## Otros Componentes

### Demo Chat Widget

**JavaScript**: ~2KB gzipped
**Técnica**: Event delegation, requestAnimationFrame para scroll
**Impact**: Mínimo, solo se activa con interacción del usuario

### Resto de la página

- **Animaciones hover**: CSS transitions simples (< 1ms)
- **Scroll suave**: CSS `scroll-behavior: smooth`
- **Imágenes**: Actualmente usando URLs, optimizable con `<Image>` de Astro

---

**Última actualización**: 2026-01-10
