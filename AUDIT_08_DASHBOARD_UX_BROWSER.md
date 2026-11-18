# Auditoría adversarial 08 — Dashboard, navegación y experiencia de demostración

**Resultado:** BLOQUEADA POR ENTORNO.

**Búsqueda:** seis secciones, mensajes de cautela, navegación, estados vacíos, recorrido de demostración y ejecución visual.

**Evidencia:** seis secciones identificadas en `app.py`; 15 minutos de recorrido documentados; 2 pruebas estructurales nuevas aprobadas. `check_environment.py --profile app` reporta 5/6 porque Streamlit no está instalado.

**Hallazgo abierto:** no fue posible iniciar Streamlit ni ejecutar pruebas de navegador/capturas de las seis secciones en este entorno.

**Acción requerida:** instalar `requirements-app.txt` en un entorno compatible; ejecutar `streamlit run app.py`; recorrer todas las páginas; probar selectores, descargas, estados de error y visualización; adjuntar evidencia de navegador.

**Dictamen:** no se declara auditoría visual aprobada.
