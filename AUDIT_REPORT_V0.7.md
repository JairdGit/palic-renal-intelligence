# PALIC Renal Intelligence v0.7 — Informe de auditorías adversariales

**Tipo de entrega:** versión incremental de estabilización  
**Base:** paquete v0.6 aportado por el usuario  
**Datos:** 100 % sintéticos  
**Uso clínico:** no habilitado  
**Inferencia del modelo real:** no conectada

## Resultado ejecutivo

La suite ejecutada en esta construcción terminó con **18/18 pruebas aprobadas**. La generación reproducible con 500 pacientes y semilla `20261105` produjo 4.293 mediciones, 500 landmarks, 347 horizontes evaluables, 153 no evaluables y 58 eventos sintéticos evaluables. Los controles técnicos de calidad fueron 14/14.

Este resultado valida los comportamientos cubiertos por las pruebas; no constituye validación clínica, validación externa del modelo ni prueba de utilidad asistencial.

## Auditoría 1 — Funcional y arquitectónica

**Comprobaciones**
- Compilación de módulos Python.
- Generación sintética reproducible.
- Selección de un landmark por paciente.
- Alineación exacta del contrato de 28 predictores.
- Rechazo de predictores faltantes.
- Verificación de que el loader joblib falla de forma cerrada por defecto.

**Resultado:** aprobada para el alcance probado.

## Auditoría 2 — Científica y metodológica

**Casos adversariales cubiertos**
- Confirmación exactamente a 30 días: aceptada.
- Confirmación a 29 días: rechazada.
- Una sola medición futura: no evaluable.
- Cruce sin confirmación: no se clasifica como evento confirmado.
- Ausencia de cruce: evaluable sin evento.
- Día 365: incluido; día 366: excluido.
- Dos registros el mismo día: no satisfacen la separación de 30 días.

**Resultado:** las reglas temporales implementadas pasan estos casos de prueba. No se evalúan aquí sesgos epidemiológicos, validez clínica ni transportabilidad.

## Auditoría 3 — Seguridad e integridad

**Comprobaciones**
- No se incluyen archivos `.joblib`, `.pkl` ni `.pickle`.
- No se incluyen datasets clínicos reales en el paquete.
- Los identificadores del conjunto de demostración usan prefijo `SYN-`.
- La carga joblib está bloqueada por defecto y exige habilitación explícita.
- Se excluyeron bytecode y cachés del paquete de distribución.

**Resultado:** aprobada para el paquete y controles inspeccionados. No equivale a una auditoría profesional de ciberseguridad ni a un análisis completo de dependencias.

## Auditoría 4 — Integral y de regresión

**Comprobaciones**
- Suite completa de pruebas.
- Reconstrucción del conjunto sintético con semilla fija.
- Reconciliación de conteos de pacientes, mediciones, landmarks, evaluabilidad y eventos.
- Actualización de metadatos de versión a v0.7.
- Limpieza de archivos temporales.

**Resultado:** aprobada para la construcción entregada.

## Hallazgos pendientes / límites explícitos

1. El dashboard presenta métricas históricas del artículo como referencias documentales; no las genera la demo.
2. El artefacto predictivo real no está incluido ni conectado.
3. La auditoría no reproduce independientemente todo el pipeline de investigación PALIC-PY-10 ni resuelve la discrepancia temporal previamente observada en el paquete de investigación original.
4. La interfaz debe revisarse con la traducción automática del navegador desactivada antes de grabar el video.
5. Antes de una liberación pública, realizar revisión adicional de dependencias, licencias, documentación y privacidad.

## Decisión de versión

**v0.7 — Aprobada como build incremental de estabilización del prototipo demostrativo**, con los límites anteriores. No se declara como versión final PALIC ni como sistema clínico validado.
