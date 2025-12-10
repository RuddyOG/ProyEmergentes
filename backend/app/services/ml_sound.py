# backend/app/services/ml_sound.py
import os
from datetime import datetime
from typing import Tuple
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sound_regressor.pkl")

_model_bundle = None

def load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"No se encontró el modelo de sonido en {MODEL_PATH}. "
                f"Ejecuta primero: python -m analytics.train_sound_model"
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle

def classify_noise(laeq_db: float) -> str:
    if laeq_db < 55:
        return "BAJO"
    elif laeq_db < 65:
        return "MODERADO"
    elif laeq_db < 75:
        return "ALTO"
    else:
        return "CRÍTICO"

def predict_sound(hour: int | None = None, dayofweek: int | None = None) -> Tuple[float, str]:
    bundle = load_model()
    model = bundle["model"]
    feature_cols = bundle["features"]

    now = datetime.utcnow()
    hour = hour if hour is not None else now.hour
    dayofweek = dayofweek if dayofweek is not None else now.weekday()

    feature_map = {
        "hour_of_day": hour,
        "dayofweek": dayofweek,
    }
    X = [[feature_map[col] for col in feature_cols]]

    laeq_pred = float(model.predict(X)[0])
    risk = classify_noise(laeq_pred)
    return laeq_pred, risk
