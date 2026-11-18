# PALIC Renal Intelligence v0.8.1 — Informe de auditorías adversariales

**Base:** paquete v0.8 recibido y verificado por SHA-256 antes de intervenir.
**Alcance:** endurecimiento del verificador del manifiesto de release. Motor longitudinal, datos, contrato de 28 predictores y conexión del modelo no modificados.
**Datos:** exclusivamente sintéticos. **Uso clínico:** no habilitado.

## Línea base
- ZIP de entrada: `PALIC_Renal_Intelligence_v0.8.zip`
- SHA-256: `390c47caf407386e950f09ac28e72425104605b8999e2cd0037f8545674c367c`
- Pruebas heredadas v0.8: 25/25 aprobadas antes de los cambios.

## Cambios v0.8.1
- Validación de que la raíz del manifiesto sea un objeto JSON.
- Rechazo de claves JSON duplicadas.
- Validación estricta de digest SHA-256 de 64 caracteres hexadecimales.
- Rechazo de rutas absolutas, traversal (`..`), separadores no portables y rutas que resuelven fuera de la raíz.
- Manejo cerrado de errores de lectura.
- Seis pruebas adversariales nuevas para parsing, digest y rutas.

## Auditoría 1 — Funcional y arquitectónica
**Pruebas:** compilación Python; suite heredada más suite v0.8.1; verificación de manifiesto válido y errores de lectura.
**Resultado:** APROBADA dentro del alcance. No se modificaron módulos del motor ni interfaz.

## Auditoría 2 — Científica y metodológica
**Pruebas:** inspección del diff para confirmar que no cambian definiciones de desenlace, horizonte, umbral, censura, landmarks, predictores ni datos.
**Resultado:** APROBADA para no-regresión metodológica por alcance; no constituye revalidación científica del estudio ni del modelo.

## Auditoría 3 — Seguridad e integridad
**Pruebas:** manifiesto raíz no-objeto, claves duplicadas, digest malformado, ruta absoluta, traversal, manifiesto válido. No se ejecuta ni deserializa contenido de archivos verificados.
**Resultado:** APROBADA para el endurecimiento implementado. No equivale a pentest, SAST/DAST, auditoría de dependencias ni firma criptográfica del manifiesto.

## Auditoría 4 — Integrada adversarial y regresión
**Pruebas:** 25 pruebas heredadas v0.8 más 6 pruebas nuevas; comprobación de que la regresión de motor, calidad de datos y contrato de predictores permanece aprobada.
**Resultado:** APROBADA para la suite ejecutada.

## Resultados de ejecución
- Pruebas: 31/31 aprobadas.
- Compilación: aprobada.
- Datos y resultados sintéticos: sin cambios.
- Modelo predictivo: sigue desconectado.

## Límites y decisión
El manifiesto incluido permite detectar alteraciones respecto de sus hashes declarados, pero no es una firma digital ni protege contra la sustitución simultánea del paquete y su manifiesto.

**Decisión:** v0.8.1 aprobada como incremento de endurecimiento del verificador de integridad, limitada al alcance y pruebas documentadas.
