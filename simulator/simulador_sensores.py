#!/usr/bin/env python3
"""
Simulador de Sensores IoT
Genera datos simulados para sensores de calidad de aire, sonido y soterrado
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
import sys

class SimuladorSensores:
    def __init__(self):
        # Configuración común para todos los sensores
        self.tenant_name = "Secretaria de ciudad digital y gobierno electronico"
        self.tenant_id = "52f14cd4-c6f1-4fbd-8f87-4025e1d49242"
        
        # Configuración de sensores - múltiples versiones por tipo
        self.sensores_versiones = {
            'aire': [
                {
                    'device_name': 'EMS-6500',
                    'app_name': 'EM500-CO2-915M',
                    'dev_eui': '24e124126d376500',
                    'profile_name': 'EM500-CO2-915M',
                    'profile_id': '1d9d2a0d-d5c2-4339-9080-8a9defc094a0',
                    'app_id': '572beadb-725b-4d67-a009-e9ca93cc5fc3',
                    'description': 'Mide la concentración de CO2, además de la temperatura, humedad y presión barométrica.',
                    'address': 'Cristo de la Concordia',
                    'name': 'Sensor CO2',
                    'location': '-17.3844962748556, -66.1353062672603',
                    'dev_addr': '01f5c500',
                    'fport': 85
                },
                {
                    'device_name': 'EMS-6962',
                    'app_name': 'EM500-CO2-915M',
                    'dev_eui': '24e124126d376962',
                    'profile_name': 'EM500-CO2-915M',
                    'profile_id': '1d9d2a0d-d5c2-4339-9080-8a9defc094a0',
                    'app_id': '572beadb-725b-4d67-a009-e9ca93cc5fc3',
                    'description': 'Mide la concentración de CO2, además de la temperatura, humedad y presión barométrica.',
                    'address': 'Cristo de la Concordia',
                    'name': 'Sensor CO2',
                    'location': '-17.3844962748556, -66.1353062672603',
                    'dev_addr': '01f5c962',
                    'fport': 85
                },
                {
                    'device_name': 'EMS-6968',
                    'app_name': 'EM500-CO2-915M',
                    'dev_eui': '24e124126d376968',
                    'profile_name': 'EM500-CO2-915M',
                    'profile_id': '1d9d2a0d-d5c2-4339-9080-8a9defc094a0',
                    'app_id': '572beadb-725b-4d67-a009-e9ca93cc5fc3',
                    'description': 'Mide la concentración de CO2, además de la temperatura, humedad y presión barométrica.',
                    'address': 'Cristo de la Concordia',
                    'name': 'Sensor CO2',
                    'location': '-17.3844962748556, -66.1353062672603',
                    'dev_addr': '01f5c968',
                    'fport': 85
                },
                {
                    'device_name': 'EMS-6993',
                    'app_name': 'EM500-CO2-915M',
                    'dev_eui': '24e124126d376993',
                    'profile_name': 'EM500-CO2-915M',
                    'profile_id': '1d9d2a0d-d5c2-4339-9080-8a9defc094a0',
                    'app_id': '572beadb-725b-4d67-a009-e9ca93cc5fc3',
                    'description': 'Mide la concentración de CO2, además de la temperatura, humedad y presión barométrica.',
                    'address': 'Cristo de la Concordia',
                    'name': 'Sensor CO2',
                    'location': '-17.3844962748556, -66.1353062672603',
                    'dev_addr': '01f5c993',
                    'fport': 85
                }
            ],
            'sonido': [
                {
                    'device_name': 'SLS-2648',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d012648',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac648',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-3164',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d013164',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac164',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-8588',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d018588',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac7ec',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-8654',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d018654',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac654',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-8709',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d018709',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac709',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-8852',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d018852',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac852',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-9199',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d019199',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac199',
                    'fport': 85
                },
                {
                    'device_name': 'SLS-9247',
                    'app_name': 'WS302-915M',
                    'dev_eui': '24e124743d019247',
                    'profile_name': 'WS302-915M',
                    'profile_id': '19da3dff-9fe0-41ed-8c8e-fb5a7017d025',
                    'app_id': 'bb9914a5-1c77-4941-9baf-1332dc8b2d40',
                    'description': 'Mide la cantidad de decibeles (dB) en el ambiente o sector',
                    'address': 'Av. Melchor Urquidi y Zenon Salinas (AWRA)',
                    'name': 'Sensor de medición de sonido',
                    'location': '-17.375344862040876, -66.14936933868707',
                    'dev_addr': '008ac247',
                    'fport': 85
                }
            ],
            'soterrado': [
                {
                    'device_name': 'UDS-6632',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d396632',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa632',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-7097',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d397097',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa097',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-7999',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d397999',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa999',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-8479',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d398479',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '01d9d6df',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-8653',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d398653',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa653',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-9228',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d399228',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa365',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-9340',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d399340',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa340',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-9510',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d399510',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa510',
                    'fport': 85
                },
                {
                    'device_name': 'UDS-9929',
                    'app_name': 'EM310-UDL-915M',
                    'dev_eui': '24e124713d399929',
                    'profile_name': 'EM310-UDL-915M',
                    'profile_id': '6a273702-1701-450e-a5ce-2757bbee4165',
                    'app_id': 'ab61f3b6-fb26-4bbb-aeff-332097b89aab',
                    'description': 'Mide el nivel de agua almacenada en el tanque',
                    'address': 'Parque Excombatientes',
                    'name': 'Sensor nivel de liquido',
                    'location': '-17.385320458924163, -66.17390941117199',
                    'dev_addr': '010fa929',
                    'fport': 85
                }
            ]
        }
    
    def generar_datos_aire(self):
        """Genera datos simulados para sensor de calidad de aire"""
        co2 = round(random.uniform(400, 1200), 1)
        temperatura = round(random.uniform(15, 30), 1)
        humedad = round(random.uniform(30, 80), 1)
        presion = round(random.uniform(950, 1050), 1)
        bateria = round(random.uniform(80, 100), 1)
        
        # Determinar estados
        if co2 < 600:
            co2_status = "Normal"
        elif co2 < 1000:
            co2_status = "Moderado"
        else:
            co2_status = "Alto"
        
        if temperatura < 20:
            temp_status = "Frio"
        elif temperatura < 25:
            temp_status = "Normal"
        else:
            temp_status = "Calido"
        
        if humedad < 40:
            hum_status = "Bajo"
        elif humedad < 70:
            hum_status = "Normal"
        else:
            hum_status = "Alto"
        
        if presion < 980:
            pres_status = "Bajo"
        elif presion < 1020:
            pres_status = "Normal"
        else:
            pres_status = "Alto"
        
        return {
            'object.co2': co2,
            'object.co2_status': co2_status,
            'object.co2_message': f"CO2: {co2} ppm",
            'object.temperature': temperatura,
            'object.temperature_status': temp_status,
            'object.temperature_message': f"Temperatura: {temperatura}°C",
            'object.humidity': humedad,
            'object.humidity_status': hum_status,
            'object.humidity_message': f"Humedad: {humedad}%",
            'object.pressure': presion,
            'object.pressure_status': pres_status,
            'object.pressure_message': f"Presión: {presion} hPa",
            'object.battery': bateria
        }
    
    def generar_datos_sonido(self):
        """Genera datos simulados para sensor de sonido"""
        laeq = round(random.uniform(45, 85), 1)
        lai = round(random.uniform(45, 85), 1)
        laimax = round(random.uniform(75, 100), 1)
        bateria = round(random.uniform(80, 100), 1)
        
        # Determinar estado
        if laeq < 55:
            status = "Normal"
        elif laeq < 70:
            status = "Moderado"
        else:
            status = "Alto"
        
        return {
            'object.LAeq': laeq,
            'object.LAI': lai,
            'object.LAImax': laimax,
            'object.battery': bateria,
            'object.status': status
        }
    
    def generar_datos_soterrado(self):
        """Genera datos simulados para sensor soterrado"""
        distancia = round(random.uniform(20, 150), 1)
        bateria = round(random.uniform(60, 100), 1)
        
        # Determinar posición y estado
        if distancia < 50:
            posicion = "normal"
            status = "Lleno"
        elif distancia < 100:
            posicion = "normal"
            status = "Medio"
        else:
            posicion = "normal"
            status = "Bajo"
        
        return {
            'object.distance': distancia,
            'object.position': posicion,
            'object.battery': bateria,
            'object.status': status
        }
    
    def generar_campos_comunes(self, sensor_type, timestamp, fcnt, config):
        """Genera campos comunes para todos los sensores usando una configuración específica"""
        
        return {
            '_id': str(uuid.uuid4().hex[:24]),
            'devAddr': config['dev_addr'],
            'deduplicationId': str(uuid.uuid4()),
            'time': timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+00:00',
            'deviceInfo.deviceClassEnabled': 'CLASS_A',
            'deviceInfo.tenantName': self.tenant_name,
            'deviceInfo.tenantId': self.tenant_id,
            'deviceInfo.deviceProfileId': config['profile_id'],
            'deviceInfo.applicationId': config['app_id'],
            'deviceInfo.deviceName': config['device_name'],
            'deviceInfo.applicationName': config['app_name'],
            'deviceInfo.devEui': config['dev_eui'],
            'deviceInfo.deviceProfileName': config['profile_name'],
            'deviceInfo.tags.Description': config['description'],
            'deviceInfo.tags.Address': config['address'],
            'deviceInfo.tags.Name': config['name'],
            'deviceInfo.tags.Location': config['location'],
            'txInfo.modulation.lora.spreadingFactor': 10,
            'txInfo.modulation.lora.bandwidth': 125000,
            'txInfo.modulation.lora.codeRate': 'CR_4_5',
            'txInfo.frequency': random.choice([915200000, 916200000, 915600000]),
            'fPort': config['fport'],
            'data': '/wv//wEB',  # Dato codificado simulado
            'fCnt': fcnt,
            'confirmed': 'FALSE',
            'adr': 'TRUE',
            'dr': 2,
            'rxInfo[0].rssi': random.randint(-120, -80),
            'rxInfo[1].rssi': random.randint(-120, -80),
            'rxInfo[2].rssi': random.randint(-120, -80),
            'rxInfo[0].snr': round(random.uniform(-10, 10), 1),
            'rxInfo[1].snr': round(random.uniform(-10, 10), 1),
            'rxInfo[2].snr': round(random.uniform(-10, 10), 1),
            'rxInfo[0].metadata.region_config_id': 'au915_0',
            'rxInfo[1].metadata.region_config_id': 'au915_0',
            'rxInfo[2].metadata.region_config_id': 'au915_0',
            'rxInfo[0].metadata.region_common_name': 'AU915',
            'rxInfo[1].metadata.region_common_name': 'AU915',
            'rxInfo[2].metadata.region_common_name': 'AU915',
            'rxInfo[0].crcStatus': 'CRC_OK',
            'rxInfo[1].crcStatus': 'CRC_OK',
            'rxInfo[2].crcStatus': 'CRC_OK',
        }
    
    def simular_sensor(self, sensor_type, num_lecturas, intervalo, fecha_inicio, unidad_tiempo='minutos'):
        """Simula lecturas de un sensor específico
        
        Args:
            sensor_type: Tipo de sensor ('aire', 'sonido', 'soterrado')
            num_lecturas: Cantidad de lecturas a generar
            intervalo: Intervalo entre lecturas (puede ser decimal)
            fecha_inicio: Fecha y hora de inicio
            unidad_tiempo: 'segundos', 'minutos', o 'rafaga' (por defecto: 'minutos')
        """
        lecturas = []
        timestamp_actual = fecha_inicio
        
        # Obtener todas las versiones del sensor
        versiones = self.sensores_versiones[sensor_type]
        num_versiones = len(versiones)
        
        # Crear lista de configuraciones a usar
        # GARANTIZAR que todas las versiones aparezcan al menos una vez
        configs_a_usar = versiones.copy()  # Primero todas las versiones
        
        # Si necesitamos más lecturas, rellenar aleatoriamente
        if num_lecturas > num_versiones:
            configs_restantes = num_lecturas - num_versiones
            configs_a_usar.extend(random.choices(versiones, k=configs_restantes))
        elif num_lecturas < num_versiones:
            # Si hay menos lecturas que versiones, seleccionar aleatoriamente
            configs_a_usar = random.sample(versiones, num_lecturas)
        
        # Mezclar para que no siempre aparezcan en el mismo orden
        random.shuffle(configs_a_usar)
        
        for i in range(num_lecturas):
            # Usar la configuración correspondiente
            config = configs_a_usar[i]
            
            # Generar campos comunes con la configuración específica
            registro = self.generar_campos_comunes(sensor_type, timestamp_actual, i + 1, config)
            
            # Generar datos específicos del sensor
            if sensor_type == 'aire':
                datos_sensor = self.generar_datos_aire()
            elif sensor_type == 'sonido':
                datos_sensor = self.generar_datos_sonido()
            elif sensor_type == 'soterrado':
                datos_sensor = self.generar_datos_soterrado()
            
            # Combinar registros
            registro.update(datos_sensor)
            lecturas.append(registro)
            
            # Incrementar timestamp según la unidad de tiempo
            if unidad_tiempo == 'rafaga':
                # Modo ráfaga: incrementos de 1 milisegundo
                timestamp_actual += timedelta(milliseconds=1)
            elif unidad_tiempo == 'segundos':
                # Soporta fracciones de segundo (0.5, 0.1, 0.01, etc.)
                timestamp_actual += timedelta(seconds=intervalo)
            else:  # minutos por defecto
                timestamp_actual += timedelta(minutes=intervalo)
        
        return lecturas
    
    def guardar_csv(self, lecturas, nombre_archivo):
        """Guarda las lecturas en un archivo CSV"""
        if not lecturas:
            print("No hay lecturas para guardar")
            return
        
        # Obtener todas las claves
        fieldnames = list(lecturas[0].keys())
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(lecturas)
        
        print(f"✓ Archivo guardado: {nombre_archivo}")
        print(f"  Total de registros: {len(lecturas)}")

def leer_fecha_hora():
    """Lee y valida fecha y hora del usuario"""
    while True:
        print("\nIngrese la fecha y hora de inicio de la simulación:")
        fecha_str = input("Formato (YYYY-MM-DD HH:MM): ").strip()
        
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
            return fecha
        except ValueError:
            print("❌ Formato incorrecto. Use YYYY-MM-DD HH:MM (ejemplo: 2024-11-15 14:30)")

def menu_principal():
    """Menú principal del simulador"""
    simulador = SimuladorSensores()
    
    print("="*60)
    print(" SIMULADOR DE SENSORES IoT ".center(60))
    print("="*60)
    print("\nSensores disponibles:")
    print("  1. Sensor de Calidad de Aire (CO2, Temperatura, Humedad, Presión)")
    print("  2. Sensor de Sonido (Decibeles)")
    print("  3. Sensor Soterrado (Nivel de líquido)")
    print("  4. Simular TODOS los sensores")
    print("  0. Salir")
    
    opcion = input("\nSeleccione una opción: ").strip()
    
    if opcion == '0':
        print("\n¡Hasta luego!")
        sys.exit(0)
    
    # Determinar qué sensores simular
    sensores_a_simular = []
    if opcion == '1':
        sensores_a_simular = ['aire']
    elif opcion == '2':
        sensores_a_simular = ['sonido']
    elif opcion == '3':
        sensores_a_simular = ['soterrado']
    elif opcion == '4':
        sensores_a_simular = ['aire', 'sonido', 'soterrado']
    else:
        print("❌ Opción inválida")
        return
    
    # Solicitar parámetros de simulación
    print("\n" + "-"*60)
    print(" PARÁMETROS DE SIMULACIÓN ".center(60))
    print("-"*60)
    
    try:
        num_lecturas = int(input("\n¿Cuántas lecturas desea simular por sensor? "))
        if num_lecturas <= 0:
            print("❌ El número de lecturas debe ser mayor a 0")
            return
        
        # Preguntar modo de generación
        print("\n¿Cómo desea generar los datos?")
        print("  1. Con intervalo en SEGUNDOS (soporta decimales: 0.5, 0.1, etc.)")
        print("  2. Con intervalo en MINUTOS")
        print("  3. MODO RÁFAGA (generación rápida con 1ms entre registros)")
        opcion_tiempo = input("Seleccione (1, 2 o 3): ").strip()
        
        if opcion_tiempo == '1':
            unidad_tiempo = 'segundos'
            texto_unidad = 'segundos'
            intervalo_input = input(f"¿Cada cuántos segundos? (puede usar decimales, ej: 0.5): ")
            try:
                intervalo = float(intervalo_input)
                if intervalo <= 0:
                    print("❌ El intervalo debe ser mayor a 0")
                    return
            except ValueError:
                print("❌ Valor inválido. Use números (pueden ser decimales).")
                return
                
        elif opcion_tiempo == '2':
            unidad_tiempo = 'minutos'
            texto_unidad = 'minutos'
            intervalo = int(input(f"¿Cada cuántos minutos desea generar una lectura? "))
            if intervalo <= 0:
                print("❌ El intervalo debe ser mayor a 0")
                return
                
        elif opcion_tiempo == '3':
            unidad_tiempo = 'rafaga'
            texto_unidad = 'ráfaga'
            intervalo = 0.001  # 1 milisegundo entre cada registro
            print("✓ Modo ráfaga: se generarán todos los registros con 1ms de diferencia")
            
        else:
            print("❌ Opción inválida")
            return
        
        fecha_inicio = leer_fecha_hora()
        
    except ValueError:
        print("❌ Valor inválido. Use números enteros.")
        return
    
    # Mostrar resumen
    if unidad_tiempo == 'rafaga':
        # Modo ráfaga: cada registro tiene 1ms de diferencia
        fecha_fin = fecha_inicio + timedelta(milliseconds=(num_lecturas - 1))
        duracion_ms = num_lecturas - 1
        if duracion_ms >= 1000:
            duracion_texto = f"{duracion_ms} milisegundos ({duracion_ms/1000:.3f} segundos)"
        else:
            duracion_texto = f"{duracion_ms} milisegundos"
        intervalo_texto = "1 milisegundo (modo ráfaga)"
        
    elif unidad_tiempo == 'segundos':
        fecha_fin = fecha_inicio + timedelta(seconds=intervalo * (num_lecturas - 1))
        duracion_total = intervalo * (num_lecturas - 1)
        
        if duracion_total >= 3600:
            duracion_texto = f"{duracion_total:.2f} segundos ({duracion_total/3600:.2f} horas)"
        elif duracion_total >= 60:
            duracion_texto = f"{duracion_total:.2f} segundos ({duracion_total/60:.1f} minutos)"
        else:
            duracion_texto = f"{duracion_total:.2f} segundos"
        
        if intervalo < 1:
            intervalo_texto = f"{intervalo} segundos ({intervalo*1000:.1f} milisegundos)"
        else:
            intervalo_texto = f"{intervalo} segundos"
            
    else:  # minutos
        fecha_fin = fecha_inicio + timedelta(minutes=intervalo * (num_lecturas - 1))
        duracion_total = intervalo * (num_lecturas - 1)
        if duracion_total >= 1440:
            duracion_texto = f"{duracion_total} minutos ({duracion_total/1440:.1f} días)"
        elif duracion_total >= 60:
            duracion_texto = f"{duracion_total} minutos ({duracion_total/60:.1f} horas)"
        else:
            duracion_texto = f"{duracion_total} minutos"
        intervalo_texto = f"{intervalo} minutos"
    
    print("\n" + "="*60)
    print(" RESUMEN DE SIMULACIÓN ".center(60))
    print("="*60)
    print(f"  Sensores: {', '.join(sensores_a_simular)}")
    print(f"  Lecturas por sensor: {num_lecturas}")
    print(f"  Intervalo: {intervalo_texto}")
    print(f"  Fecha inicio: {fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Fecha fin: {fecha_fin.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print(f"  Duración total: {duracion_texto}")
    print("="*60)
    
    confirmar = input("\n¿Desea continuar? (s/n): ").strip().lower()
    if confirmar != 's':
        print("Simulación cancelada.")
        return
    
    # Realizar simulaciones
    print("\n⏳ Generando datos simulados...\n")
    
    for sensor in sensores_a_simular:
        print(f"\n🔄 Simulando sensor: {sensor.upper()}")
        lecturas = simulador.simular_sensor(sensor, num_lecturas, intervalo, fecha_inicio, unidad_tiempo)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"simulacion_{sensor}_{timestamp}.csv"
        simulador.guardar_csv(lecturas, nombre_archivo)
    
    print("\n" + "="*60)
    print(" ✓ SIMULACIÓN COMPLETADA ".center(60))
    print("="*60)
    print("\nLos archivos CSV han sido generados exitosamente.")
    print("Puede abrirlos con Excel, Google Sheets o cualquier editor de CSV.")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠ Simulación interrumpida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
