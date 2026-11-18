# PALIC Renal Intelligence v0.8 — Informe de auditorías adversariales

**Base:** paquete v0.7 aportado por el usuario  
**Tipo:** release incremental de integridad, validación y trazabilidad  
**Datos:** exclusivamente sintéticos  
**Uso clínico:** no habilitado  
**Modelo predictivo real:** no conectado

## Resultado ejecutivo

La suite completa ejecutó **25/25 pruebas aprobadas**. La reconstrucción con 500 pacientes y semilla `20261105` generó 4.293 mediciones renales, 500 landmarks, 347 horizontes evaluables, 153 no evaluables y 58 eventos sintéticos. El reporte ampliado de calidad aprobó **16/16 controles**.

La verificación SHA-256 del paquete se incorpora al dashboard y permite detectar cambios en los archivos declarados en el manifiesto. Estas comprobaciones validan únicamente los controles técnicos implementados; no constituyen validación clínica, auditoría profesional de ciberseguridad ni validación externa del modelo.

## Auditoría 1 — Funcional y arquitectónica

**Comprobaciones**
- Compilación de todos los módulos Python.
- Suite completa de 25 pruebas.
- Regeneración determinista de los datos sintéticos.
- Versión leída desde `RELEASE_MANIFEST.json` en los elementos de interfaz.
- Verificación del manifiesto con archivos íntegros, ausentes y alterados.
- El verificador rechaza manifiesto ausente o inválido y no ejecuta contenido de los archivos.

**Resultado:** aprobada para el alcance implementado y probado.

## Auditoría 2 — Científica y metodológica

**Comprobaciones**
- Se preserva la regla operacional de horizonte de 365 días, umbral de 60 % de TFG índice y confirmación con una segunda medición al menos 30 días después.
- Se conserva el tratamiento de horizontes no evaluables con objetivo nulo.
- Se amplían pruebas de integridad referencial y calidad sin imputar faltantes de TFG.
- Los conteos del conjunto sintético se reconcilian con el reporte de ejecución.
- Se mantienen las métricas históricas del artículo como referencias documentales, no como desempeño del prototipo.

**Resultado:** aprobada para los comportamientos y límites explícitamente cubiertos. No demuestra validez epidemiológica, clínica ni transportabilidad.

## Auditoría 3 — Seguridad e integridad

**Comprobaciones**
- Manifiesto SHA-256 con hashes de archivos del paquete.
- Detección de archivo modificado y archivo ausente en pruebas controladas.
- Rechazo de rutas que intentan salir del directorio raíz en el verificador.
- No se incluyen artefactos `.joblib`, `.pkl` ni `.pickle`.
- La carga joblib permanece bloqueada por defecto.
- No se incorporan datos clínicos reales.

**Resultado:** aprobada para los controles de integridad implementados. No equivale a pentest, análisis SAST/DAST, revisión de dependencias ni auditoría profesional de seguridad.

## Auditoría 4 — Integrada adversarial y de regresión

**Comprobaciones**
- Suite histórica v0.7 más nuevas pruebas adversariales v0.8.
- Detección de referencias renales huérfanas.
- Detección de filas clínicas duplicadas.
- Detección de creatinina no positiva.
- Detección de identificadores fuera del prefijo sintético.
- Reconciliación de 500 pacientes, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos.
- Calidad técnica: 16/16 controles.

**Resultado:** aprobada para la suite de regresión ejecutada.

## Hallazgos y límites pendientes

1. El modelo predictivo real sigue sin estar conectado; no se producen probabilidades ni categorías individuales de riesgo.
2. Las métricas del artículo 2 siguen siendo referencias históricas de evaluación temporal interna, no resultados de la demo.
3. No se reproduce independientemente el pipeline completo PALIC-PY-10 ni se resuelve la discrepancia temporal documentada en el archivo de investigación original.
4. La verificación SHA-256 confirma coincidencia con el manifiesto incluido; por sí sola no demuestra que el manifiesto provenga de un editor confiable ni protege contra sustitución simultánea de archivos y manifiesto.
5. No se ha realizado auditoría externa de dependencias/licencias, pentest ni validación clínica.
6. Antes del video, revisar interfaz con traducción automática del navegador desactivada.

## Decisión de versión

**v0.8 — Aprobada como release incremental de integridad, validación y trazabilidad**, limitada al alcance de las pruebas documentadas. No es un sistema clínico, no representa PALIC v1.0 y no declara validación externa.
