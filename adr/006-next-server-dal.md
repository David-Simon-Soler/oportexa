# ADR 006: Lectura web mediante Server Components y DAL directa

- Status: Accepted
- Context: Discovery necesita leer datos públicos sin exponer PostgreSQL ni introducir una API interna prematura.
- Decision: Next.js usará Server Components y una DAL server-only basada en `pg`, con consultas parametrizadas exclusivamente sobre `core`. No habrá `/api/grants` ni ORM TypeScript en V0.2.
- Consequences: Menor superficie de ataque y arquitectura simple. La conexión debe permanecer privada; si se requieren consumidores externos, se evaluará una API pública separada.
