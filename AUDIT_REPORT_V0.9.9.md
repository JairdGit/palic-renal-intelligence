# Informe de auditoría adversarial — PALIC Renal Intelligence v0.9.9

## Dictamen

**Aprobada como incremento de consolidación documental y de empaquetado, dentro del alcance de las pruebas ejecutadas.** No constituye aprobación de v1.0, certificación de ciberseguridad, validación clínica ni validación externa.

## Cambios evaluados

- Nuevo módulo `src/release/readiness.py`.
- Nuevo comando `run_release_readiness.py` con cinco controles estáticos: archivos esenciales, historial de auditorías, perfiles de dependencias, documentación operativa e higiene del paquete.
- Actualización de `run_demo.py` a `generator_version = v0.9.9`.
- Actualización de las pruebas históricas de versión para comprobar el generador actual.
- Conservación del motor longitudinal, definición del desenlace, ventana de 365 días, confirmación mínima de 30 días, reglas de censura y contrato de 28 predictores.

## Resultados de las cuatro auditorías

### 1. Funcional y arquitectónica — APROBADA

- Suite completa: 220/220 pruebas aprobadas.
- Pruebas nuevas v0.9.9: 12/12 aprobadas.
- Compilación de módulos Python: aprobada.
- Perfil `core`: 2/2 controles aprobados.
- Generación sintética transaccional: completada.
- Puerta estática de preparación para revisión final: 5/5 controles aprobados.

### 2. Científica y metodológica — APROBADA CON LÍMITES

- Se conservan las reglas y contratos científicos documentados en las versiones previas.
- Datos de esta demostración: exclusivamente sintéticos.
- El modelo predictivo real permanece desconectado.
- Las métricas históricas de investigación no se presentan como resultados de esta demo ni como validación externa.
- La regla computacional de desenlace no se presenta como umbral diagnóstico ni como recomendación clínica.

### 3. Seguridad e integridad — APROBADA CON LÍMITES

- Manifiesto SHA-256 generado y verificado para los archivos distribuidos.
- Se excluyen cachés, bytecode y artefactos serializados de modelos del ZIP.
- El control de preparación revisa higiene estática y documentación; no ejecuta análisis dinámico, pentest ni auditoría profesional de seguridad.
- No se habilita carga de modelos ni inferencia.

### 4. Integrada y regresión — APROBADA CON LÍMITES

- Pruebas automatizadas: 220/220 aprobadas.
- Datos: 500 pacientes sintéticos, 4.293 mediciones, 500 landmarks.
- Evaluable a 365 días: 347; no evaluable: 153; eventos sintéticos: 58.
- Calidad: 27/27; trazabilidad: 10/10; conciliación agregada: 12/12.
- Aceptación reproducible de demo: 6/6 después de regenerar el manifiesto.
- Perfil `app`: 5/6; Streamlit no está instalado. La ejecución visual del dashboard y las pruebas de navegador no se realizaron.

## Limitaciones y pendientes antes de v1.0

1. Instalar Streamlit en un entorno compatible y ejecutar la interfaz en navegador.
2. Completar pruebas visuales y de interacción de las seis secciones y las exportaciones.
3. Revisar licencias y dependencias en el entorno final de distribución.
4. Resolver y documentar las discrepancias temporales del archivo histórico de investigación antes de afirmar reproducibilidad integral de PALIC-PY-10.
5. Ejecutar la auditoría final de v1.0 con el paquete definitivo, hashes, pruebas, documentación y demo.

## Comandos de reproducción

```bash
python check_environment.py --profile core
python check_environment.py --profile app
python run_demo.py --patients 500 --seed 20261105 --out data/generated
python -m unittest discover -s tests -v
python run_demo_acceptance.py
python run_release_readiness.py
```

**Conclusión:** v0.9.9 consolida la preparación documental y técnica del prototipo para revisión final. No se declara que PALIC Renal Intelligence sea un producto clínico validado ni que el modelo predictivo esté conectado.
