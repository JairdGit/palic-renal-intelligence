# Informe de liberación — PALIC Renal Intelligence v1.0.0

## Dictamen

**v1.0.0 — versión de software candidata para evaluación del concurso, con bloqueos explícitos de verificación de interfaz y entregables externos.** No se certifica como postulación completa lista para enviar hasta cerrar las acciones de auditoría 08, 09 y 10.

## Alcance de v1.0.0

- Conserva el motor longitudinal, la definición operacional del desenlace, la ventana de 365 días, confirmación mínima de 30 días, política de censura y contrato de 28 predictores.
- Datos distribuidos exclusivamente sintéticos; semilla 20261105.
- Modelo predictivo real desconectado; no se calculan probabilidades individuales.
- Se endurece la verificación SHA-256 con inventario estricto y control de versión.
- Se bloquean encabezados CSV duplicados y se mitiga inyección de fórmulas en exportaciones de texto.
- Se valida el tipo de los argumentos del generador.

## Diez auditorías adversariales

Consultar `TEN_ADVERSARIAL_AUDITS.md` y los informes individuales `AUDIT_01_...md` a `AUDIT_10_...md`.

| N.º | Auditoría | Dictamen |
|---:|---|---|
| 01 | Funcional y arquitectura | APROBADA |
| 02 | Científica y metodológica | APROBADA CON LÍMITES |
| 03 | Temporal y longitudinal | APROBADA |
| 04 | Integridad relacional y calidad | APROBADA |
| 05 | Manifiesto y cadena de suministro | APROBADA |
| 06 | Entradas/salidas y seguridad de exportación | APROBADA |
| 07 | Frontera del modelo y afirmaciones científicas | APROBADA CON LÍMITES |
| 08 | Dashboard y experiencia de navegador | BLOQUEADA: Streamlit no disponible |
| 09 | Reproducibilidad y dependencias | BLOQUEADA PARCIALMENTE |
| 10 | Documentación y entregables del concurso | BLOQUEADA PARCIALMENTE |

## Hallazgos corregidos

1. **Alta — inventario de manifiesto incompleto:** modo estricto detecta archivos no declarados, symlinks y versión incorrecta.
2. **Media — encabezados CSV duplicados:** el lector inspecciona el encabezado original y falla de forma cerrada.
3. **Alta — inyección de fórmulas en CSV:** se neutralizan cadenas textuales con prefijos de fórmula.
4. **Media — argumentos ambiguos del generador:** se exigen enteros y semilla no negativa.

Todos los hallazgos corregidos tienen pruebas de regresión específicas.

## Resultados técnicos

- Suite completa: 242/242 pruebas aprobadas; 22/22 pruebas nuevas v1.0.0.
- Parseo/compilación AST: 60 archivos Python aprobados.
- Datos sintéticos: 500 pacientes, 4.293 mediciones, 500 landmarks, 347 evaluables, 153 no evaluables y 58 eventos sintéticos.
- Calidad: 27/27; trazabilidad: 10/10; conciliación agregada: 12/12.
- Aceptación de demo: 6/6; puerta estática de liberación: 7/7.
- Manifiesto estricto: 109 archivos verificados, cero archivos no declarados.
- Perfil core: 2/2 PASS; perfil app: 5/6 BLOCKED por Streamlit ausente; perfil model: 1/2 BLOCKED por scikit-learn 1.8.0 frente al requisito opcional 1.9.0.
- Prueba visual/navegador: NO EJECUTADA.

## Bloqueos que permanecen

- **Interfaz:** `requirements-app.txt` declara Streamlit, pero no fue posible instalarlo/ejecutarlo en el entorno de auditoría; no se ejecutó prueba visual ni navegador.
- **Perfil de modelo:** la versión local de scikit-learn no coincide con la versión fijada en `requirements-model.txt`. El perfil es opcional y no se necesita para la demo sintética; no se habilita inferencia.
- **Investigación histórica:** permanece pendiente resolver la discrepancia temporal entre corte de modelo, observabilidad y landmarks en el archivo histórico. Por tanto, no se declara reproducibilidad integral del estudio.
- **Entregables del concurso:** la plantilla oficial del pitch deck, el deck diligenciado y el video público no se incluyen en este ZIP de software. Deben completarse y verificarse aparte según las reglas vigentes del concurso.

## Comandos de reproducción

```bash
python check_environment.py --profile core
python check_environment.py --profile app
python check_environment.py --profile model
python -m unittest discover -s tests -v
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python build_release_manifest.py
python run_demo_acceptance.py
python run_release_readiness.py
```

**Criterio de no sobreafirmación:** aprobar pruebas automatizadas y manifiesto no equivale a prueba visual, pentest, validación clínica, validación externa o aprobación del concurso.


## Addendum de auditoría comparativa — H-05-02

Los dos paquetes ZIP entregados (copia local y copia GitHub) contienen 122 entradas cada uno y son idénticos archivo por archivo. La revisión reprodujo 244 pruebas aprobadas, aceptación de demo 6/6 y readiness estático 7/7.

Se corrigió el inventario estricto para excluir los metadatos internos `.git` y el archivo runtime exacto `.streamlit/secrets.toml`. Este último no debe almacenarse en el repositorio público; los secretos se configuran desde Streamlit. Otros archivos no declarados siguen provocando FAIL.

**Estado:** corrección de código y pruebas aprobada en este entorno. Pendiente: confirmar que Streamlit está desplegando el commit corregido, instalar/ejecutar el entorno app y recorrer la interfaz en navegador. No se declara validación visual, clínica ni pentest.
