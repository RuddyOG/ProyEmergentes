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
under_col = mongo_db["soterrado"]

# ---------------------------
# Configuración PostgreSQL
# ---------------------------
try:
    pg_conn = get_pg_connection()
    pg_cur = pg_conn.cursor()
    print("✅ Conectado a PostgreSQL desde underground_consumer")
except Exception as e:
    print("❌ Error conectando a PostgreSQL:", e)
    sys.exit(1)


def get_or_create_sensor(dev_eui: str) -> int:
    """
    Busca el sensor por dev_eui en la tabla sensors.
    Si no existe, lo crea con tipo 'SOTERRADO'.
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
            "SOTERRADO",
            "Sensor soterrado simulado",
            "Sensor soterrado simulado vía Kafka",
        ),
    )
    sensor_id = pg_cur.fetchone()[0]
    pg_conn.commit()
    print(f"🆕 Creado sensor SOTERRADO en PostgreSQL: dev_eui={dev_eui}, id={sensor_id}")
    return sensor_id


# ---------------------------
# Configuración Kafka
# ---------------------------
consumer = KafkaConsumer(
    "underground_status",
    bootstrap_servers=["127.0.0.1:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="underground_dual",
)

print("🏗️ underground_consumer escuchando en topic 'underground_status'...")


def main():
    for msg in consumer:
        data = msg.value  # dict con gas_level, temperature, vibration
        print("📥 Recibido SOTERRADO:", data)

        dev_eui = data.get("dev_eui") or "SIM_UNDER_01"
        measured_at = datetime.now(timezone.utc)

        # Mongo
        mongo_doc = {
            "sensorDevEui": dev_eui,
            "measuredAt": measured_at,
            "object": {
                "gas_level": data.get("gas_level"),
                "temperature": data.get("temperature"),
                "vibration": data.get("vibration"),
            },
            "meta": {
                "source": "kafka_simulator",
                "topic": "underground_status",
            },
        }
        inserted = under_col.insert_one(mongo_doc)
        print(f"✅ Mongo soterrado _id: {inserted.inserted_id}")

        # Postgres
        sensor_id = get_or_create_sensor(dev_eui)
        pg_cur.execute(
            """
            INSERT INTO underground_measurements
                (sensor_id, measured_at, distance_value, distance_unit, position)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                sensor_id,
                measured_at,
                data.get("gas_level"),  # usan misma columna, solo para demo
                "UNITS",
                "N/A",
            ),
        )
        pg_conn.commit()
        print("✅ Insertado en PostgreSQL (underground_measurements)\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⛔ underground_consumer detenido por el usuario")
    finally:
        consumer.close()
        pg_cur.close()
        pg_conn.close()
        mongo_client.close()