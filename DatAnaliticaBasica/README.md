# 📊 Módulo de Analítica de Sensores IoT - API Ready

Sistema de analítica para sensores IoT con arquitectura lista para integrarse en APIs (FastAPI, Flask, etc.)

## 🎯 Características

✅ **Listo para APIs**: Diseñado como clase importable para FastAPI  
✅ **Lee archivos JSONL**: Formato de salida del ETL  
✅ **Configuración por .env**: Rutas configurables  
✅ **Cálculo de promedios**: Min, max, avg para todas las métricas  
✅ **Sistema de alertas**: Detección automática por umbrales  
✅ **Singleton pattern**: Mantiene datos en memoria  
✅ **Múltiples sensores**: Air, Sound, Liquid  

## 📁 Estructura de Archivos

```
proyecto/
├── analytics_module.py          # Módulo principal (importable)
├── fastapi_analytics_api.py     # Ejemplo FastAPI completo
├── .env                         # Configuración
├── requirements.txt             # Dependencias
└── data/                        # Archivos JSONL
    ├── air.jsonl
    ├── sound.jsonl
    └── liquid.jsonl
```

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar rutas en .env
cp .env.example .env
nano .env
```

## ⚙️ Configuración (.env)

```env
# Directorio de datos
DATA_PATH=./data

# Nombres de archivos JSONL
AIR_FILE=air.jsonl
SOUND_FILE=sound.jsonl
LIQUID_FILE=liquid.jsonl

# Configuración API (opcional)
API_HOST=0.0.0.0
API_PORT=8000
```

## 💻 Uso Directo (Sin API)

### Ejemplo Básico

```python
from analytics_module import SensorAnalytics

# Crear instancia
analytics = SensorAnalytics()

# Cargar datos
analytics.load_all_sensors()

# Obtener promedios
stats = analytics.get_averages('air')
print(stats)
# Output: {
#   "total_readings": 10,
#   "co2": {"avg": 856.8, "min": 519.0, "max": 1195.1},
#   "temperature": {"avg": 22.48, "min": 15.8, "max": 28.9},
#   ...
# }

# Detectar alertas
alerts = analytics.detect_alerts('air')
print(f"Alertas: {len(alerts)}")

# Obtener resumen completo
summary = analytics.get_summary()
```

### Filtrar por Tiempo

```python
# Últimos 30 minutos
stats = analytics.get_averages('sound', minutes=30)

# Últimas 2 horas
stats = analytics.get_averages('air', minutes=120)
```

### Filtrar Alertas

```python
# Todas las alertas críticas
criticas = analytics.get_alerts_by_level('CRÍTICO')

# Todas las alertas altas
altas = analytics.get_alerts_by_level('ALTO')
```

### Exportar Reporte

```python
analytics.export_report('mi_reporte.json')
```

## 🌐 Uso con FastAPI

### Iniciar el Servidor

```bash
python fastapi_analytics_api.py
```

O con uvicorn:

```bash
uvicorn fastapi_analytics_api:app --reload --port 8000
```

### Endpoints Disponibles

#### 1. **Resumen General**
```bash
GET /analytics/summary
```

**Respuesta:**
```json
{
  "timestamp": "2024-11-20T10:30:00Z",
  "sensors": {
    "air": {
      "total_readings": 10,
      "statistics": {...},
      "alerts_count": 3
    }
  },
  "alerts": {
    "total": 8,
    "by_level": {
      "ALTO": 5,
      "CRÍTICO": 3
    }
  }
}
```

#### 2. **Promedios por Sensor**
```bash
GET /analytics/air/averages
GET /analytics/air/averages?minutes=60
```

**Respuesta:**
```json
{
  "sensor_type": "air",
  "time_filter": "últimos 60 minutos",
  "statistics": {
    "total_readings": 10,
    "co2": {"avg": 856.8, "min": 519.0, "max": 1195.1},
    "temperature": {"avg": 22.48, "min": 15.8, "max": 28.9}
  }
}
```

#### 3. **Alertas por Sensor**
```bash
GET /analytics/air/alerts
GET /analytics/air/alerts?level=CRÍTICO
```

**Respuesta:**
```json
{
  "sensor_type": "air",
  "level_filter": "CRÍTICO",
  "total_alerts": 2,
  "alerts": [
    {
      "type": "CO2",
      "level": "CRÍTICO",
      "value": 2150.0,
      "threshold": 2000,
      "message": "CO2 crítico: 2150.0 ppm",
      "timestamp": "2024-11-20T10:15:00Z",
      "device_id": "EMS-6993",
      "location": "Cristo de la Concordia",
      "coordinates": {"lat": -17.384, "lon": -66.135}
    }
  ]
}
```

#### 4. **Estado del Sensor**
```bash
GET /analytics/air/status
```

**Respuesta:**
```json
{
  "device_id": "EMS-6993",
  "last_reading": {
    "device_id": "EMS-6993",
    "sensor_type": "air",
    "ts": "2024-11-20T10:30:00Z",
    "metrics": {
      "co2_ppm": 850.5,
      "temp_c": 23.2
    }
  },
  "recent_alerts": [...],
  "alert_count": 3
}
```

#### 5. **Últimas Lecturas**
```bash
GET /analytics/sound/latest?limit=5
```

#### 6. **Todas las Alertas**
```bash
GET /analytics/alerts/all
GET /analytics/alerts/all?level=ALTO
```

#### 7. **Recargar Datos**
```bash
POST /analytics/refresh
```

#### 8. **Exportar Reporte**
```bash
GET /analytics/export
```

## 🔧 Integración en Tu API

### Opción 1: Importar Directamente

```python
from fastapi import FastAPI
from analytics_module import analytics_api

app = FastAPI()

@app.get("/mi-endpoint")
def mi_funcion():
    # Obtener instancia de analytics
    analytics = analytics_api.get_analytics()
    
    # Usar métodos
    stats = analytics.get_averages('air')
    alerts = analytics.detect_alerts('sound')
    
    return {
        "stats": stats,
        "alerts": alerts
    }
```

### Opción 2: Crear Tu Propia Instancia

```python
from analytics_module import SensorAnalytics

# Crear instancia personalizada
analytics = SensorAnalytics(data_path="/ruta/custom")

# Cargar datos específicos
analytics.load_sensor_data('air')

# Usar métodos
stats = analytics.get_averages('air')
```

## 📊 Métodos Disponibles

### `load_sensor_data(sensor_type: str) -> bool`
Carga datos de un sensor específico.

### `load_all_sensors() -> Dict[str, bool]`
Carga datos de todos los sensores.

### `get_averages(sensor_type: str, minutes: Optional[int]) -> Dict`
Calcula estadísticas (promedio, min, max).

### `detect_alerts(sensor_type: str) -> List[Dict]`
Detecta alertas basadas en umbrales.

### `get_alerts_by_level(level: Optional[str]) -> List[Dict]`
Filtra alertas por nivel.

### `get_summary() -> Dict`
Genera resumen completo de todos los sensores.

### `get_latest_readings(sensor_type: str, limit: int) -> List[Dict]`
Obtiene últimas N lecturas.

### `get_sensor_status(sensor_type: str) -> Dict`
Estado actual del sensor con última lectura.

### `export_report(output_file: str) -> bool`
Exporta reporte completo en JSON.

## 🎚️ Umbrales de Alertas

### Sensor de Aire (air)

| Métrica | Normal | Moderado | Alto | Crítico |
|---------|--------|----------|------|---------|
| **CO2 (ppm)** | 0-800 | 800-1000 | 1000-2000 | >2000 |
| **Temperatura (°C)** | 18-26 | - | 26-30 | >30 |
| **Humedad (%)** | 30-70 | - | >70 | - |
| **Presión (hPa)** | 980-1020 | - | >1020 | <980 |

### Sensor de Sonido (sound)

| Métrica | Normal | Moderado | Alto | Muy Alto |
|---------|--------|----------|------|----------|
| **LAeq (dB)** | 40-60 | 60-75 | 75-85 | >85 |
| **LAImax (dB)** | 0-80 | - | 80-95 | >95 |

### Sensor de Líquido (liquid)

| Distancia (cm) | Estado |
|----------------|--------|
| 0-50 | Lleno |
| 50-100 | Medio |
| 100-150 | Bajo |
| >150 | Vacío (Crítico) |

## 🔍 Formato de Datos

### Entrada (JSONL)

**air.jsonl:**
```json
{"device_id": "EMS-6993", "sensor_type": "air", "ts": "2024-11-20T10:00:00Z", 
 "metrics": {"co2_ppm": 850.5, "temp_c": 23.2, "humidity_pct": 45.0, "pressure_hpa": 1013.2},
 "battery_pct": 88.9, "status": "Normal", "address": "Cristo de la Concordia",
 "location": {"lat": -17.384, "lon": -66.135}}
```

### Salida (Resumen)

```json
{
  "timestamp": "2024-11-20T10:30:00Z",
  "sensors": {
    "air": {
      "total_readings": 10,
      "statistics": {
        "co2": {"avg": 856.8, "min": 519.0, "max": 1195.1}
      }
    }
  },
  "alerts": {"total": 8}
}
```

## 📝 Ejemplos de Uso Real

### 1. Dashboard en Tiempo Real

```python
from analytics_module import analytics_api
import time

while True:
    analytics = analytics_api.get_analytics()
    analytics_api.refresh_data()
    
    # Obtener estado actual
    air_status = analytics.get_sensor_status('air')
    
    # Detectar nuevas alertas
    alerts = analytics.detect_alerts('air')
    
    if alerts:
        print(f"🚨 {len(alerts)} nuevas alertas!")
    
    time.sleep(60)  # Actualizar cada minuto
```

### 2. Reporte Diario Automático

```python
from analytics_module import SensorAnalytics
from datetime import datetime

analytics = SensorAnalytics()
analytics.load_all_sensors()

# Detectar todas las alertas
for sensor in ['air', 'sound', 'liquid']:
    analytics.detect_alerts(sensor)

# Exportar con timestamp
date_str = datetime.now().strftime('%Y%m%d')
analytics.export_report(f'reporte_diario_{date_str}.json')
```

### 3. Monitoreo de Umbrales Críticos

```python
analytics = analytics_api.get_analytics()

# Solo alertas críticas
critical = analytics.get_alerts_by_level('CRÍTICO')

if critical:
    # Enviar notificación
    for alert in critical:
        send_notification(
            title=f"⚠️ {alert['type']} Crítico",
            message=alert['message'],
            location=alert['location']
        )
```

## 🐛 Solución de Problemas

### Error: "No hay datos para X sensor"
- Verifica que el archivo JSONL existe en DATA_PATH
- Comprueba los nombres de archivo en .env
- Revisa permisos de lectura del directorio

### Error: "Archivo no encontrado"
- Confirma la ruta en DATA_PATH
- Verifica que los archivos tengan extensión .jsonl
- Usa rutas absolutas si hay problemas con relativas

### Alertas no se detectan
- Verifica que llamaste `detect_alerts()` para ese sensor
- Confirma que los valores están en el rango de los umbrales
- Revisa los logs para ver errores

### API no inicia
- Verifica que FastAPI y uvicorn estén instalados
- Comprueba que el puerto no esté en uso
- Revisa los logs de inicio

## 🚀 Despliegue

### Desarrollo
```bash
python fastapi_analytics_api.py
```

### Producción
```bash
gunicorn fastapi_analytics_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "fastapi_analytics_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📞 Soporte

Para problemas o preguntas:
1. Verifica los logs del módulo
2. Revisa el formato de los archivos JSONL
3. Confirma la configuración en .env
4. Prueba los ejemplos de uso básico primero