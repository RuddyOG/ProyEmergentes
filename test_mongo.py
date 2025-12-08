from pymongo import MongoClient
import certifi  # 👈 FALTABA ESTO

MONGO_URI = "mongodb+srv://manfredruddyog24_db_user:ZK1V4DqjOS10wgXH@cluster0.tvp3snn.mongodb.net/gamc_datos?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "gamc_datos"

# Usar el bundle de certificados de certifi
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,  # 👀 Desactiva validación
)




db = client[DB_NAME]
coll = db["test_connection"]

doc = {"msg": "Conexión exitosa!"}

result = coll.insert_one(doc)
print("Insertado con ID:", result.inserted_id)
