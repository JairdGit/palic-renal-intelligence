# Auditoría adversarial 01 — Funcional y arquitectura

**Resultado:** APROBADA. **Severidad abierta:** ninguna dentro del alcance automatizado.

**Búsqueda:** tipos inválidos, semillas booleanas, reproducibilidad, rutas de generación, orden de inicialización y dependencias importadas antes del preflight.

**Hallazgo corregido:** el generador aceptaba implícitamente valores no enteros/booleanos como argumentos. Se endureció `generate_synthetic_data` para exigir `n_patients` entero >=10 y `seed` entero no negativo.

**Evidencia:** `Audit01FunctionalArchitecture` en `tests/test_release_v1_adversarial.py`; suite de regresión histórica.

**Retest:** 3/3 pruebas nuevas aprobadas; compilación Python aprobada.

**Límite:** no reemplaza pruebas de carga o de navegador.
