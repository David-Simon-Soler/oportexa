# Plan de backfill histórico

Este documento diseña una campaña futura; no autoriza ejecutarla completa en desarrollo ni producción.

## Estrategia de cobertura

La campaña debe avanzar de reciente a antiguo. La cobertura reciente aporta utilidad de descubrimiento y SEO antes, permite validar revalidaciones y reduce el riesgo de invertir primero en un histórico que todavía no tiene demanda demostrada.

1. **Fase 1 — Actualidad:** últimos 90 días, partición diaria o semanal según densidad.
2. **Fase 2 — Año anterior:** meses recientes completos, subdividiendo ventanas densas tras dry-run.
3. **Fase 3 — Años anteriores:** avanzar año a año, mensual por defecto y semanal cuando una ventana supere el umbral operativo acordado.
4. **Fase 4 — Extensión histórica:** sólo si la calidad, coste, utilidad SEO y capacidad de almacenamiento justifican ampliar cobertura.

Cada fase requiere dry-run, revisión de densidad, límite de registros, una ventana piloto, resume probado y data quality antes de continuar. La subdivisión automática mensual → semanal → diaria queda como mejora futura; mientras no esté implementada, la división es explícita y operada por comandos.

## Campaña operativa

- Una sola campaña secuencial por IP y ventana.
- `page_size=100` como valor conservador; no subirlo sin medir.
- `--max-windows` para pilotos y `--max-records` como guardrail de sesión.
- `--resume` después de cualquier interrupción; `--retry-failed` sólo tras inspeccionar fallos.
- No borrar runs, fallos ni RAW para corregir una campaña.
- Registrar por ventana páginas, detalles, nuevos, actualizados, sin cambios, fallos, retries, 429, duración y throughput.

## Minimum useful coverage

No se fija una cifra arbitraria de convocatorias. La web puede considerarse útil públicamente cuando el dataset observado cubra simultáneamente:

- convocatorias abiertas recientes, no sólo histórico cerrado;
- las comunidades autónomas y provincias con densidad suficiente para fichas útiles;
- varios sectores y tipos de beneficiario con más de una oportunidad real;
- suficiente información en las fichas para explicar título, organismo, fechas, presupuesto y fuente oficial;
- calidad sin duplicados ni referencias huérfanas y una revalidación repetible.

El umbral debe medirse con el informe SEO y data quality por corte de fecha. Los 1.840 registros actuales son un entorno de validación técnica sesgado, no una cobertura nacional suficiente para afirmar lanzamiento.

## Revalidación futura

- **Diaria:** ingestión de convocatorias nuevas y revalidación de ventanas recientes.
- **Semanal:** revalidar los últimos días y detectar cambios de estado, fechas y presupuesto.
- **Mensual:** revisar ventanas recientes completas y fallos pendientes.
- **Histórico:** revalidar sólo cuando exista una señal de cambio, una corrección de fuente o una necesidad de calidad.

No se implementa scheduler en esta fase. Cada ejecución debe conservar procedencia, timestamps y el estado OPS.
