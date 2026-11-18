# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.7

**Resultado:** APROBADO CON LIMITACIÓN DE ENTORNO.  
**Alcance:** recorrido guiado y reproducible por las seis secciones del dashboard. No equivale a auditoría profesional de ciberseguridad, validación clínica, validación externa ni evaluación de utilidad clínica.

## Cambio evaluado

Se incorpora `src/dashboard/demo_journey.py`, módulo independiente de Streamlit que define una ruta canónica de seis secciones, propósito, acción, mensaje de cautela y duración sugerida. La barra lateral ofrece una guía interactiva de 15 minutos. La validación de navegación detecta orden incorrecto, duplicados, secciones desconocidas y ausentes. El generador declara `v0.9.7`.

## Auditoría 1 — funcional y arquitectónica

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** 14 pruebas específicas cubren inventario y duración de la ruta, contenido de cada etapa, resolución de sección, entrada vacía/desconocida, orden, duplicados, secciones faltantes/desconocidas, tipo de entrada e integración de la guía en la aplicación.
- **Retest:** suite completa 194/194 PASS; compilación Python PASS.
- **Límite:** no se ejecutó una sesión visual de Streamlit en navegador.

## Auditoría 2 — científica y metodológica

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** el recorrido mantiene explícitos el carácter 100 % sintético de los registros, la naturaleza descriptiva de las trayectorias, la conservación de objetivo nulo para no evaluables y la desconexión del modelo predictivo. Las métricas históricas permanecen identificadas como documentales y no generadas por la demo.
- **Retest:** generación reproducible: 500 pacientes, 4.293 mediciones renales, 500 landmarks; 347 evaluables, 153 no evaluables y 58 eventos sintéticos. Calidad 27/27, trazabilidad 10/10 y conciliación agregada 12/12.
- **Límite:** no se reevalúa el estudio científico original ni se resuelve la discrepancia temporal documentada en su archivo de investigación.

## Auditoría 3 — seguridad e integridad

- **Resultado:** APROBADO CON LIMITACIÓN DE ALCANCE.
- **Evidencia:** el módulo de guía no carga archivos, no ejecuta código externo, no incorpora deserialización de modelos y solo acepta secciones de la ruta predefinida. Las entradas inválidas fallan de forma controlada. Datos sintéticos y modelo desconectado se conservan.
- **Retest:** pruebas específicas 14/14 PASS; compilación Python PASS; manifiesto SHA-256 y ZIP verificados en el empaquetado final.
- **Límite:** no se ejecutó pentest, análisis SAST/DAST especializado, revisión legal de licencias ni auditoría externa.

## Auditoría 4 — integrada, adversarial y regresión

- **Resultado:** APROBADO dentro del alcance probado.
- **Evidencia:** 194/194 pruebas de la suite completa; generador v0.9.7; datos regenerados con semilla 20261105; ruta guiada coherente con las seis secciones existentes.
- **Retest:** perfil `core` PASS 2/2. Perfil `app` bloqueado 5/6 por ausencia de Streamlit; el preflight impide afirmar que la interfaz se ejecutó. La prueba visual en navegador queda pendiente.

## Estado final y limitaciones

- Datos exclusivamente sintéticos; identificadores `SYN-`.
- Modelo predictivo real desconectado; no hay probabilidades individuales ni clasificación de riesgo.
- Las métricas históricas de investigación no son resultados de esta demo.
- No es dispositivo médico ni software para uso asistencial.
- La guía de 15 minutos es una pauta sugerida, no un cronómetro ni una prueba de que la presentación haya sido ejecutada.
- La versión se aprueba como incremento de experiencia de demostración y trazabilidad de recorrido, no como PALIC v1.0 ni como sistema clínico.

## Reproducción

```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```
