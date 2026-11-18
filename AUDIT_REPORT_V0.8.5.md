# Informe de auditorías adversariales — PALIC Renal Intelligence v0.8.5

## Alcance
Incremento centrado en la trazabilidad entre mediciones renales fuente y landmarks/resultados longitudinales sintéticos. No se modificó la definición del desenlace, el horizonte de 365 días, la regla de confirmación mínima de 30 días, el contrato de 28 predictores ni la política de modelo desconectado.

## Evidencia de ejecución
- `python -m unittest discover -s tests -v`: **63/63 pruebas aprobadas**.
- `python run_demo.py --patients 500 --seed 20261105 --out data/generated`: ejecución satisfactoria.
- Datos regenerados: 500 pacientes, 4.293 mediciones renales, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos brutos sintéticos.
- Controles de calidad: 27/27.
- Auditoría de trazabilidad fuente→landmark: 10/10.
- El manifiesto SHA-256 se reconstruye después de regenerar los artefactos y se verifica contra el paquete final.

## Auditoría 1 — Funcional y arquitectónica
**Resultado: APROBADA en el alcance probado.** Se añadió `src/longitudinal_engine/traceability.py` como módulo separado, sin alterar el motor de construcción de landmarks. `run_demo.py` incorpora el resultado al archivo `longitudinal_audit.json`. Las pruebas verifican ejecución normal, columnas requeridas, duplicación, omisión y referencias huérfanas.

## Auditoría 2 — Científica y metodológica
**Resultado: APROBADA en el alcance probado.** Se contrasta que el registro índice exista en la fuente con la misma fecha y TFG; se recalculan observaciones futuras dentro de (índice, índice + 365 días]; se verifican la fecha de última observación, evaluabilidad con al menos dos observaciones futuras, fechas de cruce/confirmación, umbral de 60% de TFG índice y separación mínima de 30 días. Se comprueba que los no evaluables conserven `target_sustained_40` faltante. Estos controles no constituyen validación clínica ni reproducibilidad completa del estudio histórico.

## Auditoría 3 — Seguridad e integridad
**Resultado: APROBADA en el alcance probado.** El módulo de auditoría opera sobre copias de los DataFrames y no reescribe los datos fuente. Ante columnas obligatorias ausentes falla de forma cerrada. Se verificó el manifiesto SHA-256 del paquete. No se ejecutaron pruebas de penetración externas ni revisión independiente de dependencias/licencias; por tanto, no se declara certificación de ciberseguridad.

## Auditoría 4 — Integrada adversarial y regresión
**Resultado: APROBADA en el alcance probado.** Diez pruebas nuevas cubren salida válida, landmark duplicado, huérfano, ausente, TFG índice alterada, conteo futuro alterado, última fecha alterada, desenlace censurado recodificado, confirmación fuera de horizonte y columna obligatoria ausente. La suite completa heredada y nueva pasó 63/63.

## Hallazgos y límites
- No se identificaron hallazgos críticos o altos abiertos dentro de las pruebas automatizadas ejecutadas.
- La validación de trazabilidad depende de que las columnas de entrada cumplan el esquema declarado; ante esquema incompleto se reporta fallo.
- Los datos son exclusivamente sintéticos. Las métricas históricas de artículos no son resultados del demo.
- El modelo predictivo real permanece desconectado; no se generan probabilidades ni decisiones clínicas individuales.
- La aprobación se limita a este incremento y a la evidencia documentada; no equivale a auditoría externa, validación clínica, certificación regulatoria o validación externa.

## Dictamen
**v0.8.5 aprobada como incremento técnico del prototipo demostrativo**, condicionada a mantener explícitos los límites anteriores y a repetir las pruebas afectadas ante cambios posteriores.
