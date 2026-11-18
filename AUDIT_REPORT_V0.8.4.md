# PALIC Renal Intelligence v0.8.4 — Informe de auditorías adversariales

**Incremento:** v0.8.4 — Integridad relacional e identidad longitudinal  
**Base:** v0.8.3  
**Política de datos:** exclusivamente sintéticos  
**Uso clínico:** no autorizado; no es un dispositivo médico  
**Modelo predictivo conectado:** no

## Alcance y cambios

- Se incorporan controles explícitos de claves foráneas entre pacientes, mediciones renales y variables clínicas.
- Se detectan claves foráneas nulas, vacías y referencias huérfanas o no coincidentes.
- Se verifica la cobertura del conjunto sintético: cada paciente debe tener al menos una medición renal y una fila clínica; el control de unicidad clínica preexistente conserva la expectativa de una sola fila clínica por paciente.
- Se detectan identificadores con espacios externos y colisiones tras normalización `strip + casefold`, sin modificar los datos originales.
- Se agregan nueve pruebas adversariales sobre relaciones, cobertura, claves nulas, IDs huérfanos, espacios y colisiones.
- `run_demo.py` registra `generator_version = v0.8.4`.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA dentro del alcance probado.** La lógica se mantiene en el módulo existente `src/data_quality/validation.py`; no se agregan dependencias ni se modifica el motor longitudinal. Se verifica que el conjunto sintético de referencia satisfaga el contrato relacional y que los controles fallen ante alteraciones dirigidas. La validación no reescribe identificadores ni transforma las tablas fuente.

## Auditoría 2 — Científica y metodológica

**Resultado: APROBADA con límites explícitos.** No se modifican `Target_Sustained_40`, la confirmación mínima de 30 días, el horizonte de 365 días, la selección de landmarks, la censura ni el contrato de 28 predictores. Las reglas de cobertura (una fila clínica y al menos una medición renal por paciente) se limitan al conjunto sintético generado para esta demostración; no se presentan como reglas universales para cohortes clínicas reales.

## Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA dentro del alcance probado.** Las pruebas cubren claves nulas, vacías, huérfanas, identificadores con espacios y colisiones tras normalización. Los valores de origen no se corrigen silenciosamente. Se conserva `SYNTHETIC_ONLY`; no se incorporan datos reales ni artefactos serializados y la carga del modelo permanece cerrada por defecto. El manifiesto SHA-256 permite detectar modificaciones respecto de los hashes declarados, pero no es una firma digital.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA.** Se ejecutaron las pruebas heredadas y nuevas, la compilación Python, la generación determinista y la verificación del manifiesto. La suite completa aprobó **53/53 pruebas**. La generación con semilla `20261105` conservó 500 pacientes sintéticos, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos sintéticos brutos. El contrato de 28 predictores y la barrera de carga joblib por defecto se mantienen.

## Hallazgos y limitaciones pendientes

- Las comprobaciones son controles técnicos del prototipo, no validación clínica ni epidemiológica.
- La cobertura completa es una expectativa del generador sintético; otros conjuntos deberán declarar su propio contrato.
- El modelo predictivo real permanece desconectado y no se calculan probabilidades individuales.
- La discrepancia temporal del archivo de investigación original permanece fuera del alcance de este incremento.
- No se ha realizado pentest profesional ni validación externa independiente.

## Decisión de liberación

**v0.8.4 aprobada como incremento técnico de integridad relacional**, limitada a las pruebas y evidencias descritas. No equivale a certificación de seguridad, validación clínica ni validación externa.
