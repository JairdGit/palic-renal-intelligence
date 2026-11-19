# Diez auditorías adversariales — PALIC Renal Intelligence v1.0.0

## Protocolo
Cada auditoría buscó deliberadamente errores, incoherencias, fisuras y condiciones de fallo. Los hallazgos se clasificaron por severidad y se registró evidencia, corrección y retest. Una prueba automatizada aprobada no sustituye una revisión visual, clínica, de penetración o de terceros.

| N.º | Dominio | Resultado | Hallazgo principal / disposición |
|---:|---|---|---|
| 01 | Funcional y arquitectura | APROBADA | Se endureció validación de tipos para tamaño de generación y semilla. |
| 02 | Científica y definición del desenlace | APROBADA CON LÍMITES | Se preservan definición operacional, censura y separación entre demo e investigación. No valida utilidad clínica. |
| 03 | Temporal y longitudinal | APROBADA | Fechas, secuencias y reglas temporales cubiertas por pruebas automatizadas; discrepancia histórica del archivo de investigación permanece documentada. |
| 04 | Integridad relacional y calidad | APROBADA | Identidad sintética, unicidad y correspondencia entre tablas revisadas. |
| 05 | Seguridad de manifiesto y cadena de suministro | APROBADA | Se corrigió la aceptación de archivos no declarados; modo estricto rechaza archivos extra, versión incorrecta y symlinks. |
| 06 | Entradas, salidas y exportaciones | APROBADA | Se corrigió la aceptación silenciosa de encabezados CSV duplicados y se neutralizaron fórmulas en celdas textuales exportadas. |
| 07 | Frontera de modelo y afirmaciones científicas | APROBADA CON LÍMITES | El modelo continúa desconectado; no se ejecuta inferencia ni se publican predicciones individuales. |
| 08 | Interfaz, navegación y experiencia de demostración | BLOQUEADA | Streamlit no está instalado en el entorno; prueba visual y de navegador no ejecutada. |
| 09 | Reproducibilidad y dependencias | BLOQUEADA PARCIAL | Perfil core aprobado; app bloqueado por Streamlit ausente; model bloqueado por versión instalada distinta de la fijada. |
| 10 | Documentación y preparación de concurso | BLOQUEADA PARCIAL | El software está documentado; plantilla oficial del pitch deck y video público no se han integrado ni verificado. |

## Hallazgos corregidos

### H-05-01 — inventario incompleto del manifiesto
- **Severidad:** Alta.
- **Riesgo:** un archivo añadido al paquete podía quedar fuera del manifiesto y no ser detectado por el verificador anterior.
- **Corrección:** `verify_release_manifest(..., strict=True)` exige inventario completo, versión esperada y rechaza enlaces simbólicos.
- **Retest:** pruebas de archivo no declarado, versión incorrecta y symlink en `tests/test_release_v1_adversarial.py`.

### H-06-01 — encabezados CSV duplicados
- **Severidad:** Media.
- **Riesgo:** pandas puede renombrar encabezados duplicados de forma automática, ocultando una estructura de entrada ambigua.
- **Corrección:** lectura del encabezado bruto con `csv.reader` antes de parsear con pandas; duplicados o nombres vacíos bloquean la lectura.
- **Retest:** `test_duplicate_csv_headers_fail_closed`.

### H-06-02 — inyección de fórmulas en exportaciones
- **Severidad:** Alta en el contexto de apertura de CSV en hojas de cálculo.
- **Riesgo:** celdas textuales iniciadas por `=`, `+`, `-` o `@` podrían interpretarse como fórmulas.
- **Corrección:** se antepone apóstrofo a cadenas potencialmente ejecutables, preservando valores numéricos negativos.
- **Retest:** `test_formula_injection_is_neutralized_in_text_columns`.

### H-01-01 — parámetros de generación ambiguos
- **Severidad:** Media.
- **Riesgo:** entradas no enteras o booleanas podían llegar al generador de datos.
- **Corrección:** validación explícita de entero para pacientes y semilla no negativa.
- **Retest:** pruebas de tamaño fraccionario y semilla booleana.

## Bloqueos que no se deben ocultar
1. No se ejecutó Streamlit en navegador. Debe realizarse en un entorno que instale `requirements-app.txt`.
2. El perfil opcional de modelado no pasa en este entorno porque la versión instalada de scikit-learn no coincide con la fijada en `requirements-model.txt`. No se requiere para la demo y el modelo no está conectado.
3. La discrepancia temporal del archivo histórico de investigación no se puede resolver a partir de este prototipo sintético; no se declara reproducibilidad integral del estudio.
4. La plantilla oficial del pitch deck y el video público del concurso no están incluidos en el paquete de software.

## Regla de aprobación
Los dominios 08, 09 y 10 requieren evidencia externa a las pruebas unitarias de este contenedor. Por tanto, el resultado es una **versión v1.0.0 de software con bloqueos de verificación de presentación**, no una certificación integral ni una postulación completa lista para enviar sin completar los entregables indicados.


## Hallazgo adicional de auditoría comparativa de despliegue — v1.0.0-R1

### H-05-02 — metadatos del checkout Git y secretos runtime contaminan el inventario estricto
- **Severidad:** Alta (bloqueo de disponibilidad de la demo; no implica por sí mismo alteración de los datos).
- **Evidencia:** el diagnóstico de Streamlit reportó archivos internos `.git/*` y `.streamlit/secrets.toml` como no declarados. El verificador estricto anterior no excluía el directorio `.git` ni el archivo runtime de secretos.
- **Corrección:** el verificador y el generador de manifiesto excluyen `.git` y el archivo exacto `.streamlit/secrets.toml`. Otros archivos de `.streamlit` continúan sujetos al inventario estricto.
- **Control de seguridad:** `.streamlit/secrets.toml` es runtime-only; no debe versionarse ni incluir credenciales en el repositorio público. Usar el gestor Secrets de Streamlit.
- **Retest:** se agregan pruebas para confirmar que `.git` y el archivo runtime se excluyen, mientras que `.streamlit/config.toml` no declarado sigue provocando FAIL.
- **Límite:** esta corrección aborda el patrón de archivos adicionales observado. Los cuatro archivos con hash fallido requieren comparar el checkout remoto real con el manifiesto y comprobar que el despliegue está en el commit actualizado.
