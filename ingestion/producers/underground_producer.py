from kafka import KafkaProducer
import json, random, time

producer = KafkaProducer(
    bootstrap_servers=["127.0.0.1:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0)
)


print("🏗️ UNDERGROUND Producer listo...")

while True:
    data = {
        "gas_level": round(random.uniform(0, 300), 2),
        "temperature": round(random.uniform(15, 70), 2),
        "vibration": round(random.uniform(0, 5), 2)
    }
    producer.send("underground_status", data)
    print("📤 Enviado:", data)
    time.sleep(2)
