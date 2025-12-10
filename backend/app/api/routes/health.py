# backend/app/api/routes/health.py
from fastapi import APIRouter
from pymongo import MongoClient
from kafka import KafkaConsumer
from etl.db import get_pg_connection
import os

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/")
def health_check():
    status = {}

    # --- Mongo ---
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGO_DB", "gamc_datos")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
        client[mongo_db].command("ping")
        status["mongo"] = "ok"
    except Exception as e:
        print("❌ Mongo error:", e)
        status["mongo"] = "error"

    # --- PostgreSQL ---
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        status["postgres"] = "ok"
    except Exception as e:
        print("❌ Postgres error:", e)
        status["postgres"] = "error"

    # --- Kafka ---
    try:
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        consumer = KafkaConsumer(
            bootstrap_servers=[bootstrap],
            api_version=(3, 6, 0),
            security_protocol="PLAINTEXT",
        )
        _ = consumer.topics()
        consumer.close()
        status["kafka"] = "ok"
    except Exception as e:
        print("❌ Kafka error:", e)
        status["kafka"] = "error"

    return status
