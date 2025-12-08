import pandas as pd
from pathlib import Path
from datetime import datetime
from etl.db import get_pg_connection

# Ruta al CSV (ajusta el nombre si es otro)
CSV_PATH = Path("data/raw/EM500-CO2-915M nov 2024.csv")

# Si tu CSV usa ';' en vez de ',', cambia SEP a ';'
SEP = ","


def parse_lat_lon(location: str):
    if not isinstance(location, str) or "," not in location:
        return None, None
    lat_str, lon_str = location.split(",", 1)
    try:
        return float(lat_str), float(lon_str)
    except ValueError:
        return None, None


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encuentra el CSV: {CSV_PATH}")

    print(f"Leyendo CSV de aire: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, sep=SEP, low_memory=False)

    # Normalizamos nombres de columnas que vamos a usar
    def col(name1, name2=None):
        if name1 in df.columns:
            return df[name1]
        if name2 and name2 in df.columns:
            return df[name2]
        return None

    dev_eui = col("deviceInfo.devEui", "deviceinfo.devEui")
    device_name = col("deviceInfo.deviceName", "deviceinfo.deviceName")
    tenant_name = col("deviceInfo.tenantName", "deviceinfo.tenantName")
    application_name = col("deviceInfo.applicatioName", "deviceinfo.applicatioName")
    description = col("deviceInfo.tag.description", "deviceinfo.tag.description")
    address = col("deviceInfo.tag.Address", "deviceInfo.tag.address")
    location_raw = col("deviceInfo.tag.location", "deviceinfo.tag.location")
    dev_addr = col("devAddr", "DevAddr")
    fcnt = col("fcnt", "fCnt")
    dr = col("dr", "DR")
    time_raw = col("Time", "time")

    co2 = col("object.co2")
    temperature = col("object.temperature")
    humidity = col("object.humidity")
    battery = col("object.battery")
    status = col("object.status")

    conn = get_pg_connection()
    cur = conn.cursor()

    total = len(df)
    inserted = 0

    for i in range(total):
        try:
            row_dev_eui = str(dev_eui.iloc[i]) if dev_eui is not None else None
            if not row_dev_eui or row_dev_eui == "nan":
                continue

            row_device_name = str(device_name.iloc[i]) if device_name is not None else None
            row_tenant_name = str(tenant_name.iloc[i]) if tenant_name is not None else None
            row_app_name = str(application_name.iloc[i]) if application_name is not None else None
            row_desc = str(description.iloc[i]) if description is not None else None
            row_address = str(address.iloc[i]) if address is not None else None
            row_loc = str(location_raw.iloc[i]) if location_raw is not None else None

            lat, lon = parse_lat_lon(row_loc)

            # Parseo de fecha
            row_time = time_raw.iloc[i] if time_raw is not None else None
            if pd.isna(row_time):
                continue
            try:
                measured_at = pd.to_datetime(row_time, utc=True)
            except Exception:
                continue

            row_dev_addr = str(dev_addr.iloc[i]) if dev_addr is not None else None
            row_fcnt = int(fcnt.iloc[i]) if fcnt is not None and not pd.isna(fcnt.iloc[i]) else None
            row_dr = str(dr.iloc[i]) if dr is not None else None

            row_co2 = float(co2.iloc[i]) if co2 is not None and not pd.isna(co2.iloc[i]) else None
            row_temp = float(temperature.iloc[i]) if temperature is not None and not pd.isna(temperature.iloc[i]) else None
            row_hum = float(humidity.iloc[i]) if humidity is not None and not pd.isna(humidity.iloc[i]) else None
            row_battery = float(battery.iloc[i]) if battery is not None and not pd.isna(battery.iloc[i]) else None
            row_status = str(status.iloc[i]) if status is not None and not pd.isna(status.iloc[i]) else None

            # 1) Upsert en sensors
            cur.execute(
                """
                INSERT INTO sensors (
                    dev_eui, type, name, description, address,
                    latitude, longitude, tenant_name, application_name
                ) VALUES (
                    %(dev_eui)s, 'AIRE', %(name)s, %(description)s, %(address)s,
                    %(lat)s, %(lon)s, %(tenant)s, %(app)s
                )
                ON CONFLICT (dev_eui) DO UPDATE
                   SET name = EXCLUDED.name,
                       description = EXCLUDED.description,
                       address = EXCLUDED.address,
                       latitude = EXCLUDED.latitude,
                       longitude = EXCLUDED.longitude,
                       tenant_name = EXCLUDED.tenant_name,
                       application_name = EXCLUDED.application_name
                RETURNING sensor_id;
                """,
                {
                    "dev_eui": row_dev_eui,
                    "name": row_device_name,
                    "description": row_desc,
                    "address": row_address,
                    "lat": lat,
                    "lon": lon,
                    "tenant": row_tenant_name,
                    "app": row_app_name,
                },
            )
            sensor_id = cur.fetchone()[0]

            # 2) Insert en air_measurements
            cur.execute(
                """
                INSERT INTO air_measurements (
                    sensor_id, measured_at,
                    co2_ppm, temperature_c, humidity_pct,
                    battery_pct, status, dev_addr, fcnt, dr
                ) VALUES (
                    %(sensor_id)s, %(measured_at)s,
                    %(co2)s, %(temp)s, %(hum)s,
                    %(battery)s, %(status)s, %(dev_addr)s, %(fcnt)s, %(dr)s
                );
                """,
                {
                    "sensor_id": sensor_id,
                    "measured_at": measured_at,
                    "co2": row_co2,
                    "temp": row_temp,
                    "hum": row_hum,
                    "battery": row_battery,
                    "status": row_status,
                    "dev_addr": row_dev_addr,
                    "fcnt": row_fcnt,
                    "dr": row_dr,
                },
            )

            inserted += 1
            if inserted % 100 == 0:
                conn.commit()
                print(f"{inserted} filas insertadas...")

        except Exception as e:
            conn.rollback()
            print(f"Error en fila {i}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"ETL aire terminado. Filas insertadas: {inserted} de {total}")


if __name__ == "__main__":
    main()
