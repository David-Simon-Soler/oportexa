# Google Search Console: configuración de Oportexa

Este documento describe acciones manuales. No se accede a Google desde el repositorio ni se ejecutan cambios externos.

## 1. Crear la propiedad

1. Abrir Google Search Console con la cuenta propietaria del sitio.
2. Elegir **Añadir propiedad**.
3. Elegir **Dominio** y escribir `oportexa.com` sin protocolo ni ruta. Esta opción cubre `www`, la raíz y cualquier subdominio.
4. Copiar el registro TXT que Google proporcione.
5. Añadirlo en el proveedor DNS que gestiona actualmente la zona. No borrar registros existentes.
6. Esperar la propagación y pulsar **Verificar**. Si falla, comprobar que el TXT está en `oportexa.com`, no sólo en `www`.

## 2. Enviar el sitemap

En la propiedad verificada, abrir **Sitemaps**, introducir exactamente:

```text
https://www.oportexa.com/sitemap.xml
```

Comprobar que el estado sea procesado y que las URLs mostradas usan `https://www.oportexa.com`.

## 3. Inspección inicial

Usar **Inspección de URL** para estas URLs representativas:

- `https://www.oportexa.com/`
- `https://www.oportexa.com/subvenciones`
- `https://www.oportexa.com/subvenciones/region`
- una región con inventario real
- una ficha de subvención válida
- `https://www.oportexa.com/robots.txt`
- `https://www.oportexa.com/sitemap.xml`

Para cada página HTML, revisar URL canónica declarada, disponibilidad para Google, respuesta HTTP y ausencia de `noindex` accidental. No solicitar indexación de URLs con filtros, búsquedas o páginas vacías.

## 4. Checklist posterior

- [ ] La propiedad de dominio está verificada.
- [ ] El sitemap `www` está enviado y procesado.
- [ ] La inspección muestra canonical `www`.
- [ ] La raíz sin `www` redirige con 308 a `https://www.oportexa.com`.
- [ ] Las URLs con query (`q`, `status`, `sort`, `minBudget`, `page` y filtros) tienen `noindex,follow`.
- [ ] No hay errores de cobertura por redirecciones, bloqueos o servidor.
- [ ] Se revisan semanalmente cobertura, páginas indexadas y Core Web Vitals durante las primeras semanas.
