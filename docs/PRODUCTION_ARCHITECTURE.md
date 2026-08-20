# Oportexa — arquitectura de producción

Estado: **AUDITORÍA Y PLAN — NO PROVISIONADO**
Fecha de revisión: 2026-08-20

Este documento describe lo que Oportexa necesitará para producción. No crea cuentas, recursos cloud, DNS, remoto Git ni infraestructura.

## 1. Resumen ejecutivo

La recomendación inicial es una arquitectura separada y pequeña:

```text
Usuario
  ↓ HTTPS / CDN gestionada
Vercel Pro — Next.js Node runtime
  ↓ conexión PostgreSQL pooled, solo lectura
Neon PostgreSQL — schemas RAW / CORE / OPS

Railway Hobby — runner Python para ingestión, revalidación y backfill controlado
  ├── BDNS/SNPSAP
  └── conexión de escritura a PostgreSQL

Operador / CI protegido
  ├── migraciones Alembic
  └── pg_dump portátil y pruebas de restore
```

Es una recomendación de producción pequeña, no una obligación de proveedor. Mantiene PostgreSQL estándar, separa lectura y escritura y permite mover la web, los jobs o la base de datos por separado.

La alternativa de coste mínimo es Vercel Hobby + Neon Free, pero solo debe considerarse una preproducción o un proyecto personal mientras se confirma la elegibilidad comercial de Vercel Hobby y se aceptan los límites de pausa, cómputo y backups.

## 2. Inventario actual

| Clasificación | Componente actual | Necesidad en producción |
| --- | --- | --- |
| Runtime web | `apps/web`, Next.js 16.3.1, React 19, TypeScript | Sí |
| Database | PostgreSQL 16, schemas `raw`, `core`, `ops` | Sí |
| Background data jobs | `services/ingestion`, Python >=3.12 | Sí, separado de la web |
| Migrations | Alembic | Sí, ejecutado de forma independiente |
| Official source | BDNS/SNPSAP | Sí, salida de jobs |
| Optional | CDN, provider logs, health checks | Gestionados por proveedor al inicio |
| Development only | Docker Compose, `.venv`, DB local, test DB | No provisionar como runtime público |
| Fuera de alcance | Auth, analytics, Redis, colas, IA, pagos | No necesarios |

No hay almacenamiento local de negocio: los checkpoints, fallos y datos viven en PostgreSQL. Los jobs deben poder reiniciarse en un filesystem efímero.

## 3. Flujo de datos

```text
BDNS window
  → listing page
  → BDNS codes
  → detail one-by-one
  → RAW JSONB + provenance
  → CORE normalized data + relations
  → OPS counters/checkpoint
  → next page/window
```

Las consultas públicas no consultan BDNS en tiempo real. El web runtime lee una proyección de `core`; `raw` queda fuera del rol web y `ops` no se expone al usuario.

## 4. Next.js y runtime web

- Next.js 16.3.1 con App Router.
- Server Components y DAL server-only para las páginas que leen PostgreSQL.
- Runtime recomendado: Node.js, no Edge, porque el código usa `pg` y requiere acceso TCP/TLS compatible con PostgreSQL.
- Las rutas de catálogo, taxonomía y detalle son dinámicas desde DB; robots y metadata siguen siendo handlers de Next.js.
- No hay API pública ni Server Actions de negocio.
- El build necesita Node.js, `npm ci` y `npm run build` desde `apps/web`.
- Los assets públicos son estáticos y pequeños; no se necesita almacenamiento persistente local.
- No se necesita image processing remoto para el producto actual.
- `SITE_URL` es necesaria para metadataBase, canonical, sitemap y robots.
- El pool actual tiene `max: 5` por proceso y reutiliza un singleton mientras vive el proceso.

### Opciones web

**Vercel.** Mejor ajuste técnico para este Next.js: detección de framework, builds, HTTPS, previews, CDN y variables integradas. El plan Hobby figura como `$0/mes`, pero la propia página de precios lo describe para uso personal/no comercial; el plan Pro figura como `$20/mes` y es la opción que debe presupuestarse para producción pública. [Precios oficiales de Vercel](https://vercel.com/pricing).

**Cloudflare Workers/Pages.** Puede ser atractivo por coste y red, pero este proyecto usa Node.js y `pg` desde Server Components. Requeriría validar el adaptador, runtime y acceso a la base antes de comprometer la arquitectura. No es la opción conservadora para el primer deploy.

**Netlify.** Puede alojar Next.js, pero seguiría necesitando una base PostgreSQL externa y un mecanismo aparte para jobs Python largos. No aporta una ventaja suficiente sobre Vercel para este repositorio; precios y límites deben verificarse en el momento de provisionar.

**VPS/self-host.** Permite ejecutar Next.js, PostgreSQL y Python juntos con cron, pero introduce actualizaciones, firewall, TLS, backups, monitorización y recuperación a cargo del operador. Es la alternativa de máximo control, no la de menor mantenimiento.

## 4.1 Comparativa de proveedores

| Proveedor | Encaje PostgreSQL/web | Coste oficial observado | Pooling/backups | Riesgos o límites para Oportexa |
| --- | --- | --- | --- | --- |
| Neon | PostgreSQL gestionado, muy buen encaje con Vercel | Free `$0`; Launch usage-based, típico indicado `$15/mes` | Pooling incluido; restore window según plan | Free tiene 0,5 GB y 100 CU-horas/proyecto; verificar retención adecuada |
| Supabase | PostgreSQL gestionado y plataforma más amplia | Free `$0`; Pro desde `$25/mes` | Free 500 MB y pausa tras una semana; Pro backups diarios 7 días | Más superficie de producto de la necesaria; el Free no es base pública persistente adecuada |
| Railway | Web, worker, jobs y PostgreSQL en un mismo entorno | Free `$0` con crédito; Hobby `$5/mes` más uso | Adecuado para runner; backup/PITR exactos deben verificarse al provisionar | Coste variable y mayor lock-in si concentra todos los componentes |
| Render | Web, background workers, cron y Postgres | Precio actual de servicios: NEEDS LIVE VERIFICATION | Tiene private networking y servicios de jobs | Puede ser simple, pero comparar coste total DB+worker antes de elegir |
| Aiven | PostgreSQL gestionado | Free `$0`/1 GB; Developer `$5`; Hobbyist desde `$12` | Free/Developer sin pooling; backups limitados según plan | El Free es demasiado pequeño para crecimiento y tiene menos margen operativo |
| VPS | PostgreSQL y todos los procesos autogestionados | NEEDS LIVE VERIFICATION según proveedor/región | Total control; backups a diseñar y operar | Menor lock-in, pero mayor mantenimiento y riesgo operativo |

Los precios son una fotografía, no una garantía contractual. Neon indica 0,5 GB y 100 CU-horas en Free; Supabase indica 500 MB y pausa tras una semana de inactividad en Free; Railway separa suscripción y consumo; Aiven publica sus límites por plan. Verificar moneda, IVA, región, retención y límites antes de contratar.

## 5. PostgreSQL actual y requisitos mínimos

El modelo requiere PostgreSQL estándar con:

- PostgreSQL 16 o compatible posterior validado.
- Schemas `raw`, `core` y `ops`.
- JSONB en `raw.bdns_grant_calls.payload`.
- Índices B-tree, constraints, foreign keys, unique keys y partial index de fallos activos.
- Alembic para migraciones.
- Sin extensiones especiales, FTS ni servicios auxiliares.
- RAW, CORE y OPS persistentes y respaldados juntos.

Medición local documentada: aproximadamente 40 MB de base completa para 6.674 convocatorias. La proyección lineal orientativa del repositorio es aproximadamente 600 MB para 100k y 3,6 GB para 600k, con variación posible por JSONB, TOAST, índices y asociaciones.

Requisitos iniciales prudentes:

| Recurso | Mínimo operativo recomendado |
| --- | --- |
| Disco | 10 GB inicialmente; crecer a 25–50 GB sin rediseño |
| Memoria | 1–2 GB |
| CPU | 1–2 vCPU |
| Conexiones | Pool web limitado; runner separado; margen para migración |
| TLS | SSL requerido para conexiones externas |
| Backups | Snapshot/provider backup + `pg_dump` portable |
| Red | Endpoint gestionado, credenciales separadas y sin acceso RAW desde web |

No se observan incompatibilidades con proveedores PostgreSQL serverless, pero la URL pooled y los límites de conexiones deben configurarse según proveedor.

## 6. Capas y permisos

Roles conceptuales:

1. `oportexa_migrate`: propietario técnico o rol con DDL, usado solo desde migración controlada.
2. `oportexa_ingest`: escritura en `raw`, `core` y `ops`; lectura de lo necesario para upsert, checkpoints y quality reports.
3. `oportexa_web`: `SELECT` únicamente sobre una lista explícita de tablas `core` necesarias para el DAL.

El rol web no debe tener `USAGE` ni `SELECT` sobre `raw`. El acceso a `ops` no se concede a la web salvo una funcionalidad futura que lo justifique.

SQL conceptual, aún no aplicado:

```sql
CREATE ROLE oportexa_web LOGIN PASSWORD '<secret-managed-outside-git>';
GRANT USAGE ON SCHEMA core TO oportexa_web;
GRANT SELECT ON core.grant_calls, core.organizations, core.sectors,
  core.regions, core.beneficiary_types, core.funds,
  core.grant_call_organizations, core.grant_call_sectors,
  core.grant_call_regions, core.grant_call_beneficiary_types,
  core.grant_call_funds TO oportexa_web;
```

La aplicación de estos roles se hará antes del primer deploy y se probará con consultas reales del DAL.

## 7. Jobs de datos

| Job | Cadencia | Duración esperada | Persistencia |
| --- | --- | --- | --- |
| Ingestión incremental | Daily | Minutos, según ventana | PostgreSQL |
| Revalidación reciente | Weekly | Minutos a horas | PostgreSQL |
| Revisión amplia | Monthly | Horas potenciales | PostgreSQL |
| Backfill histórico | Manual/staged | Horas o días | PostgreSQL |
| Retry failures | Manual o junto a revalidación | Variable | PostgreSQL |
| Quality report | Tras cada campaña y semanal | Minutos | Salida de logs/artefacto, no dato de negocio |
| Coverage report | Tras campañas históricas | Minutos | Salida de logs/artefacto |

Runtime requerido: Python >=3.12, dependencias de `services/ingestion/pyproject.toml`, salida a BDNS por HTTPS y PostgreSQL por TLS. El job no debe depender de disco persistente local.

El backfill no debe ejecutarse como función HTTP de la web: el throughput observado y los checkpoints necesitan un proceso Python largo y reanudable.

## 7.1 Opciones de ejecución

| Opción | Revalidación corta | Backfill largo | Evaluación |
| --- | --- | --- | --- |
| GitHub Actions scheduled | Adecuada si el repositorio y cuotas son aceptables | Solo bloques acotados; verificar timeout y límites | Barata, pero no debe ser el único plan para campañas de horas |
| Vercel Cron | Trigger diario corto | No recomendado | Llama una función HTTP, no ejecuta Python persistente; no tiene retry automático de una invocación fallida |
| Railway worker/job | Adecuada | Adecuada, con límites de coste configurados | Mejor opción gestionada para este runner Python |
| Render cron/background worker | Adecuada | Posible | Requiere validar duración y coste del servicio |
| VPS cron/systemd | Adecuada | Adecuada | Máximo control y coste potencialmente bajo, más mantenimiento |
| DB functions | No | No | No apropiadas para llamadas BDNS, parsing y retries Python |

Separar revalidación recurrente y backfill histórico reduce el riesgo: la primera puede ser un job programado pequeño; el segundo debe ser manual, observable y limitado por ventanas.

## 8. Pooling y serverless

El `Pool` actual usa `max: 5` y una instancia por proceso. En serverless pueden existir varios procesos simultáneos, por lo que el máximo efectivo es `5 × número de instancias`.

Para Vercel + Neon:

- Usar URL pooled para el web role.
- Mantener el pool pequeño, inicialmente `max=3–5` según pruebas.
- Usar URL directa para migraciones y, si el proveedor lo recomienda, para el runner persistente.
- Medir conexiones antes de subir tráfico.

No se debe añadir PgBouncer propio, Redis ni una capa de proxy autogestionada en esta fase.

## 9. Seguridad de red

- HTTPS/TLS obligatorio entre web/jobs y PostgreSQL.
- Endpoint público con TLS y roles separados es aceptable inicialmente.
- IP allowlist no debe ser requisito para Vercel serverless porque no ofrece una IP de salida fija estándar adecuada para este caso.
- Si el proveedor ofrece private networking para el runner, usarlo para el job de escritura; no convertirlo en dependencia de la web.
- No almacenar DATABASE URLs en `NEXT_PUBLIC_*`.
- No registrar URLs de conexión, contraseñas, headers ni payloads.

## 10. Migraciones

Proceso recomendado:

1. Crear snapshot/backup verificable.
2. Ejecutar `alembic upgrade head` desde un job operador con URL directa y rol de migración.
3. Ejecutar checks de schemas, constraints e índices.
4. Desplegar web compatible con ese schema.
5. Ejecutar smoke tests de lectura.

Nunca ejecutar migraciones en cada request ni implícitamente durante el arranque de cada instancia web.

## 11. Dominio y TLS

Dominio previsto: `oportexa.com`, adquirido en Piensa Solutions.

Canonical preferido: `https://oportexa.com`.
`https://www.oportexa.com` debe redirigir a la raíz canónica.

Los registros DNS concretos dependen del proveedor elegido y no se deben inventar ni aplicar todavía. Vercel y proveedores equivalentes gestionan certificados TLS; no se debe comprar un certificado separado.

## 12. Datos de producción

Recomendación: estrategia híbrida controlada.

- Crear producción con migraciones Alembic desde cero.
- Transferir el dataset validado con `pg_dump`/`pg_restore` si el tiempo y la procedencia del dataset se aceptan.
- Conservar la historia OPS solo si se documenta que son observaciones de desarrollo, no runs de producción.
- Como alternativa reproducible, cargar esquema vacío y ejecutar una campaña controlada desde BDNS; es más lenta y más expuesta a cambios de fuente.
- No mezclar credenciales ni secretos de desarrollo.
- No generar ni versionar dumps en esta auditoría.

Antes de escoger A o B se debe comprobar que la cobertura local y su provenance son aptas para ser la base pública. La opción híbrida es la más razonable: migración reproducible, seed de datos validado y después revalidación incremental en producción.

## 13. Backups y recuperación

Protección mínima:

- Backups gestionados del proveedor: diarios, retención inicial de 7 días cuando esté disponible.
- `pg_dump` comprimido semanal, cifrado y almacenado fuera del proveedor principal.
- Un dump mensual retenido 3–6 meses.
- Restore de prueba trimestral en una base aislada.
- Secretos de backup en secret manager, nunca en logs ni Git.
- Registrar fecha, tamaño, hash y resultado de cada backup.

Un backup no se considera válido hasta comprobar que puede restaurarse y que `raw`, `core`, `ops`, constraints y conteos básicos existen.

## 14. Observabilidad mínima

- Logs de deploy y build del proveedor web.
- Errores de aplicación y latencia básica.
- Logs compactos de jobs: ventana, página, fetched, succeeded, failed, duración.
- `ops.ingestion_runs` e `ops.ingestion_failures` para detalle operacional.
- Health de DB, conexiones y almacenamiento.
- Resultado de backups y restores.

No se justifica Sentry, Datadog, Kafka, OpenTelemetry gestionado ni un dashboard propio antes de tener tráfico y fallos reales.

## 15. Legal, privacidad y analítica

No hay usuarios, cookies de terceros, ads ni analytics en runtime. Por ello no se necesita todavía CMP ni script de tracking.

Antes de producción habrá que publicar, fuera de esta auditoría, páginas de aviso legal, privacidad y condiciones aplicables. Si más adelante se incorporan analytics, ads o afiliación, habrá que revisar consentimiento, CSP, `ads.txt`, política de cookies y ubicaciones de scripts.

## 16. Escalado

### 0–1.000 visitas/mes, <50k convocatorias

El cuello de botella probable es el coste/limitación del proveedor y no PostgreSQL. Un web runtime pequeño y una base de 1–2 GB son suficientes. Mantener consultas CORE y no añadir FTS prematuramente.

### 10k–50k visitas/mes, 100k convocatorias

El primer cuello de botella será la latencia/concurrencia de consultas dinámicas y las conexiones serverless. Medir queries, activar pooling, cachear páginas seguras y revisar índices antes de añadir un motor de búsqueda.

### 100k+ visitas/mes, 600k convocatorias

Los cuellos de botella probables serán conexiones web, consultas de catálogo/taxonomía, tamaño RAW/backups y duración de revalidación. Escalar PostgreSQL y el runner, separar lecturas si hace falta y evaluar réplicas o FTS solo con métricas.

No se recomienda migrar a Kubernetes, colas distribuidas, Redis o multi-region por adelantado.

## 16.1 Arquitectura A — minimum cost

- Web: Vercel Hobby, `$0/mes` según precios actuales, sujeto a la condición de uso personal/no comercial.
- DB: Neon Free, `$0/mes`, con 0,5 GB y 100 CU-horas por proyecto.
- Jobs: GitHub Actions para revalidaciones cortas y backfill manual desde un entorno seguro.
- Backups: capacidades gratuitas del proveedor más `pg_dump` portable; almacenamiento externo NEEDS LIVE VERIFICATION.
- Coste estimado: `$0–5/mes` más dominio/IVA, **estimación**.
- Mantenimiento: bajo en web, alto riesgo de límites y pausa en DB/jobs.
- Uso: preproducción o etapa personal, no primera recomendación para un producto público monetizable.

## 16.2 Arquitectura B — balanced

- Web: Vercel Pro, `$20/mes`.
- DB: Neon Launch, coste típico indicado por Neon de `$15/mes`, usage-based.
- Jobs: Railway Hobby, `$5/mes` más consumo; configurar hard limit y alertas.
- Backups: backup gestionado de Neon más dump externo; coste externo NEEDS LIVE VERIFICATION.
- Coste estimado: aproximadamente `$40–45/mes` antes de IVA/consumo adicional, **estimación**.
- Mantenimiento: bajo-medio.
- Escalabilidad: suficiente para el dataset actual y crecimiento inicial; componentes separables.
- Uso: recomendada para producción pequeña sin revenue, una vez aceptado un coste operativo mínimo.

## 16.3 Arquitectura C — simple VPS

- Un VPS con Node.js, PostgreSQL 16, Python, systemd/cron y reverse proxy TLS.
- Backups cifrados a almacenamiento externo.
- Coste del VPS: NEEDS LIVE VERIFICATION según proveedor, región, disco y backup.
- Coste total orientativo: `$10–30/mes` antes de IVA, **estimación no verificada**.
- Mantenimiento: alto; requiere patching, firewall, monitorización, restore y renovación TLS.
- Escalabilidad: vertical sencilla hasta que DB/web/jobs compitan por recursos.
- Uso: opción si el operador acepta administrar Linux y prioriza evitar lock-in.

## 16.4 Comparación de costes

| Arquitectura | Coste mensual estimado | Mantenimiento | Persistencia | Escalabilidad | Decisión |
| --- | ---: | --- | --- | --- | --- |
| A — minimum cost | `$0–5` + dominio, estimación | Bajo-medio | Limitada por Free | Limitada | Solo preproducción/validación |
| B — balanced | `$40–45` + IVA/consumo, estimación | Bajo-medio | Buena con backups | Buena para V0.x–V1 | Recomendada |
| C — VPS | `$10–30` + backups, no verificado | Alto | Buena si se opera bien | Vertical | Alternativa de control |

Las cifras no incluyen el dominio ya adquirido, IVA, egress extraordinario, restore, soporte de pago ni trabajo humano. No deben usarse como presupuesto definitivo.

## 17. Fuentes y fecha de precios

Los precios cambian. Las cifras de esta auditoría son snapshot informativo del 2026-08-20 y deben verificarse de nuevo al provisionar. Fuentes oficiales consultadas:

- [Vercel pricing](https://vercel.com/pricing) y [límites](https://vercel.com/docs/limits).
- [Vercel Cron pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing) y [duración/concurrencia](https://vercel.com/docs/cron-jobs/manage-cron-jobs).
- [Neon pricing](https://neon.com/pricing).
- [Supabase pricing](https://supabase.com/pricing).
- [Railway pricing plans](https://docs.railway.com/pricing/plans).
- [Render pricing](https://render.com/pricing).
- [Aiven PostgreSQL pricing](https://aiven.io/pricing/postgresql).
