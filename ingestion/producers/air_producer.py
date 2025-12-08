from kafka import KafkaProducer
import json, random, time

producer = KafkaProducer(
    bootstrap_servers=["127.0.0.1:9092"],          # 👈 lista + 127.0.0.1
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    security_protocol="PLAINTEXT",                 # 👈 explícito
    api_version=(3, 6, 0)                          # 👈 evita check_version
)

print("🌬️ AIR Producer listo...")

while True:
    data = {
        "pm25": round(random.uniform(5, 120), 2),
        "co2": round(random.uniform(300, 2000), 2),
        "temperature": round(random.uniform(18, 40), 2),
        "humidity": round(random.uniform(20, 90), 2)
    }
    producer.send("air_quality", data)
    print("📤 Enviado:", data)
    time.sleep(2)
