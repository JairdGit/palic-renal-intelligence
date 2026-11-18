# PALIC Renal Intelligence — Informe de auditoría v0.8.6

**Tipo:** incremento de reconciliación de resultados agregados  
**Datos:** exclusivamente sintéticos  
**Uso clínico:** no autorizado / no previsto  
**Modelo predictivo real:** desconectado  
**Semilla:** `20261105`

## Objetivo

Comprobar que los conteos del conjunto fuente, los landmarks individuales, los estados de evaluabilidad/censura y las cifras del informe longitudinal coincidan. Esta versión añade `src/longitudinal_engine/aggregate_audit.py` y expone la conciliación en la sección de calidad del dashboard.

## Cambios

- Conciliación de conteos de pacientes, mediciones renales y filas clínicas contra `quality_report.json`.
- Conciliación de landmarks y pacientes únicos contra `longitudinal_audit.json`.
- Verificación de denominadores evaluables y no evaluables.
- Separación explícita de eventos brutos, eventos evaluables y evaluables sin evento.
- Verificación de que los no evaluables conserven el objetivo como faltante.
- Verificación de objetivos binarios para los evaluables.
- Detección de landmarks duplicados y conciliación de totales de eventos.
- Visualización del estado y detalle de conciliación en el dashboard.

## Cuatro auditorías adversariales

### 1. Funcional y arquitectónica — APROBADA

- La conciliación se ejecuta después de generar las tablas y reportes fuente.
- El resultado se incorpora a `longitudinal_audit.json` como `aggregate_reconciliation`.
- La interfaz presenta los controles sin activar inferencia ni modificar el motor científico.
- Pruebas de referencia y de discrepancias intencionales: aprobadas.

### 2. Científica y metodológica — APROBADA dentro del alcance

- Se mantiene la definición: caída de TFG de al menos 40 % respecto al índice, con confirmación al menos 30 días después y dentro de 365 días.
- Se mantiene el requisito de al menos dos observaciones futuras válidas para evaluabilidad.
- Los no evaluables conservan `target_sustained_40 = NaN`; no se convierten en no-eventos.
- Los eventos brutos y evaluables se reportan por separado.
- No se alteran predictores, selección de landmarks, ventanas ni métricas históricas.

### 3. Seguridad e integridad — APROBADA dentro del alcance

- El módulo opera sobre copias/lecturas de los DataFrames y no reescribe las entradas.
- No carga modelos serializados, no incorpora datos personales y no habilita inferencia.
- Los reportes con conteos alterados, IDs duplicados, objetivos no binarios y recodificación de censura se detectan en pruebas.
- El manifiesto SHA-256 se regenera después de cerrar el paquete.
- Esta revisión no equivale a pentest, revisión de dependencias exhaustiva ni certificación externa.

### 4. Integrada adversarial y regresión — APROBADA

- Suite completa: **73/73 pruebas aprobadas**.
- Nuevas pruebas v0.8.6: **10/10 aprobadas**.
- Generación determinista y conciliación real: **12/12 controles aprobados**.
- Compilación Python: aprobada.

## Resultado de regeneración

| Indicador | Resultado |
|---|---:|
| Pacientes sintéticos | 500 |
| Mediciones renales | 4.293 |
| Filas clínicas | 500 |
| Landmarks | 500 |
| Pacientes únicos con landmark | 500 |
| Evaluable a 365 días | 347 |
| No evaluable/censurado | 153 |
| Eventos brutos | 58 |
| Eventos evaluables | 58 |
| Evaluable sin evento | 289 |
| Controles de calidad | 27/27 |
| Controles de trazabilidad | 10/10 |
| Controles de conciliación agregada | 12/12 |

## Hallazgos y límites

- No se encontró discrepancia en el conjunto sintético regenerado con la semilla declarada.
- La igualdad entre eventos brutos y evaluables se verifica para este conjunto; no debe generalizarse a otros conjuntos sin ejecutar la conciliación.
- Las cifras de la demo no son prevalencia ni estimaciones epidemiológicas.
- Las métricas históricas del artículo no son generadas por esta demo.
- No se ha reproducido independientemente el pipeline científico completo ni resuelto la discrepancia temporal histórica documentada.
- La aprobación es interna y limitada a las pruebas y controles descritos.

## Decisión

**v0.8.6 aprobada como incremento de estabilización del prototipo sintético.** No equivale a validación clínica, validación externa, certificación de seguridad ni liberación final para uso asistencial.
