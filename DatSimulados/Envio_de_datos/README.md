# Script de Envío de Datos de Sensores IoT

Este script lee archivos CSV de sensores y envía los datos fila por fila a un endpoint configurado.

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar el archivo .env:**
   - Copia el archivo `.env.example` a `.env`
   - Edita `.env` y configura tu `ENDPOINT_URL`

```bash
cp .env.example .env
nano .env  # o usa tu editor favorito
```

## ⚙️ Configuración

Edita el archivo `.env` con tus valores:

```env
ENDPOINT_URL=http://tu-servidor.com/api/sensor-data
DELAY_BETWEEN_ROWS=1.0
RETRY_ATTEMPTS=3
TIMEOUT=10
CSV_DIRECTORY=.
```

### Parámetros:

- **ENDPOINT_URL**: URL del endpoint donde se enviarán los datos (obligatorio)
- **DELAY_BETWEEN_ROWS**: Segundos de espera entre cada fila (default: 1.0)
- **RETRY_ATTEMPTS**: Número de reintentos si falla el envío (default: 3)
- **TIMEOUT**: Tiempo máximo de espera por petición en segundos (default: 10)
- **CSV_DIRECTORY**: Directorio donde están los archivos CSV (default: .)

## 📁 Archivos CSV Soportados

El script detecta automáticamente estos tipos de archivos:

- **Calidad de Aire**: archivos que contengan "aire", "co2", "em500"
  - Ejemplo: `simulacion_aire_20251110_104657.csv`
  - Ejemplo: `Calidad aire EM500-CO2-915M nov 2024.csv`

- **Sonido**: archivos que contengan "sonido", "ws302"
  - Ejemplo: `simulacion_sonido_20251110_104657.csv`
  - Ejemplo: `Sonido WS302-915M SONIDO NOV 2024.csv`

- **Soterrados**: archivos que contengan "soterrado", "udl", "em310"
  - Ejemplo: `simulacion_soterrado_20251110_104657.csv`
  - Ejemplo: `EM310-UDL-915M soterrados nov 2024.csv`

## ▶️ Uso

Simplemente ejecuta el script:

```bash
python csv_sender.py
```

El script automáticamente:
1. Busca todos los archivos CSV en el directorio configurado
2. Identifica el tipo de sensor de cada archivo
3. Lee y envía fila por fila al endpoint
4. Muestra el progreso en tiempo real
5. Genera un resumen al finalizar

## 📊 Formato del Payload

Cada fila se envía como JSON con esta estructura:

```json
{
  "sensor_type": "aire",
  "source_file": "simulacion_aire_20251110_104657.csv",
  "row_number": 1,
  "data": {
    "_id": "0260279a2ec54bc69d403ac8",
    "devAddr": "01f5c530",
    "time": "2014-04-20T10:00:00.000+00:00",
    "object.co2": 1195.1,
    "object.temperature": 18.9,
    ...
  }
}
```
## 📊 Ejemplo del Payload para cada Csv

### Aire

```json
{
  "sensor_type": "aire",
  "source_file": "simulacion_aire_20251110_104657.csv",
  "row_number": 1,
  "data": {
    "_id": "0260279a2ec54bc69d403ac8",
    "devAddr": "01f5c530",
    "deduplicationId": "2cc46713-9aba-403e-bfbd-23b7d7309502",
    "time": "2014-04-20T10:00:00.000+00:00",
    "deviceInfo.deviceClassEnabled": "CLASS_A",
    "deviceInfo.tenantName": "Secretaria de ciudad digital y gobierno electronico",
    "deviceInfo.tenantId": "52f14cd4-c6f1-4fbd-8f87-4025e1d49242",
    "deviceInfo.deviceProfileId": "1d9d2a0d-d5c2-4339-9080-8a9defc094a0",
    "deviceInfo.applicationId": "572beadb-725b-4d67-a009-e9ca93cc5fc3",
    "deviceInfo.deviceName": "EMS-6993",
    "deviceInfo.applicationName": "EM500-CO2-915M",
    "deviceInfo.devEui": "24e124126d376993",
    "deviceInfo.deviceProfileName": "EM500-CO2-915M",
    "deviceInfo.tags.Description": "Mide la concentración de CO2, además de la temperatura, humedad y presión barométrica.",
    "deviceInfo.tags.Address": "Cristo de la Concordia",
    "deviceInfo.tags.Name": "Sensor CO2",
    "deviceInfo.tags.Location": "-17.3844962748556, -66.1353062672603",
    "txInfo.modulation.lora.spreadingFactor": 10,
    "txInfo.modulation.lora.bandwidth": 125000,
    "txInfo.modulation.lora.codeRate": "CR_4_5",
    "txInfo.frequency": 915200000,
    "fPort": 85,
    "data": "/wv//wEB",
    "fCnt": 1,
    "confirmed": false,
    "adr": true,
    "dr": 2,
    "rxInfo[0].rssi": -98,
    "rxInfo[1].rssi": -96,
    "rxInfo[2].rssi": -87,
    "rxInfo[0].snr": -1.6,
    "rxInfo[1].snr": 0.2,
    "rxInfo[2].snr": 1.2,
    "rxInfo[0].metadata.region_config_id": "au915_0",
    "rxInfo[1].metadata.region_config_id": "au915_0",
    "rxInfo[2].metadata.region_config_id": "au915_0",
    "rxInfo[0].metadata.region_common_name": "AU915",
    "rxInfo[1].metadata.region_common_name": "AU915",
    "rxInfo[2].metadata.region_common_name": "AU915",
    "rxInfo[0].crcStatus": "CRC_OK",
    "rxInfo[1].crcStatus": "CRC_OK",
    "rxInfo[2].crcStatus": "CRC_OK",
    "object.co2": 1195.1,
    "object.co2_status": "Alto",
    "object.co2_message": "CO2: 1195.1 ppm",
    "object.temperature": 18.9,
    "object.temperature_status": "Frio",
    "object.temperature_message": "Temperatura: 18.9°C",
    "object.humidity": 42.3,
    "object.humidity_status": "Normal",
    "object.humidity_message": "Humedad: 42.3%",
    "object.pressure": 1001.5,
    "object.pressure_status": "Normal",
    "object.pressure_message": "Presión: 1001.5 hPa",
    "object.battery": 88.9
  }
}
```

### Sonido
```json
{
  "sensor_type": "sonido",
  "source_file": "simulacion_sonido_20251110_104657.csv",
  "row_number": 1,
  "data": {
    "_id": "6e47df6b26e940688178c8cb",
    "devAddr": "008ac7ec",
    "deduplicationId": "ca99c172-ef85-4a1c-af1b-d33abe3230fa",
    "time": "2014-04-20T10:00:00.000+00:00",
    "deviceInfo.deviceClassEnabled": "CLASS_A",
    "deviceInfo.tenantName": "Secretaria de ciudad digital y gobierno electronico",
    "deviceInfo.tenantId": "52f14cd4-c6f1-4fbd-8f87-4025e1d49242",
    "deviceInfo.deviceProfileId": "19da3dff-9fe0-41ed-8c8e-fb5a7017d025",
    "deviceInfo.applicationId": "bb9914a5-1c77-4941-9baf-1332dc8b2d40",
    "deviceInfo.deviceName": "SLS-8588",
    "deviceInfo.applicationName": "WS302-915M",
    "deviceInfo.devEui": "24e124743d018588",
    "deviceInfo.deviceProfileName": "WS302-915M",
    "deviceInfo.tags.Description": "Mide la cantidad de decibeles (dB) en el ambiente o sector",
    "deviceInfo.tags.Address": "Av. Melchor Urquidi y Zenon Salinas (AWRA)",
    "deviceInfo.tags.Name": "Sensor de medición de sonido",
    "deviceInfo.tags.Location": "-17.375344862040876, -66.14936933868707",
    "txInfo.modulation.lora.spreadingFactor": 10,
    "txInfo.modulation.lora.bandwidth": 125000,
    "txInfo.modulation.lora.codeRate": "CR_4_5",
    "txInfo.frequency": 916200000,
    "fPort": 85,
    "data": "/wv//wEB",
    "fCnt": 1,
    "confirmed": false,
    "adr": true,
    "dr": 2,
    "rxInfo[0].rssi": -86,
    "rxInfo[1].rssi": -96,
    "rxInfo[2].rssi": -103,
    "rxInfo[0].snr": 9.7,
    "rxInfo[1].snr": 9.5,
    "rxInfo[2].snr": 5.2,
    "rxInfo[0].metadata.region_config_id": "au915_0",
    "rxInfo[1].metadata.region_config_id": "au915_0",
    "rxInfo[2].metadata.region_config_id": "au915_0",
    "rxInfo[0].metadata.region_common_name": "AU915",
    "rxInfo[1].metadata.region_common_name": "AU915",
    "rxInfo[2].metadata.region_common_name": "AU915",
    "rxInfo[0].crcStatus": "CRC_OK",
    "rxInfo[1].crcStatus": "CRC_OK",
    "rxInfo[2].crcStatus": "CRC_OK",
    "object.LAeq": 58.7,
    "object.LAI": 67.2,
    "object.LAImax": 92.6,
    "object.battery": 83.1,
    "object.status": "Moderado"
  }
}
```

### Soterrado
```json
{
  "sensor_type": "soterrado",
  "source_file": "simulacion_soterrado_20251110_104657.csv",
  "row_number": 1,
  "data": {
    "_id": "676951eb86f246f78976072a",
    "devAddr": "010fa365",
    "deduplicationId": "6e11d1ce-09ee-4be8-8e2d-d41de6040988",
    "time": "2014-04-20T10:00:00.000+00:00",
    "deviceInfo.deviceClassEnabled": "CLASS_A",
    "deviceInfo.tenantName": "Secretaria de ciudad digital y gobierno electronico",
    "deviceInfo.tenantId": "52f14cd4-c6f1-4fbd-8f87-4025e1d49242",
    "deviceInfo.deviceProfileId": "6a273702-1701-450e-a5ce-2757bbee4165",
    "deviceInfo.applicationId": "ab61f3b6-fb26-4bbb-aeff-332097b89aab",
    "deviceInfo.deviceName": "UDS-9228",
    "deviceInfo.applicationName": "EM310-UDL-915M",
    "deviceInfo.devEui": "24e124713d399228",
    "deviceInfo.deviceProfileName": "EM310-UDL-915M",
    "deviceInfo.tags.Description": "Mide el nivel de agua almacenada en el tanque",
    "deviceInfo.tags.Address": "Parque Excombatientes",
    "deviceInfo.tags.Name": "Sensor nivel de liquido",
    "deviceInfo.tags.Location": "-17.385320458924163, -66.17390941117199",
    "txInfo.modulation.lora.spreadingFactor": 10,
    "txInfo.modulation.lora.bandwidth": 125000,
    "txInfo.modulation.lora.codeRate": "CR_4_5",
    "txInfo.frequency": 915200000,
    "fPort": 85,
    "data": "/wv//wEB",
    "fCnt": 1,
    "confirmed": false,
    "adr": true,
    "dr": 2,
    "rxInfo[0].rssi": -96,
    "rxInfo[1].rssi": -106,
    "rxInfo[2].rssi": -108,
    "rxInfo[0].snr": 5.0,
    "rxInfo[1].snr": -2.0,
    "rxInfo[2].snr": 0.5,
    "rxInfo[0].metadata.region_config_id": "au915_0",
    "rxInfo[1].metadata.region_config_id": "au915_0",
    "rxInfo[2].metadata.region_config_id": "au915_0",
    "rxInfo[0].metadata.region_common_name": "AU915",
    "rxInfo[1].metadata.region_common_name": "AU915",
    "rxInfo[2].metadata.region_common_name": "AU915",
    "rxInfo[0].crcStatus": "CRC_OK",
    "rxInfo[1].crcStatus": "CRC_OK",
    "rxInfo[2].crcStatus": "CRC_OK",
    "object.distance": 73.7,
    "object.position": "normal",
    "object.battery": 78.4,
    "object.status": "Medio"
  }
}
```

## 📝 Logs

El script muestra información detallada:

```
2024-11-10 10:46:57 - INFO - ============================================================
2024-11-10 10:46:57 - INFO - INICIANDO ENVÍO DE DATOS DE SENSORES
2024-11-10 10:46:57 - INFO - ============================================================

Configuración:
  Endpoint: http://localhost:8000/api/sensor-data
  Directorio CSV: .
  Delay entre filas: 1.0s
  Reintentos: 3
  Timeout: 10s

2024-11-10 10:46:57 - INFO - Archivo encontrado: simulacion_aire.csv - Tipo: aire
2024-11-10 10:46:57 - INFO - ✓ Fila 1 enviada exitosamente [aire]
...
```

## 🔧 Solución de Problemas

### Error: ENDPOINT_URL no está configurado
- Asegúrate de tener un archivo `.env` en el mismo directorio
- Verifica que contenga la línea `ENDPOINT_URL=tu-url-aqui`

### Error: No se encontraron archivos CSV
- Verifica que los archivos CSV estén en el directorio especificado
- Comprueba la variable `CSV_DIRECTORY` en `.env`

### Errores de conexión
- Verifica que el endpoint esté disponible
- Aumenta el valor de `TIMEOUT` si la conexión es lenta
- Revisa los logs para más detalles

## 🎯 Ejemplo Completo

1. Estructura de archivos:
```
proyecto/
├── csv_sender.py
├── requirements.txt
├── .env
├── simulacion_aire.csv
├── simulacion_sonido.csv
└── simulacion_soterrado.csv
```

2. Contenido de `.env`:
```env
ENDPOINT_URL=http://localhost:8000/api/sensor-data
DELAY_BETWEEN_ROWS=0.5
```

3. Ejecutar:
```bash
python csv_sender.py
```

## 📞 Soporte

Si encuentras problemas, verifica:
- Los logs del script
- La conectividad con el endpoint
- El formato de los archivos CSV
- La configuración en `.env`