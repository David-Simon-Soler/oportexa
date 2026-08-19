# Estrategia de backfill histórico

Este documento define una carga histórica reproducible para BDNS/SNPSAP. No autoriza un backfill completo en el entorno de desarrollo.

```mermaid
flowchart TD
  A[Ventana temporal] --> B[Consulta de listado]
  B --> C[Códigos BDNS]
  C --> D[Detalles]
  D --> E[RAW]
  E --> F[CORE]
  F --> G[Checkpoint ops.ingestion_runs]
  G --> H[Siguiente ventana]
```

## Ventanas y ritmo

La densidad debe medirse primero. Para periodos recientes conviene empezar por días o semanas; para periodos antiguos con menor densidad pueden usarse meses. Una ventana debe producir un lote manejable y repetible, no maximizar el número de páginas por ejecución.

Cada página de listado produce códigos BDNS y cada código se resuelve mediante su detalle. El cliente conserva una pausa configurable, respeta los límites documentados por la fuente, evita concurrencia agresiva y aplica retries con backoff sólo para timeouts, errores de red, `429` y errores `5xx`.

## Reanudación y checkpoints

Para cargas de cientos de miles la reanudación segura necesita estado persistente. La migración `20260819_0002_ingestion_runs` crea `ops.ingestion_runs` con ventana, estado, tiempos, contadores, última página y resumen de errores. La siguiente iteración del comando de backfill deberá crear una fila `running`, actualizar `last_page` y contadores por lote, y marcar `completed` o `failed` al finalizar. El estado operacional permanece separado de `core`.

La unidad de reanudación es una ventana más su página de listado. Si una ejecución se interrumpe, se retoma desde la última página confirmada; los códigos de esa página se pueden repetir sin duplicar datos.

## Idempotencia y fallos

`bdns_code` identifica la convocatoria y el hash del payload RAW distingue sin cambios de cambios reales. RAW y CORE se escriben en una transacción por convocatoria. Los códigos que fallen deben conservarse en el resumen o en una cola de retry posterior, sin marcar la ventana como completamente correcta.

Los fallos de detalle se clasifican por código y causa: fuente, respuesta inválida, timeout, límite o error de transformación. Las reintentos posteriores deben ser acotados y no bloquear ventanas independientes.

## Actualización continua

- Reciente: revalidación diaria de una ventana corta.
- Intermedio: revalidación semanal de ventanas recientes.
- Antiguo: revalidación mensual o anual según estabilidad y documentación oficial.

La semántica exacta de inclusión de fechas y cualquier endpoint adicional siguen sujetos a `TODO: verificar contra documentación oficial` antes de automatizar una campaña histórica completa.

## Coste operativo orientativo

La carga actual hace aproximadamente una llamada de listado por página y una llamada de detalle por código. Con el ritmo conservador observado, el cuello de botella es la red y el límite de llamadas, no la transformación local. Para 1.000, 10.000, 100.000 y 600.000 convocatorias, el número de detalles es del mismo orden y el tiempo crecerá aproximadamente de forma lineal si no se paraleliza; la paralelización no debe introducirse sin una política explícita de rate limiting. RAW JSONB, índices y relaciones crecerán además con el tamaño y la variabilidad de los payloads.
