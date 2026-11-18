"""Streamlit dashboard. Dependency preflight runs before third-party imports."""
from pathlib import Path
import json
import sys

from src.environment.check import check_environment

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "generated"
ENVIRONMENT = check_environment(ROOT, profile="app")
if not ENVIRONMENT["all_checks_passed"]:
    print(
        "Entorno incompatible. Ejecute: python check_environment.py --profile app. "
        "No se cargarán datos ni resultados.",
        file=sys.stderr,
    )
    print(json.dumps(ENVIRONMENT, indent=2, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(2)

# Third-party imports are deliberately delayed until the complete preflight passes.
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.longitudinal_engine.engine import summarize_trajectory
from src.longitudinal_engine.outcome_audit import audit_patient_outcome
from src.integrity.manifest import verify_release_manifest
from src.io_safety.safe_io import ArtifactReadError, read_csv_checked, read_json_checked
from src.dashboard.validation import DashboardDataContractError, validate_dashboard_data
from src.dashboard.presentation import (
    DashboardPresentationError, build_summary, build_scenario_counts,
    build_frequency_summary, safe_export_filename, json_bytes,
)
from src.dashboard.demo_exports import DemoExportError, csv_export_with_provenance, json_export_with_provenance
from src.dashboard.diagnostics import DashboardDiagnosticsError, build_operational_diagnostics
from src.dashboard.demo_journey import DemoJourneyError, build_demo_journey, get_demo_step
from src.dashboard.demo_acceptance import DemoAcceptanceError, build_demo_acceptance
from src.dashboard.visualization import (
    DashboardVisualizationError, build_trajectory_chart_data, build_outcome_annotation, build_observation_status_counts,
)
from src.dashboard.interactions import (
    DashboardInteractionError, available_patient_ids, get_patient_view, csv_bytes,
)

st.set_page_config(page_title="PALIC Renal Intelligence", page_icon="🧬", layout="wide")
try:
    RELEASE = read_json_checked(ROOT / "RELEASE_MANIFEST.json")
    RELEASE_VERSION = RELEASE.get("version", "desconocida")
except ArtifactReadError as exc:
    st.error(f"No se puede iniciar el prototipo: manifiesto de versión inválido. Detalle: {exc}")
    st.stop()
INTEGRITY = verify_release_manifest(ROOT, strict=True, expected_version="1.0.0")
if INTEGRITY.get("status") != "PASS":
    st.error("La integridad del paquete no pudo verificarse. Se bloqueó la visualización.")
    st.json(INTEGRITY)
    st.stop()

@st.cache_data
def load_data():
    patients = read_csv_checked(
        DATA / "patients_synthetic.csv",
        required_columns=["patient_id", "age_years", "sex", "region", "scenario"],
    )
    renal = read_csv_checked(
        DATA / "renal_measurements_synthetic.csv",
        required_columns=["patient_id", "measurement_date", "egfr_ml_min_1_73m2", "measurement_sequence"],
        date_columns=["measurement_date"],
    )
    landmarks = read_csv_checked(
        DATA / "longitudinal_landmarks_synthetic.csv",
        required_columns=["patient_id", "index_date", "evaluable_365", "target_sustained_40"],
        date_columns=["index_date"],
    )
    for optional_date in ["cross_date", "confirmation_date", "last_future_date"]:
        if optional_date in landmarks.columns:
            landmarks[optional_date] = pd.to_datetime(landmarks[optional_date], errors="coerce")
    clinical = read_csv_checked(
        DATA / "clinical_variables_synthetic.csv",
        required_columns=["patient_id", "hypertension_simulated", "diabetes_simulated", "bmi_simulated"],
    )
    quality = read_json_checked(DATA / "quality_report.json")
    audit = read_json_checked(DATA / "longitudinal_audit.json")
    return patients, renal, clinical, landmarks, quality, audit

try:
    patients, renal, clinical, landmarks, quality, audit = load_data()
    DASHBOARD_CONTRACT = validate_dashboard_data(patients, renal, clinical, landmarks)
except DashboardDataContractError as exc:
    st.error("Los datos no cumplen el contrato de integridad del dashboard. Se bloqueó la visualización.")
    st.code(str(exc))
    st.stop()
except ArtifactReadError as exc:
    st.error("El prototipo se detuvo de forma segura porque uno o más archivos de demostración están ausentes, vacíos o dañados.")
    st.code(str(exc))
    st.info("Regenera el conjunto sintético con `python run_demo.py` y vuelve a iniciar la aplicación. No se mostrarán resultados parciales.")
    st.stop()
st.title("PALIC Renal Intelligence")
st.caption("Prototipo de analítica longitudinal para salud poblacional · Datos 100 % sintéticos")
st.warning("Entorno demostrativo: todos los registros son sintéticos. No es un dispositivo médico, no diagnostica ni sustituye la valoración clínica.")

with st.sidebar:
    st.header("Navegación")
    page = st.radio("Sección", ["Resumen","Trayectorias","Auditoría por paciente","Inteligencia de riesgo","Calidad de datos","Trazabilidad"])
    st.divider()
    st.caption(f"PALIC · Prototype build v{RELEASE_VERSION}")
    st.caption(f"Semilla de demostración: {audit.get('seed','ver README')}")
    with st.expander("Guía de recorrido · 15 minutos", expanded=False):
        journey = build_demo_journey()
        chosen_step = st.selectbox("Etapa de demostración", journey["sections"], key="demo_journey_step")
        try:
            step = get_demo_step(chosen_step)
            st.caption(f"Etapa {step['order']} de {len(journey['steps'])} · {step['duration_minutes']} min")
            st.markdown(f"**Propósito:** {step['purpose']}")
            st.write(f"**Acción:** {step['action']}")
            st.info(step['message'])
            st.caption("Recorrido sugerido: " + " → ".join(journey['sections']))
        except DemoJourneyError as exc:
            st.error(f"No se pudo cargar la guía: {exc}")
    with st.expander("Lista de aceptación · demostración pública", expanded=False):
        try:
            acceptance_operational = build_operational_diagnostics(ROOT, INTEGRITY)
            acceptance = build_demo_acceptance(
                root=ROOT, integrity=INTEGRITY, operational=acceptance_operational,
                data_contract=DASHBOARD_CONTRACT, journey=build_demo_journey(),
            )
            st.metric("Preparación de demo", "LISTA" if acceptance["status"] == "READY_FOR_GUIDED_DEMO" else "REVISAR",
                      f"{acceptance['checks_passed']}/{acceptance['checks_total']} controles")
            st.dataframe(pd.DataFrame(acceptance["checks"]), width="stretch", hide_index=True)
            st.caption(acceptance["scope"])
        except DemoAcceptanceError as exc:
            st.error(f"No se pudo completar la lista de aceptación: {exc}")

if page == "Resumen":
    summary = build_summary(patients, renal, landmarks)
    metrics = [
        ("Pacientes sintéticos", f"{summary['patients']:,}"),
        ("Mediciones renales", f"{summary['renal_measurements']:,}"),
        ("Landmarks", f"{summary['landmarks']:,}"),
        ("Evaluables a 365 días", f"{summary['evaluable_365']:,}"),
        ("No evaluables / censurados", f"{summary['non_evaluable_365']:,}"),
        ("Eventos sintéticos evaluables", f"{summary['events_evaluable']:,}")
    ]
    cols=st.columns(3)
    for i,(label,value) in enumerate(metrics): cols[i%3].metric(label,value)
    st.subheader("Escenarios de demostración")
    counts=build_scenario_counts(patients)
    st.plotly_chart(px.bar(counts,x="Escenario",y="Pacientes",title="Distribución de escenarios sintéticos"),width="stretch")
    st.info("La distribución fue diseñada para probar comportamientos de software; no representa prevalencia poblacional.")

elif page == "Trayectorias":
    st.subheader("Explorador de trayectoria renal")
    selected=st.selectbox("Paciente sintético", available_patient_ids(patients), key="trajectory_patient")
    try:
        patient_view = get_patient_view(selected, patients, renal, clinical, landmarks)
    except DashboardInteractionError as exc:
        st.error(f"No fue posible resolver la selección: {exc}")
        st.stop()
    p=patient_view["patient"].iloc[0]
    h=patient_view["renal"]
    lm=patient_view["landmark"]
    c1,c2,c3=st.columns(3)
    c1.metric("Edad sintética",int(p.age_years)); c2.metric("Sexo",p.sex); c3.metric("Escenario",p.scenario)
    if h.empty:
        st.info("No hay mediciones renales disponibles para este paciente sintético.")
    if not h.empty:
        stats=summarize_trajectory(h)
        st.markdown("#### Indicadores descriptivos de trayectoria")
        tiles=st.columns(4)
        tiles[0].metric("Cambio absoluto",f"{stats['absolute_change']:+.2f}")
        tiles[1].metric("Cambio porcentual",f"{stats['percent_change']:+.1f}%")
        tiles[2].metric("Pendiente anual descriptiva",f"{stats['slope_per_year']:+.2f}")
        tiles[3].metric("Mediciones",stats["n_measurements"])
        st.caption("Cálculos descriptivos sobre la serie sintética completa; no son umbrales clínicos ni estimaciones de riesgo.")
        try:
            chart_data=build_trajectory_chart_data(h,lm if not lm.empty else None)
            fig=px.line(chart_data,x="measurement_date",y="egfr_ml_min_1_73m2",markers=True,
                        color_discrete_sequence=["#2563eb"],
                        labels={"measurement_date":"Fecha","egfr_ml_min_1_73m2":"TFG (ml/min/1,73 m²)"},
                        title="Trayectoria de TFG sintética")
            if not lm.empty:
                idx=pd.to_datetime(lm.iloc[0].index_date)
                fig.add_vline(x=idx,line_dash="dash",line_color="orange",annotation_text="Landmark / inicio del horizonte")
                threshold=float(lm.iloc[0].index_egfr)*0.60
                fig.add_hline(y=threshold,line_dash="dot",line_color="red",annotation_text="Umbral operativo 60 % de TFG índice")
            fig.update_layout(yaxis_title="TFG (ml/min/1,73 m²)",xaxis_title="Fecha",legend_title_text="Serie sintética")
            st.plotly_chart(fig,width="stretch")
            st.caption("Visualización descriptiva de datos 100 % sintéticos. La línea de umbral representa la regla operacional del desenlace, no un umbral diagnóstico.")
        except DashboardVisualizationError as exc:
            st.error(f"No se puede representar esta trayectoria: {exc}")
            st.stop()
        gaps=h.measurement_date.diff().dt.days.dropna()
        if len(gaps):
            g1,g2,g3=st.columns(3)
            g1.metric("Intervalo medio",f"{gaps.mean():.0f} días")
            g2.metric("Intervalo máximo",f"{gaps.max():.0f} días")
            g3.metric("Variabilidad TFG (DE)",f"{stats['sd_egfr']:.2f}")
        st.dataframe(h,width="stretch",hide_index=True)
    if lm.empty:
        st.info("No hay landmark disponible para mostrar evaluabilidad en esta selección.")
    if not lm.empty:
        st.markdown("#### Evaluabilidad del horizonte")
        st.dataframe(lm[["index_date","index_egfr","future_valid_tfg_count","evaluable_365","observation_status","target_sustained_40"]],width="stretch",hide_index=True)
        st.caption("La variación histórica previa al landmark se presenta separada del desenlace futuro. Los no evaluables conservan objetivo nulo.")

elif page == "Auditoría por paciente":
    st.subheader("Explicación del desenlace longitudinal")
    selected=st.selectbox("Paciente sintético para auditar", available_patient_ids(patients), key="audit_patient")
    try:
        patient_view = get_patient_view(selected, patients, renal, clinical, landmarks)
    except DashboardInteractionError as exc:
        st.error(f"No fue posible resolver la selección: {exc}")
        st.stop()
    if not patient_view["has_landmark"]:
        st.warning("El paciente seleccionado no tiene un landmark disponible para auditar.")
        st.stop()
    lmrow=patient_view["landmark"].iloc[0]
    audit_result=audit_patient_outcome(renal,lmrow)
    st.write("**Estado:**", audit_result["status"])
    st.info(audit_result["explanation"])
    x1,x2,x3,x4=st.columns(4)
    x1.metric("TFG índice",f"{audit_result['index_egfr']:.2f}")
    x2.metric("Umbral 60 %",f"{audit_result['threshold_60pct']:.2f}")
    x3.metric("Mediciones futuras",audit_result["future_valid_measurements"])
    x4.metric("Evaluable", "Sí" if audit_result["evaluable_365"] else "No")
    st.markdown("#### Secuencia de verificación")
    steps=[
        ("1. Landmark",f"{audit_result['index_date'].date()} · TFG índice {audit_result['index_egfr']:.2f}"),
        ("2. Umbral",f"60 % de la TFG índice = {audit_result['threshold_60pct']:.2f}"),
        ("3. Cruce",str(audit_result["cross_date"].date()) if audit_result["cross_date"] is not None else "No identificado"),
        ("4. Confirmación",str(audit_result["confirmation_date"].date()) if audit_result["confirmation_date"] is not None else "No identificada"),
        ("5. Intervalo de confirmación",f"{audit_result['confirmation_gap_days']} días" if audit_result["confirmation_gap_days"] is not None else "No aplica")
    ]
    for label,value in steps:
        st.write(f"**{label}:** {value}")
    future=audit_result["future_observations"]
    if not future.empty:
        fig=px.scatter(future,x="measurement_date",y="egfr_ml_min_1_73m2",hover_data=["days_from_landmark"],
                       title="Observaciones futuras frente al umbral operativo",
                       labels={"measurement_date":"Fecha","egfr_ml_min_1_73m2":"TFG","days_from_landmark":"Días desde landmark"})
        fig.add_hline(y=audit_result["threshold_60pct"],line_dash="dash",annotation_text="Umbral 60 %")
        st.plotly_chart(fig,width="stretch")
        st.dataframe(future[["measurement_date","egfr_ml_min_1_73m2","days_from_landmark","threshold_60pct"]],width="stretch",hide_index=True)
        try:
            export_csv=csv_export_with_provenance(future,RELEASE_VERSION,"patient_future_observations")
            st.download_button("Descargar auditoría del paciente (CSV)",export_csv,file_name=safe_export_filename(selected, "auditoria_futura", "csv"),mime="text/csv")
        except DemoExportError as exc:
            st.error(f"No se pudo preparar la descarga: {exc}")
    audit_export={k:(v.isoformat() if hasattr(v,"isoformat") else v) for k,v in audit_result.items() if k!="future_observations"}
    try:
        export_json=json_export_with_provenance(audit_export,RELEASE_VERSION,"patient_outcome_explanation")
        st.download_button("Descargar explicación (JSON)",export_json,
                           file_name=safe_export_filename(selected, "explicacion_desenlace", "json"),mime="application/json")
    except DemoExportError as exc:
        st.error(f"No se pudo preparar la descarga: {exc}")
    st.caption("La auditoría explica la regla computacional aplicada a datos sintéticos; no es una interpretación clínica.")

elif page == "Inteligencia de riesgo":
    st.subheader("Estado de integración del modelo")
    st.error("Modelo predictivo real no conectado. No se calculan probabilidades individuales ni categorías de riesgo.")
    st.write("Contrato de investigación incorporado: 28 predictores efectivos. Esta capa permite verificar alineación de variables, pero no equivale a inferencia conectada.")
    st.subheader("Métricas documentales del estudio")
    st.dataframe(pd.DataFrame([
        {"Métrica":"ROC-AUC","Valor":"0,8689","Interpretación":"Discriminación; evaluación temporal interna"},
        {"Métrica":"PR-AUC","Valor":"0,4956","Interpretación":"Precisión-recall; depende de la frecuencia del evento"},
        {"Métrica":"Brier","Valor":"0,00619","Interpretación":"Error cuadrático de probabilidades; depende de calibración y prevalencia"}
    ]),width="stretch",hide_index=True)
    st.warning("Estas métricas no son generadas por la demo. No demuestran validación externa, utilidad clínica ni desempeño en datos sintéticos.")
    st.markdown("**Pendiente antes de inferencia:** verificar artefacto y SHA-256, reproducir entorno, resolver discrepancias temporales, ejecutar pruebas aisladas y documentar calibración.")

elif page == "Calidad de datos":
    st.subheader("Controles y observabilidad")
    st.markdown("#### Disponibilidad operativa de la demo")
    try:
        operational = build_operational_diagnostics(ROOT, INTEGRITY)
        op1, op2, op3 = st.columns(3)
        op1.metric("Estado operativo", "DISPONIBLE" if operational["status"] == "OPERATIVO_DEMO" else "BLOQUEADO")
        op2.metric("Artefactos y controles", f"{operational['checks_passed']}/{operational['checks_total']}")
        op3.metric("Fallos", operational["failures"])
        st.dataframe(pd.DataFrame(operational["checks"]), width="stretch", hide_index=True)
        st.caption(operational["scope"])
        if operational["status"] != "OPERATIVO_DEMO":
            st.error("La disponibilidad de la demo no está completa. No se debe interpretar como una ejecución íntegra.")
    except DashboardDiagnosticsError as exc:
        st.error(f"No se pudieron ejecutar los diagnósticos operativos: {exc}")
        st.stop()
    a,b,c=st.columns(3)
    a.metric("Controles aprobados",quality["checks_passed"])
    b.metric("Controles totales",quality["checks_total"])
    c.metric("Estado global","APROBADO" if quality["all_checks_passed"] else "REVISAR")
    st.dataframe(pd.DataFrame(quality["checks"]),width="stretch",hide_index=True)
    st.subheader("Contrato de integridad para visualización")
    st.metric("Controles de contrato aprobados", f"{DASHBOARD_CONTRACT['checks_passed']}/{DASHBOARD_CONTRACT['checks_total']}")
    st.dataframe(pd.DataFrame(DASHBOARD_CONTRACT["checks"]), width="stretch", hide_index=True)
    st.caption("Estas comprobaciones protegen la consistencia de lo presentado en el dashboard; no constituyen validación clínica.")
    st.subheader("Conciliación de resultados agregados")
    reconciliation = audit.get("aggregate_reconciliation", {})
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Controles conciliados", f"{reconciliation.get('checks_passed', 0)}/{reconciliation.get('checks_total', 0)}")
    rc2.metric("Estado de conciliación", "APROBADO" if reconciliation.get("all_checks_passed") else "REVISAR")
    rc3.metric("Eventos evaluables", reconciliation.get("observed", {}).get("events_evaluable", "—"))
    st.dataframe(pd.DataFrame(reconciliation.get("checks", [])), width="stretch", hide_index=True)
    st.caption("La conciliación compara filas sintéticas individuales con conteos agregados; no es validación clínica ni evidencia de desempeño predictivo.")
    st.subheader("Evaluabilidad del horizonte")
    try:
        status=build_observation_status_counts(landmarks)
        st.plotly_chart(px.bar(status,x="Estado",y="Registros",title="Estado de observación del horizonte de 365 días"),width="stretch")
    except DashboardVisualizationError as exc:
        st.error(f"No se puede representar la evaluabilidad: {exc}")
        st.stop()
    st.subheader("Patrones de frecuencia de medición")
    gap_summary=build_frequency_summary(renal)
    st.dataframe(gap_summary,width="stretch",hide_index=True)
    st.caption("Análisis descriptivo de densidad de medición por escenario. No es un análisis formal de sensibilidad del desenlace ni demuestra robustez ante cambios de frecuencia.")
    st.caption("Los controles son técnicos y demostrativos. Un resultado aprobado no equivale a validez clínica.")
    with st.expander("Ver limitaciones"):
        for item in quality["limitations"]: st.write("• "+item)

else:
    st.subheader("Trazabilidad y límites")
    st.caption(f"Versión del prototipo: v{RELEASE_VERSION} · Build incremental de estabilización")
    st.dataframe(pd.DataFrame([
        {"Elemento":"Versión","Valor":f"v{RELEASE_VERSION}"},
        {"Elemento":"Datos","Valor":"100 % sintéticos; identificadores SYN-"},
        {"Elemento":"Generador","Valor":"Semilla reproducible; escenarios de demostración"},
        {"Elemento":"Motor longitudinal","Valor":"Landmark + horizonte futuro de 365 días"},
        {"Elemento":"Evaluabilidad","Valor":"Al menos 2 mediciones futuras válidas"},
        {"Elemento":"Desenlace","Valor":"TFG futura <=60 % de TFG índice y confirmación >=30 días"},
        {"Elemento":"Predictores","Valor":"Contrato de investigación: 28 variables"},
        {"Elemento":"Modelo serializado","Valor":"No incluido ni ejecutado"},
        {"Elemento":"SHAP","Valor":"No ejecutado"},
        {"Elemento":"Uso","Valor":"Demostración técnica; no asistencial"}
    ]),width="stretch",hide_index=True)
    st.subheader("Auditoría de ejecución longitudinal")
    st.json(audit)
    st.info("La trazabilidad documenta la configuración de esta demostración. La reproducibilidad del estudio original y la validación externa siguen siendo trabajos separados.")
