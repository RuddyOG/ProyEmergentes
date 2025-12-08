import pandas as pd
from pathlib import Path
from etl.db import get_pg_connection

# Nombre REAL de tu CSV de soterrados
CSV_PATH = Path("data/raw/EM310-UDL-915M soterrados nov 2024.csv")

# Si tu CSV usa ';' en lugar de ',', cambia SEP a ';'
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

    print(f"Leyendo CSV de soterrados: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, sep=SEP, low_memory=False)

    # Helper: busca la PRIMERA columna que exista
    def col(*names):
        for name in names:
            if name in df.columns:
                return df[name]
        return None

    # ------------------------
    # METADATOS DE DISPOSITIVO
    # ------------------------
    dev_eui = col(
        "deviceInfo.devEui",
        "deviceinfo.devEui",
        "DevEui",
        "devEui",
    )
    device_name = col(
        "deviceInfo.deviceName",
        "deviceinfo.deviceName",
        "Nombre",
        "deviceName",
    )
    tenant_name = col(
        "deviceInfo.tenantName",
        "deviceinfo.tenantName",
        "tenantName",
    )
    application_name = col(
        "deviceInfo.applicatioName",
        "deviceinfo.applicatioName",
        "applicationName",
    )
    description = col(
        "deviceInfo.Tag.description",
        "deviceInfo.tag.description",
        "deviceinfo.Tag.description",
        "deviceinfo.tag.description",
        "Descripcion",
    )
    address = col(
        "deviceInfo.Tag.Address",
        "deviceInfo.tag.Address",
        "deviceInfo.tag.address",
        "deviceinfo.Tag.Address",
        "deviceinfo.tag.Address",
        "deviceinfo.tag.address",
        "Address",
    )
    location_raw = col(
        "deviceInfo.tag.location",
        "deviceInfo.Tag.location",
        "deviceinfo.tag.location",
        "location",
    )

    dev_addr = col("devAddr", "DevAddr")
    fcnt = col("fcnt", "fCnt")
    dr = col("dr", "DR")

    # Time LoRaWAN o Fecha de LLDS12
    time_raw = col("Time", "Fecha", "time")

    # ------------------------
    # CAMPOS DE MEDICIÓN
    # ------------------------
    distance = col("object.distance", "Object.distance", "Distance", "distance")
    position = col("object.position", "Object.position", "Position")
    battery = col("object.battery", "Object.battery", "Battery", "battery")
    status = col("object.status", "Object.status", "Status", "status")
    unit = col("Unidad", "unit", "object.unit", "Object.unit")

    conn = get_pg_connection()
    cur = conn.cursor()

    total = len(df)
    inserted = 0

    for i in range(total):
        try:
            # ------- dev_eui obligatorio -------
            row_dev_eui = None
            if dev_eui is not None:
                val = dev_eui.iloc[i]
                if not pd.isna(val):
                    row_dev_eui = str(val)

            if not row_dev_eui or row_dev_eui.lower() == "nan":
                # Sin devEui no podemos enlazar sensor → saltar
                continue

            # ------- metadata opcional -------
            row_device_name = str(device_name.iloc[i]) if device_name is not None and not pd.isna(device_name.iloc[i]) else None
            row_tenant_name = str(tenant_name.iloc[i]) if tenant_name is not None and not pd.isna(tenant_name.iloc[i]) else None
            row_app_name = str(application_name.iloc[i]) if application_name is not None and not pd.isna(application_name.iloc[i]) else None
            row_desc = str(description.iloc[i]) if description is not None and not pd.isna(description.iloc[i]) else None
            row_address = str(address.iloc[i]) if address is not None and not pd.isna(address.iloc[i]) else None
            row_loc = str(location_raw.iloc[i]) if location_raw is not None and not pd.isna(location_raw.iloc[i]) else None
            lat, lon = parse_lat_lon(row_loc)

            # ------- tiempo -------
            row_time = time_raw.iloc[i] if time_raw is not None else None
            if pd.isna(row_time):
                continue
            try:
                measured_at = pd.to_datetime(row_time, utc=True)
            except Exception:
                continue

            # ------- meta LoRaWAN -------
            row_dev_addr = str(dev_addr.iloc[i]) if dev_addr is not None and not pd.isna(dev_addr.iloc[i]) else None
            row_fcnt = int(fcnt.iloc[i]) if fcnt is not None and not pd.isna(fcnt.iloc[i]) else None
            row_dr = str(dr.iloc[i]) if dr is not None and not pd.isna(dr.iloc[i]) else None

            # ------- mediciones -------
            row_distance = float(distance.iloc[i]) if distance is not None and not pd.isna(distance.iloc[i]) else None
            row_position = str(position.iloc[i]) if position is not None and not pd.isna(position.iloc[i]) else None
            row_battery = float(battery.iloc[i]) if battery is not None and not pd.isna(battery.iloc[i]) else None
            row_status = str(status.iloc[i]) if status is not None and not pd.isna(status.iloc[i]) else None
            row_unit = str(unit.iloc[i]) if unit is not None and not pd.isna(unit.iloc[i]) else None

            # Si ni siquiera hay distancia, no tiene mucho sentido guardar la medición
            if row_distance is None:
                continue

            # ------- upsert sensor -------
            cur.execute(
                """
                INSERT INTO sensors (
                    dev_eui, type, name, description, address,
                    latitude, longitude, tenant_name, application_name
                ) VALUES (
                    %(dev_eui)s, 'SOTERRADO', %(name)s, %(description)s, %(address)s,
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

            # ------- insert medición -------
            cur.execute(
                """
                INSERT INTO underground_measurements (
                    sensor_id, measured_at,
                    distance_value, distance_unit, position,
                    battery_pct, status, dev_addr, fcnt, dr
                ) VALUES (
                    %(sensor_id)s, %(measured_at)s,
                    %(distance)s, %(unit)s, %(position)s,
                    %(battery)s, %(status)s, %(dev_addr)s, %(fcnt)s, %(dr)s
                );
                """,
                {
                    "sensor_id": sensor_id,
                    "measured_at": measured_at,
                    "distance": row_distance,
                    "unit": row_unit,
                    "position": row_position,
                    "battery": row_battery,
                    "status": row_status,
                    "dev_addr": row_dev_addr,
                    "fcnt": row_fcnt,
                    "dr": row_dr,
                },
            )

            inserted += 1
            if inserted % 1000 == 0:
                conn.commit()
                print(f"{inserted} filas insertadas...")

        except Exception as e:
            conn.rollback()
            print(f"Error en fila {i}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"ETL soterrados terminado. Filas insertadas: {inserted} de {total}")


if __name__ == "__main__":
    main()
