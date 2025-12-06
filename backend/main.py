from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import sensors, auth

# Crear aplicación FastAPI
app = FastAPI(
    title="GAMC Sensor Monitoring API",
    version="1.0.0",
    description="API para monitoreo de sensores IoT - GAMC Cochabamba"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(sensors.router)

@app.get("/", tags=["root"])
def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "GAMC Sensor Monitoring API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "auth": "/api/auth",
            "sensors": "/api",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/status", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GAMC API"
    }

# Para ejecutar con uvicorn
# uvicorn main:app --reload --host 0.0.0.0 --port 8000