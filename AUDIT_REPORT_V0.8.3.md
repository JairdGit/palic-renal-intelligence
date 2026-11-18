# PALIC Renal Intelligence v0.8.3 — Informe de auditorías adversariales

**Incremento:** v0.8.3 — Integridad temporal de mediciones y validación de valores finitos  
**Base:** v0.8.2  
**Política de datos:** exclusivamente sintéticos  
**Uso clínico:** no autorizado / no es dispositivo médico  
**Modelo predictivo conectado:** no

## Alcance y cambios

- Parseo temporal explícito con `format="mixed"` y normalización UTC para entradas con offsets mixtos.
- Detección de duplicados por paciente y día calendario, incluso cuando las horas difieren.
- Detección de valores no finitos (`NaN` se conserva donde es admisible; `+/-inf` no se acepta como valor numérico válido) en TFG, creatinina, secuencia, edad e IMC.
- Comprobación opcional de fechas futuras respecto de `reference_date`, únicamente cuando el operador proporciona explícitamente esa fecha. No se infiere fecha de corte ni se compara automáticamente con el reloj del sistema.
- Pruebas adversariales nuevas para fechas malformadas, zonas horarias mixtas, duplicados intradía, infinitos, orden temporal y fecha de referencia.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA dentro del alcance probado.** La validación se mantiene en `src/data_quality/validation.py`; no introduce dependencia nueva ni altera el motor longitudinal. Se ejecutó la generación sintética determinista y la compilación Python. El conjunto base produce 22/22 controles de calidad aprobados.

## Auditoría 2 — Científica y metodológica

**Resultado: APROBADA con límites explícitos.** No se modificaron la definición del desenlace `Target_Sustained_40`, la confirmación mínima de 30 días, el horizonte de 365 días, la selección de landmarks, el tratamiento de censura ni el contrato de 28 predictores. La fecha de referencia es opcional y declarada por el operador; por tanto, no se introduce un supuesto de observabilidad no documentado. Los controles son técnicos y no representan umbrales clínicos.

## Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA dentro del alcance probado.** Se verificó el manejo de fechas inválidas, offsets mixtos, duplicados intradía y valores infinitos. Se conserva la política `SYNTHETIC_ONLY`, no se habilita carga de artefactos serializados y no se incorporan datos reales. La verificación SHA-256 detecta modificaciones respecto del manifiesto, pero no equivale a firma digital ni protege frente a sustitución coordinada del paquete y manifiesto.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA.** Se ejecutó la suite heredada y nueva: **44/44 pruebas aprobadas**. Se comprobó el contrato de 28 predictores y que la carga joblib permanezca cerrada por defecto. La generación con semilla `20261105` produjo: 500 pacientes sintéticos, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos sintéticos brutos.

## Hallazgos y limitaciones pendientes

- No se realiza inferencia predictiva ni se presentan probabilidades individuales.
- Los datos sintéticos no constituyen validación externa, clínica ni epidemiológica.
- La discrepancia temporal del archivo de investigación original permanece fuera del alcance de este incremento y debe resolverse antes de afirmar reproducibilidad integral de la investigación PALIC-PY-10.
- La comprobación opcional de fecha futura solo tiene valor si el operador proporciona una fecha de referencia correcta y documentada.
- No se ha realizado pentest profesional ni revisión independiente de dependencias/licencias en esta versión.

## Decisión de liberación

**v0.8.3 aprobada como incremento técnico de integridad temporal**, limitada a las pruebas y evidencias descritas. No equivale a certificación de seguridad, validación clínica ni validación externa.
