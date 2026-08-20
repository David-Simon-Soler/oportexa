# Web Discovery

Aplicación Next.js de la primera superficie pública de Oportexa. En V0.3 usa App Router, TypeScript estricto, Server Components y una DAL server-only basada en `pg`.

## Desarrollo local

1. Arranca PostgreSQL desde la raíz: `docker compose up -d postgres`.
2. Revisa `apps/web/.env.example` y crea `.env.local` con valores locales.
3. Ejecuta `npm run dev` desde este directorio.

La web consulta exclusivamente `core` y no expone una API interna ni acceso directo a PostgreSQL desde el navegador. En producción se deberá provisionar un rol de lectura web separado, con permisos mínimos y credenciales server-only.

Comandos: `npm run lint`, `npm run test` y `npm run build`.
