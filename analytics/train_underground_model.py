# analytics/train_underground_model.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from math import sqrt

# Ruta base del proyecto
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


def load_underground_data():
    """
    Carga datos de soterrado desde PostgreSQL.
    Usamos distance_value como variable objetivo.
    """
    conn = get_pg_connection()
    query = """
        SELECT
            um.distance_value,
            um.battery_pct,
            um.measured_at,
            s.dev_eui,
            s.name
        FROM underground_measurements um
        JOIN sensors s ON um.sensor_id = s.sensor_id
        WHERE s.type = 'SOTERRADO'
          AND s.dev_eui NOT LIKE 'SIM_%'
          AND um.distance_value IS NOT NULL
          AND um.battery_pct IS NOT NULL;
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
    print("📥 Cargando datos de soterrado desde PostgreSQL...")
    df = load_underground_data()
    print(f"Total filas cargadas: {len(df)}")

    if len(df) == 0:
        print("❌ No hay datos válidos de soterrado (distance_value / battery_pct). "
              "Verifica la tabla underground_measurements.")
        return

    if len(df) < 100:
        print("⚠️ Pocos datos de soterrado, el modelo será de prueba.")
    else:
        print("✅ Suficientes datos para un modelo razonable.")

    # Añadir features de tiempo
    df = add_time_features(df)

    # Definir features X y target y
    feature_cols = ["battery_pct", "hour", "dayofweek"]
    X = df[feature_cols]
    y = df["distance_value"]

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

    print("🤖 Entrenando RandomForestRegressor para soterrado...")
    model.fit(X_train, y_train)

    # Evaluación simple
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("📊 Métricas del modelo soterrado:")
    print(f"  MAE  = {mae:.2f} (unidades de distance_value)")
    print(f"  RMSE = {rmse:.2f}")
    print(f"  R2   = {r2:.3f}")

    # Guardar modelo
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "underground_regressor.pkl")

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

    print(f"💾 Modelo soterrado guardado en: {model_path}")


if __name__ == "__main__":
    train_and_save_model()
