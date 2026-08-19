# Runbook de backfill BDNS

Este runbook describe el modo secuencial y controlado. No usar credenciales productivas localmente.

## Preparación

```bash
cd /home/dss02/Escritorio/Proyectos/opportunity-intel
docker compose up -d postgres
docker compose ps
docker compose exec -T postgres pg_isready -U opportunity_intel -d opportunity_intel
```

Aplicar migraciones:

```bash
cd services/ingestion
export DATABASE_URL='postgresql+psycopg://opportunity_intel:local_dev_only@127.0.0.1:55432/opportunity_intel'
.venv/bin/alembic upgrade head
```

## Plan y ejecución

Dry-run sin escrituras:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2025-12-08 --date-to 2025-12-13 \
  --window daily --dry-run
```

Prueba pequeña:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2025-12-08 --date-to 2025-12-08 \
  --window daily
```

Rango mensual controlado:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2024-01-01 --date-to 2024-03-31 \
  --window monthly --max-windows 2
```

Reanudar:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2024-01-01 --date-to 2024-03-31 \
  --window monthly --resume
```

Reintentar fallos pendientes:

```bash
.venv/bin/python scripts/backfill_calls.py \
  --date-from 2024-01-01 --date-to 2024-03-31 \
  --window monthly --resume --retry-failed
```

Detención: usar `Ctrl+C` una vez y esperar a que el proceso marque el run como `interrupted`. No matar el contenedor ni borrar checkpoints durante una página activa.

## Inspección y diagnóstico

```bash
.venv/bin/python scripts/inspect_ingestion_runs.py
.venv/bin/python scripts/inspect_ingestion_runs.py --failed
.venv/bin/python scripts/data_quality_report.py
.venv/bin/python scripts/inspect_db.py
```

Un run `interrupted` o `failed` se reanuda con `--resume`; `last_page` es la última página completamente confirmada. Los fallos activos se conservan en `ops.ingestion_failures` y se resuelven mediante `--retry-failed`.

## DO NOT

- No borrar `ops.ingestion_runs` ni `ops.ingestion_failures`.
- No editar checkpoints manualmente.
- No lanzar rangos grandes sin dry-run y `--max-windows`.
- No ejecutar copias simultáneas de la misma ventana.
- No superar el límite oficial de BDNS.
- No usar credenciales productivas localmente.
- No almacenar payloads RAW en logs.
- No hacer backfill completo sin una revisión operacional específica.
