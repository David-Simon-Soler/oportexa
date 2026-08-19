# SEO futuro

En V0.2 la superficie se limita a `/`, `/subvenciones`, `/subvenciones/[slug]`, `/subvenciones/region` y `/subvenciones/region/[slug]`. Las fichas incluyen metadata y canonical derivados del contenido disponible; también hay `robots.ts` y sitemap dinámico. El informe `services/ingestion/scripts/seo_opportunity_report.py` mide densidad sin generar páginas.

## Priorización futura

### Tier 1

Convocatoria individual, región, sector y tipo de beneficiario: superficies claras siempre que exista contenido suficiente y mantenimiento de datos.

### Tier 2

Región + sector y región + beneficiario: sólo cuando el informe de oportunidades muestre densidad y una página aporte contexto adicional frente al filtro.

### Tier 3

Combinaciones profundas, filtros arbitrarios y páginas con pocos registros: no crear todavía.

Una página programática sólo podrá indexarse si aporta utilidad real, procedencia visible y suficiente densidad. No se fijan thresholds definitivos hasta observar más periodos y calidad histórica; `--min-grants` es un parámetro de informe, no una regla SEO de producción.

No se crearán combinaciones programáticas indiscriminadas ni thin content. La generación dependerá de utilidad real, calidad, frescura, indexabilidad y capacidad de mantener la página actualizada. Se definirán posteriormente metadatos, enlazado interno, datos estructurados y estrategia de canonicalización.
