# Política de revalidación

## Objetivo

Mantener actualizada la capa local de Oportexa mediante el motor BDNS existente, sin consultar BDNS directamente desde la web y sin convertir timestamps locales en fechas oficiales.

## Cadencias operativas previstas

### DAILY

Revisar novedades recientes con ventanas pequeñas y explícitas. Ejecutar con `--dry-run`, `--max-windows` y `--max-records` antes de escribir. Prioridad: detectar convocatorias nuevas.

En producción, GitHub Actions ejecuta diariamente `.github/workflows/daily-revalidation.yml` a las 06:15 UTC. Revalida los últimos tres días con ventanas `daily`, `--max-records 500` y `--retry-failed`, usando exclusivamente el secreto `OPORTEXA_INGEST_DATABASE_URL`, cuya URL debe pertenecer al rol `oportexa_ingest`. El workflow también ejecuta `data_quality_report.py` y `quality_gate.py`.

### WEEKLY

Revalidar ventanas recientes para detectar cambios en estado, presupuesto, fechas, descripción o relaciones. La ejecución es idempotente: los registros sin cambios deben quedar como `unchanged`.

### MONTHLY

Revisar ventanas recientes más amplias, fallos pendientes y ventanas incompletas. Mantener el límite de requests conservador y no lanzar meses densos sin dividirlos.

### HISTORICAL

Sólo ejecutar por una razón documentada. Requiere preflight, estimación de registros, requests, tiempo y almacenamiento.

## Freshness

- `source_received_date`: fecha recibida dentro del dato de BDNS; no es necesariamente fecha de publicación.
- `first_seen_at`: primera observación local de la convocatoria.
- `last_seen_at`: última observación local de la convocatoria.
- `ops.ingestion_runs.completed_at`: momento en que terminó una ventana operacional.

La interfaz puede hablar de “Última observación por Oportexa”. Nunca debe presentar `last_seen_at` o `completed_at` como “última actualización de BDNS”.

## Histórico y ejecución manual

El workflow diario no ejecuta backfills históricos. Toda carga histórica debe lanzarse manualmente con `scripts/backfill_calls.py`, tras un dry-run y con `--max-windows` y/o `--max-records` explícitos, siguiendo `docs/BACKFILL_RUNBOOK.md`. `workflow_dispatch` permite repetir la misma revalidación corta bajo supervisión; no convierte el workflow en un lanzador de rangos históricos.

## Procedimiento seguro

1. Revisar OPS y fallos activos.
2. Ejecutar dry-run.
3. Elegir ventanas pequeñas.
4. Usar `--max-records` explícito.
5. Mantener aproximadamente 5 requests por segundo o menos.
6. Comprobar checkpoints, duplicados, huérfanos y fallos.
7. Registrar resultado y detenerse ante 429 persistentes o anomalías.

No se configura todavía un scheduler externo o cloud.
