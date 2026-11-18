# Auditoría adversarial 09 — Reproducibilidad y dependencias

**Resultado:** BLOQUEADA PARCIALMENTE.

**Evidencia:** Python 3.13.5 dentro del rango declarado; perfil `core` 2/2 PASS. Perfil `app` 5/6 por ausencia de Streamlit. Perfil `model` 1/2 porque el entorno tiene scikit-learn 1.8.0 y `requirements-model.txt` fija 1.9.0.

**Corrección aplicada:** separación documental entre dependencias del dashboard sintético y perfil opcional de modelado; la interfaz no requiere scikit-learn y no ejecuta inferencia.

**Acción requerida:** crear entorno limpio desde `requirements-app.txt` y comprobar instalación/arranque; validar el perfil opcional de modelo solo en entorno compatible con el artefacto histórico.

**Dictamen:** reproducibilidad core aprobada; instalación real de app/model no aprobada en este contenedor.
