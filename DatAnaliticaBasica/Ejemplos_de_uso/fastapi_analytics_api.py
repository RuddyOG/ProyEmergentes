"""
Ejemplo de integración del módulo de analítica con FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn
import os
from dotenv import load_dotenv

# Importar el módulo de analítica
from analytics_module import analytics_api, analytics_sensor_api

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Sensor Analytics API",
    description="API de analítica para sensores IoT (Aire, Sonido, Líquido)",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "service": "Sensor Analytics API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "summary": "/analytics/summary",
            "averages": "/analytics/{sensor_type}/averages",
            "alerts": "/analytics/{sensor_type}/alerts",
            "status": "/analytics/{sensor_type}/status",
            "latest": "/analytics/{sensor_type}/latest"
        }
    }


@app.get("/analytics/summary")
def get_summary():
    """
    Obtiene un resumen completo de todos los sensores
    
    Returns:
        Resumen con estadísticas y alertas de todos los sensores
    """
    try:
        analytics = analytics_api.get_analytics()
        
        # Detectar alertas si no se ha hecho
        if not analytics.alerts:
            for sensor_type in analytics.data.keys():
                analytics.detect_alerts(sensor_type)
        
        return analytics.get_summary()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/{sensor_type}/averages")
def get_averages(
    sensor_type: str,
    minutes: Optional[int] = Query(None, description="Últimos N minutos")
):
    """
    Obtiene los promedios de un sensor específico
    
    Args:
        sensor_type: Tipo de sensor (air, sound, liquid)
        minutes: Filtrar por últimos N minutos (opcional)
    
    Returns:
        Estadísticas del sensor (promedio, min, max)
    """
    if sensor_type not in ['air', 'sound', 'liquid']:
        raise HTTPException(
            status_code=400, 
            detail="Tipo de sensor inválido. Use: air, sound, o liquid"
        )
    
    try:
        analytics = analytics_api.get_analytics()
        stats = analytics.get_averages(sensor_type, minutes)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "sensor_type": sensor_type,
            "time_filter": f"últimos {minutes} minutos" if minutes else "todos los datos",
            "statistics": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/{sensor_type}/alerts")
def get_alerts(
    sensor_type: str,
    level: Optional[str] = Query(None, description="Filtrar por nivel")
):
    """
    Obtiene las alertas de un sensor específico
    
    Args:
        sensor_type: Tipo de sensor (air, sound, liquid)
        level: Filtrar por nivel (CRÍTICO, ALTO, BAJO) - opcional
    
    Returns:
        Lista de alertas detectadas
    """
    if sensor_type not in ['air', 'sound', 'liquid']:
        raise HTTPException(
            status_code=400,
            detail="Tipo de sensor inválido. Use: air, sound, o liquid"
        )
    
    try:
        analytics = analytics_api.get_analytics()
        
        # Detectar alertas si no existen
        alerts = analytics.detect_alerts(sensor_type)
        
        # Filtrar por nivel si se especifica
        if level:
            alerts = [a for a in alerts if a['level'] == level.upper()]
        
        return {
            "sensor_type": sensor_type,
            "level_filter": level if level else "todos",
            "total_alerts": len(alerts),
            "alerts": alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/{sensor_type}/status")
def get_sensor_status(sensor_type: str):
    """
    Obtiene el estado actual de un sensor
    
    Args:
        sensor_type: Tipo de sensor (air, sound, liquid)
    
    Returns:
        Estado del sensor con última lectura y alertas recientes
    """
    if sensor_type not in ['air', 'sound', 'liquid']:
        raise HTTPException(
            status_code=400,
            detail="Tipo de sensor inválido. Use: air, sound, o liquid"
        )
    
    try:
        analytics = analytics_api.get_analytics()
        status = analytics.get_sensor_status(sensor_type)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/{sensor_type}/latest")
def get_latest_readings(
    sensor_type: str,
    limit: int = Query(10, ge=1, le=100, description="Número de lecturas")
):
    """
    Obtiene las últimas N lecturas de un sensor
    
    Args:
        sensor_type: Tipo de sensor (air, sound, liquid)
        limit: Número de lecturas a retornar (1-100)
    
    Returns:
        Últimas N lecturas del sensor
    """
    if sensor_type not in ['air', 'sound', 'liquid']:
        raise HTTPException(
            status_code=400,
            detail="Tipo de sensor inválido. Use: air, sound, o liquid"
        )
    
    try:
        analytics = analytics_api.get_analytics()
        readings = analytics.get_latest_readings(sensor_type, limit)
        
        return {
            "sensor_type": sensor_type,
            "total": len(readings),
            "readings": readings
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analytics/refresh")
def refresh_data():
    """
    Recarga todos los datos de los sensores
    
    Returns:
        Estado de la recarga para cada sensor
    """
    try:
        results = analytics_api.refresh_data()
        
        return {
            "message": "Datos recargados",
            "results": results,
            "success": all(results.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/alerts/all")
def get_all_alerts(level: Optional[str] = Query(None, description="Filtrar por nivel")):
    """
    Obtiene todas las alertas de todos los sensores
    
    Args:
        level: Filtrar por nivel (CRÍTICO, ALTO, BAJO) - opcional
    
    Returns:
        Todas las alertas, opcionalmente filtradas por nivel
    """
    try:
        analytics = analytics_api.get_analytics()
        
        # Detectar alertas de todos los sensores si no existen
        if not analytics.alerts:
            for sensor_type in analytics.data.keys():
                analytics.detect_alerts(sensor_type)
        
        alerts = analytics.get_alerts_by_level(level.upper() if level else None)
        
        return {
            "level_filter": level if level else "todos",
            "total_alerts": len(alerts),
            "alerts": alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/export")
def export_report():
    """
    Genera y exporta un reporte completo en JSON
    
    Returns:
        Confirmación de exportación
    """
    try:
        analytics = analytics_api.get_analytics()
        
        # Detectar alertas antes de exportar
        for sensor_type in analytics.data.keys():
            analytics.detect_alerts(sensor_type)
        
        success = analytics.export_report('analytics_report.json')
        
        if success:
            return {
                "message": "Reporte exportado exitosamente",
                "file": "analytics_report.json"
            }
        else:
            raise HTTPException(status_code=500, detail="Error al exportar reporte")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Startup Event
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Cargar datos al iniciar la aplicación"""
    print("\n🚀 Iniciando Sensor Analytics API...")
    print("📂 Cargando datos de sensores...")
    
    analytics = analytics_api.get_analytics()
    results = analytics.load_all_sensors()
    
    for sensor, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {sensor}")
    
    print("✅ API lista!\n")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    reload = os.getenv('API_RELOAD', 'false').lower() == 'true'
    
    uvicorn.run(
        "fastapi_analytics_api:app",
        host=host,
        port=port,
        reload=reload
    )