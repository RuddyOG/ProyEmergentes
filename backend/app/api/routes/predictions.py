# backend/app/api/routes/predictions.py
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.ml_air import predict_co2

router = APIRouter(prefix="/predictions", tags=["ML"])

class AirPredictionInput(BaseModel):
    temperature_c: float
    humidity_pct: float
    measured_at: datetime | None = None

@router.post("/air")
def predict_air(payload: AirPredictionInput):
    """
    Predice CO2 (ppm) y nivel de riesgo a partir de temperatura y humedad.
    """
    co2_pred, risk = predict_co2(
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        measured_at=payload.measured_at
    )

    return {
        "input": {
            "temperature_c": payload.temperature_c,
            "humidity_pct": payload.humidity_pct,
            "measured_at": (
                payload.measured_at.isoformat() if payload.measured_at else None
            )
        },
        "predicted_co2_ppm": co2_pred,
        "risk_level": risk,
    }
from backend.app.services.ml_sound import predict_sound
from backend.app.services.ml_underground import predict_moisture

class SoundPredictionInput(BaseModel):
    hour: int | None = None
    dayofweek: int | None = None

@router.post("/sound")
def predict_sound_endpoint(payload: SoundPredictionInput):
    laeq, risk = predict_sound(
        hour=payload.hour,
        dayofweek=payload.dayofweek
    )
    return {
        "input": payload.dict(),
        "predicted_laeq_db": laeq,
        "risk_level": risk,
    }

class UndergroundPredictionInput(BaseModel):
    moisture_pct: float
    measured_at: datetime | None = None

@router.post("/underground")
def predict_underground_endpoint(payload: UndergroundPredictionInput):
    moisture_pred, risk = predict_moisture(
        moisture_pct=payload.moisture_pct,
        measured_at=payload.measured_at,
    )
    return {
        "input": payload.dict(),
        "predicted_moisture": moisture_pred,
        "risk_level": risk,
    }
