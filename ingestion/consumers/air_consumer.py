from confluent_kafka import Consumer
from pymongo import MongoClient
import json

# 🔹 Conexión DIRECTA a Mongo local (olvidamos .env aquí)
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "gamc_datos"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["aire"]

print(f"🟢 Mongo conectado → DB: {MONGO_DB}, colección: aire")
print(f"DEBUG MONGO_URI: {MONGO_URI}")

# 🔹 Configurar Kafka Consumer
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "air_mongo_consumer",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
consumer.subscribe(["air_quality"])

print("🌬️ Consumer escuchando el tópico: air_quality ...")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("⚠️ Error de Kafka:", msg.error())
            continue

        # Mensaje válido
        data = json.loads(msg.value().decode("utf-8"))
        print("📥 Recibido:", data)

        # Insertar en Mongo LOCAL
        result = collection.insert_one(data)
        print("✅ Guardado en Mongo con _id:", result.inserted_id)

except KeyboardInterrupt:
    print("\n🛑 Detenido por el usuario.")

finally:
    consumer.close()
    print("🔒 Consumer Kafka cerrado.")
