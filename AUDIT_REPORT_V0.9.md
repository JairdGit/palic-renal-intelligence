# Informe de auditorías adversariales — PALIC Renal Intelligence v0.9

**Tipo de liberación:** integración del contrato de datos del dashboard.  
**Base:** v0.8.9.  
**Política de datos:** exclusivamente sintéticos.  
**Modelo predictivo:** desconectado; no se producen probabilidades ni categorías individuales.

## Cambios verificados

- Nuevo módulo `src/dashboard/validation.py` con 18 controles previos a la visualización.
- La aplicación incorpora `clinical_variables_synthetic.csv` a la carga controlada.
- Se exige estado `PASS` del manifiesto SHA-256 antes de cargar artefactos y mostrar resultados.
- Se valida la consistencia de identidad entre pacientes, mediciones, variables clínicas y landmarks.
- Se verifica unicidad de pacientes y landmarks, prefijo sintético, columnas requeridas, referencias no huérfanas, flags binarios, objetivos evaluables binarios y objetivos nulos para no evaluables.
- La sección de calidad presenta los controles del contrato de dashboard.
- `run_demo.py` registra `generator_version = v0.9`.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA EN EL ALCANCE EJECUTABLE.**

Evidencia:
- 111 pruebas automatizadas aprobadas.
- Compilación Python de aplicación, scripts, módulos y pruebas aprobada.
- El contrato de datos del dashboard aprobó 18/18 controles sobre el conjunto sintético regenerado.
- Se verificó por pruebas estáticas que la comprobación del manifiesto antecede la carga de datos y que el contrato antecede el renderizado del título y contenido.
- La ejecución directa de `app.py` terminó con código 2 por preflight de dependencias, antes de importar Streamlit, según diseño fail-closed.

Limitación: no se pudo ejecutar Streamlit ni completar una prueba visual/interactiva porque Streamlit no está instalado en el entorno de auditoría y scikit-learn 1.8.0 no satisface el pin 1.9.0 de `requirements.txt`. No se declara validación visual aprobada.

## Auditoría 2 — Científica y metodológica

**Resultado: APROBADA PARA CAMBIOS NO METODOLÓGICOS.**

Evidencia:
- Se regeneró el conjunto con semilla 20261105.
- 500 pacientes sintéticos; 4.293 mediciones; 500 landmarks.
- 347 evaluables y 153 no evaluables/censurados.
- 58 eventos sintéticos brutos/evaluables; 289 evaluables sin evento.
- Controles de calidad 27/27; trazabilidad 10/10; conciliación agregada 12/12.
- Se conserva el tratamiento de censura: los objetivos no evaluables permanecen nulos.
- No se alteraron el horizonte de 365 días, la confirmación mínima de 30 días, la definición del desenlace ni el contrato de 28 predictores.

Alcance: esta auditoría verifica que el cambio de integración no alteró las reglas documentadas y los resultados del generador. No constituye validación clínica, externa ni reproducción completa del estudio original.

## Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA EN EL ALCANCE PROBADO.**

Evidencia:
- El dashboard bloquea la visualización si el manifiesto no devuelve `PASS`.
- El contrato rechaza identificadores huérfanos, duplicados, no sintéticos, columnas ausentes, objetivos evaluables fuera de {0,1} y objetivos no nulos en registros censurados.
- Pruebas negativas específicas verifican el bloqueo ante alteraciones relacionales y metodológicas de presentación.
- No se incorporan datos reales ni artefactos serializados de modelo.

Limitación: no equivale a pentest, análisis SAST/DAST integral ni certificación de seguridad.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA EN EL ALCANCE EJECUTABLE.**

Evidencia:
- 111/111 pruebas aprobadas.
- Se mantuvieron las suites previas v0.7 y v0.8.1–v0.8.9.
- Se añadieron nueve pruebas para el contrato del dashboard y orden de compuertas.
- Compilación completa aprobada.
- Regeneración sintética y validaciones de calidad, trazabilidad y conciliación aprobadas.

Limitación: la regresión visual e interactiva queda pendiente de un entorno con dependencias de interfaz compatibles.

## Estado de liberación

**v0.9 aprobada como incremento de integración del contrato de datos y bloqueo de integridad del dashboard.** No se declara lista la demostración visual completa. Antes de v0.9.1 deberá prepararse un entorno de aplicación que satisfaga `requirements.txt`, iniciar Streamlit y realizar pruebas de navegación y visualización documentadas.

## Comandos de reproducción

```bash
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python check_environment.py --profile app
streamlit run app.py
```
