# Auditoría de preparación SEO para lanzamiento

Fecha de revisión: 2026-08-20

## Resultado ejecutivo

La aplicación tiene una base SEO técnica razonable: metadata por ruta, canonical, `robots.ts`, sitemap dinámico, Open Graph/Twitter, manifest, favicon, H1, breadcrumbs, 404 y URLs limpias para fichas y taxonomías. El host canónico de producción es `https://www.oportexa.com`.

La variable de producción debe ser exactamente:

```text
SITE_URL=https://www.oportexa.com
```

El código conserva `http://localhost:3000` como fallback de desarrollo. No se ha cambiado ninguna variable externa.

## Hallazgos y decisiones

- `oportexa.com` sin `www` se conserva únicamente cuando describe el alias que redirige, una fuente oficial o un identificador de marca; las referencias de producción, canonical y configuración se han alineado con `www`.
- Las búsquedas y filtros de `/subvenciones` llevan canonical a `/subvenciones` y `noindex,follow` cuando existe cualquier query parameter, incluyendo paginación y ordenación.
- Las páginas de detalle de región, sector y beneficiario aplican la misma regla a queries. Además, una taxonomía sin inventario queda `noindex,follow`.
- El sitemap incluye home, catálogo, índice de regiones, fichas válidas y regiones con inventario. No incluye búsquedas, filtros, sectores, organismos o beneficiarios de forma masiva, porque su elegibilidad editorial/densidad debe revisarse con datos reales.
- La implementación actual genera un único sitemap dinámico y, con aproximadamente 6.674 fichas, permanece muy por debajo del límite operativo habitual de 50.000 URLs por sitemap. Antes de acercarse a ese orden de magnitud —especialmente hacia 100k/600k convocatorias— deberá migrarse a sitemap index + shards deterministas; no se introduce todavía porque añadiría complejidad sin beneficio para el dataset actual.
- Se implementó `BreadcrumbList` porque refleja breadcrumbs visibles y URLs reales. No se implementó `Organization` ni `WebSite/SearchAction`: no hay datos corporativos verificados y el buscador no tiene todavía un contrato de URL suficientemente estable para justificarlo.
- No se detectaron analytics, Google Tag, píxeles, iframes publicitarios, AdSense ni cookies/tracker de terceros en `apps/web`.
- No hay páginas públicas completas de Aviso legal, Privacidad o Cookies. No se han inventado datos personales, fiscales o societarios; esto bloquea un lanzamiento publicitario y debe resolverse antes de AdSense.

## Riesgos a verificar en producción

- Confirmar que Vercel tiene `SITE_URL=https://www.oportexa.com` en el entorno que sirve la web.
- Confirmar en HTML servido que canonical, `og:url`, sitemap y robots usan `www`.
- Confirmar que las fichas y taxonomías realmente tienen contenido y datos suficientes; el sitemap no sustituye la revisión de calidad de páginas thin o vacías.
- Medir Core Web Vitals con datos de usuarios tras publicar. El código usa Server Components y no carga trackers ni fuentes externas; queda por observar el coste de consultas PostgreSQL, imágenes sociales y renderizado dinámico.

## Inventario auditado

- Metadata: `apps/web/src/app/layout.tsx` y `generateMetadata` de home, catálogo, fichas y taxonomías.
- Indexación: `apps/web/src/app/robots.ts`, `apps/web/src/app/sitemap.ts` y `apps/web/src/lib/seo.ts`.
- UX rastreable: H1 en las rutas principales, enlaces internos desde home/footer, breadcrumbs, paginación y `not-found.tsx`.
- Marca: favicon, iconos, manifest, Open Graph PNG/SVG y Twitter `summary_large_image`.
- Legal/privacidad: footer sin enlaces legales publicados; especificación interna en `docs/PRIVACY.md`.
