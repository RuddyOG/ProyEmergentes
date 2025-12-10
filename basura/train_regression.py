# analytics/training/train_regression_pm25.py
import os
from pymongo import MongoClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np
import joblib

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "gamc_datos")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
aire_col = db["aire"]

# 1) Cargar datos de Mongo a DataFrame
docs = list(aire_col.find({}, {"_id": 0, "object": 1}))
df = pd.json_normalize(docs, sep="_")  # convierte object.pm25 en object_pm25, etc.

df = df.dropna()

# 2) Definir X (variables de entrada) e y (objetivo)
X = df[["object_co2", "object_temperature", "object_humidity"]]
y = df["object_pm25"]

# 3) Train / test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4) Entrenar regresión lineal
model = LinearRegression()
model.fit(X_train, y_train)

# 5) Predicciones y métricas
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

print("R²:", r2)
print("RMSE:", rmse)
print("MAE:", mae)

# 6) Guardar modelo para posibles predicciones vía API
os.makedirs("analytics/models", exist_ok=True)
joblib.dump(model, "analytics/models/air_quality_regression.pkl")
print("✅ Modelo guardado en analytics/models/air_quality_regression.pkl")
