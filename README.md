# Oportexa

Oportexa es una plataforma gratuita para descubrir, entender y verificar oportunidades públicas en España. El proyecto comienza con convocatorias de ayudas y subvenciones publicadas en la BDNS/SNPSAP (Base de Datos Nacional de Subvenciones / Sistema Nacional de Publicidad de Subvenciones y Ayudas Públicas). El dominio previsto es `oportexa.com`.

## Problema y propuesta

La información pública de oportunidades está dispersa, tiene lenguaje técnico y cambia con el tiempo. La plataforma pretende convertir fuentes oficiales en información más descubrible, comprensible y trazable, sin presentarse como asesoría jurídica, fiscal ni administrativa.

## Arquitectura prevista

Un servicio Python ingerirá datos oficiales, conservará la respuesta RAW y su procedencia, validará y normalizará los registros en una capa propia sobre PostgreSQL. Una aplicación web futura en Next.js + TypeScript consultará esa capa local. Las consultas de usuarios no dependerán directamente de la API de BDNS.

## Estado actual

V0.1 Data Core, V0.2 Discovery, V0.2.5 Recent Data Foundation y V0.3 Product Discovery están completados. V0.4 Data Launch Readiness está preparado con limitaciones documentadas de cobertura. No hay usuarios, autenticación, IA, matching, pagos, email ni despliegue.

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

V0.1 Data Core → V0.2 Discovery → V0.2.5 Recent Data Foundation → V0.3 Product Discovery → V0.4 Data Launch Readiness → V1 Personalization → V2 Intelligence → V3 Expansion → V4 Platform. El detalle está en [`docs/ROADMAP.md`](docs/ROADMAP.md).

El nombre público actual es “Oportexa” y el dominio principal de producción es `https://www.oportexa.com`; `https://oportexa.com` redirige al host principal. El identificador técnico del repositorio continúa siendo `opportunity-intel` por trazabilidad y compatibilidad local.
