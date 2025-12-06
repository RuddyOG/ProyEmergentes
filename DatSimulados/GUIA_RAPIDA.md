# 🚀 GUÍA RÁPIDA - Simulador de Sensores IoT

## Inicio Rápido en 3 Pasos

### 1️⃣ Ejecutar el Simulador
```bash
python simulador_sensores.py
```

### 2️⃣ Seleccionar Opción
```
Opciones disponibles:
1 = Solo sensor de aire
2 = Solo sensor de sonido  
3 = Solo sensor soterrado
4 = Todos los sensores
```

### 3️⃣ Configurar Parámetros
```
Ejemplo:
- Lecturas: 100
- Intervalo: 15 (minutos,segundos,milesegundos)
- Fecha: 2024-11-15 08:00
```

## Ejemplos de Uso Común

### 📊 Caso 1: Datos para Dashboard (1 día)
```
Lecturas: 96
Intervalo: 15 minutos
Resultado: 1 día completo de datos cada 15 minutos
```

### 🧪 Caso 2: Pruebas Rápidas
```
Lecturas: 20
Intervalo: 5 minutos
Resultado: 100 minutos de datos para testing
```

### 📈 Caso 3: Análisis Semanal
```
Lecturas: 672
Intervalo: 15 minutos
Resultado: 1 semana de datos
```

### 🔬 Caso 4: Demostración
```
Lecturas: 50
Intervalo: 10 minutos
Resultado: ~8 horas de datos para demo
```

## 📁 Archivos Generados

Los archivos CSV se guardan automáticamente con nombres como:
- `simulacion_aire_20241115_143022.csv`
- `simulacion_sonido_20241115_143022.csv`
- `simulacion_soterrado_20241115_143022.csv`

## 📊 Datos Incluidos

### Sensor de Aire (EM500-CO2-915M)
- ✅ CO2 (ppm)
- ✅ Temperatura (°C)
- ✅ Humedad (%)
- ✅ Presión (hPa)
- ✅ Batería (%)
- ✅ Estados automáticos

### Sensor de Sonido (WS302-915M)
- ✅ LAeq - Nivel equivalente (dB)
- ✅ LAI - Promedio (dB)
- ✅ LAImax - Pico máximo (dB)
- ✅ Batería (%)
- ✅ Estado (Normal/Moderado/Alto)

### Sensor Soterrado (EM310-UDL-915M)
- ✅ Distancia (cm)
- ✅ Posición
- ✅ Batería (%)
- ✅ Estado (Lleno/Medio/Bajo)

## 💡 Consejos Pro

1. **Fechas Realistas**: Usa fechas recientes para mejor contexto
2. **Intervalos Comunes**: 5, 10, 15, 30 minutos son los más usados
3. **Testing**: Empieza con pocas lecturas para validar
4. **Múltiples Escenarios**: Genera varios conjuntos con diferentes parámetros

## ⚠️ Errores Comunes

❌ **Formato de fecha incorrecto**
```
Incorrecto: 15/11/2024 14:30
Correcto:   2024-11-15 14:30
```

❌ **Valores negativos**
```
Incorrecto: -10 lecturas
Correcto:   10 lecturas
```

❌ **Intervalos muy pequeños**
```
No recomendado: 1 minuto (genera muchos datos)
Recomendado:    5-15 minutos
```

## 🎯 Resultados Esperados

Después de ejecutar verás:
```
✓ Archivo guardado: simulacion_aire_20241115_143022.csv
  Total de registros: 100

✓ Archivo guardado: simulacion_sonido_20241115_143022.csv
  Total de registros: 100

✓ Archivo guardado: simulacion_soterrado_20241115_143022.csv
  Total de registros: 100

========================================================
         ✓ SIMULACIÓN COMPLETADA
========================================================
```

## 📝 Formato CSV

Los archivos son compatibles con:
- ✅ Microsoft Excel
- ✅ Google Sheets
- ✅ Python Pandas
- ✅ R
- ✅ Cualquier herramienta de análisis de datos

## 🔧 Personalización

Los datos simulados incluyen:
- IDs únicos para cada registro
- Timestamps secuenciales correctos
- Información completa del dispositivo
- Valores realistas dentro de rangos normales
- Estados calculados automáticamente
- Datos de comunicación LoRa

## 📞 Necesitas Ayuda?

1. Lee el archivo `README.md` completo
2. Revisa los archivos de ejemplo incluidos
3. Verifica los mensajes de error del programa
4. Asegúrate de tener Python 3.6+

## ✨ Características Especiales

- 🎲 Valores aleatorios realistas
- 📅 Timestamps precisos
- 🔋 Niveles de batería variables
- 📊 Estados automáticos según valores
- 🆔 IDs únicos por registro
- 🌐 Formato compatible con sistemas IoT

---

**¡Listo para empezar!** 🚀

Ejecuta: `python simulador_sensores.py`
