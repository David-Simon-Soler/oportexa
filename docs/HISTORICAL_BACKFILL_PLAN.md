# Plan de backfill histórico

Este documento diseña una campaña futura; no autoriza ejecutarla completa en desarrollo ni producción.

## Stages operativos

La campaña debe avanzar de reciente a antiguo. La cobertura reciente aporta utilidad de descubrimiento y SEO antes, permite validar revalidaciones y reduce el riesgo de invertir primero en un histórico que todavía no tiene demanda demostrada.

1. **STAGE 0 — Validación operacional:** completado. Incluye migraciones limpias, dry-run, SIGINT, resume, locking, idempotencia y gates de calidad.
2. **STAGE 1 — 2026 reciente:** `2026-01-01`–fecha actual de la campaña. Prioridad alta; usar semanal porque enero–julio anuncian entre 4.971 y 6.783 registros mensuales. El bloque actual cubrió parcialmente julio y agosto.
3. **STAGE 2 — 2025:** año completo. El preflight anuncia aproximadamente 70.213 registros; dividir semanalmente los meses >5.000 y usar bloques de 1.000–1.500 intentos.
4. **STAGE 3 — 2024:** año completo, comenzar por meses con densidad observada y mantener división semanal cuando el listado supere 5.000.
5. **STAGE 4 — 2023–2020:** histórico medio, mensual sólo después de dry-run; objetivo de cobertura y calidad, no descarga masiva.
6. **STAGE 5 — histórico restante:** sólo si la utilidad, frescura, almacenamiento y coste operativo justifican continuar.

Cada fase requiere dry-run, revisión de densidad, límite de registros, una ventana piloto, resume probado y data quality antes de continuar. La subdivisión automática mensual → semanal → diaria queda como mejora futura; mientras no esté implementada, la división es explícita y operada por comandos.

Cada stage se detiene si aparecen duplicados, huérfanos, fallos activos crecientes, más de 5% de fallos en una página, 429 persistentes, PostgreSQL inestable o RSS creciente. La cobertura anunciada por BDNS no equivale a filas CORE locales: los totales son una expectativa de listado y deben validarse durante la ingestión.

## Campaña operativa

- Una sola campaña secuencial por IP y ventana.
- `page_size=100` como valor conservador; no subirlo sin medir.
- `--max-windows` para pilotos y `--max-records` como guardrail de sesión.
- `--resume` después de cualquier interrupción; `--retry-failed` sólo tras inspeccionar fallos.
- Cada ejecución real debe incluir `--max-records`; no se aceptan comandos abiertos para campañas largas.
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

## Comandos recomendados

Siempre ejecutar primero un dry-run y después un bloque limitado:

```bash
cd /home/dss02/Escritorio/Proyectos/opportunity-intel/services/ingestion
export DATABASE_URL='postgresql+psycopg://opportunity_intel:local_dev_only@127.0.0.1:55432/opportunity_intel'
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2026-07-01 --date-to 2026-07-31 \
  --window weekly --max-records 1500 --dry-run
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2026-07-01 --date-to 2026-07-31 \
  --window weekly --max-records 1500
```

Para continuar un stage:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2026-07-01 --date-to 2026-07-31 \
  --window weekly --max-records 1500 --resume
```

No se documentan comandos sin límite que puedan lanzar accidentalmente una campaña histórica completa.
