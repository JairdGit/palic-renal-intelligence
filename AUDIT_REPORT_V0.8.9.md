# Informe de auditorías adversariales — PALIC Renal Intelligence v0.8.9

## Alcance

Incremento centrado en la preparación reproducible del entorno y, especialmente, en el orden de inicialización del dashboard. La comprobación de dependencias debe ejecutarse antes de importar Streamlit, Plotly, pandas, NumPy u otros paquetes de terceros utilizados por la interfaz.

## Cambio principal

En v0.8.8, `app.py` importaba Streamlit y otras dependencias de terceros antes de ejecutar el preflight `profile="app"`. En un entorno sin Streamlit, el proceso podía terminar con `ModuleNotFoundError` antes de emitir el diagnóstico de incompatibilidad. En v0.8.9 se reordenó el arranque: primero se ejecuta el preflight usando módulos estándar y el verificador del proyecto; si falla, se imprime un informe legible en stderr y se termina con código 2. Solo después de superar el preflight se importan las dependencias de la aplicación.

También se añadió una suite adversarial específica para el orden de inicialización, perfiles core/app, restricciones de requirements y metadatos de liberación.

## Auditoría 1 — Funcional y arquitectónica

**Resultado: aprobada dentro del alcance probado.**

- Se comprobó que el perfil core no depende de las bibliotecas exclusivas de interfaz.
- Se comprobó que el perfil app detecta tanto una dependencia ausente como una versión incompatible.
- Se ejecutó `app.py` en el entorno de auditoría: finalizó de forma controlada con código 2 y diagnóstico de incompatibilidad, antes de intentar importar Streamlit.
- Se verificó sintácticamente el orden del preflight respecto a las importaciones de terceros.

## Auditoría 2 — Científica y metodológica

**Resultado: aprobada para no regresión del alcance.**

- El cambio no modifica el motor longitudinal, el desenlace, la ventana de 365 días, la confirmación de 30 días, el tratamiento de censura ni el contrato de 28 predictores.
- Se conserva la política `SYNTHETIC_ONLY` y `predictive_model_connected=false`.
- La generación sintética determinista se ejecuta con el perfil core.
- Esta auditoría de software no equivale a validación clínica ni reproduce de forma independiente el pipeline de investigación original.

## Auditoría 3 — Seguridad e integridad

**Resultado: aprobada dentro del alcance probado.**

- El preflight no instala paquetes, no modifica el entorno y no realiza solicitudes de red.
- Los requisitos con directivas de inclusión, instalación editable o configuración de índices no admitida siguen rechazándose.
- El manifiesto de liberación identifica versión, política de datos y estado de conexión del modelo.
- Se recalcularon hashes de los archivos incluidos en el manifiesto: el total exacto se registra en `RELEASE_MANIFEST.json`.

## Auditoría 4 — Integrada adversarial y regresión

**Resultado: aprobada dentro del alcance probado.**

- Suite completa ejecutada mediante `python -m unittest discover -s tests -v`: **100/100 pruebas aprobadas**.
- Se añadieron siete pruebas adversariales v0.8.9.
- Se compiló el código Python.
- Se regeneraron datos sintéticos y se verificaron controles de calidad, trazabilidad y conciliación.
- Se comprobó la integridad estructural del ZIP.

## Resultados del entorno de auditoría

- Python: 3.13.5 (rango declarado compatible).
- Perfil core: aprobado.
- Perfil app: rechazado correctamente por `scikit-learn` instalado 1.8.0 frente a `==1.9.0` y por ausencia de Streamlit.
- Arranque visual de Streamlit: **no ejecutado**, debido al resultado negativo del perfil app.
- No se afirma instalación limpia ni validación visual de la interfaz.

## Resultados del conjunto sintético

Se conservan 500 pacientes sintéticos, 4.293 mediciones renales, 500 landmarks, 347 evaluables, 153 no evaluables/censurados y 58 eventos sintéticos brutos. Los totales son resultados del generador de demostración, no estimaciones epidemiológicas.

## Hallazgos pendientes y límites

1. Para validar visualmente el dashboard, instalar las dependencias exactas declaradas en `requirements.txt` en un entorno limpio compatible y ejecutar Streamlit.
2. La versión `scikit-learn==1.9.0` se conserva como requisito declarado; el entorno de auditoría solo dispone de 1.8.0. No se cambió el pin para acomodar el entorno.
3. No se realizó pentest profesional, revisión externa de dependencias ni validación clínica.

## Dictamen

**v0.8.9 aprobada como incremento de endurecimiento del arranque y diagnóstico de entorno, con limitación explícita: la interfaz no queda visualmente validada en este entorno.** No debe presentarse el preflight aprobado como prueba de que el dashboard completo se ejecutó.
