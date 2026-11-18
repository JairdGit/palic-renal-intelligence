# Auditoría adversarial 04 — Integridad relacional y calidad

**Resultado:** APROBADA dentro de los artefactos sintéticos.

**Búsqueda:** IDs duplicados, IDs no sintéticos, pacientes huérfanos, cobertura entre tablas y cardinalidad de pacientes/landmarks.

**Evidencia:** validadores `src/data_quality/validation.py`, `src/dashboard/validation.py` y `Audit04RelationalDataQuality`.

**Retest:** 2/2 pruebas nuevas aprobadas; 500 IDs únicos `SYN-`, cobertura de tabla clínica y mediciones sin huérfanos.

**Límite:** la consistencia interna sintética no constituye garantía de calidad de una futura fuente clínica real.
