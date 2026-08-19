# Opportunity Intel

Opportunity Intel es el nombre provisional de una futura plataforma gratuita para descubrir, entender y analizar oportunidades públicas en España. El proyecto comienza con convocatorias de ayudas y subvenciones publicadas en la BDNS/SNPSAP (Base de Datos Nacional de Subvenciones / Sistema Nacional de Publicidad de Subvenciones y Ayudas Públicas).

## Problema y propuesta

La información pública de oportunidades está dispersa, tiene lenguaje técnico y cambia con el tiempo. La plataforma pretende convertir fuentes oficiales en información más descubrible, comprensible y trazable, sin presentarse como asesoría jurídica, fiscal ni administrativa.

## Arquitectura prevista

Un servicio Python ingerirá datos oficiales, conservará la respuesta RAW y su procedencia, validará y normalizará los registros en una capa propia sobre PostgreSQL. Una aplicación web futura en Next.js + TypeScript consultará esa capa local. Las consultas de usuarios no dependerán directamente de la API de BDNS.

## Estado actual

V0.1 Data Core está completado: cliente BDNS, modelos RAW, PostgreSQL/Alembic, transformación RAW → CORE, ETL incremental, validación y 50 convocatorias de comprobación. V0.2 Discovery está en progreso con una base Next.js server-side, catálogo, fichas, regiones y SEO técnico inicial. No hay usuarios, autenticación, IA, matching, pagos, email ni despliegue.

## Organización

- `apps/web/`: aplicación Next.js de Discovery; consulta sólo `core` mediante DAL server-only.
- `services/ingestion/`: espacio reservado para pipelines Python.
- `packages/database/`: contrato y futura capa de acceso/migraciones de datos.
- `docs/`: documentación de producto, arquitectura y operación.
- `adr/`: decisiones arquitectónicas registradas.

## Principios clave

1. La fuente oficial y su procedencia deben ser visibles y trazables.
2. La plataforma mantiene una capa de datos propia; no se consulta BDNS en tiempo real desde cada usuario.
3. Nunca se presenta un dato derivado como información oficial.
4. Minimización: si no necesitamos un dato sensible, no lo almacenamos.
5. La información pública básica seguirá siendo accesible; lo premium será la automatización, personalización e inteligencia.
6. La calidad, auditabilidad y utilidad preceden a la escala.

## Roadmap resumido

V0.1 Data Core → V0.2 Discovery → V1 Personalization → V2 Intelligence → V3 Expansion → V4 Platform. El detalle está en [`docs/ROADMAP.md`](docs/ROADMAP.md).

El nombre “Opportunity Intel” es provisional y se revisará antes del lanzamiento público.
