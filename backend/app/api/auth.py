# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from db.mongo import get_mongo_collection

# CONFIG
router = APIRouter(prefix="/api/auth", tags=["authentication"])
SECRET_KEY = "tu_clave_secreta_super_segura_cambiala_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MODELOS
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "Usuario"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class RoleChangeRequest(BaseModel):
    new_role: str


# UTILS
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(username=payload.get("sub"), role=payload.get("role"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


# DEPENDENCIAS
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    data = decode_token(token)

    users = get_mongo_collection("users")
    user = users.find_one({"username": data.username})

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user


# IMPORTANTE: ESTA ES LA CORRECCIÓN REAL
def require_role(roles: list):
    def wrapper(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(403, f"No autorizado, requiere: {roles}")
        return current_user
    return wrapper


require_admin = require_role(["Admin"])
require_gamc = require_role(["GAMC", "Admin"])
require_any = require_role(["Admin", "Usuario", "GAMC"])


# ENDPOINTS
@router.post("/register")
def register_user(data: UserRegister):
    users = get_mongo_collection("users")

    if users.find_one({"username": data.username}):
        raise HTTPException(400, "Nombre ya registrado")
    if users.find_one({"email": data.email}):
        raise HTTPException(400, "Email ya registrado")

    user_doc = {
        "username": data.username,
        "email": data.email,
        "password": get_password_hash(data.password),
        "full_name": data.full_name,
        "role": data.role,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }
    result = users.insert_one(user_doc)
    return {"user_id": str(result.inserted_id)}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    users = get_mongo_collection("users")
    user = users.find_one({"username": credentials.username})

    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(401, "Credenciales inválidas")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "user": {
        "username": user["username"], "email": user["email"], "role": user["role"]
    }}


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user=Depends(require_any)
):
    users = get_mongo_collection("users")
    user = users.find_one({"username": current_user["username"]})

    if not verify_password(payload.current_password, user["password"]):
        raise HTTPException(400, "Contraseña actual incorrecta")

    new_hash = get_password_hash(payload.new_password)
    users.update_one({"username": current_user["username"]},
                     {"$set": {"password": new_hash, "updated_at": datetime.utcnow()}})
    return {"message": "Contraseña actualizada"}


@router.put("/users/{username}/role")
async def change_user_role(
    username: str,
    payload: RoleChangeRequest,
    admin=Depends(require_admin)
):
    users = get_mongo_collection("users")
    if not users.find_one({"username": username}):
        raise HTTPException(404, "Usuario no existe")

    users.update_one({"username": username},
                     {"$set": {"role": payload.new_role, "updated_at": datetime.utcnow()}})
    return {"message": "Rol cambiado"}


@router.get("/users")
async def list_users(admin=Depends(require_admin)):
    users = get_mongo_collection("users")
    data = list(users.find({}, {"password": 0}))
    for u in data:
        u["_id"] = str(u["_id"])
    return {"count": len(data), "users": data}
