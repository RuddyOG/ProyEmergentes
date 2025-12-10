# backend/app/api/routes/sensors.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from psycopg2.extras import RealDictCursor
from etl.db import get_pg_connection  # usamos la misma función que los consumers

router = APIRouter(
    prefix="/sensors",
    tags=["sensors"],
)

@router.get("/air/latest")
def get_latest_air():
    try:
        conn = get_pg_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT measured_at, co2_ppm, temperature_c, humidity_pct
            FROM air_measurements
            ORDER BY measured_at DESC
            LIMIT 1;
        """)

        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="No hay mediciones de aire registradas")

        return {
            "measured_at": row["measured_at"],
            "co2": row["co2_ppm"],
            "temperature": row["temperature_c"],
            "humidity": row["humidity_pct"],
        }

    except Exception as e:
        print("❌ Error en /sensors/air/latest:", e)
        raise HTTPException(status_code=500, detail="Error consultando PostgreSQL")
