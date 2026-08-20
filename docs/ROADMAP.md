# Roadmap

## V0.1 — Data Core — COMPLETE

PostgreSQL local aislado, migraciones Alembic, ingestión persistente incremental, RAW/CORE, provenance, idempotencia real, tests de integración, inspección, consultas analíticas y quality report inicial completados. El dataset de validación se limita a 50 convocatorias recientes; no incluye backfill histórico.

## V0.2 — Discovery — COMPLETE

Base web Next.js con lectura server-side de PostgreSQL, catálogo, detalle, regiones, metadata y sitemap completada. Incluye lint, tests unitarios, integración PostgreSQL y build. Limitación: no existe validación visual automatizada porque `agent-browser` no está disponible en el entorno; se mantiene validación estructural y CSS responsive.

## V0.2.5 — Recent Data Foundation — COMPLETE

Motor de backfill staged con streaming, checkpoints, resume, idempotencia, advisory locks, failure tracking, retries, SIGINT seguro y `--max-records`. Se validaron migraciones desde cero, campañas limitadas de 2026, cobertura exacta por códigos BDNS, freshness OPS, calidad RAW/CORE y regresión web. El dataset local queda en 6.273 convocatorias, pero la cobertura 2026 sigue parcial salvo agosto; no equivale a cobertura nacional completa.

## V0.3 — Product Discovery — COMPLETE

Experiencia pública de búsqueda, filtros, resultados, fichas, taxonomías, estados, accesibilidad y navegación SEO-first completada. La dirección visual, el UX polish y la documentación de diseño están cerrados. No incluye usuarios, auth, alertas, IA, pagos, publicidad ni API pública.

## V1 — Personalization

Cuenta, perfil, favoritos, matching y alertas.

## V2 — Intelligence

Histórico, estadísticas, visualizaciones y análisis.

## V3 — Expansion

Licitaciones públicas y otras oportunidades.

## V4 — Platform

API, Business e integraciones.

No se asignan fechas artificiales en esta etapa.
