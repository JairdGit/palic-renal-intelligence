# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.8

**Versión:** 0.9.8  
**Base:** v0.9.7  
**Alcance:** contrato reproducible de aceptación para la demostración sintética y su integración en la barra lateral.

## Resumen ejecutivo

La versión incorpora `src/dashboard/demo_acceptance.py` y `run_demo_acceptance.py`. El contrato reúne seis controles: integridad SHA-256, disponibilidad de artefactos, contrato de datos del dashboard, recorrido canónico de seis secciones en 15 minutos, declaraciones explícitas de alcance/seguridad y disponibilidad de exportaciones con procedencia. La barra lateral muestra el resultado y la terminal permite ejecutar el mismo control sin iniciar Streamlit.

**Resultado de pruebas unitarias:** 208/208 aprobadas. **Pruebas nuevas v0.9.8:** 14/14 aprobadas. **Aceptación de demo:** 6/6 aprobada tras generar el manifiesto de release.

## Auditoría 1 — funcional y arquitectónica

- Verificado que el módulo de aceptación es independiente de Streamlit.
- Verificado que el mismo contrato se puede ejecutar desde CLI y presentar en la barra lateral.
- Verificado que un fallo de integridad, disponibilidad, contrato de datos, recorrido, declaraciones o exportaciones impide el estado `READY_FOR_GUIDED_DEMO`.
- Verificado que rutas no canónicas y duración distinta de 15 minutos bloquean la aceptación.
- **Resultado:** aprobado dentro del alcance de pruebas automatizadas.

## Auditoría 2 — científica y metodológica

- Se conserva el conjunto exclusivamente sintético y la regla longitudinal existente.
- Se preserva la política de censura: no evaluables no se reinterpretan como ausencia de evento.
- El checklist no transforma métricas históricas en resultados de la demo ni genera inferencias individuales.
- El contrato declara expresamente que no evalúa validación clínica ni conexión del modelo.
- **Resultado:** aprobado; sin cambios a la definición del desenlace, horizonte, predictores o métricas históricas.

## Auditoría 3 — seguridad e integridad

- Se usa el verificador SHA-256 existente; el checklist no ejecuta ni deserializa modelos.
- Se conserva la lectura segura y la validación cruzada de los artefactos antes de la aceptación.
- La aceptación falla de forma cerrada cuando un control requerido no pasa.
- Las exportaciones se verifican por presencia de las funciones de procedencia; no se afirma una auditoría de seguridad externa.
- **Resultado:** aprobado dentro del alcance técnico. No equivale a pentest, certificación de ciberseguridad ni evaluación independiente.

## Auditoría 4 — integrada y regresión

- Suite completa: **208/208 PASS**.
- Pruebas nuevas: **14/14 PASS**.
- Compilación de módulos Python: PASS.
- Perfil `core`: **2/2 PASS**.
- Regeneración sintética: 500 pacientes, 4.293 mediciones, 500 landmarks; calidad 27/27, trazabilidad 10/10 y conciliación 12/12.
- Aceptación reproducible: **6/6 PASS**.
- Integridad del manifiesto y ZIP: verificados al empaquetar.
- **Resultado:** aprobado dentro del alcance automatizado.

## Estado de entorno y limitaciones

El perfil `app` obtuvo **5/6** porque Streamlit no está instalado en el entorno disponible. Se intentó instalar la dependencia, pero el entorno no pudo resolver el índice de paquetes por falta de conectividad. Por tanto:

- La aplicación no se ejecutó en navegador durante esta auditoría.
- No se declara prueba visual ni prueba real de interacción de widgets.
- La aceptación `READY_FOR_GUIDED_DEMO` se limita al contrato reproducible de artefactos, datos, recorrido y declaraciones; no reemplaza la validación visual pendiente.

El perfil `core` y las pruebas no requieren Streamlit. El modelo predictivo real permanece desconectado y el paquete no contiene un artefacto de inferencia activado.

## Datos de demostración

| Indicador | Resultado |
|---|---:|
| Pacientes sintéticos | 500 |
| Mediciones renales | 4.293 |
| Landmarks | 500 |
| Evaluables a 365 días | 347 |
| No evaluables | 153 |
| Eventos sintéticos | 58 |
| Calidad | 27/27 |
| Trazabilidad | 10/10 |
| Conciliación agregada | 12/12 |

## Dictamen

**v0.9.8 aprobada como incremento técnico de preparación reproducible de demostración.** No se aprueba como validación visual del dashboard, producto clínico, dispositivo médico, modelo predictivo conectado ni validación externa del estudio.

## Reproducción

```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python run_demo_acceptance.py
```
