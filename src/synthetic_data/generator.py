import numpy as np
import pandas as pd

def generate_synthetic_data(n_patients=500, seed=20261105):
    """Generate reproducible, explicitly synthetic longitudinal data."""
    if isinstance(n_patients, bool) or not isinstance(n_patients, (int, np.integer)) or n_patients < 10:
        raise ValueError("n_patients debe ser un entero >= 10")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed debe ser un entero no negativo")
    rng = np.random.default_rng(int(seed))
    scenarios = np.resize(np.array(["stable", "declining", "variable", "incomplete", "sparse"], dtype=object), n_patients)
    rng.shuffle(scenarios)
    patients, renal, clinical = [], [], []
    start = pd.Timestamp("2022-01-01")

    for i, scenario in enumerate(scenarios, 1):
        pid = f"SYN-{i:06d}"
        pathology = str(rng.choice(["Hipertensión", "Diabetes", "Hipertensión y diabetes", "Otra"]))
        age = int(rng.integers(35, 86))
        patients.append({
            "patient_id": pid, "age_years": age, "sex": str(rng.choice(["F", "M"])),
            "region": str(rng.choice(["Caribe", "Andina", "Pacífica", "Orinoquía", "Amazonía"])),
            "scenario": scenario
        })
        base = float(rng.uniform(78, 112))
        visits = int(rng.integers(9, 11))
        if scenario == "sparse":
            visits = 5
        dates = sorted(start + pd.Timedelta(days=120*j + int(rng.integers(-8, 9))) for j in range(visits))

        for j, date in enumerate(dates):
            noise = rng.normal(0, 1.8)
            if scenario == "stable":
                value = base + rng.normal(0, 2.0)
            elif scenario == "declining":
                # Smooth nonlinear decline with measurement noise; no hard floor plateau.
                value = base * np.exp(-0.42*max(0, j-5)) + noise
            elif scenario == "variable":
                value = base + np.sin(j * 1.35) * rng.uniform(4, 10) + rng.normal(0, 2.0)
            elif scenario == "incomplete":
                value = base - 2.5*j + rng.normal(0, 3.0)
            else:
                value = base - 1.0*j + rng.normal(0, 2.5)

            value = float(np.clip(value, 7.0, 150.0))
            creat = float(np.clip(1.15 * (90 / max(value, 7.0)) + rng.normal(0, .07), .3, 9.0))
            missing = scenario == "incomplete" and j == visits - 2
            renal.append({
                "patient_id": pid, "measurement_date": date.date().isoformat(),
                "egfr_ml_min_1_73m2": np.nan if missing else round(value, 2),
                "creatinine_mg_dl": round(creat, 3),
                "measurement_sequence": j + 1, "synthetic_scenario": scenario
            })

        clinical.append({
            "patient_id": pid,
            "hypertension_simulated": int(pathology in ["Hipertensión", "Hipertensión y diabetes"]),
            "diabetes_simulated": int(pathology in ["Diabetes", "Hipertensión y diabetes"]),
            "bmi_simulated": round(float(np.clip(rng.normal(27, 4.5), 12, 65)), 1),
            "smoking_status_simulated": str(rng.choice(["never", "former", "current"]))
        })
    return pd.DataFrame(patients), pd.DataFrame(renal), pd.DataFrame(clinical)
