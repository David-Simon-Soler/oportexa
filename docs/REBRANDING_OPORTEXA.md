# Rebranding Oportexa

## Decisión

- Nombre público anterior: Opportunity Intel.
- Nombre público nuevo: Oportexa.
- Dominio previsto: `https://oportexa.com`.

Oportexa comunica una plataforma para descubrir, entender y verificar ayudas y subvenciones públicas. La dirección visual Editorial Data Intelligence, las rutas y la arquitectura no cambian.

## Superficies actualizadas

- Wordmark del header y footer.
- Homepage y texto accesible de orientación.
- Provenance y fuente de confianza.
- Mensajes de observación local.
- Metadata raíz y `applicationName`.
- Descripciones y títulos SEO de taxonomías.
- README y documentación actual de producto, UX, SEO y arquitectura.

## Identificadores conservados

Se conserva `opportunity-intel` en el nombre del repositorio, rutas de filesystem, ejemplos de base de datos, nombres Docker, `application_name` de PostgreSQL, claves internas de locking, user-agent histórico de ingestion y paths de documentación. Son identificadores técnicos o históricos; cambiarlos no aporta valor público y podría romper compatibilidad local.

## Site URL

La aplicación ya usa `SITE_URL` como configuración central para `metadataBase`, sitemap y robots. Desarrollo mantiene el fallback `http://localhost:3000`; producción deberá definir:

```text
SITE_URL=https://oportexa.com
```

No se introducen secretos ni se activan URLs absolutas de producción en desarrollo.

## Pendiente antes del deploy

- Definir `SITE_URL=https://oportexa.com` en el entorno de producción.
- Verificar canonical, sitemap y robots en el deploy real.
- Verificar favicon, manifest y metadata social en el deploy real.
- Configurar DNS y hosting fuera de esta tarea.
- Verificar Search Console después de que exista producción.

## Assets y metadata de producción

Completado en el checkpoint posterior:

- Isotipo vectorial OX GEO en `apps/web/public/logo-mark.svg`.
- Favicon de navegador basado solo en el isotipo.
- Iconos de aplicación 192×192, 512×512 y Apple Touch Icon.
- Manifest básico de Oportexa, sin service worker.
- Imagen Open Graph 1200×630 reutilizada para Twitter.
- `themeColor`, `icons`, `manifest`, Open Graph y Twitter metadata.
- Integración mínima del isotipo en el header, conservando el wordmark HTML.

Pendiente fuera de este checkpoint: configuración real de dominio, hosting y deploy.
