# Simulador de Sensores IoT

## Descripción
Este script simula la lectura de tres tipos de sensores IoT:
- **Sensor de Calidad de Aire**: Mide CO2, temperatura, humedad y presión barométrica
- **Sensor de Sonido**: Mide niveles de decibeles (dB)
- **Sensor Soterrado**: Mide el nivel de líquido en tanques

## Requisitos
- Python 3.6 o superior
- No requiere librerías externas (solo usa módulos estándar de Python)

## Características

### Datos Simulados

#### Sensor de Aire (EM500-CO2-915M)
- **CO2**: 400-1200 ppm
- **Temperatura**: 15-30°C
- **Humedad**: 30-80%
- **Presión**: 950-1050 hPa
- **Batería**: 80-100%
- **Estados**: Normal, Moderado, Alto (según valores)

#### Sensor de Sonido (WS302-915M)
- **LAeq**: 45-85 dB (nivel equivalente)
- **LAI**: 45-85 dB (promedio)
- **LAImax**: 75-100 dB (pico máximo)
- **Batería**: 80-100%
- **Estados**: Normal, Moderado, Alto

#### Sensor Soterrado (EM310-UDL-915M)
- **Distancia**: 20-150 cm
- **Posición**: normal
- **Batería**: 60-100%
- **Estados**: Lleno, Medio, Bajo

### Campos Generados

Cada lectura incluye:
- ID único de registro
- Timestamp personalizado
- Información del dispositivo
- Configuración de comunicación LoRa
- Datos del sensor (object.*)
- Información de recepción (RSSI, SNR)
- Estados y mensajes

## Uso

### Ejecución
```bash
python simulador_sensores.py
```

### Menú Principal
```
========================================================
         SIMULADOR DE SENSORES IoT
========================================================

Sensores disponibles:
  1. Sensor de Calidad de Aire
  2. Sensor de Sonido
  3. Sensor Soterrado
  4. Simular TODOS los sensores
  0. Salir

Seleccione una opción:
```

### Parámetros de Configuración

1. **Número de lecturas**: Cantidad de registros a generar por sensor
   - Ejemplo: 100 lecturas

2. **Intervalo de tiempo**: Minutos entre cada lectura
   - Ejemplo: 15 minutos

3. **Fecha y hora de inicio**: Punto de partida para la simulación
   - Formato: `YYYY-MM-DD HH:MM`
   - Ejemplo: `2024-11-15 14:30`

### Ejemplo de Uso

```
Seleccione una opción: 4
¿Cuántas lecturas desea simular por sensor? 50
¿Cada cuántos minutos desea generar una lectura? 10
Formato (YYYY-MM-DD HH:MM): 2024-11-15 08:00

========================================================
              RESUMEN DE SIMULACIÓN
========================================================
  Sensores: aire, sonido, soterrado
  Lecturas por sensor: 50
  Intervalo: 10 minutos
  Fecha inicio: 2024-11-15 08:00
  Fecha fin: 2024-11-15 16:10
  Duración total: 490 minutos
========================================================

¿Desea continuar? (s/n): s
```

## Archivos Generados

Los archivos CSV se generan con el formato:
```
simulacion_{tipo_sensor}_{timestamp}.csv
```

Ejemplos:
- `simulacion_aire_20241115_143022.csv`
- `simulacion_sonido_20241115_143022.csv`
- `simulacion_soterrado_20241115_143022.csv`

## Estructura del CSV

Cada archivo CSV contiene:
- Cabeceras con nombres de campos
- Registros con valores simulados
- Compatible con Excel, Google Sheets, pandas, etc.

### Campos Principales por Sensor

**Aire:**
```
object.co2, object.temperature, object.humidity, object.pressure,
object.battery, object.co2_status, object.temperature_status, etc.
```

**Sonido:**
```
object.LAeq, object.LAI, object.LAImax, object.battery, object.status
```

**Soterrado:**
```
object.distance, object.position, object.battery, object.status
```

## Casos de Uso

### 1. Testing de Aplicaciones
Genera datos de prueba para validar aplicaciones de monitoreo IoT

### 2. Desarrollo de Dashboards
Crea conjuntos de datos para diseñar y probar visualizaciones

### 3. Capacitación
Genera datos de ejemplo para entrenar usuarios en el uso del sistema

### 4. Análisis de Rendimiento
Simula cargas de datos para pruebas de estrés

### 5. Documentación
Genera ejemplos realistas para documentación técnica

## Notas Técnicas

- Los timestamps son secuenciales según el intervalo especificado
- Los valores se generan aleatoriamente dentro de rangos realistas
- Los estados se calculan automáticamente según los valores
- Cada registro tiene un ID único
- Los datos son compatibles con el formato original de los sensores

## Consejos

1. **Pruebas Cortas**: Comience con pocas lecturas (10-20) para validar
2. **Intervalos Realistas**: Use intervalos típicos (5, 10, 15 minutos)
3. **Fechas Coherentes**: Use fechas recientes para datos más realistas
4. **Múltiples Ejecuciones**: Genere varios conjuntos para diferentes escenarios

## Solución de Problemas

**Error de formato de fecha:**
- Verifique el formato: `YYYY-MM-DD HH:MM`
- Ejemplo válido: `2024-11-15 14:30`

**Valores inválidos:**
- Use solo números enteros positivos
- Verifique que los intervalos sean mayores a 0

**Archivos no se generan:**
- Verifique permisos de escritura en el directorio
- Asegúrese de tener espacio en disco

## Contacto y Soporte

Para preguntas o problemas:
- Revise la documentación
- Verifique los mensajes de error
- Consulte los ejemplos de uso

---

**Versión**: 1.0  
**Última actualización**: Noviembre 2024
