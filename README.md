# Oportexa

Oportexa es una plataforma web para descubrir y consultar convocatorias de ayudas y subvenciones públicas en España. Trabaja principalmente con información pública de la Base de Datos Nacional de Subvenciones y del Sistema Nacional de Publicidad de Subvenciones y Ayudas Públicas (BDNS/SNPSAP), y la organiza para hacerla más fácil de explorar y verificar.

🌐 Producción: <https://www.oportexa.com>

Oportexa no es un sitio oficial, no representa a la Administración Pública y no sustituye a las fuentes oficiales. Para requisitos, plazos y trámites debe consultarse siempre el organismo competente y la convocatoria original.

## Qué permite hacer

- Explorar convocatorias y subvenciones mediante búsqueda, filtros y ordenación.
- Consultar fichas individuales con estado, fechas, presupuesto, organismo, taxonomías y procedencia.
- Navegar por región, sector, organismo y tipo de beneficiario.
- Identificar convocatorias marcadas como abiertas por BDNS.
- Acceder a las bases reguladoras, sedes electrónicas y otras fuentes oficiales cuando están disponibles.

La aplicación muestra la cobertura disponible en el dataset local; esa cobertura es parcial y no equivale al universo completo de BDNS.

## Arquitectura

~~~mermaid
flowchart TD
    A[BDNS / SNPSAP] --> B[Servicio Python de ingesta]
    B --> C[RAW JSONB + provenance]
    C --> D[CORE normalizado]
    D --> E[(PostgreSQL)]
    E --> F[DAL server-only de Next.js]
    F --> G[oportexa.com]
~~~

- **BDNS/SNPSAP**: fuente primaria de convocatorias públicas.
- **Servicio Python**: cliente BDNS, ingesta incremental y backfill controlado, validación, transformación y persistencia.
- **RAW**: conserva la respuesta recibida, hash, endpoint y timestamps de procedencia.
- **CORE**: modelo normalizado de convocatorias, catálogos y relaciones N:M.
- **OPS**: seguimiento de ejecuciones, checkpoints y fallos de ingesta.
- **Web Next.js**: consulta únicamente la proyección pública de core mediante una DAL server-only. Las peticiones web no consultan BDNS en tiempo real.
- **PostgreSQL**: persistencia de RAW, CORE y OPS.

## Pipeline de datos

El servicio de ingesta obtiene primero códigos de convocatoria mediante listados por ventana temporal y recupera después el detalle de cada código. La carga se procesa de forma secuencial y paginada, con pausas y reintentos limitados para errores recuperables.

Cada convocatoria sigue este flujo:

1. Obtener el registro desde BDNS.
2. Guardar la respuesta en raw.bdns_grant_calls junto con su hash y procedencia.
3. Validar y transformar los campos verificados.
4. Persistir la convocatoria normalizada y sus relaciones en core.
5. Ejecutar RAW y CORE en una transacción por convocatoria.

La idempotencia se apoya en el código BDNS único, el hash del payload RAW, las claves únicas de catálogos y las claves compuestas de las relaciones. Las actualizaciones no dependen de una transacción gigante por lote.

Las ejecuciones incrementales y los backfills controlados se registran en ops.ingestion_runs, con estado, contadores y checkpoints de página. ops.ingestion_failures conserva los fallos por código, permite reintentos limitados y mantiene el historial cuando un fallo se resuelve. La reconciliación sólo marca un fallo como resuelto cuando existe evidencia de una ingestión posterior; la mera existencia del código en CORE no basta.

El motor de backfill admite ventanas diarias, semanales y mensuales, streaming por páginas, --resume, --dry-run, reintentos y límites explícitos. Los advisory locks de PostgreSQL evitan procesar simultáneamente la misma ventana. El workflow diario de GitHub Actions revalida una ventana corta y ejecuta el informe de calidad, el quality gate y la inspección operacional.

## Stack

| Capa | Tecnología |
| --- | --- |
| Web | Next.js 16, React 19, TypeScript |
| Ingesta | Python 3.12+, httpx, Pydantic, SQLAlchemy, psycopg |
| Migraciones | Alembic |
| Datos | PostgreSQL 16; esquemas raw, core y ops |
| Testing | Vitest, pytest e integración PostgreSQL |
| Deploy | Vercel para la aplicación web |
| Automatización | GitHub Actions para revalidación BDNS y quality gates |

## SEO y descubrimiento

La web dispone de:

- URLs públicas para fichas de convocatorias y exploración por región, sector, organismo y beneficiario.
- Metadata y canonicalización mediante la configuración de Next.js y SITE_URL.
- robots.txt.
- Sitemap dinámico con la portada, páginas de exploración, fichas y páginas institucionales.
- Páginas de error y rutas no encontradas controladas.
- Páginas de búsqueda y filtros que evitan indexar combinaciones arbitrarias mediante noindex cuando contienen parámetros.

Estas capacidades describen la implementación técnica. No implican una posición concreta en buscadores ni un volumen determinado de tráfico.

## Estructura del repositorio

~~~text
apps/
  web/                 # Aplicación Next.js y DAL server-only
services/
  ingestion/           # Cliente BDNS, ETL, backfill, calidad y operaciones
packages/
  database/            # Espacio para contratos y utilidades compartidas de datos
docs/                  # Producto, arquitectura, operación, SEO y gobernanza
adr/                   # Decisiones arquitectónicas
~~~

## Desarrollo local

### Web

~~~bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
~~~

Variables disponibles en apps/web/.env.example:

~~~bash
DATABASE_URL=postgresql+psycopg://user:password@127.0.0.1:55432/opportunity_intel
SITE_URL=http://localhost:3000
~~~

Comandos de validación web:

~~~bash
npm run lint
npm run test
npm run build
~~~

### PostgreSQL e ingesta

Desde la raíz del repositorio, PostgreSQL local puede levantarse con Docker Compose:

~~~bash
docker compose up -d postgres
docker compose ps
~~~

Después, para preparar el servicio Python:

~~~bash
cd services/ingestion
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
export DATABASE_URL='postgresql+psycopg://user:password@127.0.0.1:55432/opportunity_intel'
alembic upgrade head
pytest
~~~

La contraseña del ejemplo es ficticia. No se deben guardar credenciales en Git.

Ejemplos de comandos operativos:

~~~bash
python scripts/inspect_db.py
python scripts/data_quality_report.py
python scripts/quality_gate.py
python scripts/inspect_ingestion_runs.py --failed
python scripts/backfill_calls.py \
  --date-from 2026-08-18 \
  --date-to 2026-08-19 \
  --window daily \
  --dry-run
~~~

Para una operación real de backfill deben seguirse los límites, comprobaciones y pasos de docs/BACKFILL_RUNBOOK.md.

## Calidad y testing

El repositorio incluye:

- Tests unitarios de cliente BDNS, transformaciones, parámetros, ventanas y operaciones de backfill.
- Tests de integración opcionales contra PostgreSQL.
- Lint, tests y build de la aplicación web.
- Migraciones Alembic como fuente de verdad del esquema.
- Informe de calidad de datos sobre duplicados, integridad, referencias RAW/CORE, fechas y relaciones.
- Quality gate que bloquea fallos de integridad o fallos de ingesta no resueltos.
- Inspección read-only de ejecuciones y fallos operacionales.

Los tests que requieren PostgreSQL se omiten cuando no se proporciona una base de datos de prueba aislada.

## Estado del proyecto

Oportexa está publicada en producción y se encuentra en una fase inicial de indexación y observación. La base técnica de Discovery, la ingesta persistente, la revalidación y el backfill controlado están implementados; la cobertura de datos continúa siendo parcial.

El proyecto seguirá evolucionando a partir de la cobertura disponible, la calidad del dato y la observación del uso real. Actualmente no hay usuarios, autenticación, newsletter, pagos, IA, matching ni monetización implementados.

## Fuente de los datos y aviso

La información procede principalmente de datos públicos de BDNS/SNPSAP. Oportexa es un proyecto independiente y no es una web oficial de la Administración.

La información puede cambiar o contener diferencias respecto de otras publicaciones. Para la información definitiva, requisitos, plazos y trámites deben consultarse las fuentes oficiales enlazadas y el organismo competente.

## Autor

David José Simón Soler
