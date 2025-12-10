# etl/etl_sound_from_csv.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import glob

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

SOUND_CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "WS302-915M SONIDO NOV 2024.csv"  # file with spaces
)


def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "gamc_sensores"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )

import glob

def load_csv():
    # buscar cualquier archivo que contenga WS302 y SONIDO
    pattern = os.path.join(BASE_DIR, "data", "*WS302*SONIDO*.csv")
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("❌ No encontré ningún CSV que contenga WS302 y SONIDO en /data")

    csv_path = files[0]
    print(f"📥 Detectado archivo CSV de sonido: {csv_path}")

    df = pd.read_csv(csv_path, encoding="latin-1", low_memory=False)

    print(f"Filas cargadas crudas: {len(df)}")
    return df

def main():
    df = load_csv()

    # Nos quedamos solo con las columnas que nos interesan
    needed_cols = [
        "time",
        "deviceInfo.devEui",
        "devAddr",
        "fCnt",
        "dr",
        "object.LAeq",
        "object.LAI",
        "object.LAImax",
        "object.battery",
        "object.status",
    ]

    for col in needed_cols:
        if col not in df.columns:
            raise ValueError(f"❌ Falta la columna '{col}' en el CSV. Revisa el encabezado.")

    df = df[needed_cols].copy()

    # Filtramos filas con LAeq válido
    df = df[df["object.LAeq"].notnull()]
    print(f"Filas con LAeq válido: {len(df)}")

    if df.empty:
        print("❌ No hay filas con LAeq. Revisa que el CSV tenga datos en object.LAeq.")
        return

    # Parsear tiempo (viene en UTC con +00:00) y convertir a hora local
    df["measured_at_utc"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df[df["measured_at_utc"].notnull()]
    print(f"Filas con timestamp válido: {len(df)}")

    # Ajustamos a zona horaria de Cochabamba (UTC-4)
    df["measured_at"] = df["measured_at_utc"].dt.tz_convert("America/La_Paz")
    df["hour_of_day"] = df["measured_at"].dt.hour
    df["dayofweek"] = df["measured_at"].dt.dayofweek  # 0=lunes

    # Conexión a Postgres
    conn = get_pg_connection()
    cur = conn.cursor()

    # Mapeo dev_eui -> sensor_id
    cur.execute("""
        SELECT sensor_id, dev_eui
        FROM sensors
        WHERE type = 'SONIDO';
    """)
    rows = cur.fetchall()
    dev_eui_to_id = {dev_eui: sensor_id for (sensor_id, dev_eui) in rows}
    print(f"Sensores de sonido en tabla sensors: {len(dev_eui_to_id)}")

    # Opcional: limpiar tabla antes de cargar (porque ahora sí cargamos datos reales)
    print("🧹 Limpiando tabla sound_measurements...")
    cur.execute("TRUNCATE TABLE sound_measurements RESTART IDENTITY;")
    conn.commit()

    insert_sql = """
        INSERT INTO sound_measurements (
            sensor_id,
            measured_at,
            laeq_db,
            lai_db,
            lai_max_db,
            battery_pct,
            status,
            dev_addr,
            fcnt,
            dr
        )
        VALUES (%(sensor_id)s, %(measured_at)s, %(laeq_db)s, %(lai_db)s, %(lai_max_db)s,
                %(battery_pct)s, %(status)s, %(dev_addr)s, %(fcnt)s, %(dr)s)
    """

    inserted = 0
    skipped_no_sensor = 0

    for _, row in df.iterrows():
        dev_eui = row["deviceInfo.devEui"]

        sensor_id = dev_eui_to_id.get(dev_eui)
        if sensor_id is None:
            skipped_no_sensor += 1
            continue

        measured_at = row["measured_at"].to_pydatetime()  # tz-aware, Postgres timestamptz lo acepta

        payload = {
            "sensor_id": sensor_id,
            "measured_at": measured_at,
            "laeq_db": float(row["object.LAeq"]) if pd.notnull(row["object.LAeq"]) else None,
            "lai_db": float(row["object.LAI"]) if pd.notnull(row["object.LAI"]) else None,
            "lai_max_db": float(row["object.LAImax"]) if pd.notnull(row["object.LAImax"]) else None,
            "battery_pct": float(row["object.battery"]) if pd.notnull(row["object.battery"]) else None,
            "status": str(row["object.status"]) if pd.notnull(row["object.status"]) else None,
            "dev_addr": str(row["devAddr"]) if pd.notnull(row["devAddr"]) else None,
            "fcnt": int(row["fCnt"]) if pd.notnull(row["fCnt"]) else None,
            "dr": str(row["dr"]) if pd.notnull(row["dr"]) else None,
        }

        cur.execute(insert_sql, payload)
        inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Filas insertadas en sound_measurements: {inserted}")
    print(f"⚠️ Filas saltadas por no encontrar sensor en 'sensors' (dev_eui): {skipped_no_sensor}")

if __name__ == "__main__":
    main()
