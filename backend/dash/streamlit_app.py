# backend/dash/streamlit_app.py
import os
import time
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st

# === Carga .env ===
load_dotenv()  # usa el .env de la raíz
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "gamc_datos")

# === Conexión Mongo ===
_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]

COLLS = {
    "Aire": "aire",
    "Sonido": "sonido",
    "Soterrado": "soterrado",
}

st.set_page_config(page_title="GAMC - Dashboard", layout="wide")
st.title("🌎 GAMC – Dashboard de Sensores (Atlas)")

# Panel de control
with st.sidebar:
    st.header("⚙️ Controles")
    coll_label = st.selectbox("Colección", list(COLLS.keys()), index=0)
    coll = COLLS[coll_label]
    limit = st.slider("Filas a mostrar", 10, 500, 50, step=10)
    refresh = st.checkbox("Autorefrescar", value=True)
    interval = st.number_input("Intervalo (seg)", min_value=2, value=5, step=1)

# Métricas
c1, c2, c3, c4 = st.columns(4)
try:
    total_aire = _db["aire"].count_documents({})
    total_sonido = _db["sonido"].count_documents({})
    total_soterrado = _db["soterrado"].count_documents({})

    c1.metric("Docs Aire", total_aire)
    c2.metric("Docs Sonido", total_sonido)
    c3.metric("Docs Soterrado", total_soterrado)
    c4.metric("Última actualización", datetime.utcnow().strftime("%H:%M:%S UTC"))
except Exception as e:
    st.error(f"Error contando documentos: {e}")

st.subheader(f"📄 Últimos {limit} documentos: {coll}")
try:
    # Trae los últimos por _id desc (orden cronológico inverso)
    cursor = _db[coll].find({}, {"_id": 0}).sort([("_id", -1)]).limit(limit)
    df = pd.DataFrame(list(cursor))
    if not df.empty:
        # Muestra time si existe, y algunas “object.*” si están
        cols_prefer = [c for c in df.columns if c in (
            "time", "sensor_type", "source_file", "row_number",
            "object.co2", "object.temperature", "object.humidity",
            "object.LAeq", "object.distance", "object.status", "object.battery"
        )]
        # Ordena: preferidos al frente
        ordered = cols_prefer + [c for c in df.columns if c not in cols_prefer]
        df = df[ordered]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sin datos todavía en esta colección.")
except Exception as e:
    st.error(f"Error consultando Mongo: {e}")

# Autorefresco suave
if refresh:
    st.caption("Autorefresco activado…")
    time.sleep(int(interval))
    st.rerun()
