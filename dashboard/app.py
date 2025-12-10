# dashboard/app.py
import os
from datetime import datetime, timedelta

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import joblib

# ===========================
# CONFIGURACIÓN BÁSICA
# ===========================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

st.set_page_config(
    page_title="Dashboard GAMC",
    page_icon="📊",
    layout="wide",
)

# ===========================
# CONEXIÓN A POSTGRES
# ===========================
def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "gamc_sensores"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )

# ===========================
# HELPERS COMUNES
# ===========================
def seleccionar_rango_fechas(conn, tabla, sensor_id, col_fecha="measured_at"):
    """
    Obtiene min y max de fechas para el sensor y muestra un selector
    de rango [fecha_inicio, fecha_fin]. Devuelve (desde_dt, hasta_dt, etiqueta).
    """
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT MIN({col_fecha}), MAX({col_fecha}) "
            f"FROM {tabla} WHERE sensor_id = %s",
            (int(sensor_id),)
        )
        min_dt, max_dt = cur.fetchone()

    if min_dt is None or max_dt is None:
        return None, None, "Sin datos"

    min_date = min_dt.date()
    max_date = max_dt.date()

    # Por defecto últimos 7 días dentro del rango disponible
    default_start = max_date - timedelta(days=7)
    if default_start < min_date:
        default_start = min_date

    fecha_inicio, fecha_fin = st.date_input(
        "Rango de fechas",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Pasamos a datetimes (inicio del día / fin del día)
    desde_dt = datetime.combine(fecha_inicio, datetime.min.time())
    hasta_dt = datetime.combine(fecha_fin, datetime.max.time())

    etiqueta = f"{fecha_inicio.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
    return desde_dt, hasta_dt, etiqueta


def plot_timeseries(df, x_col, y_col, title, color=None, y_label=None):
    if df.empty:
        st.warning("No hay datos en el rango seleccionado.")
        return
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color,
        title=title,
    )
    fig.update_layout(xaxis_title="Tiempo", yaxis_title=y_label or y_col)
    st.plotly_chart(fig, use_container_width=True)


def load_model(path):
    try:
        return joblib.load(path)
    except Exception:
        return None

# ===========================
# VISTA: AIRE
# ===========================
def vista_aire():
    st.header("🌬️ Sensor de Aire – CO₂ / Temperatura / Humedad")

    conn = get_pg_connection()
    sens_df = pd.read_sql(
        "SELECT sensor_id, name FROM sensors "
        "WHERE type = 'AIRE' AND dev_eui NOT LIKE 'SIM_%' "
        "ORDER BY name",
        conn,
    )

    if sens_df.empty:
        st.error("No hay sensores de AIRE configurados en la tabla sensors.")
        conn.close()
        return

    sensor_name = st.selectbox("Sensor", sens_df["name"])
    sensor_id = int(sens_df.loc[sens_df["name"] == sensor_name, "sensor_id"].iloc[0])

    desde, hasta, rango_label = seleccionar_rango_fechas(
        conn, "air_measurements", sensor_id, col_fecha="measured_at"
    )

    if desde is None:
        st.warning("No hay datos de aire para este sensor.")
        conn.close()
        return

    query = """
        SELECT
            am.measured_at,
            am.co2_ppm,
            am.temperature_c,
            am.humidity_pct
        FROM air_measurements am
        WHERE am.sensor_id = %s
          AND am.measured_at BETWEEN %s AND %s
          AND am.co2_ppm IS NOT NULL
        ORDER BY am.measured_at;
    """

    df = pd.read_sql(query, conn, params=(sensor_id, desde, hasta))
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total registros", len(df))
    with col2:
        st.metric("CO₂ promedio (ppm)", f"{df['co2_ppm'].mean():.1f}" if not df.empty else "—")
    with col3:
        st.metric("Temp. promedio (°C)", f"{df['temperature_c'].mean():.1f}" if not df.empty else "—")
    with col4:
        st.metric("Humedad promedio (%)", f"{df['humidity_pct'].mean():.1f}" if not df.empty else "—")

    st.subheader(f"Evolución de CO₂ – {sensor_name} ({rango_label})")
    plot_timeseries(df, "measured_at", "co2_ppm", "CO₂ (ppm) en el tiempo", y_label="CO₂ (ppm)")

    with st.expander("Ver temperatura y humedad"):
        plot_timeseries(df, "measured_at", "temperature_c", "Temperatura (°C)", y_label="°C")
        plot_timeseries(df, "measured_at", "humidity_pct", "Humedad (%)", y_label="%")

# ===========================
# VISTA: SONIDO
# ===========================
def vista_sonido():
    st.header("🔊 Sensor de Sonido – LAeq / LAI / LAImax")

    conn = get_pg_connection()
    sens_df = pd.read_sql(
        "SELECT sensor_id, name FROM sensors "
        "WHERE type = 'SONIDO' AND dev_eui NOT LIKE 'SIM_%' "
        "ORDER BY name",
        conn,
    )

    if sens_df.empty:
        st.error("No hay sensores de SONIDO configurados en la tabla sensors.")
        conn.close()
        return

    sensor_name = st.selectbox("Sensor", sens_df["name"])
    sensor_id = int(sens_df.loc[sens_df["name"] == sensor_name, "sensor_id"].iloc[0])

    desde, hasta, rango_label = seleccionar_rango_fechas(
        conn, "sound_measurements", sensor_id, col_fecha="measured_at"
    )

    if desde is None:
        st.warning("No hay datos de sonido para este sensor.")
        conn.close()
        return

    query = """
        SELECT
            sm.measured_at,
            sm.laeq_db,
            sm.lai_db,
            sm.lai_max_db
        FROM sound_measurements sm
        WHERE sm.sensor_id = %s
          AND sm.measured_at BETWEEN %s AND %s
          AND sm.laeq_db IS NOT NULL
        ORDER BY sm.measured_at;
    """

    df = pd.read_sql(query, conn, params=(sensor_id, desde, hasta))
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total registros", len(df))
    with col2:
        st.metric("LAeq promedio (dB)", f"{df['laeq_db'].mean():.1f}" if not df.empty else "—")
    with col3:
        st.metric("LAI promedio (dB)", f"{df['lai_db'].mean():.1f}" if not df.empty else "—")
    with col4:
        st.metric("LAImax promedio (dB)", f"{df['lai_max_db'].mean():.1f}" if not df.empty else "—")

    st.subheader(f"Evolución LAeq – {sensor_name} ({rango_label})")
    plot_timeseries(df, "measured_at", "laeq_db", "LAeq (dB) en el tiempo", y_label="dB")

    with st.expander("Ver LAI y LAImax"):
        plot_timeseries(df, "measured_at", "lai_db", "LAI (dB)", y_label="dB")
        plot_timeseries(df, "measured_at", "lai_max_db", "LAImax (dB)", y_label="dB")

# ===========================
# VISTA: SOTERRADO
# ===========================
def vista_soterrado():
    st.header("🕳️ Sensor Soterrado – Distancia / Batería / Estado")

    conn = get_pg_connection()
    sens_df = pd.read_sql(
        "SELECT sensor_id, name FROM sensors "
        "WHERE type = 'SOTERRADO' AND dev_eui NOT LIKE 'SIM_%' "
        "ORDER BY name",
        conn,
    )

    if sens_df.empty:
        st.error("No hay sensores SOTERRADO configurados en la tabla sensors.")
        conn.close()
        return

    sensor_name = st.selectbox("Sensor", sens_df["name"])
    sensor_id = int(sens_df.loc[sens_df["name"] == sensor_name, "sensor_id"].iloc[0])

    desde, hasta, rango_label = seleccionar_rango_fechas(
        conn, "underground_measurements", sensor_id, col_fecha="measured_at"
    )

    if desde is None:
        st.warning("No hay datos soterrados para este sensor.")
        conn.close()
        return

    query = """
        SELECT
            um.measured_at,
            um.distance_value,
            um.battery_pct,
            um.status
        FROM underground_measurements um
        WHERE um.sensor_id = %s
          AND um.measured_at BETWEEN %s AND %s
          AND um.distance_value IS NOT NULL
        ORDER BY um.measured_at;
    """

    df = pd.read_sql(query, conn, params=(sensor_id, desde, hasta))
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total registros", len(df))
    with col2:
        st.metric("Distancia promedio", f"{df['distance_value'].mean():.1f}" if not df.empty else "—")
    with col3:
        st.metric(
            "Batería promedio (%)",
            f"{df['battery_pct'].mean():.1f}" if ("battery_pct" in df and not df.empty) else "—",
        )
    with col4:
        if "status" in df and not df.empty:
            st.metric("Estados distintos", df["status"].nunique())
        else:
            st.metric("Estados distintos", "—")

    st.subheader(f"Evolución de distancia – {sensor_name} ({rango_label})")
    plot_timeseries(df, "measured_at", "distance_value", "Distancia medida", y_label="unidades")

# ===========================
# VISTA: PROYECCIONES ML
# (igual que antes, sólo lectura de modelos + ejemplo)
# ===========================
def vista_ml():
    st.header("🤖 Proyecciones con Machine Learning")

    st.markdown(
        """
        Aquí mostramos un resumen de los **modelos entrenados en Python** 
        (`analytics/train_air_model.py`, `analytics/train_sound_model.py`, 
        `analytics/train_underground_model.py`) y una proyección sencilla 
        a partir de los últimos datos históricos.
        """
    )

    models_dir = os.path.join(BASE_DIR, "models")

    air_path = os.path.join(models_dir, "air_co2_regressor.pkl")
    sound_path = os.path.join(models_dir, "sound_regressor.pkl")
    und_path = os.path.join(models_dir, "underground_regressor.pkl")

    col1, col2, col3 = st.columns(3)

    # --- Modelo Aire ---
    with col1:
        st.subheader("🌬️ Aire – CO₂")
        air_model_obj = load_model(air_path)
        if air_model_obj is None:
            st.error("No se encontró air_co2_regressor.pkl")
        else:
            metrics = air_model_obj.get("metrics", {})
            st.write("Modelo RandomForestRegressor entrenado.")
            st.metric("R²", f"{metrics.get('r2', 0):.3f}" if metrics else "ver consola")
            st.metric("MAE (ppm)", f"{metrics.get('mae', 0):.2f}" if metrics else "ver consola")
            st.metric("RMSE (ppm)", f"{metrics.get('rmse', 0):.2f}" if metrics else "ver consola")

    # --- Modelo Sonido ---
    with col2:
        st.subheader("🔊 Sonido – LAeq")
        sound_model_obj = load_model(sound_path)
        if sound_model_obj is None:
            st.error("No se encontró sound_regressor.pkl")
        else:
            st.write("Modelo RandomForestRegressor entrenado.")
            st.caption("Métricas se vieron al entrenar (MAE≈5.06 dB, RMSE≈8.01 dB, R²≈0.35).")

    # --- Modelo Soterrado ---
    with col3:
        st.subheader("🕳️ Soterrado – Distancia")
        und_model_obj = load_model(und_path)
        if und_model_obj is None:
            st.error("No se encontró underground_regressor.pkl")
        else:
            metrics = und_model_obj.get("metrics", {})
            st.write("Modelo RandomForestRegressor entrenado.")
            st.metric("R²", f"{metrics.get('r2', 0):.3f}" if metrics else "ver consola")
            st.metric("MAE", f"{metrics.get('mae', 0):.2f}" if metrics else "ver consola")
            st.metric("RMSE", f"{metrics.get('rmse', 0):.2f}" if metrics else "ver consola")

    st.markdown("---")
    st.subheader("Ejemplo de proyección rápida (aire) usando el modelo entrenado")

    air_model_obj = load_model(air_path)
    if air_model_obj is not None:
        conn = get_pg_connection()
        df = pd.read_sql(
            """
            SELECT am.measured_at, am.co2_ppm, am.temperature_c, am.humidity_pct
            FROM air_measurements am
            JOIN sensors s ON am.sensor_id = s.sensor_id
            WHERE s.type = 'AIRE'
              AND s.dev_eui NOT LIKE 'SIM_%'
              AND am.co2_ppm IS NOT NULL
            ORDER BY am.measured_at DESC
            LIMIT 7*24
            """,
            conn,
        )
        conn.close()
        if df.empty:
            st.warning("No hay suficientes datos de aire para hacer una proyección de ejemplo.")
            return

        df = df.sort_values("measured_at")
        df["hour"] = df["measured_at"].dt.hour
        df["dayofweek"] = df["measured_at"].dt.dayofweek

        model = air_model_obj["model"]
        features = air_model_obj["features"]

        future_horizonte = 7 * 24
        last_row = df.iloc[-1].copy()

        future_rows = []
        for i in range(1, future_horizonte + 1):
            ts = last_row["measured_at"] + timedelta(hours=i)
            future_rows.append(
                {
                    "measured_at": ts,
                    "temperature_c": last_row["temperature_c"],
                    "humidity_pct": last_row["humidity_pct"],
                    "hour": ts.hour,
                    "dayofweek": ts.weekday(),
                }
            )

        future_df = pd.DataFrame(future_rows)
        future_X = future_df[features]
        future_df["co2_pred"] = model.predict(future_X)

        hist_df = df[["measured_at", "co2_ppm"]].rename(columns={"co2_ppm": "CO2 (histórico)"})
        proj_df = future_df[["measured_at", "co2_pred"]].rename(columns={"co2_pred": "CO2 (proyección)"})

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=hist_df["measured_at"],
                y=hist_df["CO2 (histórico)"],
                mode="markers",
                name="Histórico",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=proj_df["measured_at"],
                y=proj_df["CO2 (proyección)"],
                mode="lines",
                name="Proyección 7 días",
            )
        )
        fig.update_layout(
            title="CO₂ histórico y proyección (7 días) – ejemplo",
            xaxis_title="Tiempo",
            yaxis_title="CO₂ (ppm)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Entrena primero el modelo de aire para ver la proyección.")

# ===========================
# MAIN LAYOUT
# ===========================
def main():
    st.sidebar.title("Dashboard GAMC")
    opcion = st.sidebar.radio(
        "Vista",
        ["Aire", "Sonido", "Soterrado", "Proyecciones ML"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Datos en PostgreSQL • ML en Python • GAMC")

    if opcion == "Aire":
        vista_aire()
    elif opcion == "Sonido":
        vista_sonido()
    elif opcion == "Soterrado":
        vista_soterrado()
    else:
        vista_ml()


if __name__ == "__main__":
    main()
