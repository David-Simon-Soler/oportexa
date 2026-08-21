# Checklist de smoke test en producción

Host esperado: `https://www.oportexa.com`. La raíz `https://oportexa.com` debe redirigir con 308 al host principal.

## HTTP, dominio e indexación

- [ ] Home responde 200 por HTTPS.
- [ ] `oportexa.com` redirige a `www.oportexa.com` sin cadena adicional.
- [ ] Certificado válido y sin contenido mixto.
- [ ] `/robots.txt` responde 200 y anuncia `https://www.oportexa.com/sitemap.xml`.
- [ ] `/sitemap.xml` responde 200, es XML válido y sólo contiene URLs canónicas e indexables.
- [ ] No aparecen queries, filtros, `page`, URLs vacías ni hosts sin `www` en el sitemap.

## Rutas y contenido

- [ ] Home tiene un único H1, title, description, canonical, Open Graph y Twitter metadata.
- [ ] Catálogo funciona sin filtros y muestra resultados o estado vacío controlado.
- [ ] Search y filtros funcionan, pero sus URLs tienen canonical limpio y `noindex,follow`.
- [ ] Detalle de subvención válido muestra H1, procedencia, enlace a fuente oficial y canonical estable.
- [ ] Slug incorrecto de una ficha válida redirige al slug canónico.
- [ ] Índices de taxonomías funcionan.
- [ ] Taxonomías con inventario muestran contenido y enlaces internos; taxonomías vacías no se indexan.
- [ ] Paginación conserva el contexto de consulta y no se indexa como landing independiente.
- [ ] Breadcrumbs son visibles, accesibles y generan `BreadcrumbList` válido.
- [ ] `/404-prueba-inexistente` muestra 404 controlado, navegación de recuperación y no filtra errores internos.

## Social, accesibilidad y runtime

- [ ] Open Graph apunta al asset correcto y la tarjeta se puede descargar.
- [ ] Favicon, iconos y manifest responden correctamente.
- [ ] Navegación por teclado, foco visible, labels de formularios y contraste pasan revisión manual móvil/desktop.
- [ ] No hay errores de consola ni errores runtime en home, catálogo, detalle y taxonomías.
- [ ] Revisar LCP, CLS, INP y consultas lentas con datos reales después de tráfico inicial.
- [ ] No se han añadido trackers, cookies de terceros, AdSense ni `ads.txt` sin aprobación y documentación.

## Operación de datos

- [ ] El workflow `.github/workflows/daily-revalidation.yml` queda habilitado sólo con `OPORTEXA_INGEST_DATABASE_URL` y permisos de contenido de lectura.
- [ ] La revalidación BDNS escribe en Neon mediante el rol de ingestión y la web sigue leyendo la capa `core`.
- [ ] Quality report y quality gate finalizan correctamente.
- [ ] No se han modificado secretos, variables de Vercel, DNS ni conexiones externas durante esta revisión.
