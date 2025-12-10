# analytics/train_sound_model.py

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

def load_sound_data():
    conn = get_pg_connection()
    query = """
        SELECT
            sm.laeq_db,
            sm.measured_at,
            s.dev_eui,
            s.name
        FROM sound_measurements sm
        JOIN sensors s ON sm.sensor_id = s.sensor_id
        WHERE s.type = 'SONIDO'
          AND s.dev_eui NOT LIKE 'SIM_%'
          AND sm.laeq_db IS NOT NULL;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df["hour_of_day"] = df["measured_at"].dt.hour
    df["dayofweek"] = df["measured_at"].dt.dayofweek
    return df

def train_and_save_model():
    print("📥 Cargando datos de sonido desde PostgreSQL...")
    df_raw = load_sound_data()
    print(f"Total filas cargadas crudas: {len(df_raw)}")

    if df_raw.empty:
        print("❌ No hay datos de sonido con laeq_db. Ejecuta primero el ETL de sonido.")
        return

    df = add_time_features(df_raw)

    feature_cols = ["hour_of_day", "dayofweek"]
    X = df[feature_cols]
    y = df["laeq_db"]

    if len(df) < 50:
        print("⚠️ Pocos datos de sonido, el modelo será básico, más demostrativo que robusto.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1
    )

    print("🤖 Entrenando RandomForestRegressor para sonido (LAeq)...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("📊 Métricas del modelo de sonido:")
    print(f"  MAE  = {mae:.2f} dB")
    print(f"  RMSE = {rmse:.2f} dB")
    print(f"  R2   = {r2:.3f}")

    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "sound_regressor.pkl")

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

    print(f"💾 Modelo de sonido guardado en: {model_path}")

if __name__ == "__main__":
    train_and_save_model()
