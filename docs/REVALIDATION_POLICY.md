# Política de revalidación

## Objetivo

Mantener actualizada la capa local de Oportexa mediante el motor BDNS existente, sin consultar BDNS directamente desde la web y sin convertir timestamps locales en fechas oficiales.

## Cadencias operativas previstas

### DAILY

Revisar novedades recientes con ventanas pequeñas y explícitas. Ejecutar con `--dry-run`, `--max-windows` y `--max-records` antes de escribir. Prioridad: detectar convocatorias nuevas.

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

## Procedimiento seguro

1. Revisar OPS y fallos activos.
2. Ejecutar dry-run.
3. Elegir ventanas pequeñas.
4. Usar `--max-records` explícito.
5. Mantener aproximadamente 5 requests por segundo o menos.
6. Comprobar checkpoints, duplicados, huérfanos y fallos.
7. Registrar resultado y detenerse ante 429 persistentes o anomalías.

No se configura todavía un scheduler externo o cloud.
