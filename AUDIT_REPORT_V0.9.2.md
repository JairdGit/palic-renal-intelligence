# PALIC Renal Intelligence — Informe de auditoría v0.9.2

**Release:** v0.9.2  
**Tipo:** contrato de presentación del dashboard, conciliación de indicadores y endurecimiento de exportaciones  
**Datos:** exclusivamente sintéticos  
**Modelo predictivo conectado:** no  
**Uso clínico:** no

## 1. Alcance del incremento

La v0.9.2 separa cálculos de presentación en `src/dashboard/presentation.py`, un módulo puro sin dependencia de Streamlit. `app.py` consume estas funciones para los indicadores del resumen, distribución de escenarios, resumen de intervalos de medición y descargas de auditoría.

Cambios principales:
- `build_summary`: calcula KPIs a partir de las tablas fuente y exige conciliación entre pacientes, landmarks, evaluabilidad, eventos y no-eventos evaluables.
- Valida que `evaluable_365` sea estrictamente binario y que los objetivos de los no evaluables permanezcan nulos.
- `build_scenario_counts`: produce una distribución de escenarios cuya suma debe coincidir con el total de pacientes; representa escenarios faltantes explícitamente.
- `build_frequency_summary`: calcula intervalos por paciente después de validar fechas; no modifica los datos fuente.
- `safe_export_filename`: restringe nombres de archivos descargables para impedir componentes de ruta y caracteres no permitidos.
- `json_bytes`: serializa JSON UTF-8 y rechaza NaN/Infinity.
- `run_demo.py` identifica el generador como `v0.9.2`.

## 2. Auditoría 1 — funcional y arquitectónica

**Resultado: aprobada en el alcance automatizado.**

Evidencia:
- Funciones de presentación aisladas de Streamlit, comprobables con pruebas unitarias.
- `app.py` utiliza los helpers para KPIs, escenarios, frecuencias y exportaciones.
- Pruebas de conciliación de resumen, columnas ausentes, escenarios faltantes, fechas inválidas y navegación de seis secciones.
- `py_compile` aprobó `app.py`, `run_demo.py`, `check_environment.py` y el nuevo módulo.

**Límite:** no fue posible ejecutar Streamlit en este entorno porque el paquete `streamlit` no está instalado y no hubo acceso de red para instalarlo. No se declara aprobada la prueba visual, interactiva ni de navegador.

## 3. Auditoría 2 — científica y metodológica

**Resultado: aprobada para los cálculos de presentación; sin cambios en metodología del desenlace.**

Evidencia:
- La conciliación separa evaluables, no evaluables, eventos evaluables y no-eventos evaluables.
- Los pacientes no evaluables deben conservar `target_sustained_40` nulo.
- La bandera `evaluable_365` solo admite 0/1.
- Los helpers no generan riesgo individual, no entrenan modelos y no cambian el contrato de 28 predictores.
- La frecuencia de medición se presenta como estadística descriptiva sintética, no como sensibilidad clínica ni evidencia epidemiológica.

Resultados regenerados con semilla `20261105`: 500 pacientes, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables, 58 eventos brutos; conciliación de evaluables: 58 eventos + 289 no-eventos = 347.

## 4. Auditoría 3 — seguridad e integridad

**Resultado: aprobada en el alcance de los helpers y las pruebas ejecutadas.**

Evidencia:
- Los nombres de exportación se normalizan mediante lista permitida; se rechazan nombres vacíos después de la normalización.
- La serialización JSON usa `allow_nan=False` y convierte errores de serialización en excepción controlada.
- Los datos fuente no se reescriben ni normalizan de forma silenciosa.
- El manifiesto SHA-256 se reconstruyó después de incorporar los cambios.

**Límite:** los hashes detectan cambios respecto al manifiesto, pero no equivalen a una firma digital ni protegen contra la sustitución simultánea del paquete y su manifiesto.

## 5. Auditoría 4 — integrada adversarial y regresión

**Resultado: aprobada en las pruebas automatizadas.**

Casos adversariales nuevos: bandera evaluable no binaria, landmarks/pacientes desbalanceados, objetivo no nulo en paciente censurado, escenarios faltantes, fechas inválidas, rutas en nombres de archivo, nombre de exportación vacío y JSON con valores no finitos.

- Suite total: **131/131 pruebas aprobadas**.
- Pruebas nuevas v0.9.2: **12/12 aprobadas**.
- Compilación Python: aprobada.
- Regeneración sintética: aprobada.
- Perfil `core`: 2/2 dependencias aprobadas.
- Perfil `app`: 5/6 dependencias aprobadas; Streamlit ausente.
- Arranque `python app.py`: termina de forma segura con código 2 antes de importar/cargar datos al detectar Streamlit ausente.

## 6. Matriz de resultados

| Control | Resultado |
|---|---:|
| Pruebas automatizadas | 131/131 PASS |
| Calidad de datos | 27/27 PASS |
| Trazabilidad longitudinal | 10/10 PASS |
| Conciliación agregada | 12/12 PASS |
| Contrato de dashboard | 18/18 PASS |
| Perfil core | PASS |
| Perfil app | BLOCKED: Streamlit ausente |
| Prueba visual real | NO EJECUTADA |

## 7. Hallazgos abiertos y límites

1. La prueba visual real del dashboard queda pendiente hasta ejecutar el paquete en un entorno con las dependencias de `requirements-app.txt` instaladas.
2. No se ejecutó prueba de navegador ni prueba de usabilidad con usuarios.
3. No se realizó pentest externo, validación clínica ni validación externa del modelo.
4. El modelo predictivo permanece desconectado; las métricas históricas documentales no son resultados generados por esta demo.

No se registraron hallazgos críticos o altos abiertos dentro del alcance de las pruebas automatizadas de este incremento. Esto no debe interpretarse como certificación integral de seguridad o validez clínica.

## 8. Comandos de reproducción

```bash
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python -m py_compile app.py run_demo.py check_environment.py src/dashboard/presentation.py
python check_environment.py --profile app
streamlit run app.py
```

El último comando requiere instalar previamente `requirements-app.txt` en un entorno compatible.
