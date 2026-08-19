# Seguridad

Principio central: **Si no necesitamos un dato sensible, no lo almacenamos.**

Se aplicarán mínimo privilegio, secretos solo mediante variables de entorno o secret manager, nunca secretos en Git, separación entre development/preview/production, HTTPS obligatorio en producción, validación de entradas, control de acceso, logging sin secretos, dependencias auditables y backups probados. El threat modelling se formalizará antes de exponer funcionalidades; OWASP será referencia.

En V0.1 no existirán usuarios ni datos privados. Cualquier futura incorporación deberá definir amenazas, retención, acceso, recuperación y auditoría antes de implementarse.

