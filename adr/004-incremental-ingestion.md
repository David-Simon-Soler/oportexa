# ADR 004: Ingestión incremental

- Status: Accepted
- Context: La fuente puede crecer y cambiar; una carga completa frecuente sería costosa y menos operable. La guía oficial recomienda ventanas por fecha de registro, detalle por código BDNS y revalidaciones semanal, mensual y anual.
- Decision: Usar ingestión incremental por `fechaDesde`/`fechaHasta`, seguida de detalle por código BDNS, con revalidación periódica, idempotencia y auditoría.
- Consequences: Menor coste operativo y mejor frescura; la fecha de registro permanece estable cuando se edita una convocatoria, pero hay que gestionar correcciones, inserciones, modificaciones y eliminaciones. La inclusión exacta de los extremos de fecha queda pendiente de verificación.
