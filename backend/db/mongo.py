# backend/db/mongo.py
import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

# Carga el .env más cercano al CWD (raíz del proyecto) y pisa valores previos.
env_path = find_dotenv(usecwd=True)
load_dotenv(dotenv_path=env_path, override=True)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB  = os.getenv("MONGO_DB", "gamc_datos")

# Debug útil en desarrollo (puedes comentar luego):
print("[mongo.py] .env usado:", env_path)
print("[mongo.py] MONGO_URI (oculta credenciales):", (MONGO_URI or "").split("@")[0] + "@***")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI no está definido. Crea .env en la RAÍZ del repo con MONGO_URI y MONGO_DB.")

if "localhost" in MONGO_URI or "127.0.0.1" in MONGO_URI:
    raise RuntimeError(f"MONGO_URI apunta a localhost ({MONGO_URI}). Debe ser tu SRV de Atlas.")

client = MongoClient(MONGO_URI)
mongo_db = client[MONGO_DB]

def get_mongo_collection(name: str):
    return mongo_db[name]
