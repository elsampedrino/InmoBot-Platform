Crear el Deploy Hook en Vercel

## PASO 1 ## 
Entrá a vercel.com → seleccioná el proyecto Navines-Landing-Page
Ir a Settings → Git (menú lateral)
Bajá hasta la sección "Deploy Hooks"
Hacé clic en "Create Hook":
Hook Name: Panel Admin
Git Branch to Trigger: main
Hacé clic en "Create"
Copiá la URL que genera (algo como https://api.vercel.com/v1/integrations/deploy/prj_XXXX/YYYYY)

## Paso 2 — Agregar el webhook en GitHub ##
Ir a github.com/elsampedrino/bot-inmobiliaria-data → Settings → Webhooks → Add webhook
Completar:
Payload URL: la URL del Deploy Hook que copiaste en el paso anterior
Content type: application/json
Which events: "Just the push event" ✓
Asegurate que esté Active tildado
Clic en "Add webhook"

## Paso 3 — Verificar GITHUB_TOKEN en Render ##
Test del flujo completo
Con todo configurado:

En el Panel Admin, entrá a Propiedades (empresa Navines)
Hacé clic en "Publicar en landing"
Debería aparecer confirmación con el commit SHA
En Vercel, en Deployments del proyecto Navines, deberías ver un nuevo deploy disparado