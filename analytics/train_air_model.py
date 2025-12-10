# analytics/train_air_model.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from math import sqrt

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "gamc_sensores"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )

def load_air_data():
    """
    Carga datos de aire desde PostgreSQL.
    Filtra:
      - type = 'AIRE'
      - dev_eui que NO empiece con 'SIM_' (para evitar simuladores).
      - co2_ppm, temperature_c, humidity_pct no nulos.
    """
    conn = get_pg_connection()
    query = """
        SELECT
            am.co2_ppm,
            am.temperature_c,
            am.humidity_pct,
            am.measured_at,
            s.dev_eui,
            s.name
        FROM air_measurements am
        JOIN sensors s ON am.sensor_id = s.sensor_id
        WHERE s.type = 'AIRE'
          AND s.dev_eui NOT LIKE 'SIM_%'
          AND am.co2_ppm IS NOT NULL
          AND am.temperature_c IS NOT NULL
          AND am.humidity_pct IS NOT NULL;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade columnas derivadas del tiempo: hora del día, día de la semana.
    """
    df = df.copy()
    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df["hour"] = df["measured_at"].dt.hour
    df["dayofweek"] = df["measured_at"].dt.dayofweek   # 0=lunes, 6=domingo
    return df

def train_and_save_model():
    print("📥 Cargando datos de aire desde PostgreSQL...")
    df = load_air_data()
    print(f"Total filas cargadas: {len(df)}")

    if len(df) < 100:
        print("⚠️ Muy pocos datos para entrenar algo serio, pero igual entrenaré un modelo de prueba.")
    else:
        print("✅ Suficientes datos para un modelo razonable.")

    # Añadir features de tiempo
    df = add_time_features(df)

    # Definir features X y target y
    feature_cols = ["temperature_c", "humidity_pct", "hour", "dayofweek"]
    X = df[feature_cols]
    y = df["co2_ppm"]

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modelo: RandomForestRegressor
    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )

    print("🤖 Entrenando RandomForestRegressor para CO2...")
    model.fit(X_train, y_train)

    # Evaluación simple
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("📊 Métricas del modelo:")
    print(f"  MAE  = {mae:.2f} ppm")
    print(f"  RMSE = {rmse:.2f} ppm")
    print(f"  R2   = {r2:.3f}")

    # Guardar modelo
        # Guardar modelo
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "air_co2_regressor.pkl")

    joblib.dump(
        {
            "model": model,
            "features": feature_cols,
            "metrics": {
                "mae": float(mae),
                "rmse": float(rmse),
                "r2": float(r2),
            }
        },
        model_path
    )

    print(f"💾 Modelo guardado en: {model_path}")


if __name__ == "__main__":
    train_and_save_model()
