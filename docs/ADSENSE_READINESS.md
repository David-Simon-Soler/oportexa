# AdSense readiness

Oportexa no tiene AdSense, `ads.txt`, publisher ID ni scripts publicitarios en el repositorio. No insertar ninguno hasta que exista una cuenta aprobada y una configuración deliberada.

## Requisitos previos

1. El sitio debe estar publicado de forma estable en `https://www.oportexa.com`.
2. Search Console debe estar verificado y el sitemap enviado.
3. Debe existir contenido útil, original y mantenido: fichas de convocatorias, taxonomías con inventario y contexto claro sobre la fuente BDNS.
4. Deben estar publicadas y completas las páginas aplicables de Aviso legal, Privacidad y Cookies. Deben contener datos reales del responsable; no usar placeholders en producción.
5. Si se añaden cookies o tecnologías de medición/publicidad no estrictamente necesarias, debe definirse el consentimiento y una CMP conforme al ámbito aplicable antes de cargar dichas tecnologías.
6. Revisar accesibilidad, navegación, errores 404/5xx, velocidad y experiencia móvil.

## Secuencia recomendada

1. Completar datos legales y publicar las páginas legales.
2. Verificar Search Console y resolver problemas de indexación.
3. Observar cobertura, estabilidad del contenido y Core Web Vitals.
4. Crear AdSense y esperar aprobación/configuración.
5. Sólo después, añadir el script aprobado con una estrategia de consentimiento revisada.
6. Crear `ads.txt` únicamente con la línea exacta que proporcione AdSense; nunca crear un archivo falso o de ejemplo.
7. Verificar que anuncios, consentimiento, política de privacidad y `ads.txt` funcionan en producción sin bloquear el contenido principal.

## Blockers actuales

- Faltan datos reales del responsable legal: nombre o razón social, NIF, domicilio, email y demás información que corresponda.
- Faltan textos legales revisados y publicables.
- No existe publisher ID aprobado.
- No existe decisión aprobada sobre CMP/consentimiento para publicidad.

Por tanto, el estado actual es **técnicamente preparado para continuar la configuración**, pero **no listo para insertar publicidad**.
