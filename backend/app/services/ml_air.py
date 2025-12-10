# backend/app/services/ml_air.py

import os
from datetime import datetime
from typing import Tuple

import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "air_co2_regressor.pkl")

_model_bundle = None

def load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"No se encontró el modelo de aire en {MODEL_PATH}. "
                f"Ejecuta primero: python -m analytics.train_air_model"
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle

def classify_risk(co2_ppm: float) -> str:
    """
    Clasificación simple de riesgo de CO2.
    Puedes ajustar los umbrales según norma / criterio.
    """
    if co2_ppm <= 800:
        return "BAJO"
    elif co2_ppm <= 1200:
        return "MODERADO"
    elif co2_ppm <= 2000:
        return "ALTO"
    else:
        return "CRÍTICO"

def predict_co2(
    temperature_c: float,
    humidity_pct: float,
    measured_at: datetime | None = None
) -> Tuple[float, str]:
    """
    Realiza la predicción de CO2 a partir de temperatura, humedad y timestamp.
    Si no se pasa measured_at, se asume ahora().
    Devuelve (co2_ppm_estimado, nivel_riesgo).
    """
    bundle = load_model()
    model = bundle["model"]
    feature_cols = bundle["features"]

    if measured_at is None:
        measured_at = datetime.utcnow()

    hour = measured_at.hour
    dayofweek = measured_at.weekday()

    # Ordenar las features según feature_cols
    feature_map = {
        "temperature_c": temperature_c,
        "humidity_pct": humidity_pct,
        "hour": hour,
        "dayofweek": dayofweek,
    }
    X = [[feature_map[col] for col in feature_cols]]

    co2_pred = float(model.predict(X)[0])
    risk = classify_risk(co2_pred)
    return co2_pred, risk
