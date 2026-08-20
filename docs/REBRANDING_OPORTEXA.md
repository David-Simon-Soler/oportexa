# Rebranding Oportexa

## Decisión

- Nombre público anterior: Opportunity Intel.
- Nombre público nuevo: Oportexa.
- Dominio previsto: `https://oportexa.com`.

Oportexa comunica una plataforma para descubrir, entender y verificar ayudas y subvenciones públicas. La dirección visual Editorial Data Intelligence, las rutas y la arquitectura no cambian.

## Superficies actualizadas

- Wordmark del header y footer.
- Homepage y texto accesible de orientación.
- Provenance y fuente de confianza.
- Mensajes de observación local.
- Metadata raíz y `applicationName`.
- Descripciones y títulos SEO de taxonomías.
- README y documentación actual de producto, UX, SEO y arquitectura.

## Identificadores conservados

Se conserva `opportunity-intel` en el nombre del repositorio, rutas de filesystem, ejemplos de base de datos, nombres Docker, `application_name` de PostgreSQL, claves internas de locking, user-agent histórico de ingestion y paths de documentación. Son identificadores técnicos o históricos; cambiarlos no aporta valor público y podría romper compatibilidad local.

## Site URL

La aplicación ya usa `SITE_URL` como configuración central para `metadataBase`, sitemap y robots. Desarrollo mantiene el fallback `http://localhost:3000`; producción deberá definir:

```text
SITE_URL=https://oportexa.com
```

No se introducen secretos ni se activan URLs absolutas de producción en desarrollo.

## Pendiente antes del deploy

- Definir `SITE_URL=https://oportexa.com` en el entorno de producción.
- Verificar canonical, sitemap y robots en el deploy real.
- Revisar favicon y manifest si se incorpora identidad de marca explícita.
- Configurar DNS y hosting fuera de esta tarea.
- Verificar Search Console después de que exista producción.

No se crea un logo complejo, isotipo, favicon especulativo ni integración con proveedores externos.
