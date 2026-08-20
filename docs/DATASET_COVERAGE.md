# Cobertura del dataset

Estado: **LOCAL PARTIAL DATASET**.

Este informe describe el estado de desarrollo tras la campaña staged de julio–agosto de 2026. No representa cobertura nacional completa de BDNS.

## Qué tenemos

- 6.273 convocatorias RAW y CORE.
- 6.273 códigos BDNS únicos.
- 1.146 organizations.
- 255 sectors.
- 99 regions.
- 4 beneficiary types.
- 11 funds.
- Presupuesto conocido en el 100% del CORE actual.
- 350 convocatorias abiertas, 5,58% del CORE.

## Cobertura temporal

El dataset combina la carga inicial, pruebas históricas y bloques recientes. La densidad local por mes muestra especialmente:

- 2026-01: 1.220.
- 2026-07: 342.
- 2026-08: 177.
- 2025-01: 489.
- 2025-12: 219.

El preflight de listados BDNS anunció aproximadamente 45.036 convocatorias para enero–agosto de 2026 y 70.213 para 2025. Esos totales no son filas CORE y muestran que falta cobertura significativa.

## Cobertura exacta 2026 por códigos listados

La siguiente tabla compara códigos obtenidos del listado BDNS para el rango con códigos CORE locales. La fecha es la semántica del filtro de listado BDNS utilizado por la API; no debe interpretarse automáticamente como fecha de inicio de solicitud.

| Mes | BDNS anunciadas | CORE matching | Cobertura | Estado |
|---|---:|---:|---:|---|
| 2026-01 | 4.971 | 0 | 0,00% | PARTIAL |
| 2026-02 | 5.705 | 0 | 0,00% | PARTIAL |
| 2026-03 | 6.033 | 0 | 0,00% | PARTIAL |
| 2026-04 | 6.311 | 0 | 0,00% | PARTIAL |
| 2026-05 | 6.217 | 0 | 0,00% | PARTIAL |
| 2026-06 | 6.783 | 0 | 0,00% | PARTIAL |
| 2026-07 | 6.541 | 2.408 | 36,81% | PARTIAL |
| 2026-08 | 2.475 | 2.475 | 100,00% | COMPLETE |

`COMPLETE` sólo se asigna cuando todos los códigos listados fueron comparados y están en CORE. Los ceros de enero–junio son ceros de matching bajo este filtro de listado, no una afirmación de que CORE no contenga convocatorias con fechas de aplicación en esos meses.

## Freshness

- Agosto 2026: ventanas del 1–21 de agosto `completed`, última confirmación el 19 de agosto de 2026.
- Julio 2026, 1–7: `completed`, última confirmación el 19 de agosto de 2026.
- Julio 2026, 8–14: `interrupted` por `--max-records=1000`, última confirmación el 20 de agosto de 2026, reanudable.
- Enero–junio 2026: no revalidados por campaña de detalles en esta sesión.

La freshness se obtiene de `ops.ingestion_runs.completed_at` y `last_page`; no representa una fecha oficial de modificación BDNS.

## Cobertura territorial y sectorial

Las regiones y sectores están representados, pero de forma desigual. Las mayores concentraciones CORE son Cataluña (309), Valencia (308), Barcelona (261), Toledo (190) y Galicia (159). Los sectores principales son actividades artísticas/deportivas/entretenimiento (864), otros servicios (662), actividades sanitarias y sociales (572) y educación (472).

## Oportunidades abiertas

Hay 350 convocatorias abiertas. Por beneficiario, predominan personas jurídicas que no desarrollan actividad económica (294 abiertas), personas físicas no económicas (29), pymes/personas físicas económicas (27) y gran empresa (10).

No se observaron convocatorias abiertas que cierren en los próximos 7, 14 o 30 días con fecha final conocida en la fecha de consulta.

## Qué falta

- Cobertura completa de enero–julio de 2026 y revalidación reciente.
- Cobertura completa de 2025, 2024 y años anteriores.
- Freshness medible por stage.
- Revalidación programada.
- Densidad suficiente y estable para todas las combinaciones SEO.
- Validación de representatividad territorial fuera de este dataset parcial.

## Launch data gate

`LAUNCH-DATA-READY: NOT READY`.

Para alcanzarlo se requieren cobertura reciente completa, revalidación repetible, cero duplicados y huérfanos, error rate aceptable, freshness conocida y un inventario abierto suficiente por regiones y sectores relevantes. Este documento no autoriza publicar ni desplegar.
