from confluent_kafka import Consumer
from pymongo import MongoClient
import json

# 🔹 Mongo LOCAL
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "gamc_datos"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["sonido"]

print(f"🟢 Mongo conectado → DB: {MONGO_DB}, colección: sonido")
print(f"DEBUG MONGO_URI: {MONGO_URI}")

# 🔹 Kafka Consumer (sonido)
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "sound_mongo_consumer",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)
consumer.subscribe(["noise_levels"])

print("🔊 Consumer escuchando el tópico: noise_levels ...")

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("⚠️ Error de Kafka:", msg.error())
            continue

        data = json.loads(msg.value().decode("utf-8"))
        print("📥 Recibido:", data)

        result = collection.insert_one(data)
        print("✅ Guardado en Mongo con _id:", result.inserted_id)

except KeyboardInterrupt:
    print("\n🛑 Detenido por el usuario.")

finally:
    consumer.close()
    print("🔒 Consumer Kafka cerrado.")
