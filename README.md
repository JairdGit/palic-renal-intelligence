# PALIC Renal Intelligence — v1.0.0

La guía operativa de esta liberación está en [`README_V1.0.md`](README_V1.0.md). El historial de versiones se conserva debajo.

**Límites de uso:** datos exclusivamente sintéticos; modelo predictivo real no conectado; no es un dispositivo médico ni una herramienta diagnóstica. Las métricas históricas se identifican como referencias de investigación y no como desempeño de esta demo.

**Cierre adversarial:** diez auditorías documentadas en `TEN_ADVERSARIAL_AUDITS.md`. Consultar el dictamen y los bloqueos de interfaz y entregables en `AUDIT_REPORT_V1.0.0.md`.

---

# PALIC Renal Intelligence — historial de versiones

## v0.9.5 — procedencia de exportaciones y estados vacíos
- Se incorpora `src/dashboard/demo_exports.py` para exportaciones con metadatos de versión, clasificación sintética y límites de uso.
- Las descargas CSV incorporan una línea de comentario de procedencia antes del encabezado; consumidores CSV deben omitir líneas de comentario (`comment=#`) al importar.
- Las descargas JSON usan un sobre `metadata` + `data`, rechazan NaN/Infinity y declaran modelo desconectado y uso no clínico.
- Las vistas individuales muestran estados informativos cuando faltan mediciones o landmarks; no se generan gráficas vacías engañosas.
- Se mantienen los datos exclusivamente sintéticos y el modelo predictivo desconectado.

# PALIC Renal Intelligence — v0.9.4

## v0.9.4 — contrato de visualización longitudinal
- Se incorpora `src/dashboard/visualization.py`, módulo puro para preparar trayectorias, anotaciones de landmark y estados de observación sin importar Streamlit ni Plotly.
- Las trayectorias se ordenan cronológicamente, validan fechas/TFG finitas, rechazan duplicados por fecha y marcan explícitamente el carácter sintético.
- El landmark y la línea operacional del 60 % se muestran de forma diferenciada; la línea se describe como regla del desenlace, no como umbral diagnóstico.
- Los estados evaluable/censurado se validan y concilian antes de graficarse.
- Se conserva la política de datos sintéticos y el modelo predictivo desconectado.
- La prueba visual real requiere un entorno con Streamlit instalado; las pruebas puras no sustituyen la validación en navegador.

# PALIC Renal Intelligence — v0.9.3

## v0.9.3 — navegación coherente y vistas por paciente
- Se incorpora `src/dashboard/interactions.py`, módulo puro sin dependencia de Streamlit para resolver selección de pacientes y vistas consistentes entre tablas.
- Los selectores de Trayectorias y Auditoría por paciente utilizan identificadores únicos, ordenados y validados.
- Las cuatro tablas se filtran con el mismo identificador; se rechazan filas maestras, clínicas o landmarks ambiguos.
- Las mediciones individuales se ordenan cronológicamente y las fechas inválidas bloquean esa vista con un mensaje controlado.
- Las exportaciones CSV utilizan un serializador común UTF-8 con BOM y sin índice; se rechazan columnas duplicadas.
- Se eliminó una fila duplicada en la tabla de trazabilidad del dashboard.
- La suite completa de pruebas y los cuatro controles adversariales se documentan en `AUDIT_REPORT_V0.9.3.md`.
- La ejecución visual real sigue pendiente mientras Streamlit no esté disponible en el entorno de auditoría.

### Instalación y ejecución
```bash
pip install -r requirements-app.txt
python check_environment.py --profile app
streamlit run app.py

python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

Informe: `AUDIT_REPORT_V0.9.3.md`.

---

# PALIC Renal Intelligence — v0.9.2

## v0.9.2 — contrato de presentación y conciliación del dashboard
- Se incorpora `src/dashboard/presentation.py`, módulo puro sin dependencia de Streamlit para cálculos y validaciones de presentación.
- Los KPIs se derivan de las tablas fuente y concilian pacientes, landmarks, evaluabilidad, eventos y no-eventos evaluables.
- La bandera `evaluable_365` se valida como binaria; los pacientes no evaluables deben conservar objetivo nulo.
- Se centralizan la distribución de escenarios y el resumen descriptivo de intervalos de medición.
- Se endurecen las descargas: nombres de archivo con lista permitida y JSON UTF-8 que rechaza NaN/Infinity.
- `run_demo.py` identifica la versión del generador como v0.9.2.
- Suite completa: 131/131 pruebas aprobadas; datos sintéticos: 500 pacientes, 4.293 mediciones y 500 landmarks.
- La prueba visual real sigue pendiente: el entorno de auditoría no tiene Streamlit instalado; el preflight bloquea el arranque antes de cargar datos.

### Instalación y ejecución
```bash
pip install -r requirements-app.txt
python check_environment.py --profile app
streamlit run app.py

python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

Informe: `AUDIT_REPORT_V0.9.2.md`.

---

# PALIC Renal Intelligence — v0.9.1

## v0.9.1 — separación de dependencias de interfaz y modelado
- Se separan las dependencias del dashboard en `requirements-app.txt` de las dependencias opcionales de investigación/modelado en `requirements-model.txt`.
- El dashboard no requiere instalar scikit-learn para visualizar datos sintéticos: no ejecuta el modelo ni importa scikit-learn.
- `check_environment.py` admite perfiles `core`, `app` y `model`; cada perfil comprueba su archivo de requisitos correspondiente sin instalar paquetes ni acceder a internet.
- Se mantiene `scikit-learn==1.9.0` y `joblib==1.5.3` en el perfil de modelado; no se relajan sus versiones ni se habilita inferencia.
- `run_demo.py` identifica el generador como v0.9.1.
- La prueba de interfaz real sigue pendiente cuando Streamlit no está disponible en el entorno de auditoría; las pruebas estructurales no se presentan como validación visual.

### Instalación reproducible por perfil
```bash
# Dashboard de datos sintéticos
pip install -r requirements-app.txt
python check_environment.py --profile app
streamlit run app.py

# Generación de datos (sin interfaz)
pip install -r requirements.txt
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated

# Dependencias de investigación/modelado (solo cuando corresponda)
pip install -r requirements-model.txt
python check_environment.py --profile model
```

---

# PALIC Renal Intelligence — v0.9.1

## v0.8.9 — Preflight antes de importar la interfaz
- Se corrigió el orden de arranque de `app.py`: el perfil `app` se verifica antes de importar Streamlit, Plotly, pandas y NumPy.
- Si el entorno es incompatible, el proceso informa el diagnóstico en `stderr` y termina con código 2, sin depender de que Streamlit esté instalado.
- Se añadieron siete pruebas adversariales para perfiles, restricciones de dependencias, orden de inicialización y metadatos de liberación.
- Se conserva la comprobación offline: no instala ni actualiza paquetes y no accede a internet.
- En el entorno de auditoría, `core` pasó y `app` se bloqueó correctamente por `scikit-learn` 1.8.0 frente al pin 1.9.0 y por ausencia de Streamlit. El dashboard visual no se declara ejecutado.

### Verificación
```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
streamlit run app.py
```

---

# PALIC Renal Intelligence — v0.8.8

## v0.8.8 — Preflight de entorno y reproducibilidad de ejecución
- Se incorpora `src/environment/check.py` y el comando `check_environment.py` para verificar la versión de Python y las restricciones declaradas en `requirements.txt` sin instalar paquetes ni acceder a internet.
- Se definen perfiles `core` (pandas y numpy, necesarios para generar la demo) y `app` (todas las dependencias declaradas para la interfaz).
- `run_demo.py` detiene la ejecución antes de modificar salidas si el entorno del perfil core es incompatible.
- `app.py` comprueba el perfil app y detiene la carga de datos si faltan dependencias o sus versiones no cumplen los rangos.
- Se documenta soporte Python `>=3.10,<3.14`, se declara `packaging` y se añaden pruebas para versiones incompatibles, dependencias ausentes, especificaciones inválidas y perfiles.
- La comprobación es offline y no instala ni actualiza dependencias automáticamente.
- En el entorno de auditoría, el perfil core pasó; el perfil app detectó correctamente `scikit-learn 1.8.0` frente al requisito `1.9.0` y la ausencia de Streamlit. Por ello, la interfaz Streamlit no se declaró ejecutada ni validada visualmente en este entorno.

### Verificación del entorno
```bash
python -m pip install -r requirements.txt
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
streamlit run app.py
```

---

# PALIC Renal Intelligence — Prototype

## Release v0.8.6

Incremento dedicado a la conciliación entre registros individuales y resultados agregados. Incorpora `src/longitudinal_engine/aggregate_audit.py`, añade 12 controles de conciliación a `longitudinal_audit.json` y expone su resultado en el dashboard.

- Suite completa: 73/73 pruebas aprobadas.
- Calidad de datos: 27/27 controles.
- Trazabilidad de landmarks: 10/10 controles.
- Conciliación agregada: 12/12 controles.
- Datos exclusivamente sintéticos; modelo predictivo real desconectado.
- No es un dispositivo médico ni está destinado a uso clínico.

Ejecutar: `python run_demo.py --patients 500 --seed 20261105 --out data/generated`
Pruebas: `python -m unittest discover -s tests -v`
Informe: `AUDIT_REPORT_V0.8.6.md`.

---


Primera entrega: generador de datos sintéticos y módulo de control de calidad.

## Alcance
- Genera pacientes, mediciones renales y variables clínicas completamente sintéticas.
- Produce trayectorias estables, descendentes y variables, además de datos incompletos para probar controles.
- Ejecuta controles de estructura, tipos, duplicados, rangos configurables, cronología y faltantes.
- Exporta CSV y un informe JSON de calidad.

**No contiene ni utiliza datos clínicos reales.** No reproduce las métricas del artículo 2 ni entrena un modelo predictivo. Es una base de demostración independiente.

## Instalación
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Generar datos y auditar
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
```

Salidas:
- `patients_synthetic.csv`
- `renal_measurements_synthetic.csv`
- `clinical_variables_synthetic.csv`
- `quality_report.json`

## Principios
1. Los identificadores `SYN-...` son artificiales.
2. La etiqueta `scenario` sirve para pruebas de interfaz, no es un diagnóstico.
3. Los umbrales de calidad son controles técnicos de demostración, no criterios clínicos.
4. Las mediciones sintéticas no deben combinarse con predicciones o métricas publicadas como si fueran una validación.
5. El motor del artículo PALIC-PY-10 se mantiene separado y sin modificaciones.

## Estructura
- `src/synthetic_data/generator.py`: generación reproducible.
- `src/data_quality/validation.py`: controles y reporte.
- `run_demo.py`: ejecución completa.
- `tests/`: pruebas básicas.


## v0.3 — Model Integration Layer
- Importa el contrato original de predictores efectivos.
- Fija y valida el orden de las 28 variables del modelo principal `RandomForest_full_clinical`.
- Comprueba el número de variables esperado por el artefacto.
- Proporciona una función de inferencia por probabilidades.
- La carga joblib permanece bloqueada por defecto porque los artefactos pickle/joblib pueden ejecutar código al deserializarse.
- No se incluye el modelo serializado ni datos clínicos en este paquete.
- No se generan predicciones ficticias ni se atribuyen métricas del artículo a los datos sintéticos.

Ejecutar comprobación del contrato:
```bash
python run_model_contract_check.py
```

Ejecutar pruebas:
```bash
python -m unittest discover -s tests
```

Para habilitar la carga del modelo real se requiere verificar su SHA-256, procedencia y compatibilidad de entorno, y ejecutarlo en un entorno aislado. La versión registrada del estudio fue Python 3.13.13 y scikit-learn 1.9.0.


## Dashboard local v0.4

### Ejecutar
1. Crear y activar un entorno virtual de Python.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Iniciar el dashboard: `streamlit run app.py`.

El dashboard utiliza exclusivamente los CSV sintéticos incluidos en `data/generated/`.
La sección **Inteligencia de riesgo** no ejecuta inferencia: el artefacto predictivo real
no está conectado ni incluido. Las métricas del artículo aparecen únicamente como
referencia documental de evaluación temporal interna, no como resultados de la demo.

### Límites de esta versión
- No es un sistema clínico ni un dispositivo médico.
- No realiza diagnóstico, recomendación terapéutica ni priorización clínica real.
- No carga archivos serializados de modelos.
- No incluye datos identificables ni datos clínicos reales.
- La integración del modelo queda pendiente de verificación independiente y pruebas.


## v0.5 — Exploración longitudinal y observabilidad ampliada

- Indicadores descriptivos por paciente: cambio absoluto/porcentual, pendiente anual descriptiva, intervalos y variabilidad de TFG.
- Landmark marcado en la gráfica para separar historia previa y horizonte futuro.
- Controles técnicos ampliados y nombres explícitos para conteos de duplicados.
- Auditoría longitudinal visible desde el dashboard.
- Generador sintético actualizado para reducir mesetas artificiales por límites rígidos; sigue siendo una simulación, no historia natural.
- Se preservan el contrato de 28 predictores y las barreras de seguridad: el modelo real no se carga ni se ejecuta.
- La definición de desenlace y la regla de censura permanecen sin cambios.

Ejecutar:
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
streamlit run app.py
python -m unittest discover -s tests
```


## v0.6 — Explicabilidad del desenlace y auditoría por paciente

- Nueva sección **Auditoría por paciente** que explica landmark, umbral del 60 %, cruce, confirmación e intervalo entre mediciones.
- Estados diferenciados: evento confirmado, cruce no confirmado, sin cruce y horizonte no evaluable.
- Visualización de las observaciones futuras frente al umbral.
- Exportación de la auditoría individual en CSV y JSON.
- Panel descriptivo de intervalos de medición por escenario sintético.
- La frecuencia de medición se describe; no se presenta como análisis formal de sensibilidad.
- Se mantienen sin cambios la definición del desenlace, el horizonte de 365 días, la confirmación de al menos 30 días y la regla de censura.
- El modelo predictivo real sigue desconectado y no se calculan probabilidades individuales.

Ejecutar pruebas y dashboard:
```bash
python -m unittest discover -s tests -v
streamlit run app.py
```


## v0.7 — Estabilización y primera ronda adversarial

Esta versión parte del paquete v0.6 recibido y conserva el alcance demostrativo con datos 100 % sintéticos.

### Cambios
- Actualización de la etiqueta de compilación a v0.7.
- Actualización de `generator_version` en las nuevas ejecuciones.
- Limpieza de cachés y bytecode del paquete de distribución.
- Pruebas adversariales explícitas del desenlace: confirmación a 30 días, 29 días, cruce no confirmado, ausencia de cruce, una sola observación futura, límite de 365 días y duplicados en el mismo día.

### Cuatro auditorías adversariales de v0.7
1. **Funcional y arquitectónica:** pruebas del motor, navegación y contrato de integración.
2. **Científica y metodológica:** límites del horizonte, censura, cruce y confirmación temporal.
3. **Seguridad e integridad:** no se incluyen datos clínicos reales ni artefactos joblib; la carga del modelo permanece deshabilitada por defecto.
4. **Integral y de regresión:** reconstrucción de salidas, consistencia de conteos, compilación y suite completa.

### Límites
- El modelo predictivo real no está conectado ni ejecutado.
- Las métricas históricas del artículo no son resultados de esta demo.
- Los datos y escenarios son sintéticos y no representan prevalencia ni historia natural.
- Esta versión no tiene validación clínica externa.

### Ejecutar
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
streamlit run app.py
```

## v0.8 — Controles adicionales
- El reporte de calidad distingue los faltantes admisibles de TFG de los valores inválidos.
- El verificador SHA-256 solo compara archivos declarados; no ejecuta ni deserializa artefactos.
- La tabla de trazabilidad obtiene la versión desde el manifiesto de release.
- Las pruebas adversariales v0.8 cubren referencias huérfanas, duplicación de filas clínicas, creatinina inválida, identificadores no sintéticos y manipulación de archivos.



## v0.8.1 — Endurecimiento del verificador de integridad
- El verificador rechaza manifiestos cuya raíz no sea un objeto JSON y claves JSON duplicadas.
- Valida formato SHA-256, rutas relativas POSIX y bloquea rutas absolutas, traversal y escapes por resolución de rutas.
- Los errores de lectura se manejan de forma cerrada sin interrumpir la aplicación.
- Se agregan pruebas adversariales específicas del manifiesto.
- No se modifica el motor longitudinal, el contrato de predictores ni los datos sintéticos.


## v0.8.2 — Contrato de secuencia longitudinal
- Se amplía la validación técnica de mediciones longitudinales para detectar secuencias duplicadas por paciente.
- Se comprueba que la secuencia respete el orden cronológico y que sea entera, positiva y consecutiva desde 1.
- Se agregan pruebas adversariales para duplicación, inversión temporal, saltos, valores fraccionarios y negativos.
- El generador registra `generator_version` v0.8.2 en la auditoría longitudinal.
- No se modifica la definición científica del desenlace, la selección de landmarks, el horizonte de 365 días ni la censura.
- Los controles son de integridad estructural de datos sintéticos; no son reglas clínicas.

Ejecutar:
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
streamlit run app.py
```


## v0.8.3 — Integridad temporal de mediciones
- Normaliza fechas con zona horaria explícita para realizar validaciones reproducibles ante entradas con offsets mixtos.
- Detecta duplicados por paciente y día calendario, incluso si las marcas horarias difieren.
- Detecta valores numéricos no finitos en campos de edad, IMC, secuencia, TFG y creatinina.
- Añade una comprobación de fechas posteriores a una fecha de referencia solo cuando el operador la proporciona explícitamente; no infiere una fecha de corte ni usa la fecha actual como sustituto.
- Añade pruebas adversariales para fechas inválidas, offsets mixtos, duplicados intradía, valores infinitos, orden temporal y fecha de referencia.
- No altera el motor longitudinal, la definición del desenlace, el horizonte de 365 días, la censura ni el contrato de 28 predictores.


## v0.8.4 — Integridad relacional e identidad longitudinal
- Se amplían los controles de integridad referencial entre el maestro de pacientes, las mediciones renales y las variables clínicas.
- Se detectan claves foráneas nulas, vacías, huérfanas o inconsistentes.
- Se comprueba la cobertura esperada del conjunto sintético: al menos una medición renal y exactamente una fila clínica por paciente.
- Se detectan identificadores con espacios externos y colisiones después de normalización sin modificar los valores originales.
- Se agregan pruebas adversariales para eliminación, sustitución, nulidad, espacios y colisiones de identidad.
- No se modifica el motor longitudinal, el desenlace, el horizonte de 365 días, la censura ni el contrato de 28 predictores.
- Estas expectativas de cobertura corresponden al generador sintético de demostración; no deben imponerse automáticamente a cohortes clínicas reales sin un contrato de datos específico.

Ejecutar:
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

## v0.8.5 — Trazabilidad de landmarks y resultados longitudinales
- Se incorpora `src/longitudinal_engine/traceability.py` para contrastar los landmarks generados con los registros renales de origen.
- Se verifican unicidad y cobertura de pacientes, existencia del registro índice (fecha y TFG), conteo de observaciones futuras, última fecha observada y consistencia de evaluabilidad/estado.
- Se audita la trazabilidad de eventos: fechas de cruce y confirmación deben corresponder a mediciones fuente, respetar el intervalo mínimo de 30 días y permanecer dentro del horizonte de 365 días.
- Se comprueba la política de censura: los no evaluables mantienen el desenlace como valor faltante; los evaluables conservan concordancia entre el indicador bruto y el desenlace.
- `run_demo.py` incorpora el informe de trazabilidad al `longitudinal_audit.json` y registra `generator_version` como `v0.8.5`.
- La validación es una comprobación técnica del conjunto sintético y no representa validación clínica ni externa. No modifica la definición científica del desenlace ni conecta el modelo predictivo.

Ejecución reproducible:
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

## v0.8.7 — Ejecución resiliente y lectura segura de artefactos
- Se incorpora `src/io_safety/safe_io.py` para lectura fail-closed de CSV/JSON: verifica existencia, tamaño, columnas obligatorias, fechas, estructura JSON, claves duplicadas y constantes no finitas.
- `run_demo.py` genera todos los artefactos en un directorio temporal, ejecuta controles de lectura posterior y publica el conjunto completo mediante sustitución transaccional del directorio de salida.
- Si la generación, validación o promoción falla, no se presenta un conjunto parcial como válido; ante fallo de promoción se restaura el directorio anterior.
- La aplicación detiene la carga con un mensaje explícito cuando faltan archivos o están vacíos, dañados o tienen estructura incompatible; no continúa con resultados parciales.
- Se añadieron pruebas adversariales para CSV ausente/vacío/malformado, columnas faltantes, fechas inválidas, JSON con claves duplicadas, raíz incorrecta, NaN y rollback transaccional.
- No se modifica el motor científico, la definición del desenlace, el horizonte de 365 días, la censura ni el contrato de 28 predictores. El modelo predictivo sigue desconectado.

Ejecución reproducible:
```bash
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

## v0.9 — Integración del contrato de datos del dashboard
- Se incorpora `src/dashboard/validation.py` como puerta de integridad previa a la visualización.
- La aplicación carga también la tabla sintética de variables clínicas y verifica identidades entre pacientes, mediciones, variables clínicas y landmarks.
- Se comprueba unicidad de pacientes y landmarks, identificadores `SYN-`, ausencia de pacientes huérfanos, cobertura relacional, indicadores binarios y objetivos nulos para pacientes no evaluables.
- Si falla el manifiesto SHA-256 o el contrato de datos del dashboard, la aplicación detiene la visualización y no presenta resultados parciales.
- La sección de calidad muestra los controles del contrato de visualización.
- Se agregan pruebas adversariales de identidades sustituidas, registros huérfanos, duplicados, columnas faltantes, objetivos no binarios y violaciones de la política de censura.
- Se mantiene el modelo predictivo desconectado, el conjunto 100 % sintético, la definición del desenlace, el horizonte de 365 días, la confirmación mínima de 30 días y el contrato de 28 predictores.
- El perfil `core` puede generar y auditar los datos sin dependencias de interfaz. El arranque visual de Streamlit requiere satisfacer el perfil `app`; en el entorno de auditoría disponible Streamlit no está instalado y scikit-learn no cumple la versión fijada, por lo que no se declara una prueba visual completada.

Ejecución y comprobación:
```bash
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python check_environment.py --profile app
streamlit run app.py
```

# PALIC Renal Intelligence — v0.9.6

## v0.9.6 — observabilidad operativa y disponibilidad de artefactos
- Se incorpora `src/dashboard/diagnostics.py`, módulo puro que verifica la presencia y contenido no vacío de los siete artefactos requeridos por la demo y el resultado de integridad SHA-256.
- La sección **Calidad de datos** incorpora un panel de disponibilidad operativa con estado, conteo de controles y detalle de fallos.
- La disponibilidad se declara `OPERATIVO_DEMO` únicamente si todos los artefactos existen y el manifiesto pasa la verificación; cualquier ausencia, archivo vacío o fallo de integridad produce `BLOQUEADO`.
- El diagnóstico se limita a disponibilidad de artefactos e integridad del paquete. No certifica ciberseguridad, validez clínica, utilidad clínica ni inferencia predictiva.
- Se conserva el uso exclusivo de datos sintéticos y el modelo predictivo real desconectado.

### Verificación v0.9.6
```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

Informe: `AUDIT_REPORT_V0.9.6.md`.

# PALIC Renal Intelligence — v0.9.7

## v0.9.7 — recorrido guiado y demostración reproducible
- Se incorpora `src/dashboard/demo_journey.py`, módulo independiente de Streamlit con una ruta canónica de seis secciones, propósito, acción, mensaje de cautela y duración sugerida.
- La barra lateral incorpora una guía interactiva de 15 minutos que permite consultar la pauta de cada sección y visualizar el orden recomendado.
- Se agrega validación fail-closed del orden de navegación, duplicados, secciones desconocidas y secciones ausentes.
- La guía mantiene explícitos el carácter exclusivamente sintético de los datos y la desconexión del modelo predictivo real.
- No se modifican la definición del desenlace, los datos sintéticos, los predictores ni las métricas históricas.

### Recorrido recomendado
1. **Resumen (2 min):** tamaño y composición del conjunto sintético.
2. **Trayectorias (3 min):** serie temporal de TFG y landmark.
3. **Auditoría por paciente (3 min):** evaluabilidad y regla computacional del desenlace.
4. **Inteligencia de riesgo (2 min):** contrato documental, métricas históricas y modelo desconectado.
5. **Calidad de datos (3 min):** calidad, conciliación y disponibilidad operativa.
6. **Trazabilidad (2 min):** configuración, reglas y límites.

### Verificación v0.9.7
```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
```

Informe: `AUDIT_REPORT_V0.9.7.md`.

# PALIC Renal Intelligence — v0.9.8

## v0.9.8 — contrato de aceptación y preparación reproducible de demostración
- Se incorpora `src/dashboard/demo_acceptance.py`, módulo independiente de Streamlit que consolida seis controles de preparación: integridad SHA-256, disponibilidad de artefactos, contrato de datos, recorrido de seis secciones en 15 minutos, declaraciones de seguridad/alcance y exportaciones con procedencia.
- La barra lateral incorpora la lista de aceptación para una demostración pública, con estado `READY_FOR_GUIDED_DEMO` o `NOT_READY` y detalle de cada control.
- Se incorpora `run_demo_acceptance.py` para ejecutar el mismo contrato desde terminal, sin iniciar Streamlit ni depender de un navegador.
- La lista de aceptación no sustituye pruebas visuales, pruebas de navegador, validación clínica ni validación externa. Informa explícitamente que esas dimensiones no son evaluadas por este contrato.
- Se mantiene el uso exclusivo de datos sintéticos, el modelo predictivo desconectado, el horizonte de 365 días, la regla de confirmación mínima de 30 días y el contrato documental de 28 predictores.

### Verificación v0.9.8
```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python run_demo_acceptance.py
```

Informe: `AUDIT_REPORT_V0.9.8.md`.

# PALIC Renal Intelligence — v0.9.9

## v0.9.9 — consolidación de empaquetado y puerta de preparación para revisión final
- Se incorpora `src/release/readiness.py` y `run_release_readiness.py` para verificar estáticamente cinco dimensiones: archivos esenciales, historial de auditorías, perfiles de dependencias, instrucciones operativas y limpieza del paquete.
- El resultado `READY_FOR_FINAL_REVIEW` indica que los controles estáticos de documentación y empaquetado pasaron; no equivale a aprobación de v1.0 ni sustituye ejecución visual, pruebas de navegador, pentest o validación clínica.
- Se actualiza el generador sintético a v0.9.9 sin modificar reglas del desenlace, horizonte de 365 días, confirmación mínima de 30 días, censura ni contrato documental de 28 predictores.
- Se preservan los datos sintéticos y el modelo predictivo desconectado (predictive model disconnected).

### Verificación v0.9.9
```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python run_demo_acceptance.py
python run_release_readiness.py
```

Informe: `AUDIT_REPORT_V0.9.9.md`.
