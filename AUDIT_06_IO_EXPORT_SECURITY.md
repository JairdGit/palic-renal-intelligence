# Auditoría adversarial 06 — Entradas, salidas y seguridad de exportación

**Resultado:** APROBADA para los casos cubiertos.

**Hallazgos corregidos:**
- Encabezados CSV duplicados podían ser renombrados automáticamente por pandas y ocultar ambigüedad.
- Cadenas exportadas que comienzan por `=`, `+`, `-` o `@` pueden activar fórmulas en hojas de cálculo.

**Corrección:** `read_csv_checked` inspecciona el encabezado bruto y bloquea duplicados o vacíos; `csv_export_with_provenance` neutraliza cadenas potencialmente ejecutables y preserva números negativos.

**Evidencia:** `Audit06InputOutputSecurity`.

**Retest:** 2/2 pruebas nuevas aprobadas.

**Límite:** no es pentest ni análisis de seguridad de una plataforma alojada.
