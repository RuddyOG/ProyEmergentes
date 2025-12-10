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
sound_col = mongo_db["sonido"]

# ---------------------------
# Configuración PostgreSQL
# ---------------------------
try:
    pg_conn = get_pg_connection()
    pg_cur = pg_conn.cursor()
    print("✅ Conectado a PostgreSQL desde sound_consumer")
except Exception as e:
    print("❌ Error conectando a PostgreSQL:", e)
    sys.exit(1)


def get_or_create_sensor(dev_eui: str) -> int:
    """
    Busca el sensor por dev_eui en la tabla sensors.
    Si no existe, lo crea con tipo 'SONIDO'.
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
            "SONIDO",
            "Sensor sonido simulado",
            "Sensor de sonido simulado vía Kafka",
        ),
    )
    sensor_id = pg_cur.fetchone()[0]
    pg_conn.commit()
    print(f"🆕 Creado sensor SONIDO en PostgreSQL: dev_eui={dev_eui}, id={sensor_id}")
    return sensor_id


# ---------------------------
# Configuración Kafka
# ---------------------------
consumer = KafkaConsumer(
    "noise_levels",
    bootstrap_servers=["127.0.0.1:9092"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="sound_dual",
)

print("🔊 sound_consumer escuchando en topic 'noise_levels'...")


def main():
    for msg in consumer:
        data = msg.value  # dict con db_level, peak, duration
        print("📥 Recibido SONIDO:", data)

        dev_eui = data.get("dev_eui") or "SIM_SOUND_01"
        measured_at = datetime.now(timezone.utc)

        # Mongo
        mongo_doc = {
            "sensorDevEui": dev_eui,
            "measuredAt": measured_at,
            "object": {
                "laeq": data.get("db_level"),
                "lai": data.get("db_level"),     # si luego quieres otro cálculo
                "laiMax": data.get("peak"),
                "duration": data.get("duration"),
            },
            "meta": {
                "source": "kafka_simulator",
                "topic": "noise_levels",
            },
        }
        inserted = sound_col.insert_one(mongo_doc)
        print(f"✅ Mongo sonido _id: {inserted.inserted_id}")

        # Postgres
        sensor_id = get_or_create_sensor(dev_eui)
        pg_cur.execute(
            """
            INSERT INTO sound_measurements
                (sensor_id, measured_at, laeq_db, lai_db, lai_max_db)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                sensor_id,
                measured_at,
                data.get("db_level"),
                data.get("db_level"),  # mismo valor por ahora
                data.get("peak"),
            ),
        )
        pg_conn.commit()
        print("✅ Insertado en PostgreSQL (sound_measurements)\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⛔ sound_consumer detenido por el usuario")
    finally:
        consumer.close()
        pg_cur.close()
        pg_conn.close()
        mongo_client.close()
