# backend/etl/preprocess.py
import json, re, os
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

# === CONFIG ===
IN_DIR = Path(r"C:\Users\manfr\Documents\Ruddy\6to Semestre\Realidad Virtual\TecnologiasEmergentes\DatSimulados")
OUT_DIR = Path(r"C:\Users\manfr\Documents\Ruddy\6to Semestre\Realidad Virtual\TecnologiasEmergentes\backend\out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# detecta automáticamente el último archivo por tipo
def find_latest(prefix: str):
    files = sorted(IN_DIR.glob(f"{prefix}_*.csv"))
    if not files:
        print(f"[WARN] No se encontró {prefix}_*.csv en {IN_DIR}")
        return None
    return files[-1]

IN_FILES = {
    "air": find_latest("simulacion_aire"),
    "sound": find_latest("simulacion_sonido"),
    "liquid": find_latest("simulacion_soterrado"),
}

def parse_latlon(s: str):
    if not isinstance(s, str): return None, None
    m = re.findall(r"-?\d+\.?\d*", s)
    if len(m) >= 2: return float(m[0]), float(m[1])
    return None, None

def to_utc(ts):
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z","+00:00"))
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
    except Exception:
        return None

def normalize_row(row, sensor_type):
    device = row.get("deviceInfo.deviceName")
    address = row.get("deviceInfo.tags.Address")
    loc = row.get("deviceInfo.tags.Location")
    lat, lon = parse_latlon(loc)
    ts = to_utc(row.get("time"))
    battery = row.get("object.battery")
    status = None
    metrics = {}

    if sensor_type == "air":
        metrics = {
            "co2_ppm": row.get("object.co2"),
            "temp_c": row.get("object.temperature"),
            "humidity_pct": row.get("object.humidity"),
            "pressure_hpa": row.get("object.pressure"),
        }
        status = row.get("object.co2_status") or row.get("object.temperature_status")
    elif sensor_type == "sound":
        metrics = {
            "LAeq": row.get("object.LAeq"),
            "LAI": row.get("object.LAI"),
            "LAImax": row.get("object.LAImax"),
        }
        status = row.get("object.status")
    elif sensor_type == "liquid":
        metrics = {
            "distance_cm": row.get("object.distance"),
            "position": row.get("object.position"),
        }
        status = row.get("object.status")

    return {
        "device_id": device,
        "sensor_type": sensor_type,
        "ts": ts,
        "metrics": {k: v for k, v in metrics.items() if v is not None},
        "battery_pct": battery,
        "status": status,
        "address": address,
        "location": {"lat": lat, "lon": lon} if lat is not None else None,
    }

def process(kind: str, path: Path | None):
    if not path or not path.exists():
        print(f"[WARN] {kind}: no hay archivo fuente")
        return 0
    df = pd.read_csv(path)
    recs = [normalize_row(r, kind) for r in df.to_dict(orient="records")]
    out = OUT_DIR / f"{kind}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[OK] {kind}: {len(recs)} → {out}")
    return len(recs)

if __name__ == "__main__":
    total = 0
    for kind, src in IN_FILES.items():
        total += process(kind, src)
    print(f"[DONE] total registros: {total}")
