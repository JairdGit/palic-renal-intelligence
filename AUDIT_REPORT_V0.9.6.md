# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.6

**Resultado:** APROBADO CON LIMITACIÓN DE ENTORNO.  
**Alcance:** incremento de observabilidad operativa de la demo sintética. No equivale a auditoría profesional de ciberseguridad, validación clínica, validación externa ni evaluación de utilidad clínica.

## Cambio evaluado

Se incorpora `src/dashboard/diagnostics.py`, módulo independiente de Streamlit que comprueba siete artefactos requeridos y el resultado de la verificación SHA-256 del manifiesto. La sección «Calidad de datos» presenta disponibilidad, conteo de controles y detalle de fallos. El estado `OPERATIVO_DEMO` requiere todos los artefactos presentes/no vacíos y manifiesto íntegro; en cualquier otro caso el resultado es `BLOQUEADO`.

## Auditoría 1 — funcional y arquitectónica

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** 10 pruebas específicas verifican inventario, artefacto ausente, archivo vacío, manifiesto fallido/ausente, estados inválidos, tipo de entrada, alcance declarado y orden de controles.
- **Retest:** suite completa 180/180 PASS; compilación Python PASS.
- **Límite:** la ejecución del dashboard en navegador no se realizó en este entorno.

## Auditoría 2 — científica y metodológica

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** el diagnóstico se define como disponibilidad técnica e integridad de artefactos; el texto excluye expresamente inferencia, validez clínica y utilidad clínica. Datos permanecen 100 % sintéticos y el modelo predictivo real desconectado.
- **Retest:** generación reproducible: 500 pacientes, 4.293 mediciones renales, 500 landmarks; 347 evaluables, 153 no evaluables y 58 eventos sintéticos. Calidad 27/27, trazabilidad 10/10 y conciliación agregada 12/12.
- **Límite:** no se reevalúa el estudio científico original ni se resuelve la discrepancia temporal documentada en su archivo de investigación.

## Auditoría 3 — seguridad e integridad

- **Resultado:** APROBADO CON LIMITACIÓN DE ALCANCE.
- **Evidencia:** verificación SHA-256 del paquete, diagnóstico fail-closed cuando faltan artefactos o falla el manifiesto, sin deserialización de modelos ni activación de inferencia. Compilación Python PASS.
- **Retest:** los diez casos adversariales específicos pasan; el paquete final se somete a verificación de manifiesto y prueba ZIP.
- **Límite:** no se ejecutó pentest, análisis SAST/DAST especializado, revisión legal de licencias ni auditoría externa.

## Auditoría 4 — integrada, adversarial y regresión

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** 180/180 pruebas de la suite completa; generador v0.9.6; datos regenerados con semilla 20261105; manifestación de artefactos y resultados de entorno documentados.
- **Retest:** perfil `core` PASS 2/2. Perfil `app` bloqueado 5/6 por ausencia de Streamlit; el preflight impide afirmar que la interfaz se ejecutó. La prueba visual en navegador queda pendiente.

## Estado final y limitaciones

- Datos exclusivamente sintéticos; identificadores `SYN-`.
- Modelo predictivo real desconectado; no hay probabilidades individuales ni clasificación de riesgo.
- Las métricas históricas de investigación no son resultados de esta demo.
- No es dispositivo médico ni software para uso asistencial.
- La versión se aprueba como incremento de estabilización y observabilidad técnica de la demo, no como PALIC v1.0 ni como sistema clínico.

## Reproducción

```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```
