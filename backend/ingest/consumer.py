# backend/ingest/consumer.py
import os, json
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Lee .env en la raíz
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB  = os.getenv("MONGO_DB", "gamc_datos")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

SRC = Path("backend/out")  # donde deja preprocess.py sus .jsonl
MAP = {
    "air": "aire",
    "sound": "sonido",
    "liquid": "soterrado",
}

def consume(kind: str) -> int:
    src = SRC / f"{kind}.jsonl"
    if not src.exists():
        print(f"[WARN] No existe {src}")
        return 0
    coll = db[MAP[kind]]
    n = 0
    with src.open("r", encoding="utf-8") as f:
        batch = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                batch.append(doc)
                if len(batch) >= 1000:
                    coll.insert_many(batch)
                    n += len(batch)
                    batch = []
            except Exception as e:
                print(f"[ERR] línea inválida: {e}")
        if batch:
            coll.insert_many(batch)
            n += len(batch)
    print(f"[OK] Consumido {kind}: {n} docs → {MAP[kind]}")
    return n

if __name__ == "__main__":
    total = 0
    for k in ["air", "sound", "liquid"]:
        total += consume(k)
    print(f"[DONE] total: {total}")
