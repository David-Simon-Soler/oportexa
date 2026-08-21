# Oportexa — brand assets

Especificación interna de los assets secundarios de la identidad pública de Oportexa.

## Isotipo OX GEO

`apps/web/public/logo-mark.svg` es la representación vectorial del isotipo aprobado OX GEO:

- O geométrica carbón, con abertura inferior sutil.
- X geométrica bosque, integrada en el mismo volumen visual.
- Sin gradients, filtros ni dependencias externas.
- Fondo transparente para uso sobre superficies claras.

El wordmark `Oportexa` continúa siendo texto HTML/CSS para conservar accesibilidad y flexibilidad responsive.

## Paleta

| Token | Valor | Uso |
| --- | --- | --- |
| Carbón | `#0F1412` | O, texto principal y contraste |
| Bosque | `#1F5D46` | X, acentos y acciones |
| Marfil | `#F6F6F3` | Fondo de marca y superficies de iconos |

## Favicon e iconos

- `apps/web/src/app/favicon.ico`: favicon navegador, solo isotipo.
- `apps/web/public/icons/icon-192.png`: icono de aplicación sobre fondo marfil.
- `apps/web/public/icons/icon-512.png`: icono de aplicación sobre fondo marfil.
- `apps/web/public/apple-icon.png`: icono Apple Touch coherente con los anteriores.

No se añade variante maskable: no es necesaria para esta fase y no se marca un icono normal como maskable.

## Manifest y metadata social

`apps/web/src/app/manifest.ts` publica el manifest básico de Oportexa sin service worker ni install prompt.

`apps/web/public/opengraph-image.png` es una tarjeta 1200×630 reutilizada por Open Graph y Twitter (`summary_large_image`). La versión SVG fuente se conserva como `opengraph-image.svg` para futuras ediciones controladas.

## Accesibilidad

El isotipo del header es decorativo (`alt=""`, `aria-hidden="true"`). El enlace de inicio tiene el nombre accesible `Oportexa — Inicio`.

## URL

La metadata usa `SITE_URL`. En producción debe ser `https://www.oportexa.com`; en desarrollo se conserva el fallback `http://localhost:3000`.

## Instrucciones futuras

No crear variantes adicionales, animaciones, logos alternativos ni tarjetas sociales dinámicas sin una decisión explícita de identidad. Cualquier nuevo asset debe respetar la paleta, la geometría OX GEO y el criterio de legibilidad en tamaños pequeños.
