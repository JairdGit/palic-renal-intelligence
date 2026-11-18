# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.5

**Alcance:** procedencia de exportaciones sintéticas, estados vacíos y claridad de los límites del prototipo. Base: v0.9.4. Modelo predictivo desconectado.

## Cambios
- Nuevo `src/dashboard/demo_exports.py` con metadatos de versión, clasificación `SYNTHETIC_ONLY`, `clinical_use=false` y `predictive_model_connected=false`.
- CSV con línea inicial de comentario JSON de procedencia; la cabecera de datos se conserva. Los lectores programáticos deben omitir comentarios con `comment="#"`.
- JSON con envoltura `metadata` y `data`; se rechazan NaN e infinitos.
- Estados informativos cuando faltan mediciones o landmarks.
- Descargas de auditoría individual integradas con el serializador con procedencia.

## Cuatro auditorías
1. **Funcional y arquitectónica: APROBADA en alcance probado.** Módulo puro sin Streamlit, integrado en las descargas existentes.
2. **Científica y metodológica: APROBADA.** No cambian desenlace, horizonte, confirmación, censura ni contrato de predictores. Las exportaciones declaran naturaleza sintética y ausencia de inferencia.
3. **Seguridad e integridad: APROBADA en alcance probado.** Se rechazan versiones malformadas, tipos inválidos, esquemas CSV ambiguos, JSON no finito y conteos negativos.
4. **Integrada adversarial y regresión: APROBADA.** 170/170 pruebas aprobadas; compilación, regeneración sintética y controles de calidad/trazabilidad/conciliación comprobados.

## Resultados
500 pacientes; 4.293 mediciones; 500 landmarks; 347 evaluables; 153 no evaluables/censurados; 58 eventos sintéticos brutos. Calidad 27/27; trazabilidad 10/10; conciliación 12/12.

## Entorno y límites
- Perfil core: PASS 2/2.
- Perfil app: bloqueado por Streamlit ausente (5/6).
- La interfaz visual en navegador no se ejecutó.
- CSV incorpora línea de comentario de metadatos; usar `comment="#"` al importar.
- No es pentest profesional, validación clínica ni validación externa.

**Dictamen:** v0.9.5 aprobada como incremento técnico de procedencia de exportaciones y comunicación de estados vacíos. La validación visual en navegador permanece pendiente.
