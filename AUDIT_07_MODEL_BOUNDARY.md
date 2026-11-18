# Auditoría adversarial 07 — Frontera del modelo y afirmaciones científicas

**Resultado:** APROBADA CON LÍMITES.

**Búsqueda:** carga accidental de artefactos serializados, inferencia individual, uso de métricas históricas como métricas de demo y alteración del contrato de predictores.

**Resultado:** el contrato conserva 28 predictores efectivos en orden; la aplicación declara que el modelo real no está conectado y no llama al flujo de predicción.

**Evidencia:** `Audit07ModelBoundary`, `tests/test_model_integration.py`, `src/model_integration/loader.py`.

**Retest:** 2/2 pruebas nuevas aprobadas.

**Límite:** artefacto de modelo no integrado; no se presentan probabilidades individuales ni clasificación de riesgo. Métricas históricas no prueban validación externa ni utilidad clínica.
