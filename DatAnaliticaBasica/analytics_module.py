"""
Módulo de Analítica de Sensores IoT
API-Ready: Listo para integrarse en FastAPI u otra API
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SensorAnalytics:
    """
    Clase de analítica para sensores IoT
    Diseñada para ser usada fácilmente en APIs
    """
    
    # Umbrales de alertas
    THRESHOLDS = {
        'air': {
            'co2_ppm': {
                'normal': (0, 800),
                'moderado': (800, 1000),
                'alto': (1000, 2000),
                'critico': (2000, float('inf'))
            },
            'temp_c': {
                'frio': (float('-inf'), 18),
                'normal': (18, 26),
                'calido': (26, 30),
                'muy_calido': (30, float('inf'))
            },
            'humidity_pct': {
                'bajo': (0, 30),
                'normal': (30, 70),
                'alto': (70, 100)
            },
            'pressure_hpa': {
                'bajo': (0, 980),
                'normal': (980, 1020),
                'alto': (1020, float('inf'))
            }
        },
        'sound': {
            'LAeq': {
                'silencioso': (0, 40),
                'normal': (40, 60),
                'moderado': (60, 75),
                'alto': (75, 85),
                'muy_alto': (85, float('inf'))
            },
            'LAImax': {
                'normal': (0, 80),
                'alto': (80, 95),
                'muy_alto': (95, float('inf'))
            }
        },
        'liquid': {
            'distance_cm': {
                'lleno': (0, 50),
                'medio': (50, 100),
                'bajo': (100, 150),
                'vacio': (150, float('inf'))
            }
        }
    }
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializa el módulo de analítica
        
        Args:
            data_path: Ruta donde están los archivos JSONL. 
                      Si es None, usa DATA_PATH del .env
        """
        self.data_path = data_path or os.getenv('DATA_PATH', '.')
        self.data: Dict[str, List[Dict]] = {}
        self.alerts: List[Dict] = []
        
        logger.info(f"📂 Ruta de datos configurada: {self.data_path}")
    
    def load_sensor_data(self, sensor_type: str) -> bool:
        """
        Carga datos de un tipo de sensor desde archivo JSONL
        
        Args:
            sensor_type: 'air', 'sound', o 'liquid'
        
        Returns:
            True si se cargó exitosamente, False si no
        """
        filename_map = {
            'air': os.getenv('AIR_FILE', 'air.jsonl'),
            'sound': os.getenv('SOUND_FILE', 'sound.jsonl'),
            'liquid': os.getenv('LIQUID_FILE', 'liquid.jsonl')
        }
        
        if sensor_type not in filename_map:
            logger.error(f"Tipo de sensor inválido: {sensor_type}")
            return False
        
        filepath = Path(self.data_path) / filename_map[sensor_type]
        
        if not filepath.exists():
            logger.warning(f"Archivo no encontrado: {filepath}")
            return False
        
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            
            self.data[sensor_type] = data
            logger.info(f"✓ Cargados {len(data)} registros de {sensor_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando {filepath}: {str(e)}")
            return False
    
    def load_all_sensors(self) -> Dict[str, bool]:
        """
        Carga datos de todos los sensores disponibles
        
        Returns:
            Diccionario con el estado de carga de cada sensor
        """
        results = {}
        for sensor_type in ['air', 'sound', 'liquid']:
            results[sensor_type] = self.load_sensor_data(sensor_type)
        return results
    
    def get_averages(self, sensor_type: str, minutes: Optional[int] = None) -> Dict:
        """
        Calcula promedios de las métricas
        
        Args:
            sensor_type: Tipo de sensor
            minutes: Últimos N minutos (None = todos los datos)
        
        Returns:
            Diccionario con estadísticas
        """
        if sensor_type not in self.data:
            return {"error": f"No hay datos cargados para {sensor_type}"}
        
        data = self.data[sensor_type]
        
        # Filtrar por tiempo si se especifica
        if minutes:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            data = [
                d for d in data 
                if datetime.fromisoformat(d['ts'].replace('Z', '+00:00')) >= cutoff_time
            ]
        
        if not data:
            return {"error": "No hay datos en el rango especificado"}
        
        stats = {
            "total_readings": len(data),
            "time_range": {
                "start": data[0]['ts'] if data else None,
                "end": data[-1]['ts'] if data else None
            }
        }
        
        # Calcular estadísticas según tipo de sensor
        if sensor_type == 'air':
            metrics = [d['metrics'] for d in data]
            stats.update({
                "co2": self._calc_stats([m['co2_ppm'] for m in metrics]),
                "temperature": self._calc_stats([m['temp_c'] for m in metrics]),
                "humidity": self._calc_stats([m['humidity_pct'] for m in metrics]),
                "pressure": self._calc_stats([m['pressure_hpa'] for m in metrics]),
                "battery": self._calc_stats([d['battery_pct'] for d in data])
            })
        
        elif sensor_type == 'sound':
            metrics = [d['metrics'] for d in data]
            stats.update({
                "LAeq": self._calc_stats([m['LAeq'] for m in metrics]),
                "LAI": self._calc_stats([m['LAI'] for m in metrics]),
                "LAImax": self._calc_stats([m['LAImax'] for m in metrics]),
                "battery": self._calc_stats([d['battery_pct'] for d in data])
            })
        
        elif sensor_type == 'liquid':
            metrics = [d['metrics'] for d in data]
            stats.update({
                "distance": self._calc_stats([m['distance_cm'] for m in metrics]),
                "battery": self._calc_stats([d['battery_pct'] for d in data])
            })
        
        return stats
    
    def _calc_stats(self, values: List[float]) -> Dict:
        """Calcula estadísticas básicas de una lista de valores"""
        if not values:
            return {"avg": None, "min": None, "max": None}
        
        return {
            "avg": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2)
        }
    
    def detect_alerts(self, sensor_type: str) -> List[Dict]:
        """
        Detecta alertas basadas en umbrales
        
        Args:
            sensor_type: Tipo de sensor
        
        Returns:
            Lista de alertas detectadas
        """
        if sensor_type not in self.data:
            return []
        
        alerts = []
        
        for record in self.data[sensor_type]:
            metrics = record['metrics']
            
            if sensor_type == 'air':
                # Alerta CO2
                co2 = metrics['co2_ppm']
                if co2 >= 2000:
                    alerts.append(self._create_alert(
                        record, 'CO2', 'CRÍTICO', co2, 2000,
                        f'CO2 crítico: {co2} ppm'
                    ))
                elif co2 >= 1000:
                    alerts.append(self._create_alert(
                        record, 'CO2', 'ALTO', co2, 1000,
                        f'CO2 alto: {co2} ppm'
                    ))
                
                # Alerta Temperatura
                temp = metrics['temp_c']
                if temp >= 30:
                    alerts.append(self._create_alert(
                        record, 'Temperatura', 'ALTO', temp, 30,
                        f'Temperatura alta: {temp}°C'
                    ))
                elif temp < 18:
                    alerts.append(self._create_alert(
                        record, 'Temperatura', 'BAJO', temp, 18,
                        f'Temperatura baja: {temp}°C'
                    ))
                
                # Alerta Humedad
                humidity = metrics['humidity_pct']
                if humidity >= 70:
                    alerts.append(self._create_alert(
                        record, 'Humedad', 'ALTO', humidity, 70,
                        f'Humedad alta: {humidity}%'
                    ))
            
            elif sensor_type == 'sound':
                # Alerta Ruido
                laeq = metrics['LAeq']
                if laeq >= 85:
                    alerts.append(self._create_alert(
                        record, 'Ruido', 'MUY_ALTO', laeq, 85,
                        f'Ruido muy alto: {laeq} dB'
                    ))
                elif laeq >= 75:
                    alerts.append(self._create_alert(
                        record, 'Ruido', 'ALTO', laeq, 75,
                        f'Ruido alto: {laeq} dB'
                    ))
                
                # Alerta Pico
                laimax = metrics['LAImax']
                if laimax >= 95:
                    alerts.append(self._create_alert(
                        record, 'Pico de Ruido', 'MUY_ALTO', laimax, 95,
                        f'Pico de ruido: {laimax} dB'
                    ))
            
            elif sensor_type == 'liquid':
                # Alerta Nivel bajo
                distance = metrics['distance_cm']
                if distance >= 150:
                    alerts.append(self._create_alert(
                        record, 'Nivel', 'CRÍTICO', distance, 150,
                        f'Tanque casi vacío: {distance} cm'
                    ))
                elif distance >= 100:
                    alerts.append(self._create_alert(
                        record, 'Nivel', 'BAJO', distance, 100,
                        f'Nivel bajo: {distance} cm'
                    ))
        
        self.alerts.extend(alerts)
        return alerts
    
    def _create_alert(self, record: Dict, alert_type: str, level: str, 
                      value: float, threshold: float, message: str) -> Dict:
        """Crea un objeto de alerta estandarizado"""
        return {
            "type": alert_type,
            "level": level,
            "value": value,
            "threshold": threshold,
            "message": message,
            "timestamp": record['ts'],
            "device_id": record['device_id'],
            "location": record['address'],
            "coordinates": record['location']
        }
    
    def get_alerts_by_level(self, level: Optional[str] = None) -> List[Dict]:
        """
        Obtiene alertas filtradas por nivel
        
        Args:
            level: Nivel de alerta ('CRÍTICO', 'ALTO', 'BAJO', None=todas)
        
        Returns:
            Lista de alertas
        """
        if level:
            return [a for a in self.alerts if a['level'] == level]
        return self.alerts
    
    def get_summary(self) -> Dict:
        """
        Genera un resumen completo de todos los sensores
        
        Returns:
            Diccionario con resumen completo
        """
        summary = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "sensors": {},
            "alerts": {
                "total": len(self.alerts),
                "by_level": {}
            }
        }
        
        # Estadísticas por sensor
        for sensor_type in self.data.keys():
            summary['sensors'][sensor_type] = {
                "total_readings": len(self.data[sensor_type]),
                "statistics": self.get_averages(sensor_type),
                "alerts_count": len([a for a in self.alerts 
                                    if a.get('device_id') in 
                                    [d['device_id'] for d in self.data[sensor_type]]])
            }
        
        # Alertas por nivel
        levels = ['CRÍTICO', 'ALTO', 'MUY_ALTO', 'BAJO']
        for level in levels:
            alerts_level = self.get_alerts_by_level(level)
            if alerts_level:
                summary['alerts']['by_level'][level] = len(alerts_level)
        
        return summary
    
    def get_latest_readings(self, sensor_type: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene las últimas N lecturas de un sensor
        
        Args:
            sensor_type: Tipo de sensor
            limit: Número de lecturas a retornar
        
        Returns:
            Lista de lecturas más recientes
        """
        if sensor_type not in self.data:
            return []
        
        return self.data[sensor_type][-limit:]
    
    def get_sensor_status(self, sensor_type: str) -> Dict:
        """
        Obtiene el estado actual de un sensor
        
        Args:
            sensor_type: Tipo de sensor
        
        Returns:
            Estado del sensor con última lectura y alertas activas
        """
        if sensor_type not in self.data or not self.data[sensor_type]:
            return {"error": f"No hay datos para {sensor_type}"}
        
        latest = self.data[sensor_type][-1]
        recent_alerts = [
            a for a in self.alerts 
            if a['device_id'] == latest['device_id']
        ][-5:]  # Últimas 5 alertas
        
        return {
            "device_id": latest['device_id'],
            "last_reading": latest,
            "recent_alerts": recent_alerts,
            "alert_count": len(recent_alerts)
        }
    
    def export_report(self, output_file: str = 'analytics_report.json') -> bool:
        """
        Exporta un reporte completo en JSON
        
        Args:
            output_file: Nombre del archivo de salida
        
        Returns:
            True si se exportó exitosamente
        """
        try:
            report = {
                "generated_at": datetime.utcnow().isoformat() + 'Z',
                "summary": self.get_summary(),
                "all_alerts": self.alerts,
                "statistics_by_sensor": {
                    sensor_type: self.get_averages(sensor_type)
                    for sensor_type in self.data.keys()
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Reporte exportado: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando reporte: {str(e)}")
            return False


# ============================================================
# API Helper Functions (para usar en FastAPI)
# ============================================================

class AnalyticsAPI:
    """
    Wrapper para usar fácilmente en FastAPI
    Singleton pattern para mantener datos cargados
    """
    _instance = None
    _analytics = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_analytics(self) -> SensorAnalytics:
        """Obtiene instancia de SensorAnalytics (singleton)"""
        if self._analytics is None:
            self._analytics = SensorAnalytics()
            self._analytics.load_all_sensors()
        return self._analytics
    
    def refresh_data(self) -> Dict[str, bool]:
        """Recarga todos los datos"""
        if self._analytics is None:
            self._analytics = SensorAnalytics()
        return self._analytics.load_all_sensors()


# Instancia global para usar en APIs
analytics_api = AnalyticsAPI()
analytics_sensor_api = SensorAnalytics()


# ============================================================
# Ejemplo de uso standalone
# ============================================================

def main():
    """Ejemplo de uso del módulo"""
    print("\n" + "="*70)
    print("📊 MÓDULO DE ANALÍTICA DE SENSORES")
    print("="*70)
    
    # Crear instancia
    analytics = SensorAnalytics()
    
    # Cargar datos
    print("\n🔄 Cargando datos...")
    load_results = analytics.load_all_sensors()
    for sensor, success in load_results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {sensor}")
    
    # Calcular estadísticas
    print("\n📊 Estadísticas:")
    for sensor_type in analytics.data.keys():
        print(f"\n  🔹 {sensor_type.upper()}")
        stats = analytics.get_averages(sensor_type)
        print(f"     Total lecturas: {stats['total_readings']}")
    
    # Detectar alertas
    print("\n⚠️  Detectando alertas...")
    total_alerts = 0
    for sensor_type in analytics.data.keys():
        alerts = analytics.detect_alerts(sensor_type)
        print(f"  {sensor_type}: {len(alerts)} alertas")
        total_alerts += len(alerts)
    
    # Mostrar alertas críticas
    critical_alerts = analytics.get_alerts_by_level('CRÍTICO')
    if critical_alerts:
        print(f"\n🚨 Alertas CRÍTICAS ({len(critical_alerts)}):")
        for alert in critical_alerts[:5]:
            print(f"  • {alert['message']} - {alert['location']}")
    
    # Exportar reporte
    print("\n📄 Exportando reporte...")
    analytics.export_report()
    
    print("\n" + "="*70)
    print(f"✅ Análisis completado. Total alertas: {total_alerts}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()