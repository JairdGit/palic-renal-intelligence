"""Pure visualization contracts for longitudinal dashboard charts.

The module prepares chart-ready data without importing Streamlit or Plotly.
It labels synthetic observations and event annotations explicitly and refuses
ambiguous or non-finite inputs rather than silently drawing misleading charts.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

class DashboardVisualizationError(ValueError):
    """Raised when chart inputs are incomplete, ambiguous, or unsafe."""


def build_trajectory_chart_data(renal: pd.DataFrame, landmark: pd.DataFrame | None = None) -> pd.DataFrame:
    required={"measurement_date","egfr_ml_min_1_73m2"}
    missing=required-set(renal.columns)
    if missing: raise DashboardVisualizationError(f"Faltan columnas de trayectoria: {', '.join(sorted(missing))}")
    data=renal.copy()
    data["measurement_date"]=pd.to_datetime(data["measurement_date"],errors="coerce")
    if data["measurement_date"].isna().any(): raise DashboardVisualizationError("La trayectoria contiene fechas inválidas")
    values=pd.to_numeric(data["egfr_ml_min_1_73m2"],errors="coerce")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise DashboardVisualizationError("La trayectoria contiene valores TFG no finitos")
    data["egfr_ml_min_1_73m2"]=values.astype(float)
    if data["measurement_date"].duplicated().any():
        raise DashboardVisualizationError("La trayectoria contiene más de una medición en la misma fecha")
    data=data.sort_values("measurement_date",kind="stable").reset_index(drop=True)
    data["days_from_first_measurement"]=(data["measurement_date"]-data["measurement_date"].iloc[0]).dt.total_seconds()/86400
    data["point_role"]="observacion_sintetica"
    data["synthetic_data"]=True
    data["landmark_date"]=pd.NaT
    data["threshold_60pct"]=np.nan
    if landmark is not None and not landmark.empty:
        if len(landmark)!=1: raise DashboardVisualizationError("La vista debe contener exactamente un landmark")
        row=landmark.iloc[0]
        if "index_date" not in landmark.columns or "index_egfr" not in landmark.columns:
            raise DashboardVisualizationError("El landmark no contiene fecha y TFG índice")
        idx=pd.to_datetime(row["index_date"],errors="coerce")
        egfr=pd.to_numeric(pd.Series([row["index_egfr"]]),errors="coerce").iloc[0]
        if pd.isna(idx) or pd.isna(egfr) or not np.isfinite(float(egfr)) or float(egfr)<=0:
            raise DashboardVisualizationError("La referencia del landmark no es válida")
        data["landmark_date"]=idx
        data["threshold_60pct"]=float(egfr)*0.60
        data.loc[data["measurement_date"].eq(idx),"point_role"]="landmark"
    return data


def build_outcome_annotation(landmark: pd.DataFrame) -> dict:
    required={"evaluable_365","target_sustained_40","observation_status"}
    missing=required-set(landmark.columns)
    if missing: raise DashboardVisualizationError(f"Faltan campos de desenlace: {', '.join(sorted(missing))}")
    if len(landmark)!=1: raise DashboardVisualizationError("La anotación requiere exactamente un landmark")
    row=landmark.iloc[0]
    evaluable=pd.to_numeric(pd.Series([row.evaluable_365]),errors="coerce").iloc[0]
    if pd.isna(evaluable) or evaluable not in (0,1): raise DashboardVisualizationError("evaluable_365 debe ser 0/1")
    target=pd.to_numeric(pd.Series([row.target_sustained_40]),errors="coerce").iloc[0]
    if int(evaluable)==0 and not pd.isna(target): raise DashboardVisualizationError("Un paciente no evaluable debe conservar objetivo nulo")
    if int(evaluable)==1 and (pd.isna(target) or target not in (0,1)): raise DashboardVisualizationError("El objetivo evaluable debe ser 0/1")
    status=str(row.observation_status)
    expected="EVALUABLE" if int(evaluable)==1 else "CENSORED_NON_EVALUABLE"
    if status!=expected: raise DashboardVisualizationError("El estado de observación contradice la evaluabilidad")
    if int(evaluable)==0: label="No evaluable / censurado"
    elif int(target)==1: label="Evento sintético confirmado"
    else: label="Sin evento sintético confirmado"
    return {"evaluable_365":int(evaluable),"target_sustained_40":None if pd.isna(target) else int(target),"observation_status":status,"display_label":label,"synthetic_data":True}


def build_observation_status_counts(landmarks: pd.DataFrame) -> pd.DataFrame:
    if "observation_status" not in landmarks.columns: raise DashboardVisualizationError("Falta observation_status")
    allowed={"EVALUABLE","CENSORED_NON_EVALUABLE"}
    values=landmarks["observation_status"].astype(str)
    unexpected=sorted(set(values)-allowed)
    if unexpected: raise DashboardVisualizationError("Estados de observación desconocidos: "+", ".join(unexpected))
    result=values.value_counts().rename_axis("Estado").reset_index(name="Registros")
    if int(result["Registros"].sum())!=len(landmarks): raise DashboardVisualizationError("Los estados no concilian con landmarks")
    return result.sort_values("Estado",kind="stable").reset_index(drop=True)
