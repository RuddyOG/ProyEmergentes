import os
import time
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
ENDPOINT_URL = os.getenv('ENDPOINT_URL')
DELAY_BETWEEN_ROWS = float(os.getenv('DELAY_BETWEEN_ROWS', '1.0'))  # segundos
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', '3'))
TIMEOUT = int(os.getenv('TIMEOUT', '10'))  # segundos
CSV_DIRECTORY = os.getenv('CSV_DIRECTORY', '.')

# Palabras clave para identificar tipos de archivos
SENSOR_TYPES = {
    'aire': ['aire', 'co2', 'em500'],
    'sonido': ['sonido', 'ws302'],
    'soterrado': ['soterrado', 'soterrados', 'udl', 'em310']
}

def identify_sensor_type(filename):
    """Identifica el tipo de sensor basándose en el nombre del archivo"""
    filename_lower = filename.lower()
    
    for sensor_type, keywords in SENSOR_TYPES.items():
        if any(keyword in filename_lower for keyword in keywords):
            return sensor_type
    
    return 'desconocido'

def find_csv_files(directory):
    """Encuentra todos los archivos CSV en el directorio"""
    path = Path(directory)
    csv_files = list(path.glob('*.csv'))
    
    if not csv_files:
        logger.warning(f"No se encontraron archivos CSV en {directory}")
        return []
    
    # Clasificar archivos por tipo de sensor
    classified_files = []
    for csv_file in csv_files:
        sensor_type = identify_sensor_type(csv_file.name)
        classified_files.append({
            'path': csv_file,
            'name': csv_file.name,
            'type': sensor_type
        })
        logger.info(f"Archivo encontrado: {csv_file.name} - Tipo: {sensor_type}")
    
    return classified_files

def send_row_to_endpoint(row_data, sensor_type, row_number, filename):
    """Envía una fila de datos al endpoint con reintentos"""
    
    # Preparar payload con metadata adicional
    payload = {
        'sensor_type': sensor_type,
        'source_file': filename,
        'row_number': row_number,
        'data': row_data
    }
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(
                ENDPOINT_URL,
                json=payload,
                timeout=TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Fila {row_number} enviada exitosamente [{sensor_type}]")
                return True
            else:
                logger.warning(
                    f"⚠ Intento {attempt + 1}/{RETRY_ATTEMPTS} - "
                    f"Status code: {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"✗ Timeout en intento {attempt + 1}/{RETRY_ATTEMPTS}")
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error en intento {attempt + 1}/{RETRY_ATTEMPTS}: {str(e)}")
        
        if attempt < RETRY_ATTEMPTS - 1:
            time.sleep(2 ** attempt)  # Backoff exponencial
    
    logger.error(f"✗ Falló el envío de la fila {row_number} después de {RETRY_ATTEMPTS} intentos")
    return False

def process_csv_file(file_info):
    """Procesa un archivo CSV y envía fila por fila"""
    csv_path = file_info['path']
    sensor_type = file_info['type']
    filename = file_info['name']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Procesando archivo: {filename}")
    logger.info(f"Tipo de sensor: {sensor_type}")
    logger.info(f"{'='*60}\n")
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_path)
        total_rows = len(df)
        logger.info(f"Total de filas a enviar: {total_rows}")
        
        # Estadísticas
        success_count = 0
        failed_count = 0
        
        # Enviar fila por fila
        for index, row in df.iterrows():
            # Convertir fila a diccionario, manejando valores NaN
            row_dict = row.to_dict()
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
            
            # Enviar al endpoint
            if send_row_to_endpoint(row_dict, sensor_type, index + 1, filename):
                success_count += 1
            else:
                failed_count += 1
            
            # Delay entre envíos
            if index < total_rows - 1:  # No hacer delay después de la última fila
                time.sleep(DELAY_BETWEEN_ROWS)
        
        # Resumen
        logger.info(f"\n{'='*60}")
        logger.info(f"Resumen para {filename}:")
        logger.info(f"  ✓ Exitosas: {success_count}/{total_rows}")
        logger.info(f"  ✗ Fallidas: {failed_count}/{total_rows}")
        logger.info(f"{'='*60}\n")
        
        return success_count, failed_count
        
    except Exception as e:
        logger.error(f"Error al procesar {filename}: {str(e)}")
        return 0, 0

def main():
    """Función principal"""
    logger.info("="*60)
    logger.info("INICIANDO ENVÍO DE DATOS DE SENSORES")
    logger.info("="*60)
    
    # Validar configuración
    if not ENDPOINT_URL:
        logger.error("ERROR: ENDPOINT_URL no está configurado en el archivo .env")
        return
    
    logger.info(f"\nConfiguración:")
    logger.info(f"  Endpoint: {ENDPOINT_URL}")
    logger.info(f"  Directorio CSV: {CSV_DIRECTORY}")
    logger.info(f"  Delay entre filas: {DELAY_BETWEEN_ROWS}s")
    logger.info(f"  Reintentos: {RETRY_ATTEMPTS}")
    logger.info(f"  Timeout: {TIMEOUT}s\n")
    
    # Buscar archivos CSV
    csv_files = find_csv_files(CSV_DIRECTORY)
    
    if not csv_files:
        logger.error("No se encontraron archivos CSV para procesar")
        return
    
    # Procesar cada archivo
    total_success = 0
    total_failed = 0
    
    for file_info in csv_files:
        success, failed = process_csv_file(file_info)
        total_success += success
        total_failed += failed
    
    # Resumen final
    logger.info("\n" + "="*60)
    logger.info("RESUMEN FINAL")
    logger.info("="*60)
    logger.info(f"Archivos procesados: {len(csv_files)}")
    logger.info(f"Total de filas enviadas exitosamente: {total_success}")
    logger.info(f"Total de filas fallidas: {total_failed}")
    logger.info("="*60)

if __name__ == "__main__":
    main()