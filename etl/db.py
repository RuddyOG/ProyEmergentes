# etl/db.py
import os
import psycopg2
from dotenv import load_dotenv

# Carga variables del archivo .env en la raíz del proyecto
load_dotenv()

def get_pg_connection():
    """
    Devuelve una conexión abierta a PostgreSQL usando las variables
    definidas en el archivo .env.
    """
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "gamc_sensores"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )
    return conn
