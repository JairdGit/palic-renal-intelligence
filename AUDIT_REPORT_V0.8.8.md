# Informe de auditoría adversarial — PALIC Renal Intelligence v0.8.8

## Alcance
Incremento centrado en la verificación previa del entorno de ejecución y la documentación de compatibilidad. Se conserva el motor longitudinal, el generador sintético, el contrato de 28 predictores y la política de no conectar el modelo predictivo.

## Cambios examinados
- `src/environment/check.py`: verificación offline de Python y dependencias declaradas.
- `check_environment.py`: CLI con perfiles `core` y `app`, códigos de salida 0/2.
- `run_demo.py`: preflight `core` antes de preparar o modificar el directorio de salida.
- `app.py`: preflight `app` y detención explícita antes de cargar datos si el entorno no cumple.
- `requirements.txt`: declaración de `packaging` y rango de Python documentado.
- `tests/test_adversarial_v088.py`: pruebas de perfiles, dependencias faltantes, versión exacta, límites de Python y requirements inválidos.

## Auditoría 1 — Funcional y arquitectónica
**Resultado: aprobada en el alcance probado; smoke test de interfaz pendiente.**
- Compilación de todos los archivos Python: aprobada.
- Perfil core: aprobado con Python 3.13.5, pandas 2.2.3 y numpy 2.3.5.
- Generación demo: 500 pacientes, 4.293 mediciones, 500 landmarks; 27/27 controles de calidad, 10/10 trazabilidad y 12/12 conciliación.
- El preflight se ejecuta antes de generar los artefactos. No se ejecutó una sesión visual Streamlit porque el entorno no cumple el perfil app.

## Auditoría 2 — Científica y metodológica
**Resultado: aprobada.**
- No se modificaron definiciones de desenlace, horizonte de 365 días, confirmación mínima de 30 días, censura ni reglas de evaluabilidad.
- Resultados sintéticos conservados: 347 evaluables, 153 no evaluables y 58 eventos brutos.
- Los perfiles de entorno son controles de software, no reglas clínicas ni evidencia de rendimiento del modelo.
- Modelo predictivo real permanece desconectado; no se generan probabilidades individuales.

## Auditoría 3 — Seguridad e integridad
**Resultado: aprobada en el alcance probado.**
- El verificador solo consulta metadatos locales de distribución; no ejecuta instalaciones, no realiza solicitudes de red y no modifica dependencias.
- Requirements ausente, malformado o con directivas no admitidas produce fallo cerrado.
- Python fuera del rango `>=3.10,<3.14`, paquetes ausentes y versiones fuera de especificación son reportados como incompatibles.
- El perfil app bloquea la carga de datos si el entorno no satisface las dependencias.

## Auditoría 4 — Integrada adversarial y regresión
**Resultado: aprobada para el alcance automatizado.**
- `python -m unittest discover -s tests -v`: 93/93 pruebas aprobadas.
- Casos nuevos: perfil core, dependencia app ausente, versión exacta incompatible, Python inferior al mínimo, Python en límite superior excluido, perfil desconocido, requirements ausente y malformado.
- Compilación Python: aprobada.

## Hallazgo de entorno — no ocultar
En el entorno disponible para esta auditoría se observó:
- Python 3.13.5: compatible.
- pandas 2.2.3: compatible.
- numpy 2.3.5: compatible.
- scikit-learn 1.8.0: incompatible con el pin `==1.9.0`.
- Streamlit: no instalado.

El perfil `app` falló correctamente (código 2), identificando ambos problemas. Esto demuestra que el preflight detecta el entorno incompatible, pero **no demuestra que la interfaz haya arrancado correctamente**. Para una liberación de demostración visual, instalar las dependencias del archivo `requirements.txt`, ejecutar `python check_environment.py --profile app` y realizar un smoke test de Streamlit en un entorno compatible.

## Límites
- No se realizó instalación desde internet ni prueba en un segundo sistema operativo.
- No se generó un lockfile con hashes de wheels; los rangos/pins de `requirements.txt` siguen siendo el contrato de dependencias.
- La comprobación no sustituye pruebas de despliegue, SBOM, escaneo de vulnerabilidades ni revisión de licencias.
- No equivale a certificación de seguridad, validación clínica o validación externa.

## Dictamen
v0.8.8 queda aprobada como incremento de preflight y reproducibilidad de entorno, con **condición pendiente explícita para validar la interfaz Streamlit** en un entorno que satisfaga el perfil app. No declarar el prototipo visual listo para la convocatoria hasta cerrar ese smoke test.
