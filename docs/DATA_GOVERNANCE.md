# Gobernanza del dato

La fuente de verdad del contenido oficial será la fuente primaria identificada, no una inferencia local. Cada registro deberá conservar provenance (origen), lineage (transformaciones), identificador de fuente y timestamps de registro, actualización e ingestión.

## Implementación RAW / CORE

La capa RAW (`raw.bdns_grant_calls`) conserva el payload JSONB de BDNS, endpoint, código BDNS, hash SHA-256 determinista, `source_retrieved_at`, `first_seen_at`, `last_seen_at` y timestamps internos. No se crea una versión histórica por cada lectura idéntica: si el hash no cambia, se actualiza principalmente `last_seen_at`.

La capa CORE (`core.*`) contiene el modelo normalizado y enlaza cada convocatoria con su RAW mediante `core.grant_calls.raw_id`. Las entidades de catálogo y relaciones se crean mediante upsert y constraints únicos; el ETL sincroniza las relaciones N:M sin duplicarlas.

El provenance mínimo consultable es: código BDNS, endpoint de fuente, momento de recuperación y referencia al registro RAW. La transformación RAW → CORE solo usa campos verificados de la respuesta y no debe interpretarse como fuente oficial independiente.

Las actualizaciones serán idempotentes, trazables y preferentemente incrementales. La deduplicación combinará identificadores oficiales con reglas documentadas; nunca se eliminará silenciosamente una discrepancia. La validación cubrirá esquema, tipos, rangos, fechas, enlaces y consistencia entre campos.

Clasificación:

- **Datos oficiales:** copiados o referenciados desde la fuente.
- **Datos normalizados:** estandarizados por el sistema.
- **Datos derivados:** calculados, clasificados o resumidos internamente.

> Nunca presentar un dato derivado como si fuera información oficial.

Las correcciones deberán conservar el valor anterior y el motivo, actor y timestamp de la corrección. La calidad se medirá con completitud, validez, frescura, unicidad, consistencia y trazabilidad. La auditoría registrará ejecuciones, versiones de esquema, conteos, errores y cambios relevantes sin almacenar secretos.

Cada convocatoria se procesa en una transacción propia: si falla su transformación o persistencia, se registra el código BDNS y el lote continúa con las demás. La idempotencia se basa en el código BDNS único, hash RAW, claves únicas de catálogos y claves primarias compuestas de relaciones.

Las ejecuciones de backfill se registran separadamente en `ops.ingestion_runs`: una fila representa una ventana temporal y su estado operativo. Esta tabla no es fuente de verdad de convocatorias y no sustituye la procedencia conservada en RAW/CORE.

## Control inicial del dataset local

En la ampliación controlada del 2026-08-19 se persistieron 530 convocatorias: 530 códigos RAW únicos y 530 códigos CORE únicos, sin duplicados ni referencias huérfanas. El lote presentó 32,45% de convocatorias sin fecha de inicio, 29,25% sin fecha de fin y 98 convocatorias con múltiples sectores; no presentó presupuestos, organismos, regiones, sectores o beneficiarios ausentes. Estas cifras describen únicamente el dataset local parcial, no el universo completo de BDNS.
