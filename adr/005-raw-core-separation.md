# ADR 005: Separación RAW / CORE

- Status: Accepted
- Context: El proyecto necesita conservar fielmente la respuesta BDNS para trazabilidad y reprocesamiento, sin convertirla en el modelo de producto.
- Decision: Persistir el payload y su provenance en `raw.bdns_grant_calls`, y mantener un modelo normalizado independiente en el esquema `core`, enlazado por `raw_id`.
- Consequences: Se facilita auditoría, detección de cambios y reprocesamiento. El ETL debe mantener hashes, upserts, relaciones idempotentes y una frontera clara entre datos oficiales y normalizados.
