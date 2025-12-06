"""
Ejemplos prácticos de uso del módulo de analítica
"""

from analytics_module import SensorAnalytics, analytics_api
import json


# ============================================================
# EJEMPLO 1: Uso Básico
# ============================================================

def ejemplo_uso_basico():
    """Uso más simple del módulo"""
    print("\n" + "="*70)
    print("EJEMPLO 1: Uso Básico")
    print("="*70)
    
    # Crear instancia y cargar datos
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    # Obtener promedios de aire
    stats = analytics.get_averages('air')
    print(f"\n📊 Estadísticas de sensor de aire:")
    print(f"  Total lecturas: {stats['total_readings']}")
    print(f"  CO2 promedio: {stats['co2']['avg']} ppm")
    print(f"  Temperatura promedio: {stats['temperature']['avg']}°C")
    
    # Detectar alertas
    alerts = analytics.detect_alerts('air')
    print(f"\n⚠️  Alertas detectadas: {len(alerts)}")
    if alerts:
        print(f"  Primera alerta: {alerts[0]['message']}")


# ============================================================
# EJEMPLO 2: Análisis por Tiempo
# ============================================================

def ejemplo_analisis_temporal():
    """Análisis de datos en ventanas de tiempo"""
    print("\n" + "="*70)
    print("EJEMPLO 2: Análisis Temporal")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_sensor_data('sound')
    
    # Últimos 30 minutos
    stats_30min = analytics.get_averages('sound', minutes=30)
    print(f"\n📊 Últimos 30 minutos:")
    print(f"  LAeq promedio: {stats_30min.get('LAeq', {}).get('avg', 'N/A')} dB")
    
    # Todos los datos
    stats_all = analytics.get_averages('sound')
    print(f"\n📊 Todos los datos:")
    print(f"  LAeq promedio: {stats_all.get('LAeq', {}).get('avg', 'N/A')} dB")


# ============================================================
# EJEMPLO 3: Filtrado de Alertas
# ============================================================

def ejemplo_filtrado_alertas():
    """Filtrar alertas por nivel de severidad"""
    print("\n" + "="*70)
    print("EJEMPLO 3: Filtrado de Alertas")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    # Detectar alertas de todos los sensores
    for sensor in ['air', 'sound', 'liquid']:
        analytics.detect_alerts(sensor)
    
    # Alertas críticas
    criticas = analytics.get_alerts_by_level('CRÍTICO')
    print(f"\n🚨 Alertas CRÍTICAS: {len(criticas)}")
    for alert in criticas[:3]:
        print(f"  • {alert['message']}")
    
    # Alertas altas
    altas = analytics.get_alerts_by_level('ALTO')
    print(f"\n⚠️  Alertas ALTAS: {len(altas)}")
    for alert in altas[:3]:
        print(f"  • {alert['message']}")


# ============================================================
# EJEMPLO 4: Resumen Completo
# ============================================================

def ejemplo_resumen_completo():
    """Generar resumen de todos los sensores"""
    print("\n" + "="*70)
    print("EJEMPLO 4: Resumen Completo")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    # Detectar alertas
    for sensor in ['air', 'sound', 'liquid']:
        analytics.detect_alerts(sensor)
    
    # Obtener resumen
    summary = analytics.get_summary()
    
    print(f"\n📊 Resumen generado: {summary['timestamp']}")
    print(f"\nSensores analizados:")
    for sensor, data in summary['sensors'].items():
        print(f"  • {sensor}: {data['total_readings']} lecturas, "
              f"{data['alerts_count']} alertas")
    
    print(f"\nTotal de alertas: {summary['alerts']['total']}")
    if summary['alerts']['by_level']:
        print("Por nivel:")
        for level, count in summary['alerts']['by_level'].items():
            print(f"  • {level}: {count}")


# ============================================================
# EJEMPLO 5: Estado de Sensores
# ============================================================

def ejemplo_estado_sensores():
    """Consultar estado actual de cada sensor"""
    print("\n" + "="*70)
    print("EJEMPLO 5: Estado de Sensores")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    for sensor_type in ['air', 'sound', 'liquid']:
        status = analytics.get_sensor_status(sensor_type)
        
        if "error" not in status:
            print(f"\n🔹 {sensor_type.upper()}")
            print(f"  Device ID: {status['device_id']}")
            print(f"  Última lectura: {status['last_reading']['ts']}")
            print(f"  Alertas recientes: {status['alert_count']}")


# ============================================================
# EJEMPLO 6: Exportar Reporte
# ============================================================

def ejemplo_exportar_reporte():
    """Exportar reporte completo a JSON"""
    print("\n" + "="*70)
    print("EJEMPLO 6: Exportar Reporte")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    # Detectar todas las alertas
    for sensor in ['air', 'sound', 'liquid']:
        analytics.detect_alerts(sensor)
    
    # Exportar
    success = analytics.export_report('ejemplo_reporte.json')
    
    if success:
        print("\n✅ Reporte exportado: ejemplo_reporte.json")
        
        # Leer y mostrar parte del reporte
        with open('ejemplo_reporte.json', 'r') as f:
            report = json.load(f)
        
        print(f"\nContenido del reporte:")
        print(f"  • Generado: {report['generated_at']}")
        print(f"  • Total alertas: {report['summary']['alerts']['total']}")


# ============================================================
# EJEMPLO 7: Uso con Singleton (para APIs)
# ============================================================

def ejemplo_singleton_api():
    """Uso del patrón singleton para APIs"""
    print("\n" + "="*70)
    print("EJEMPLO 7: Singleton para APIs")
    print("="*70)
    
    # Primera llamada - carga los datos
    analytics1 = analytics_api.get_analytics()
    print(f"\nPrimera instancia - ID: {id(analytics1)}")
    
    # Segunda llamada - misma instancia
    analytics2 = analytics_api.get_analytics()
    print(f"Segunda instancia - ID: {id(analytics2)}")
    print(f"¿Son la misma instancia? {analytics1 is analytics2}")
    
    # Refrescar datos
    print("\n🔄 Refrescando datos...")
    results = analytics_api.refresh_data()
    for sensor, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {sensor}")


# ============================================================
# EJEMPLO 8: Últimas Lecturas
# ============================================================

def ejemplo_ultimas_lecturas():
    """Obtener últimas N lecturas"""
    print("\n" + "="*70)
    print("EJEMPLO 8: Últimas Lecturas")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_sensor_data('air')
    
    # Últimas 5 lecturas
    readings = analytics.get_latest_readings('air', limit=5)
    
    print(f"\n📋 Últimas {len(readings)} lecturas de aire:")
    for i, reading in enumerate(readings, 1):
        metrics = reading['metrics']
        print(f"\n  {i}. {reading['ts']}")
        print(f"     CO2: {metrics['co2_ppm']} ppm")
        print(f"     Temp: {metrics['temp_c']}°C")
        print(f"     Status: {reading['status']}")


# ============================================================
# EJEMPLO 9: Análisis Personalizado
# ============================================================

def ejemplo_analisis_personalizado():
    """Análisis personalizado con los datos cargados"""
    print("\n" + "="*70)
    print("EJEMPLO 9: Análisis Personalizado")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_sensor_data('air')
    
    # Acceder a los datos directamente
    data = analytics.data['air']
    
    # Análisis personalizado: CO2 sobre 1000 ppm
    high_co2 = [d for d in data if d['metrics']['co2_ppm'] > 1000]
    print(f"\n📊 Lecturas con CO2 > 1000 ppm: {len(high_co2)}")
    
    # Temperatura promedio cuando CO2 es alto
    if high_co2:
        avg_temp = sum(d['metrics']['temp_c'] for d in high_co2) / len(high_co2)
        print(f"📊 Temperatura promedio en esas lecturas: {avg_temp:.1f}°C")
    
    # Batería baja
    low_battery = [d for d in data if d['battery_pct'] < 85]
    print(f"🔋 Lecturas con batería < 85%: {len(low_battery)}")


# ============================================================
# EJEMPLO 10: Comparación de Sensores
# ============================================================

def ejemplo_comparacion_sensores():
    """Comparar estadísticas entre sensores"""
    print("\n" + "="*70)
    print("EJEMPLO 10: Comparación de Sensores")
    print("="*70)
    
    analytics = SensorAnalytics()
    analytics.load_all_sensors()
    
    print("\n📊 Comparación de batería entre sensores:")
    for sensor_type in ['air', 'sound', 'liquid']:
        stats = analytics.get_averages(sensor_type)
        if 'battery' in stats:
            print(f"\n  {sensor_type.upper()}:")
            print(f"    Promedio: {stats['battery']['avg']}%")
            print(f"    Mínimo: {stats['battery']['min']}%")
            print(f"    Máximo: {stats['battery']['max']}%")


# ============================================================
# EJECUTAR TODOS LOS EJEMPLOS
# ============================================================

def ejecutar_todos():
    """Ejecuta todos los ejemplos"""
    ejemplos = [
        ejemplo_uso_basico,
        ejemplo_analisis_temporal,
        ejemplo_filtrado_alertas,
        ejemplo_resumen_completo,
        ejemplo_estado_sensores,
        ejemplo_exportar_reporte,
        ejemplo_singleton_api,
        ejemplo_ultimas_lecturas,
        ejemplo_analisis_personalizado,
        ejemplo_comparacion_sensores
    ]
    
    print("\n" + "🚀 EJEMPLOS DE USO DEL MÓDULO DE ANALÍTICA\n")
    
    for ejemplo in ejemplos:
        try:
            ejemplo()
        except Exception as e:
            print(f"\n❌ Error en {ejemplo.__name__}: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ Ejemplos completados")
    print("="*70 + "\n")


if __name__ == "__main__":
    ejecutar_todos()