# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.4

**Alcance:** contrato de visualización longitudinal, anotaciones de landmark y estados de observación.
**Base:** v0.9.3; suite base reproducida: 146/146 antes de cambios.
**Datos:** exclusivamente sintéticos; modelo predictivo desconectado.

## Cambios
- Nuevo `src/dashboard/visualization.py`, independiente de Streamlit/Plotly.
- Preparación cronológica de trayectorias, validación de fechas y TFG finita, rechazo de mediciones duplicadas por fecha.
- Anotación explícita de landmark y cálculo de línea de referencia al 60 % del valor índice, identificada como regla operacional del desenlace y no como umbral diagnóstico.
- Validación de la relación entre evaluabilidad, objetivo y estado de observación antes de presentación.
- Integración del helper en la vista de trayectoria y en la distribución de estados del dashboard.

## Cuatro auditorías
1. **Funcional y arquitectónica — APROBADA en el alcance probado.** Helpers puros, sin importación de Streamlit/Plotly; integración de la capa de visualización en app.py; errores controlados.
2. **Científica y metodológica — APROBADA.** No cambia definición de desenlace, horizonte 365 días, confirmación mínima 30 días, censura ni contrato de 28 predictores. La línea del 60 % se rotula como regla operacional, no como diagnóstico.
3. **Seguridad e integridad — APROBADA en el alcance probado.** Rechazo de fechas inválidas, valores TFG no finitos, duplicados temporales, landmarks ambiguos y estados desconocidos. Datos siguen siendo sintéticos.
4. **Integrada adversarial y regresión — APROBADA.** Suite completa: 158/158 pruebas aprobadas. Regeneración determinista, compilación y controles de datos se verificaron.

## Resultados de datos
- 500 pacientes; 4.293 mediciones renales; 500 landmarks.
- 347 evaluables; 153 no evaluables/censurados; 58 eventos sintéticos brutos.
- Calidad 27/27; trazabilidad 10/10; conciliación 12/12.

## Entorno y límites
- Perfil core: PASS.
- Perfil app: bloqueado por ausencia de Streamlit.
- La validación visual real en navegador **no se ejecutó**.
- No es pentest profesional, validación clínica ni validación externa.

## Dictamen
**v0.9.4 aprobada como incremento técnico del contrato de visualización sintética.** La validación visual en navegador sigue pendiente y no se infiere de las pruebas unitarias.
