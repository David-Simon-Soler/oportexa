# Modelo de datos V0.1

La migración `20260819_0001` crea dos namespaces PostgreSQL: `raw` y `core`.

## RAW

`raw.bdns_grant_calls` contiene `id`, `bdns_code`, `payload` JSONB, `payload_hash`, `source_endpoint`, `source_retrieved_at`, `first_seen_at`, `last_seen_at`, `created_at` y `updated_at`. `bdns_code` es texto, único e indexado. El hash usa JSON canónico ordenado y SHA-256.

## CORE

Entidades: `core.grant_calls`, `core.organizations`, `core.sectors`, `core.regions`, `core.beneficiary_types` y `core.funds`.

`core.grant_calls` contempla ID interno bigint identity, código BDNS único, referencia `raw_id`, título/descripción, tipo, presupuesto `NUMERIC(20,2)`, `is_open`, fechas de solicitudes `DATE`, finalidad, bases reguladoras, URL de bases, sede electrónica, fecha de recepción, primera/última observación y timestamps internos.

`organization` conserva los niveles `level1`, `level2` y `level3` entregados por la API, sin inventar una taxonomía. Los catálogos tienen `source_key`, código cuando existe y descripción. En regiones se conserva la descripción oficial y se extrae el prefijo visible como código solo cuando sigue el patrón observado `CODIGO - descripción`.

Relaciones N:M: `grant_call_organizations`, `grant_call_sectors`, `grant_call_regions`, `grant_call_beneficiary_types` y `grant_call_funds`. Sus claves primarias compuestas evitan duplicados.

Los importes usan decimal, las fechas de fuente usan `DATE` y los tiempos internos usan timestamps con zona horaria. El código BDNS permanece como texto para no imponer supuestos sobre su formato futuro.
