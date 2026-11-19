# PALIC Renal Intelligence v1.0.0

## Propósito
Prototipo científico-tecnológico demostrativo para exploración longitudinal de función renal en un contexto de salud poblacional. Esta distribución está diseñada para evaluación de software y demostración con datos sintéticos; no es un dispositivo médico, no diagnostica, no recomienda tratamientos y no sustituye el juicio clínico.

## Límites obligatorios
- Todos los registros incluidos en `data/generated/` son sintéticos y reproducibles.
- El modelo predictivo real permanece desconectado. No se producen probabilidades individuales ni categorías de riesgo.
- Las métricas de investigación presentadas en el dashboard son referencias históricas internas del estudio, no resultados de esta demostración ni validación externa.
- La regla de desenlace (descenso sostenido de TFG de al menos 40 %, confirmado por una segunda medición con separación mínima de 30 días dentro de 365 días) es una definición operacional de investigación, no un umbral diagnóstico.
- La reproducibilidad integral del archivo histórico de investigación continúa condicionada a resolver la discrepancia temporal documentada en auditorías previas.

## Requisitos
Python `>=3.10,<3.14`.

### Dashboard
```bash
python -m pip install -r requirements-app.txt
python check_environment.py --profile app
streamlit run app.py
```

### Regenerar datos sintéticos
```bash
python -m pip install -r requirements.txt
python check_environment.py --profile core
python run_demo.py --patients 500 --seed 20261105 --out data/generated
```
Después de regenerar datos, debe reconstruirse el manifiesto SHA-256 y repetirse la aceptación y las auditorías. No se debe modificar un paquete ya firmado por el manifiesto sin regenerarlo.

### Pruebas y aceptación
```bash
python -m unittest discover -s tests -v
python run_demo_acceptance.py
python run_release_readiness.py
```

### Manifiesto de distribución
```bash
python build_release_manifest.py
```
El verificador de producción usa modo estricto: comprueba versión, hashes, archivos no declarados y enlaces simbólicos. Excluye metadatos internos de Git (`.git`) y el archivo runtime exacto `.streamlit/secrets.toml`; este último nunca debe versionarse y sus valores deben configurarse en Streamlit Secrets. El manifiesto no se incluye en su propia lista de hashes.

## Dependencias opcionales de modelado
`requirements-model.txt` corresponde a un entorno opcional de investigación/modelado. No es necesario para el dashboard sintético y no habilita inferencia. Debe instalarse únicamente en un entorno compatible con el artefacto de investigación y después de verificar sus procedencia, hash y compatibilidad.

## Auditorías de v1.0.0
Consultar `TEN_ADVERSARIAL_AUDITS.md` y los diez informes `AUDIT_01_...md` a `AUDIT_10_...md`. Las auditorías distinguen aprobaciones de verificaciones bloqueadas por falta de entorno o entregables del concurso.

## Alcance de la liberación
La versión de software no equivale al paquete completo de postulación. La plantilla oficial del pitch deck, el pitch deck diligenciado y el video público de demostración son entregables separados y no se incluyen en este ZIP porque no fueron suministrados para su integración y verificación.
