# 🔄 GitHub Actions - Keep Alive para N8N

Este workflow mantiene activo tu servicio de N8N en Render haciendo ping cada 10 minutos.

## 📋 ¿Qué hace?

- Hace ping a `https://n8n-bot-inmobiliario.onrender.com/` cada 10 minutos
- Previene que Render suspenda el servicio por inactividad
- Se ejecuta automáticamente 24/7

## 🚀 Cómo activarlo

### 1. Subir el código a GitHub

Si aún no lo hiciste:

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Add keep-alive workflow for N8N"

# Crear repo en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

# Subir
git push -u origin main
```

### 2. Verificar que funcione

1. Ve a tu repositorio en GitHub
2. Click en la pestaña **"Actions"**
3. Deberías ver el workflow **"Keep N8N Alive"**
4. El workflow se ejecutará automáticamente cada 10 minutos

### 3. Ejecutar manualmente (opcional)

Para probar que funciona:

1. Ve a **Actions** → **Keep N8N Alive**
2. Click en **"Run workflow"**
3. Click en **"Run workflow"** (botón verde)
4. Espera unos segundos y verás la ejecución

## ⏰ Frecuencia

- **Cada 10 minutos**: `*/10 * * * *`
- Si quieres cambiar la frecuencia, edita la línea del `cron` en el archivo

### Ejemplos de cron:

```yaml
# Cada 5 minutos
- cron: '*/5 * * * *'

# Cada 15 minutos
- cron: '*/15 * * * *'

# Cada hora
- cron: '0 * * * *'
```

## ✅ Ventajas

- ✅ **100% gratis** con GitHub Actions
- ✅ **No necesitas otra cuenta**
- ✅ **Confiable** - se ejecuta automáticamente
- ✅ **Visible** - puedes ver el historial de ejecuciones
- ✅ **Fácil de desactivar** - simplemente elimina el archivo o deshabilita el workflow

## ⚠️ Notas importantes

1. **GitHub Actions tiene límites**:
   - 2000 minutos/mes en cuentas gratuitas
   - Este workflow usa ~1 minuto/día = ~30 minutos/mes ✅

2. **El workflow solo funciona si el repositorio es público** o tienes GitHub Pro/Team

3. **Primera ejecución**: Puede tardar hasta 10 minutos después de subir el código

## 🔧 Troubleshooting

### El workflow no aparece en Actions

- Verifica que el archivo esté en `.github/workflows/keep-alive.yml`
- Asegúrate de haber hecho push a GitHub
- El repositorio debe ser público o tener GitHub Actions habilitado

### El workflow está pausado

GitHub puede pausar workflows automáticos si no hay actividad en el repo por 60 días. Para reactivarlo:

1. Ve a Actions
2. Click en el mensaje de pausa
3. Click en "Enable workflow"

## 📊 Monitorear

Para ver el historial:

1. GitHub → Tu repo → Actions
2. Click en "Keep N8N Alive"
3. Verás todas las ejecuciones con sus logs

---

**Creado:** 1 de Diciembre 2024
**Estado:** ✅ Activo
