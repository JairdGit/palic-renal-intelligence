# PALIC Renal Intelligence — Informe de auditorías v0.8.7

**Tipo de versión:** endurecimiento de ejecución y lectura segura de artefactos.  
**Datos:** exclusivamente sintéticos.  
**Uso clínico:** no autorizado; el prototipo no diagnostica ni recomienda tratamientos.  
**Modelo predictivo:** desconectado; no produce probabilidades ni clasificaciones individuales.

## Alcance y cambios

- Nuevo módulo `src/io_safety/safe_io.py` para lectura validada de CSV y JSON.
- Lectura fail-closed ante archivos ausentes, vacíos, malformados, con columnas requeridas ausentes, fechas inválidas, claves JSON duplicadas, raíz JSON inesperada o constantes no finitas.
- `run_demo.py` genera en un directorio temporal, valida calidad, trazabilidad y conciliación, relee los artefactos y solo entonces publica el conjunto completo.
- Sustitución transaccional del directorio de salida; si falla la promoción se intenta restaurar el conjunto anterior.
- `app.py` detiene el inicio de forma explícita si el manifiesto o los artefactos obligatorios no son legibles y válidos; evita presentar resultados parciales.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA en el alcance ejecutado.**

Evidencia:
- Compilación de todos los módulos Python completada sin errores.
- Ejecución de `python run_demo.py --patients 500 --seed 20261105` completada.
- La generación valida calidad, trazabilidad y conciliación antes de publicar.
- Las escrituras se preparan fuera del directorio publicado y la promoción sustituye el directorio completo.
- Pruebas de sustitución completa y recuperación tras fallo simulado de promoción aprobadas.

## Auditoría 2 — Científica y metodológica

**Resultado: APROBADA en el alcance ejecutado.**

Evidencia:
- No se modificaron `engine.py`, `outcome_audit.py`, `traceability.py`, `aggregate_audit.py`, el generador científico ni el contrato de predictores.
- Semilla `20261105`; 500 pacientes, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos brutos.
- Controles de calidad: 27/27; trazabilidad: 10/10; conciliación agregada: 12/12.
- Se conserva el objetivo faltante para pacientes no evaluables/censurados.
- Las cifras corresponden al generador sintético; no son estimaciones epidemiológicas ni validación clínica.

## Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA en el alcance ejecutado.**

Evidencia adversarial:
- CSV ausente, vacío, malformado, con columnas faltantes y fechas inválidas: rechazo controlado.
- JSON con claves duplicadas, raíz no objeto y `NaN`: rechazo controlado.
- Fallo simulado al promover la nueva salida: restauración del directorio previo comprobada.
- La aplicación no continúa con artefactos obligatorios inválidos.
- El modelo sigue desconectado; no se añadieron ni cargaron artefactos serializados.

Límite: estas pruebas no equivalen a pentest profesional, análisis de amenazas completo ni certificación de seguridad.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA en el alcance ejecutado.**

- `python -m unittest discover -s tests -v`: **84/84 pruebas aprobadas**.
- Compilación Python: aprobada.
- Generación sintética determinista y lectura posterior de los seis artefactos: aprobadas.
- Suite histórica de motor, contrato de modelo, integridad, temporalidad, relaciones, trazabilidad y conciliación: sin regresiones detectadas.

## Hallazgos y limitaciones abiertas

- No se realizó una prueba visual manual de todos los estados de Streamlit en navegadores distintos.
- No se realizó pentest externo ni auditoría independiente de dependencias/licencias.
- La publicación transaccional usa renombrados locales dentro del mismo sistema de archivos; garantías ante pérdida abrupta de energía dependen del sistema de archivos y no se declaran como equivalentes a una transacción de base de datos.
- Persisten las limitaciones científicas documentadas en versiones anteriores: discrepancia temporal histórica por resolver y ausencia de validación externa/uso clínico.

## Decisión de liberación

**v0.8.7 aprobada como incremento técnico del prototipo sintético**, dentro del alcance y las evidencias descritas. No es una certificación clínica, regulatoria ni de ciberseguridad. El modelo predictivo real permanece desconectado.
