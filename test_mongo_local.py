python - <<EOF
from dotenv import load_dotenv
import os

path = r"C:\Users\manfr\Documents\Ruddy\6to Semestre\Tecnologias Emergentes\ProyEmergentes\backend\app\core\.env"
load_dotenv(path)

print("MONGO_URI:", os.getenv("MONGO_URI"))
print("MONGO_DB:", os.getenv("MONGO_DB"))
EOF