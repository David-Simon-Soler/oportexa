# Fuentes de datos

## BDNS/SNPSAP

Es la fuente primaria inicial para convocatorias de ayudas y subvenciones públicas en España. El SNPSAP es la parte pública de la BDNS y ofrece una API REST pública en JSON.

**Fecha de verificación:** 2026-08-19.

### Referencias oficiales utilizadas

- [Swagger/API REST de SNPSAP](https://www.infosubvenciones.es/bdnstrans/doc/swagger)
- [Especificación OpenAPI oficial JSON](https://www.infosubvenciones.es/bdnstrans/estaticos/doc/snpsap-api.json)
- [Buenas prácticas para el uso de la API SNPSAP](https://www.infosubvenciones.es/bdnstrans/estaticos/ayuda/Buenas%20pr%C3%A1cticas%20API%20SNPSAP.pdf)
- [Ficha oficial de datos.gob.es](https://datos.gob.es/es/catalogo/e05250001-base-de-datos-nacional-de-subvenciones)
- [Aviso legal del SNPSAP](https://www.infosubvenciones.es/bdnstrans/GE/es/avisolegal)

### URL base confirmada

La especificación OpenAPI declara como servidor de producción principal:

```text
https://www.infosubvenciones.es/bdnstrans/api
```

También declara estos servidores alternativos, no necesarios para el cliente inicial:

```text
https://www.infosubvenciones.gob.es/bdnstrans/api
https://www.pap.hacienda.gob.es/bdnstrans/api
https://www.subvenciones.gob.es/bdnstrans/api
```

No se documenta autenticación para estos endpoints públicos; la guía oficial describe el acceso como público e irrestricto, sujeto a buenas prácticas y posibles medidas ante abuso.

### Endpoints confirmados para convocatorias

- `GET /convocatorias/busqueda`: búsqueda paginada de convocatorias con publicidad.
- `GET /convocatorias/ultimas`: últimas convocatorias.
- `GET /convocatorias`: detalle por `numConv` y, opcionalmente, `vpd`.
- `GET /convocatorias/documentos`: documento por `idDocumento`.
- `GET /convocatorias/zip`: documentos de una convocatoria por `id` y, opcionalmente, `vpd`.
- `GET /convocatorias/exportar`, `/ultimas/exportar` y `/pdf`: exportaciones/documentos; quedan fuera del cliente exploratorio inicial.

La URL de detalle confirmada usa `GET /convocatorias?numConv=...`; el código se denomina `numeroConvocatoria` en el resumen y `codigoBDNS` en el detalle.

### Parámetros confirmados

Para `/convocatorias/busqueda`: `page`, `pageSize`, `order`, `direccion`, `vpd`, `descripcion`, `descripcionTipoBusqueda`, `numeroConvocatoria`, `mrr`, `contribucion`, `fechaDesde`, `fechaHasta`, `tipoAdministracion`, `organos`, `regiones`, `tiposBeneficiario`, `instrumentos`, `finalidad` y `ayudaEstado`.

Para `/convocatorias/ultimas`: `page`, `pageSize`, `order`, `direccion` y `vpd`.

Para `/convocatorias`: `numConv` obligatorio y `vpd` opcional.

Los tipos y descripciones de estos parámetros constan en OpenAPI. La semántica detallada de algunos filtros, especialmente `descripcionTipoBusqueda`, formatos completos de arrays y valores permitidos de catálogos, queda **UNVERIFIED** hasta una prueba específica/documentación adicional.

### Paginación y límites

La respuesta paginada contiene `content`, `pageable`, `totalPages`, `totalElements`, `last`, `numberOfElements`, `first`, `size`, `number`, `empty` y `advertencia`. `page` comienza en 0 según OpenAPI y la guía oficial.

La guía oficial confirma un máximo de **10.000 registros por página/llamada** y recomienda utilizar paginación. También confirma un límite de **10 peticiones GET por IP y segundo**. No se usará ese máximo como ritmo operativo: el cliente exploratorio introduce una pausa configurable de 200 ms por defecto y no realiza llamadas concurrentes.

La respuesta real probada el 2026-08-19 con `pageSize=5` devolvió cinco elementos y `totalElements=10000` para `/convocatorias/ultimas`; este valor parece corresponder a la ventana de últimas convocatorias y queda documentado como comportamiento observado, no como regla general.

### Estructura y campos verificados

El resumen (`Convocatoria`) devuelve, entre otros campos confirmados: `id`, `mrr`, `numeroConvocatoria`, `descripcion`, `descripcionLeng`, `fechaRecepcion`, `nivel1`, `nivel2`, `nivel3` y `codigoInvente`.

El detalle (`ConvocatoriaDetalle`) puede devolver: `id`, `organo`, `sedeElectronica`, `codigoBDNS`, `fechaRecepcion`, `instrumentos`, `tipoConvocatoria`, `presupuestoTotal`, `mrr`, `descripcion`, `descripcionLeng`, `tiposBeneficiarios`, `sectores`, `regiones`, `descripcionFinalidad`, `descripcionBasesReguladoras`, `urlBasesReguladoras`, `sePublicaDiarioOficial`, `abierto`, `fechaInicioSolicitud`, `fechaFinSolicitud`, `textInicio`, `textFin`, `ayudaEstado`, `urlAyudaEstado`, `fondos`, `reglamento`, `objetivos`, `sectoresProductos`, `documentos`, `anuncios` y `advertencia`.

Los campos pueden ser nulos, arrays vacíos o no aparecer en respuestas reales. El modelo exploratorio tolera campos adicionales y conserva la estructura oficial sin convertirla todavía en el dominio interno.

### Fechas y actualización incremental

La API devuelve fechas ISO observadas como `YYYY-MM-DD` para `fechaRecepcion`, fechas de solicitud y metadatos de documentos. En cambio, OpenAPI exige para los filtros `fechaDesde` y `fechaHasta` el patrón `DD/MM/YYYY` (por ejemplo, `18/12/2017`). Una prueba con formato ISO devolvió HTTP 400; el ETL usa el formato documentado `DD/MM/YYYY`. El comportamiento exacto de inclusión de los extremos sigue **UNVERIFIED**.

La guía oficial recomienda:

1. Descargar diariamente las convocatorias registradas el día anterior usando `fechaDesde` y `fechaHasta`.
2. Recuperar el detalle por cada código BDNS obtenido.
3. Revalidar documentos de la última semana semanalmente.
4. Revalidar el último mes mensualmente y el último año anualmente.

La fecha de registro no cambia cuando una convocatoria se edita. La guía también advierte que los datos son dinámicos y pueden sufrir correcciones, inserciones, modificaciones y eliminaciones. El portal no ofrece un sistema de notificaciones de cambios; por tanto, la revalidación periódica es necesaria.

### Códigos HTTP y errores

OpenAPI documenta `200` y `400` para la búsqueda. El cliente trata `4xx` como errores no reintentables por defecto, salvo `429`; trata `429` y `5xx` como recuperables solo con pocos reintentos acotados y backoff.

Los códigos concretos y cuerpos de error para `401`, `403`, `404`, `408`, `429` y `5xx` no están descritos de forma suficiente en la especificación consultada: **UNVERIFIED**. El cliente los distingue por código sin registrar cuerpos completos.

### Catálogos auxiliares

La especificación OpenAPI declara tags/catálogos para regiones, finalidades, tipos de beneficiarios, instrumentos de ayuda, reglamentos UE, sectores de productos, actividades NACE, objetivos y órganos. Sus endpoints concretos y esquemas deberán verificarse antes de incorporarlos: **UNVERIFIED** para el cliente inicial.

### Observaciones y estrategia

Se conservarán el código BDNS, la respuesta RAW en memoria durante la exploración, la URL/endpoint, los parámetros, el timestamp de ingestión y la versión de la especificación utilizada cuando se implemente persistencia. No se guardan respuestas en esta fase.

Se respetarán el límite de 10 GET/s/IP, la pausa entre llamadas, la ausencia de concurrencia agresiva, los términos del aviso legal y la recomendación de probar consultas antes de programar cargas masivas. No se descargan documentos ni ZIP en el cliente exploratorio.

### Puntos todavía no verificados

- **UNVERIFIED:** inclusión exacta de los extremos de `fechaDesde` y `fechaHasta`.
- **UNVERIFIED:** valores cerrados y semántica completa de todos los filtros y catálogos.
- **UNVERIFIED:** comportamiento específico de cada endpoint ante 404, 429, 5xx, timeouts y JSON no válido.
- **UNVERIFIED:** si todos los servidores alternativos mantienen idéntica versión y disponibilidad.
- **UNVERIFIED:** política formal de versionado/avisos de cambios de OpenAPI.
