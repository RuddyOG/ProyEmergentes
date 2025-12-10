from kafka import KafkaConsumer
from pymongo import MongoClient
from etl.db import get_pg_connection
from datetime import datetime, timezone
import json
import os
import sys

# ---------------------------
# Configuración Mongo
# ---------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "gamc_datos")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
air_col = mongo_db["aire"]

# ---------------------------
# Configuración PostgreSQL
# ---------------------------
try:
    pg_conn = get_pg_connection()
    pg_cur = pg_conn.cursor()
    print("✅ Conectado a PostgreSQL desde air_consumer")
except Exception as e:
    print("❌ Error conectando a PostgreSQL:", e)
    sys.exit(1)


def get_or_create_sensor(dev_eui: str) -> int:
    """
    Busca el sensor por dev_eui en la tabla sensors.
    Si no existe, lo crea con tipo 'AIRE' y dev_eui simulado.
    """
    pg_cur.execute("SELECT sensor_id FROM sensors WHERE dev_eui = %s", (dev_eui,))
    row = pg_cur.fetchone()
    if row:
        return row[0]

    pg_cur.execute(
        """
        INSERT INTO sensors (dev_eui, type, name, description)
        VALUES (%s, %s, %s, %s)
        RETURNING sensor_id
        """,
        (
            dev_eui,
            "AIRE",
            "Sensor aire simulado",
            "Sensor de aire simulado vía Kafka"
        ),
    )
    sensor_id = pg_cur.fetchone()[0]
    pg_conn.commit()
    print(f"🆕 Creado sensor AIRE en PostgreSQL: dev_eui={dev_eui}, id={sensor_id}")
    return sensor_id


# ---------------------------
# Configuración Kafka
# ---------------------------
consumer = KafkaConsumer(
    "air_quality",
    bootstrap_servers=["127.0.0.1:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="air_dual",
)

print("air_consumer escuchando en topic 'air_quality'...")


def main():
    for msg in consumer:
        data = msg.value  # dict con pm25, co2, temperature, humidity
        print("📥 Recibido AIRE:", data)

        # 1) Asegurar dev_eui (como producer no lo manda)
        dev_eui = data.get("dev_eui") or "SIM_AIR_01"

        # 2) Timestamp estándar
        measured_at = datetime.now(timezone.utc)

        # 3) Insertar en Mongo con esquema unificado
        mongo_doc = {
            "sensorDevEui": dev_eui,
            "measuredAt": measured_at,
            "object": {
                "pm25": data.get("pm25"),
                "co2": data.get("co2"),
                "temperature": data.get("temperature"),
                "humidity": data.get("humidity"),
            },
            "meta": {
                "source": "kafka_simulator",
                "topic": "air_quality",
            },
        }
        inserted = air_col.insert_one(mongo_doc)
        print(f"✅ Mongo aire _id: {inserted.inserted_id}")

        # 4) Asegurar sensor en PostgreSQL
        sensor_id = get_or_create_sensor(dev_eui)

        # 5) Insertar medición en PostgreSQL
        pg_cur.execute(
            """
            INSERT INTO air_measurements
                (sensor_id, measured_at, co2_ppm, temperature_c, humidity_pct)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                sensor_id,
                measured_at,
                data.get("co2"),
                data.get("temperature"),
                data.get("humidity"),
            ),
        )
        pg_conn.commit()
        print("✅ Insertado en PostgreSQL (air_measurements)\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⛔ air_consumer detenido por el usuario")
    finally:
        consumer.close()
        pg_cur.close()
        pg_conn.close()
        mongo_client.close()
