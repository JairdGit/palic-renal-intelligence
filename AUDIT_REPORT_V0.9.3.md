# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.3

**Alcance:** navegación coherente, selección de paciente, filtrado entre tablas y exportación CSV del dashboard.  
**Base:** paquete v0.9.2 recibido y verificado; línea base previa: 131/131 pruebas aprobadas.  
**Política de datos:** exclusivamente sintéticos. El modelo predictivo permanece desconectado.

## 1. Cambios examinados

- Nuevo `src/dashboard/interactions.py`, sin dependencia de Streamlit.
- Listado estable y validado de identificadores de pacientes.
- Resolución del mismo paciente en tablas maestras, renales, clínicas y landmarks.
- Rechazo de pacientes maestros duplicados y de filas clínicas/landmarks ambiguas.
- Orden cronológico de las mediciones seleccionadas y rechazo de fechas inválidas.
- Serialización CSV común en UTF-8 con BOM, sin índice y con rechazo de columnas duplicadas.
- Integración de los helpers en las secciones Trayectorias y Auditoría por paciente.
- Eliminación de una fila duplicada en la tabla de trazabilidad de la interfaz.

## 2. Cuatro auditorías adversariales

### Auditoría 1 — Funcional y arquitectónica

**Resultado: APROBADA en el alcance probado.** Los helpers de selección y filtrado son módulos puros, no importan Streamlit y se prueban de forma independiente. La aplicación utiliza el mismo mecanismo de resolución para ambas vistas por paciente. Las pruebas estructurales confirman la integración de los helpers.

### Auditoría 2 — Científica y metodológica

**Resultado: APROBADA.** No se modificaron el motor longitudinal, la definición del desenlace, la ventana de 365 días, la confirmación mínima de 30 días, la política de censura ni el contrato de 28 predictores. La vista individual presenta los registros fuente filtrados por el mismo identificador y ordena las mediciones por fecha. La regeneración conservó 500 pacientes, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos sintéticos brutos.

### Auditoría 3 — Seguridad e integridad

**Resultado: APROBADA en el alcance probado.** Se rechazan identificadores nulos/vacíos/duplicados, pacientes desconocidos, filas maestras ambiguas, múltiples landmarks, múltiples filas clínicas y fechas de medición inválidas. El CSV se genera sin índice y no permite nombres de columnas duplicados. No se agregan datos reales ni se habilita inferencia.

### Auditoría 4 — Integrada adversarial y regresión

**Resultado: APROBADA.** La suite completa ejecutó **146/146 pruebas aprobadas**, incluidas 15 pruebas nuevas para v0.9.3 y las suites históricas. La compilación de 43 archivos Python fue satisfactoria. La regeneración sintética terminó con 27/27 controles de calidad, 10/10 de trazabilidad y 12/12 de conciliación agregada.

## 3. Entorno y limitaciones

- Python 3.13.5: compatible con el rango declarado.
- Perfil `core`: PASS, 2/2 dependencias.
- Perfil `app`: BLOQUEADO, 5/6; Streamlit no está instalado.
- La ejecución de `app.py` termina de forma controlada antes de importar dependencias de interfaz o cargar datos.
- **La prueba visual/interactiva real del dashboard no se ejecutó.** Las pruebas de helpers y de estructura no se presentan como sustituto de una prueba visual en navegador.
- No se realizó pentest profesional, validación clínica, validación externa ni prueba de usabilidad con participantes.

## 4. Datos sintéticos regenerados

| Indicador | Resultado |
|---|---:|
| Pacientes | 500 |
| Mediciones renales | 4.293 |
| Landmarks | 500 |
| Evaluable a 365 días | 347 |
| No evaluable/censurado | 153 |
| Eventos sintéticos brutos | 58 |
| Calidad de datos | 27/27 |
| Trazabilidad | 10/10 |
| Conciliación agregada | 12/12 |

## 5. Dictamen

**v0.9.3 aprobada como incremento técnico de navegación, selección y exportación del prototipo sintético.** La liberación no acredita todavía la ejecución visual real del dashboard. Esa verificación continúa pendiente de un entorno con Streamlit instalado y compatible.
