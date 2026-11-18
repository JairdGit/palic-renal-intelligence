# Informe de auditorías adversariales — PALIC Renal Intelligence v0.9.1

**Base:** v0.9.  
**Tipo de liberación:** separación de dependencias de ejecución del dashboard y dependencias de investigación/modelado.  
**Datos:** exclusivamente sintéticos.  
**Modelo predictivo:** desconectado; no se ejecuta inferencia ni se generan probabilidades individuales.

## Cambios implementados

- Se creó `requirements-app.txt` para las dependencias de la interfaz Streamlit y lectura/visualización de datos sintéticos.
- Se creó `requirements-model.txt` para dependencias opcionales del entorno de investigación/modelado (`scikit-learn==1.9.0`, `joblib==1.5.3`).
- Se retiró scikit-learn del `requirements.txt` general de generación y uso de la demo, porque el dashboard no importa ni ejecuta scikit-learn.
- `src/environment/check.py` admite los perfiles `core`, `app` y `model` y selecciona el archivo de requisitos correspondiente.
- `check_environment.py` expone los tres perfiles.
- `run_demo.py` identifica el generador como `v0.9.1`.
- Se añadieron ocho pruebas adversariales para verificar separación de dependencias, perfil app, perfil model, fallo cerrado por Streamlit ausente, secciones del dashboard y conservación de límites científicos.

No se modificaron el motor longitudinal, la definición del desenlace, el horizonte de 365 días, la confirmación mínima de 30 días, la política de censura ni el contrato de 28 predictores.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA EN EL ALCANCE EJECUTABLE.**

Evidencia:
- 119/119 pruebas automatizadas aprobadas.
- Compilación de todos los archivos Python aprobada.
- El perfil `core` pasó con pandas 2.2.3 y NumPy 2.3.5.
- El perfil `app` ahora evalúa seis dependencias de ejecución y ya no incluye scikit-learn.
- El perfil `model` comprueba por separado scikit-learn y joblib.
- Se verificó que el dashboard conserva sus seis secciones de navegación.
- El generador ejecutó correctamente y produjo el conjunto sintético esperado.

Limitación: no se pudo ejecutar el dashboard visual porque Streamlit no está instalado en el entorno. La prueba de estructura de navegación no se presenta como prueba visual ni interactiva.

## Auditoría 2 — Científica y metodológica

**Resultado: APROBADA PARA CAMBIOS NO METODOLÓGICOS.**

Evidencia de regeneración determinista con semilla `20261105`:
- 500 pacientes sintéticos.
- 4.293 mediciones renales.
- 500 landmarks.
- 347 pacientes evaluables a 365 días.
- 153 pacientes no evaluables/censurados.
- 58 eventos sintéticos brutos.
- Calidad 27/27; trazabilidad 10/10; conciliación 12/12.

Se conserva el objetivo nulo para pacientes no evaluables. La separación de dependencias no cambia datos, reglas ni definiciones metodológicas.

Alcance: esta comprobación no constituye validación clínica, validación externa ni reproducción completa del estudio original.

## Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA EN EL ALCANCE PROBADO.**

Evidencia:
- La comprobación de dependencias continúa siendo offline; no instala paquetes ni accede a internet.
- Los perfiles usan archivos de requisitos explícitos y no relajan las versiones del entorno de modelado.
- El dashboard mantiene su preflight fail-closed.
- La ejecución directa de `app.py` terminó con código 2 por ausencia de Streamlit, antes de cargar datos o importar la interfaz.
- Se mantiene el bloqueo de carga de artefactos serializados de modelo por defecto.
- No se agregaron datos reales ni archivos de modelo.

Limitación: no equivale a pentest, SAST/DAST integral ni certificación de seguridad.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA EN EL ALCANCE EJECUTABLE.**

Evidencia:
- 119/119 pruebas aprobadas.
- Suites anteriores conservadas y ejecutadas.
- Ocho pruebas nuevas específicas de v0.9.1.
- Compilación Python completa aprobada.
- Regeneración sintética, calidad, trazabilidad y conciliación aprobadas.
- Perfil `app` detectó exclusivamente la dependencia faltante Streamlit; scikit-learn dejó de ser requisito del dashboard.
- Perfil `model` detectó scikit-learn 1.8.0 frente al pin 1.9.0, como corresponde al entorno de modelado separado.

Limitación: no se ejecutó prueba visual/interactiva real porque Streamlit no está instalado. La integración visual permanece pendiente.

## Matriz de entorno observada

| Perfil | Resultado | Hallazgo |
|---|---|---|
| core | PASS | pandas y NumPy compatibles |
| app | BLOCKED_AS_EXPECTED | Streamlit ausente; las demás dependencias de interfaz verificadas cumplen |
| model | BLOCKED_AS_EXPECTED | scikit-learn 1.8.0; se requiere exactamente 1.9.0 |

## Estado de liberación

**v0.9.1 aprobada como incremento de separación de dependencias y endurecimiento del preflight.** No se declara validada visualmente la interfaz. Para completar esa validación se debe instalar `requirements-app.txt` en un entorno limpio con acceso autorizado al índice de paquetes, ejecutar `streamlit run app.py` y documentar navegación, gráficas, tablas y descargas.

## Comandos de reproducción

```bash
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python check_environment.py --profile app
python check_environment.py --profile model

# En un entorno con dependencias de interfaz instaladas:
# pip install -r requirements-app.txt
# streamlit run app.py
```
