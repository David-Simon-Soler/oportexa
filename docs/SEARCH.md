# Búsqueda PostgreSQL V1

## Medición actual

Con 508 convocatorias, el listado ordenado tarda aproximadamente `0,7 ms` en `EXPLAIN ANALYZE`; el filtro de texto con tres `ILIKE` tarda aproximadamente `2,0 ms`. Los filtros por región, sector y beneficiario se sitúan aproximadamente entre `0,15` y `0,22 ms`, y `is_open` usa su índice con aproximadamente `0,04 ms`. Las consultas hacen `Seq Scan` sobre tablas pequeñas y las relaciones usan joins/hash o índices de clave primaria. Estos tiempos no predicen producción.

Las mediciones se realizaron con `EXPLAIN (ANALYZE, BUFFERS)` sobre la base local. No justifican microoptimización con este volumen.

## Alternativas nativas

### Full-text search

Un campo `tsvector` generado desde `title`, `description`, `purpose_description` y una representación controlada de organización/taxonomías permitiría buscar con `websearch_to_tsquery('spanish', ...)` y un índice GIN. Es apropiado para relevancia lingüística y prefijar pesos: título y finalidad por encima de descripción.

### Normalización

`unaccent` puede reducir diferencias entre `educacion` y `educación`, pero debe instalarse/documentarse como extensión y probarse con español. No conviene ocultar el texto oficial; la normalización debe vivir en una columna auxiliar de búsqueda.

### Fuzzy y parcial

`pg_trgm` con índices GIN/GiST es útil para errores tipográficos, nombres administrativos y coincidencias parciales. Tiene coste de almacenamiento y debe evaluarse con datos reales antes de activar búsquedas difusas de forma general.

## Recomendación

Mantener PostgreSQL como motor mientras el catálogo esté en este orden de magnitud. La primera implementación V1 recomendada es una columna `search_vector` mantenida por migración/ETL, índice GIN y `websearch_to_tsquery('spanish', ...)`, con `unaccent` sólo si las pruebas de relevancia lo justifican. Añadir `pg_trgm` para organización y fallback parcial después de medir consultas reales.

En esta fase no se implementan FTS, extensiones ni nuevos índices: el volumen actual es pequeño, la evidencia sólo muestra `ILIKE` barato y todavía hay que fijar pesos, idioma, refresco y compatibilidad de despliegue. No se incorporan Elasticsearch, Meilisearch, Typesense ni Algolia.
