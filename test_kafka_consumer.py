from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "air_quality",
    bootstrap_servers=["127.0.0.1:9092"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    security_protocol="PLAINTEXT",
    api_version=(3, 6, 0)
)

print("✅ Conectado a Kafka, esperando mensajes...")

for msg in consumer:
    print("📥", msg.value)
