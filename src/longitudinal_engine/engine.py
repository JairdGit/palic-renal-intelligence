import pandas as pd
import numpy as np

HORIZON_DAYS = 365


def _prepare(renal):
    required = {'patient_id','measurement_date','egfr_ml_min_1_73m2'}
    missing = required - set(renal.columns)
    if missing: raise ValueError(f'Faltan columnas: {sorted(missing)}')
    r = renal.copy()
    r['measurement_date'] = pd.to_datetime(r['measurement_date'], errors='coerce')
    r['egfr_ml_min_1_73m2'] = pd.to_numeric(r['egfr_ml_min_1_73m2'], errors='coerce')
    return r.dropna(subset=['patient_id','measurement_date','egfr_ml_min_1_73m2']).sort_values(['patient_id','measurement_date']).reset_index(drop=True)


def select_landmarks(renal):
    """Adaptación sintética de la regla exacta del contrato PALIC-PY-10 V12.1.0."""
    r = _prepare(renal)
    if r.empty: raise ValueError('No hay mediciones válidas')
    source_max = r.measurement_date.max(); cutoff = source_max - pd.Timedelta(days=HORIZON_DAYS)
    r['ord'] = r.groupby('patient_id').cumcount()
    candidates = r[(r.measurement_date <= cutoff) & (r['ord'] >= 1)].copy()
    lm = candidates.groupby('patient_id', sort=False).tail(1).copy()
    first = r.groupby('patient_id').measurement_date.min().rename('first_renal_date')
    lm = lm.join(first, on='patient_id').rename(columns={'measurement_date':'index_date','egfr_ml_min_1_73m2':'index_egfr'})
    lm['prior_valid_measurements'] = lm['ord'].astype(int)
    lm['history_days'] = (lm.index_date-lm.first_renal_date).dt.days
    lm = lm[['patient_id','index_date','index_egfr','prior_valid_measurements','first_renal_date','history_days']].reset_index(drop=True)
    audit = {'source_max_date':source_max.date().isoformat(),'cutoff_date':cutoff.date().isoformat(),'horizon_days':365,
             'landmarks':len(lm),'unique_patients':lm.patient_id.nunique(),'one_landmark_per_patient':bool(lm.patient_id.is_unique),
             'uses_future_for_index_selection':False,
             'selection_rule':'LAST eligible landmark <= source_max - 365 days with >=1 prior valid TFG; no future patient observations used'}
    return lm,audit


def build_longitudinal_dataset(renal):
    r = _prepare(renal)
    lm, audit = select_landmarks(r)
    future = r.merge(lm[['patient_id','index_date','index_egfr']],on='patient_id',how='inner',validate='many_to_one')
    future = future[(future.measurement_date>future.index_date)&(future.measurement_date<=future.index_date+pd.Timedelta(days=365))].copy()
    limit = future.index_egfr * .60
    below = future[future.egfr_ml_min_1_73m2 <= limit]
    events=[]
    for pid,g in below.groupby('patient_id',sort=False):
        g=g.sort_values('measurement_date')
        for _,cross in g.iterrows():
            later=g[g.measurement_date>=cross.measurement_date+pd.Timedelta(days=30)]
            if not later.empty:
                events.append({'patient_id':pid,'cross_date':cross.measurement_date,'confirmation_date':later.iloc[0].measurement_date,'target_sustained_40_raw':1})
                break
    ev=pd.DataFrame(events,columns=['patient_id','cross_date','confirmation_date','target_sustained_40_raw'])
    out=lm[['patient_id','index_date','index_egfr']].merge(ev,on='patient_id',how='left',validate='one_to_one')
    out['target_sustained_40_raw']=out.target_sustained_40_raw.fillna(0).astype(int)
    obs=future.groupby('patient_id').agg(future_valid_tfg_count=('egfr_ml_min_1_73m2','size'),last_future_date=('measurement_date','max'))
    out=out.merge(obs,on='patient_id',how='left',validate='one_to_one')
    out['future_valid_tfg_count']=out.future_valid_tfg_count.fillna(0).astype(int)
    out['evaluable_365']=out.future_valid_tfg_count.ge(2)
    out['observation_status']=np.where(out.evaluable_365,'EVALUABLE','CENSORED_NON_EVALUABLE')
    out['target_sustained_40']=out.target_sustained_40_raw.astype(float)
    out.loc[~out.evaluable_365,'target_sustained_40']=np.nan
    audit.update({'future_observations':len(future),'evaluable_365':int(out.evaluable_365.sum()),
                  'non_evaluable_365':int((~out.evaluable_365).sum()),'events_raw':int(out.target_sustained_40_raw.sum()),
                  'events_evaluable':int(out.loc[out.evaluable_365,'target_sustained_40'].sum()),
                  'non_evaluable_policy':'censored/non-evaluable; target NaN; never recoded as no-event',
                  'outcome_definition':'>=40% decline from index eGFR (future eGFR <=60% of index), confirmed by another qualifying observation >=30 days later within 365 days'})
    return out,audit


def summarize_trajectory(history):
    """Descriptive statistics only; no clinical thresholds or diagnosis."""
    r = _prepare(history)
    if r.empty:
        return {'n_measurements': 0}
    r = r.sort_values('measurement_date')
    first = float(r.iloc[0]['egfr_ml_min_1_73m2'])
    last = float(r.iloc[-1]['egfr_ml_min_1_73m2'])
    days = int((r.iloc[-1]['measurement_date'] - r.iloc[0]['measurement_date']).days)
    slope = float('nan')
    if len(r) >= 2 and days > 0:
        x = (r['measurement_date'] - r['measurement_date'].min()).dt.days.to_numpy(dtype=float)
        y = r['egfr_ml_min_1_73m2'].to_numpy(dtype=float)
        slope = float(np.polyfit(x, y, 1)[0] * 365.25)
    gaps = r['measurement_date'].diff().dt.days.dropna()
    return {
        'n_measurements': int(len(r)),
        'first_egfr': first,
        'last_egfr': last,
        'absolute_change': float(last - first),
        'percent_change': float((last - first) / first * 100) if first != 0 else float('nan'),
        'history_days': days,
        'slope_per_year': slope,
        'mean_gap_days': float(gaps.mean()) if len(gaps) else float('nan'),
        'max_gap_days': int(gaps.max()) if len(gaps) else None,
        'min_egfr': float(r['egfr_ml_min_1_73m2'].min()),
        'max_egfr': float(r['egfr_ml_min_1_73m2'].max()),
        'sd_egfr': float(r['egfr_ml_min_1_73m2'].std(ddof=1)) if len(r) > 1 else 0.0
    }
