# Servicio de ingestión y Data Core

Cliente BDNS/SNPSAP y primer ETL incremental persistente de convocatorias. La persistencia usa exclusivamente PostgreSQL y separa una capa RAW fiel a la respuesta oficial de una capa CORE normalizada.

## Instalación local

Requiere Python 3.12+.

```bash
cd services/ingestion
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Configura `DATABASE_URL` solo para los comandos que escriben o inspeccionan PostgreSQL:

```bash
export DATABASE_URL='postgresql+psycopg://user:password@localhost:5432/opportunity_intel'
```

La contraseña del ejemplo es ficticia. No se guardan credenciales en Git.

## Migraciones

Las tablas no se crean automáticamente en runtime. La fuente de verdad del esquema es Alembic:

```bash
alembic upgrade head
```

La migración inicial crea los esquemas PostgreSQL `raw` y `core`.

## PostgreSQL local con Docker Compose

Requiere Docker y Docker Compose. La configuración levanta únicamente PostgreSQL, con volumen dedicado, contraseña local ficticia y binding en `127.0.0.1:55432`:

```bash
docker compose up -d postgres
docker compose ps
docker compose down
```

El volumen no se borra con `down`; la base local queda disponible para desarrollo. No se añade pgAdmin ni ningún servicio adicional.

## Scripts manuales

```bash
python scripts/inspect_calls.py
python scripts/inspect_calls.py --limit 10
python scripts/inspect_call_detail.py 925673
python scripts/ingest_calls.py --date-from 2026-08-18 --date-to 2026-08-19 --limit 20
python scripts/ingest_calls.py --date-from 2026-08-18 --date-to 2026-08-19 --limit 5 --dry-run
python scripts/inspect_db.py
```

`ingest_calls.py` consulta códigos por fecha, recupera los detalles, escribe una convocatoria y sus relaciones en una transacción propia y continúa si una convocatoria falla. `--dry-run` consulta y transforma, pero no crea una conexión ni escribe en PostgreSQL.

## Consultas y calidad

Las consultas son de lectura y siempre muestran una advertencia de dataset parcial:

```bash
python scripts/query_intelligence.py summary
python scripts/query_intelligence.py top-sectors --limit 10
python scripts/query_intelligence.py top-regions --limit 10
python scripts/query_intelligence.py top-organizations --limit 10
python scripts/query_intelligence.py closing-soon --days 30
python scripts/query_intelligence.py search --region "Tarragona" --open
python scripts/data_quality_report.py
```

Los resultados reflejan sólo el dataset local ingerido y no son necesariamente representativos de toda la BDNS.

## Revalidación automática en producción

GitHub Actions ejecuta `.github/workflows/daily-revalidation.yml` diariamente. El flujo consulta BDNS, revalida una ventana corta y escribe en Neon usando únicamente el secreto `OPORTEXA_INGEST_DATABASE_URL`; la aplicación web consulta después la capa `core` con su conexión de lectura. A continuación ejecuta el informe de calidad, el quality gate y una inspección de fallos. No hace backfills históricos ni modifica DNS, Vercel o secretos.

## Tests

```bash
pytest
```

Los tests unitarios usan transporte mock y fixtures sintéticos. La integración PostgreSQL está separada y se omite si `DATABASE_URL` no apunta a PostgreSQL.

## Limitaciones actuales

- Solo se cubren los endpoints confirmados de búsqueda, últimas y detalle.
- Los modelos representan un subconjunto de campos verificados y toleran campos adicionales.
- No hay SQLite como alternativa, cache persistente de HTTP, dumps ni descarga persistente de documentos.
- La API pública no requiere autenticación según la documentación verificada.
- No hay concurrencia; el cliente aplica pausa configurable y reintentos limitados para errores recuperables.
- El smoke test PostgreSQL requiere una instancia aislada ya disponible; no se instala un servicio del sistema ni Docker en esta fase.
