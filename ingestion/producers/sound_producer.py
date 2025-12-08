from kafka import KafkaProducer
import json, random, time

producer = KafkaProducer(
    bootstrap_servers=["127.0.0.1:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0)
)


print("🔊 SOUND Producer listo...")

while True:
    data = {
        "db_level": round(random.uniform(30, 130), 2),
        "peak": round(random.uniform(40, 150), 2),
        "duration": random.randint(1, 10)
    }
    producer.send("noise_levels", data)
    print("📤 Enviado:", data)
    time.sleep(2)
