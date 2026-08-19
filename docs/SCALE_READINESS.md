# Scale-readiness: medición local

Medición realizada sobre PostgreSQL 16.15, con 530 convocatorias CORE y 530 RAW. Son observaciones de desarrollo, no compromisos de capacidad.

## Benchmark ETL observado

La ejecución principal de 450 elementos (`2026-01-01`–`2026-08-19`, páginas de listado de 100, pausa de 0,15 s) tardó `181,947 ms`: `Fetched 450`, `New 237`, `Unchanged 190`, `Failed 23`. Hubo aproximadamente 5 llamadas de listado y unas 476 respuestas de detalle 2xx, además de reintentos/errores; el orden de magnitud es unas 480–500 peticiones HTTP. El throughput observado fue aproximadamente 2,47 elementos procesados por segundo.

Los 23 fallos se reprodujeron en códigos BDNS concretos y se debieron a un bug real del repositorio: el upsert genérico enviaba `code` al catálogo `Fund`, cuya tabla no tiene esa columna. Se corrigió el repositorio, se añadió test de integración y se reintentaron los 22 códigos únicos con éxito.

Otra ejecución de control de 200 elementos tardó `46,154 ms` (`196` sin cambios, `4` fallos de la primera versión); la ventana histórica de 80 elementos tardó `17,611 ms` y creó `80` registros. La primera tentativa sólo recorrió listados con tamaño 5 y no persistió datos; se descartó como benchmark de carga.

## Coste operacional aproximado

La siguiente extrapolación lineal usa el throughput anterior, una llamada de detalle por convocatoria y una pequeña sobrecarga de listado. No incluye cambios de rate limit, reintentos, errores, mantenimiento, paralelización ni variación de densidad. Por ello no debe interpretarse como una promesa.

| Convocatorias | Detalles aproximados | Tiempo lineal orientativo | Peticiones aproximadas |
| ---: | ---: | ---: | ---: |
| 1.000 | 1.000 | 6,8 min | 1.010 |
| 10.000 | 10.000 | 1,1 h | 10.100 |
| 100.000 | 100.000 | 11,3 h | 101.000 |
| 600.000 | 600.000 | 67,5 h | 606.000 |

Cuellos de botella observados: red y detalle BDNS, pausa/rate limiting y una transacción PostgreSQL por convocatoria. La memoria del proceso actual es baja para lotes moderados, pero el listado completo de una ventana se acumula antes de resolver detalles; para cientos de miles se debe procesar por página y checkpoint. El logging actual, una línea por request y convocatoria, sería demasiado voluminoso para una campaña grande.

## Almacenamiento medido

| Objeto | Tamaño actual |
| --- | ---: |
| `raw.bdns_grant_calls` | 1.957.888 bytes |
| `core.grant_calls` | 598.016 bytes |
| schema `raw` | 1.957.888 bytes |
| schema `core` | aproximadamente 1,39 MB sumando tablas e índices observados |
| schema `ops` | 32 KB |
| base de datos completa | 11.656.215 bytes |

La media lineal de la relación RAW es aproximadamente 3,7 KB por convocatoria y la de `core.grant_calls` aproximadamente 1,1 KB. Tomando sólo como ejercicio la base completa actual, las extrapolaciones simples serían aproximadamente 220 MB para 10k, 2,2 GB para 100k y 13,2 GB para 600k. El tamaño real puede variar por payload, TOAST, índices, catálogos, asociaciones y sobre todo por el contenido histórico; son extrapolaciones lineales simplificadas.

## Decisiones de preparación

- Se mantiene `bdns_code` único y hash RAW para idempotencia.
- RAW y CORE se escriben en una transacción independiente por convocatoria.
- Se añadió `ops.ingestion_runs` mediante Alembic para separar estado de carga y datos de producto.
- La siguiente evolución debe procesar una ventana/página por vez y actualizar `last_page` y contadores de `ops.ingestion_runs`; todavía no se activa una campaña histórica completa.
- No se optimizan índices ni se añade un motor externo sin evidencia de volumen y consultas reales.

## Motor de backfill controlado

El motor posterior al checkpoint usa ventanas inclusivas, streaming página-a-página, `page_size=100`, transacción por convocatoria, checkpoints OPS y advisory locks. Una prueba diaria de dos ventanas de baja densidad procesó 3 detalles en 1,107 segundos y aproximadamente 5 peticiones, con 3 nuevos.

También se probó una ventana mensual de diciembre de 2025 cuyo listado anunciaba 7.338 elementos. El proceso alcanzó 1.298 detalles confirmados y `last_page=12` antes de ser detenido para respetar el límite de esta sesión; el run quedó `interrupted` y sin fallos pendientes tras reintentar los fallos de interrupción. El dataset final alcanzó 1.811 convocatorias, por encima del objetivo aproximado de 1.500 debido a que el proceso inicialmente no propagaba correctamente `SIGINT` desde el manejo de fallos individuales. Ese bug se corrigió y no se lanzarán más cargas reales en esta sesión.

Tras la prueba, las medidas finales fueron: RAW/CORE 1.811, `core.grant_calls` 1.646.592 bytes, `raw.bdns_grant_calls` 6.537.216 bytes y base completa 18.390.039 bytes. Las extrapolaciones anteriores siguen basadas en la medición controlada de 530 registros y no deben recalcularse linealmente a partir de esta ejecución parcial, que tiene una distribución temporal sesgada.

## Prueba SIGINT y resume posterior al checkpoint

El checkpoint del motor quedó registrado en `ab14a93` (`feat: add resumable historical backfill engine`). La prueba limpia de interrupción utilizó `2025-12-20`, `daily`, `page_size=1`: se confirmaron las páginas 0–3, se recibió SIGINT durante el procesamiento posterior y el run 6 quedó `interrupted` con `fetched=4`, `succeeded=4`, `failed=0`, `last_page=3`. La reanudación arrancó en la página 4, confirmó un detalle y terminó la ventana con cinco registros, sin duplicados.

Durante una tentativa anterior, SIGINT llegó dentro de un rollback de PostgreSQL y produjo un fallo operacional transitorio. El manejo se corrigió después del checkpoint para diferir SIGINT hasta un punto seguro; la regresión y la prueba real posterior no generaron ese fallo. El run 4 conserva la auditoría de la tentativa, pero terminó con cero fallos activos tras retry.

El dataset de desarrollo queda en 1.840 RAW/CORE, no se realizarán más cargas reales en esta sesión. Mediciones actuales aproximadas: schema RAW 6,48 MB, schema CORE 3,08 MB, schema OPS 160 KB y base completa 18 MB. Son tamaños locales con índices y catálogos, no una garantía de almacenamiento histórico.
