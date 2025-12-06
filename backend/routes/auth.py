# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from db.mongo import get_mongo_collection


# CONFIGURACIÓN


router = APIRouter(prefix="/api/auth", tags=["authentication"])

# IMPORTANTE: En producción, usa variables de entorno
SECRET_KEY = "tu_clave_secreta_super_segura_cambiala_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad
security = HTTPBearer()



# MODELOS


class UserRegister(BaseModel):
    """Modelo para registro de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=3)
    role: str = Field("Usuario", pattern="^(Admin|Usuario|GAMC)$")


class UserLogin(BaseModel):
    """Modelo para login"""
    username: str
    password: str


class Token(BaseModel):
    """Modelo de respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    """Datos extraídos del token"""
    username: Optional[str] = None
    role: Optional[str] = None



# FUNCIONES DE UTILIDAD


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera hash de contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decodifica y valida un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return TokenData(username=username, role=role)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token"
        )



# DEPENDENCIAS DE AUTENTICACIÓN


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtiene el usuario actual del token"""
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Buscar usuario en la base de datos
    users_collection = get_mongo_collection("users")
    user = users_collection.find_one({"username": token_data.username})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    # Convertir ObjectId a string
    user["_id"] = str(user["_id"])
    # Remover contraseña del objeto
    user.pop("password", None)
    
    return user


async def require_role(required_roles: list):
    """Factory para crear dependencias de roles específicos"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker


# Dependencias específicas por rol
require_admin = require_role(["Admin"])
require_gamc = require_role(["GAMC", "Admin"])
require_any_user = require_role(["Admin", "Usuario", "GAMC"])



# ENDPOINTS DE AUTENTICACIÓN


@router.post("/register", summary="Registrar nuevo usuario")
def register_user(user_data: UserRegister):
    """
    Registra un nuevo usuario en el sistema.
    
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico
    - **password**: Contraseña (mínimo 6 caracteres)
    - **full_name**: Nombre completo
    - **role**: Rol del usuario (Admin, Usuario, GAMC)
    
    Returns:
        dict: Confirmación de registro
    """
    users_collection = get_mongo_collection("users")
    
    # Verificar si el usuario ya existe
    if users_collection.find_one({"username": user_data.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    # Crear documento de usuario
    user_document = {
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    try:
        result = users_collection.insert_one(user_document)
        
        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "user_id": str(result.inserted_id),
            "username": user_data.username,
            "role": user_data.role
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )


@router.post("/login", response_model=Token, summary="Iniciar sesión")
def login(credentials: UserLogin):
    """
    Inicia sesión y devuelve un token JWT.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Returns:
        Token: Token de acceso JWT y datos del usuario
    """
    users_collection = get_mongo_collection("users")
    
    # Buscar usuario
    user = users_collection.find_one({"username": credentials.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    # Verificar contraseña
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    # Verificar si el usuario está activo
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # Preparar datos del usuario (sin contraseña)
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.get("/me", summary="Obtener perfil del usuario actual")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.
    
    Requiere: Token JWT válido
    
    Returns:
        dict: Datos del usuario actual
    """
    return {
        "success": True,
        "user": current_user
    }


@router.put("/me", summary="Actualizar perfil")
async def update_profile(
    full_name: Optional[str] = None,
    email: Optional[EmailStr] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza el perfil del usuario autenticado.
    
    - **full_name**: Nuevo nombre completo (opcional)
    - **email**: Nuevo correo electrónico (opcional)
    
    Returns:
        dict: Confirmación de actualización
    """
    users_collection = get_mongo_collection("users")
    
    update_data = {}
    if full_name:
        update_data["full_name"] = full_name
    if email:
        # Verificar que el email no esté en uso
        existing = users_collection.find_one({
            "email": email,
            "username": {"$ne": current_user["username"]}
        })
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )
        update_data["email"] = email
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos para actualizar"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = users_collection.update_one(
            {"username": current_user["username"]},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Perfil actualizado exitosamente",
            "updated_fields": list(update_data.keys())
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando perfil: {str(e)}"
        )


@router.post("/change-password", summary="Cambiar contraseña")
async def change_password(
    current_password: str,
    new_password: str = Field(..., min_length=6),
    current_user: dict = Depends(get_current_user)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 6 caracteres)
    
    Returns:
        dict: Confirmación de cambio
    """
    users_collection = get_mongo_collection("users")
    
    # Obtener usuario completo con contraseña
    user = users_collection.find_one({"username": current_user["username"]})
    
    # Verificar contraseña actual
    if not verify_password(current_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Actualizar contraseña
    new_hash = get_password_hash(new_password)
    
    try:
        users_collection.update_one(
            {"username": current_user["username"]},
            {"$set": {
                "password": new_hash,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Contraseña cambiada exitosamente"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cambiando contraseña: {str(e)}"
        )



# ENDPOINTS ADMINISTRATIVOS


@router.get("/users", summary="Listar todos los usuarios (Admin)")
async def list_users(
    role: Optional[str] = None,
    admin_user: dict = Depends(require_admin)
):
    """
    Lista todos los usuarios del sistema (solo Admin).
    
    - **role**: Filtrar por rol (opcional)
    
    Returns:
        dict: Lista de usuarios
    """
    users_collection = get_mongo_collection("users")
    
    query = {}
    if role and role in ["Admin", "Usuario", "GAMC"]:
        query["role"] = role
    
    users = list(users_collection.find(query, {"password": 0}))
    
    # Convertir ObjectId a string
    for user in users:
        user["_id"] = str(user["_id"])
    
    return {
        "success": True,
        "count": len(users),
        "users": users
    }


@router.put("/users/{username}/role", summary="Cambiar rol de usuario (Admin)")
async def change_user_role(
    username: str,
    new_role: str = Field(..., pattern="^(Admin|Usuario|GAMC)$"),
    admin_user: dict = Depends(require_admin)
):
    """
    Cambia el rol de un usuario (solo Admin).
    
    - **username**: Nombre del usuario
    - **new_role**: Nuevo rol (Admin, Usuario, GAMC)
    
    Returns:
        dict: Confirmación de cambio
    """
    users_collection = get_mongo_collection("users")
    
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    try:
        users_collection.update_one(
            {"username": username},
            {"$set": {
                "role": new_role,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": f"Rol de {username} cambiado a {new_role}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cambiando rol: {str(e)}"
        )


@router.delete("/users/{username}", summary="Desactivar usuario (Admin)")
async def deactivate_user(
    username: str,
    admin_user: dict = Depends(require_admin)
):
    """
    Desactiva un usuario (solo Admin).
    
    - **username**: Nombre del usuario a desactivar
    
    Returns:
        dict: Confirmación de desactivación
    """
    if username == admin_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    users_collection = get_mongo_collection("users")
    
    result = users_collection.update_one(
        {"username": username},
        {"$set": {
            "is_active": False,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "success": True,
        "message": f"Usuario {username} desactivado exitosamente"
    }