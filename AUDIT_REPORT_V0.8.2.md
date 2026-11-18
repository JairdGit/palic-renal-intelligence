# PALIC Renal Intelligence v0.8.2 — Informe de auditorías adversariales

**Incremento:** v0.8.2 — Contrato de secuencia longitudinal  
**Base:** paquete v0.8.1 recibido y verificado antes de la intervención.  
**Alcance:** validación estructural de la secuencia de mediciones renales sintéticas.  
**Política de datos:** exclusivamente sintéticos. **Uso clínico:** no habilitado.

## Cambios implementados

- Se valida que `measurement_sequence` contenga valores enteros, positivos y finitos.
- Se detectan secuencias duplicadas dentro de un mismo paciente.
- Se comprueba que la secuencia aumente al ordenar las mediciones por fecha.
- Se comprueba que la secuencia de cada paciente sea consecutiva desde 1, sin saltos.
- Se incorporan pruebas adversariales para secuencias duplicadas, invertidas, con saltos, fraccionarias y negativas.
- `run_demo.py` registra `generator_version: v0.8.2`.
- Se regeneran los datos sintéticos con la semilla de release 20261105.

## Auditoría 1 — Funcional y arquitectónica

**Ejecución:** suite completa de pruebas unitarias y adversariales; compilación de todos los archivos Python; regeneración del paquete de datos.  
**Resultado:** APROBADA dentro del alcance ejecutado. La validación se incorpora en el módulo de calidad existente, sin alterar la interfaz ni el motor de desenlace.

## Auditoría 2 — Científica y metodológica

**Ejecución:** revisión del alcance del cambio y comparación de las reglas longitudinales preservadas: definición de desenlace, caída sostenida de al menos 40 %, confirmación separada por al menos 30 días, horizonte de 365 días, selección de landmarks y política de censura.  
**Resultado:** APROBADA como control de no-regresión metodológica por alcance. Las nuevas reglas de secuencia son controles de integridad de registros sintéticos, no criterios clínicos. No se revalida el estudio original ni se afirma validación externa.

## Auditoría 3 — Seguridad e integridad

**Ejecución:** pruebas adversariales con secuencias duplicadas, invertidas, discontinuas, fraccionarias y negativas; verificación del manifiesto SHA-256 del paquete.  
**Resultado:** APROBADA para los controles implementados. No equivale a pentest, auditoría independiente de dependencias ni certificación de seguridad.

## Auditoría 4 — Integrada adversarial y regresión

**Ejecución:** pruebas heredadas v0.7, v0.8 y v0.8.1 junto con las nuevas pruebas v0.8.2; verificación de contrato de 28 predictores, carga del modelo cerrada por defecto, motor longitudinal y censura.  
**Resultado:** APROBADA para la suite ejecutada.

## Evidencia de ejecución

- Pruebas unitarias y adversariales: **37/37 aprobadas**.
- Compilación Python: **aprobada**.
- Controles de calidad de datos sintéticos: **19/19 aprobados**.
- Pacientes sintéticos: **500**.
- Mediciones renales sintéticas: **4.293**.
- Landmarks: **500**.
- Evaluable a 365 días: **347**.
- No evaluable/censurado: **153**.
- Eventos sintéticos brutos: **58**.
- Modelo predictivo: **desconectado**; no se producen probabilidades individuales.

## Limitaciones y decisión

Los resultados anteriores describen exclusivamente el generador y las pruebas del prototipo. No representan prevalencia, historia natural, rendimiento clínico ni validación externa. Las métricas históricas de los artículos científicos no son resultados de esta demostración.

**Decisión:** v0.8.2 aprobada como incremento de endurecimiento del contrato estructural de secuencia longitudinal, limitado al alcance y evidencia documentados.
