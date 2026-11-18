from src.model_integration.contract import load_predictor_contract
features = load_predictor_contract()
print("Modelo de referencia: RandomForest_full_clinical")
print("Familia primaria: full_clinical")
print("Predictores efectivos:", len(features))
for i, feature in enumerate(features, 1):
    print(f"{i:02d}. {feature}")
print("\nNo se cargó el archivo joblib ni se generaron predicciones.")
