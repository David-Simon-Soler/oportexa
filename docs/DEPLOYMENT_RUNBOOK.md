# Oportexa — deployment runbook

Estado: **PLAN — NO EJECUTADO**
Última revisión: 2026-08-20

Este runbook describe una futura puesta en producción. No contiene credenciales reales, no crea recursos y no debe ejecutarse sin completar los gates.

## 0. Gate previo

No comenzar hasta confirmar:

- Dominio `oportexa.com` bajo control del operador.
- Proveedor y región elegidos.
- Plan de backups y restore probado.
- Roles DB preparados.
- `SITE_URL` y URLs de conexión disponibles mediante secret manager.
- Cobertura y limitaciones del dataset aprobadas para exposición pública.
- No hay migraciones pendientes sin revisar.

## 1. Crear cuentas y recursos

Crear manualmente, sin compartir credenciales entre servicios:

1. Cuenta de proveedor web.
2. Proyecto PostgreSQL gestionado.
3. Runner de jobs Python.
4. Almacenamiento de backups fuera del proveedor principal.
5. Cuenta GitHub privada inicialmente, cuando se autorice crear remoto.

No crear recursos enterprise, réplicas, multi-region ni servicios auxiliares todavía.

## 2. Provisionar PostgreSQL

1. Elegir PostgreSQL 16 o versión compatible validada.
2. Seleccionar inicialmente 10 GB o más de disco y 1–2 GB de RAM.
3. Activar TLS requerido.
4. Crear base y schemas mediante Alembic, no manualmente.
5. Guardar URL directa de migración/ingestión y URL pooled de web si el proveedor las ofrece.

## 3. Crear roles

Crear fuera de la aplicación:

- `oportexa_migrate`: DDL y migraciones.
- `oportexa_ingest`: escritura RAW/CORE/OPS.
- `oportexa_web`: SELECT explícito sobre CORE.

Probar que `oportexa_web` no puede leer `raw` ni modificar `core`.

## 4. Ejecutar migraciones

Desde un entorno operador seguro:

```bash
cd /path/to/opportunity-intel/services/ingestion
export DATABASE_URL='postgresql+psycopg://<migration-role>:<secret>@<direct-host>/<database>?sslmode=require'
alembic upgrade head
```

Comprobar schemas `raw`, `core`, `ops`, `alembic_version`, foreign keys, índices y constraints.

No ejecutar Alembic desde una request web.

## 5. Seed/transfer del dataset

Elegir una única estrategia documentada:

### Híbrida recomendada

1. Crear schema limpio.
2. Restaurar un dump validado, fuera de Git, si se acepta su provenance.
3. Ejecutar quality report.
4. Ejecutar una revalidación pequeña contra BDNS.
5. Registrar el punto de corte y el origen del seed.

### Reproducible desde BDNS

1. Crear schema limpio.
2. Ejecutar ventanas pequeñas con `--dry-run`.
3. Ejecutar campaña controlada y reanudable.
4. Comprobar DATA QUALITY después de cada bloque.

No mezclar dumps de desarrollo con producción sin registrar su origen y fecha.

## 6. Validar DB

Ejecutar, desde el runner o un entorno seguro:

```bash
python scripts/data_quality_report.py
python scripts/inspect_ingestion_runs.py
```

Comprobar duplicados, huérfanos, campos obligatorios, RAW references, fallos activos y conteos CORE/RAW.

## 7. Preparar GitHub y CI

Cuando se autorice crear remoto:

1. Preferir repositorio privado inicialmente.
2. Configurar secrets en GitHub/Vercel/Railway, nunca en YAML ni Git.
3. Añadir checks de `npm run lint`, `npm run test`, `npm run build` y pytest.
4. Separar preview y production.
5. Bloquear deploy si falla build o hay migración pendiente.

No configurar remoto ni push como parte de este plan.

## 8. Desplegar web

Configurar el root directory `apps/web` o la configuración equivalente de monorepo.

Build esperado:

```bash
npm ci
npm run lint
npm run test
npm run build
```

Usar Node.js compatible con Next.js 16.3.1. Configurar primero preview, ejecutar smoke test y promover después a producción.

## 9. Variables de entorno

### Web runtime

```text
SITE_URL=https://oportexa.com
DATABASE_URL=<pooled-web-read-only-url>
```

La separación futura de nombres (`DATABASE_URL_WEB` y `DATABASE_URL_INGESTION`) requerirá un pequeño cambio coordinado en código/configuración; actualmente ambos runtimes leen `DATABASE_URL`.

### Runner

```text
DATABASE_URL=<direct-ingestion-write-url>
BDNS_API_BASE_URL=<official-base-url>
BDNS_TIMEOUT_SECONDS=20
BDNS_PAGE_SIZE=100
```

### Migraciones

```text
DATABASE_URL=<direct-migration-url>
```

`TEST_DATABASE_URL` queda solo para CI/desarrollo. Ninguna variable de base de datos debe comenzar por `NEXT_PUBLIC_`.

## 10. DNS y TLS

Después de conocer el proveedor, añadir únicamente los registros oficiales que indique:

- `oportexa.com` como dominio principal.
- `www.oportexa.com` como alias/redirección.

Configurar `https://oportexa.com` como canonical y redirigir `www` a la raíz. Verificar certificado gestionado y renovación automática.

## 11. Smoke test de producción

Comprobar:

```text
/
/subvenciones
/subvenciones/<slug-real>
/subvenciones/region
/robots.txt
/sitemap.xml
/manifest.webmanifest
/favicon.ico
/opengraph-image.png
```

Validar `200`, `404` controlado, Content-Type, metadata, canonical, Oportexa, ausencia de secretos y que la web solo muestre datos CORE.

## 12. Jobs

### Revalidación recurrente

Preferencia inicial: runner Python separado. Ejecutar una ventana pequeña y explícita, con límites, advisory lock y lectura posterior de OPS.

Cadencia propuesta:

- Daily: novedades recientes.
- Weekly: revalidación de ventanas recientes.
- Monthly: revisión amplia y fallos pendientes.

### Backfill histórico

Solo manual/staged:

```bash
python scripts/backfill_calls.py \
  --date-from YYYY-MM-DD \
  --date-to YYYY-MM-DD \
  --window monthly \
  --dry-run
```

Después del dry-run, usar `--max-windows`, `--max-records` y `--resume`. No ejecutar campañas masivas sin observar requests, tasa, memoria y OPS.

Vercel Cron no es el runner recomendado para backfill: invoca funciones HTTP, tiene límites de duración y no reintenta automáticamente una invocación fallida. Puede ser suficiente para un trigger corto futuro, no para el proceso Python largo actual.

## 13. Backups

1. Activar backup gestionado diario.
2. Ejecutar `pg_dump` semanal desde un runner seguro.
3. Comprimir, cifrar y subir a almacenamiento externo.
4. Mantener retención diaria 7 días, semanal 4 semanas y mensual 3–6 meses.
5. Probar restore trimestralmente.
6. Registrar resultado sin incluir credenciales ni payloads en logs.

## 14. Rollback y recuperación

### DB no disponible

Mostrar error controlado, revisar provider health, conexiones y TLS. No reintentar agresivamente desde la web.

### Deploy fallido

Mantener deployment anterior y revisar build/runtime logs. No cambiar DB para solucionar un fallo de frontend.

### Migración defectuosa

Detener promoción web, restaurar snapshot si procede, aplicar una migración correctiva revisada. No editar migraciones consolidadas.

### Ingestión fallida

Inspeccionar `ops.ingestion_runs` y `ops.ingestion_failures`, usar `--retry-failed` tras clasificar el error. No borrar auditoría.

### BDNS no disponible o rate limit

Detener la campaña, conservar el run reanudable y esperar. No subir concurrencia ni ignorar 429 persistentes.

### Borrado accidental

Detener escrituras, identificar snapshot/dump más reciente, restaurar en una base aislada y comparar antes de reemplazar.

### Outage del proveedor

Usar restore portátil en un proveedor alternativo solo con un plan explícito. No mantener una segunda región activa de forma prematura.

## 15. Do not

- No poner secretos en Git, `.env` versionado, logs o comandos compartidos.
- No ejecutar migraciones en cada request.
- No exponer RAW al rol web.
- No lanzar backfill desde una función HTTP.
- No ejecutar dos campañas sobre la misma ventana.
- No editar checkpoints manualmente.
- No borrar `ops` para “limpiar” una ejecución.
- No usar credenciales de desarrollo en producción.
- No configurar DNS antes de elegir proveedor.
- No activar analytics, AdSense o Search Console como requisito de runtime.
- No crear Kubernetes, Redis, Kafka, Elasticsearch ni multi-region sin evidencia.
