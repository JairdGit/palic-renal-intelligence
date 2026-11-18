# Auditoría adversarial 05 — Manifiesto, integridad y cadena de suministro

**Resultado:** APROBADA para inventario local del paquete.

**Hallazgo alto corregido:** el verificador anterior validaba los hashes declarados, pero no detectaba necesariamente archivos adicionales fuera del manifiesto.

**Corrección:** modo estricto de `verify_release_manifest` exige versión esperada, inventario completo de archivos regulares, rechaza symlinks y conserva controles de traversal y digest SHA-256. Se añade `build_release_manifest.py`.

**Evidencia:** `Audit05ManifestAndSupplyChain`.

**Retest:** archivo no declarado, versión incorrecta y symlink rechazados.

**Límite:** SHA-256 detecta cambios frente al manifiesto distribuido; no demuestra quién creó el paquete ni sustituye firma digital, SBOM firmado o análisis de vulnerabilidades de dependencias.
