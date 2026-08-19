# ADR 002: Capa de datos local

- Status: Accepted
- Context: Las consultas de usuarios necesitan rendimiento, consistencia, histórico y control de calidad.
- Decision: Ingerir y consultar una capa propia sobre PostgreSQL; no consultar BDNS en tiempo real desde el usuario.
- Consequences: Aumentan almacenamiento y operación, pero mejoran resiliencia, auditoría, normalización y evolución del producto.

