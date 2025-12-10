# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers (los agregaremos más abajo)
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.sensors import router as sensors_router
#from backend.app.api.routes.predictions import router as predictions_router

app = FastAPI(title="GAMC Sensor API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root ---
@app.get("/")
def root():
    return {"msg": "Backend GAMC funcionando correctamente"}

# --- Rutas ---
app.include_router(health_router)
app.include_router(sensors_router)
#app.include_router(predictions_router)
