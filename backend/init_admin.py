"""
Script para crear el usuario administrador inicial
Ejecutar: python init_admin.py
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext

# Cargar variables de entorno
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "gamc_datos")

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Crea el usuario administrador inicial"""
    
    print("=" * 60)
    print("CREACIÓN DE USUARIO ADMINISTRADOR INICIAL")
    print("=" * 60)
    
    # Conectar a MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        users_collection = db["users"]
        print(f"✓ Conectado a MongoDB: {MONGO_DB}")
    except Exception as e:
        print(f"✗ Error conectando a MongoDB: {e}")
        return
    
    # Verificar si ya existe un admin
    existing_admin = users_collection.find_one({"role": "Admin"})
    if existing_admin:
        print(f"\n⚠ Ya existe un usuario administrador: {existing_admin['username']}")
        overwrite = input("¿Deseas crear otro administrador? (s/n): ").lower()
        if overwrite != 's':
            print("Operación cancelada")
            return
    
    # Solicitar datos del admin
    print("\n" + "-" * 60)
    print("Ingresa los datos del administrador:")
    print("-" * 60)
    
    username = input("Nombre de usuario: ").strip()
    if not username or len(username) < 3:
        print("✗ El nombre de usuario debe tener al menos 3 caracteres")
        return
    
    # Verificar si el username ya existe
    if users_collection.find_one({"username": username}):
        print(f"✗ El usuario '{username}' ya existe")
        return
    
    email = input("Correo electrónico: ").strip()
    if not email or '@' not in email:
        print("✗ Correo electrónico inválido")
        return
    
    # Verificar si el email ya existe
    if users_collection.find_one({"email": email}):
        print(f"✗ El correo '{email}' ya está registrado")
        return
    
    full_name = input("Nombre completo: ").strip()
    if not full_name or len(full_name) < 3:
        print("✗ El nombre completo debe tener al menos 3 caracteres")
        return
    
    password = input("Contraseña (mínimo 6 caracteres): ").strip()
    if not password or len(password) < 6:
        print("✗ La contraseña debe tener al menos 6 caracteres")
        return
    
    password_confirm = input("Confirmar contraseña: ").strip()
    if password != password_confirm:
        print("✗ Las contraseñas no coinciden")
        return
    
    # Crear documento del usuario
    admin_document = {
        "username": username,
        "email": email,
        "password": pwd_context.hash(password),
        "full_name": full_name,
        "role": "Admin",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Insertar en la base de datos
    try:
        result = users_collection.insert_one(admin_document)
        print("\n" + "=" * 60)
        print("✓ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"ID: {result.inserted_id}")
        print(f"Usuario: {username}")
        print(f"Email: {email}")
        print(f"Nombre: {full_name}")
        print(f"Rol: Admin")
        print("=" * 60)
        print("\nYa puedes iniciar sesión con estas credenciales")
        print(f"Endpoint de login: POST /api/auth/login")
        
    except Exception as e:
        print(f"\n✗ Error creando usuario: {e}")


def create_sample_users():
    """Crea usuarios de ejemplo para testing"""
    
    print("\n" + "=" * 60)
    print("CREAR USUARIOS DE EJEMPLO")
    print("=" * 60)
    
    create = input("¿Deseas crear usuarios de ejemplo? (s/n): ").lower()
    if create != 's':
        return
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        users_collection = db["users"]
        
        sample_users = [
            {
                "username": "gamc_user",
                "email": "gamc@cochabamba.gob.bo",
                "password": pwd_context.hash("gamc123"),
                "full_name": "Usuario GAMC",
                "role": "GAMC",
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "username": "usuario_test",
                "email": "usuario@test.com",
                "password": pwd_context.hash("test123"),
                "full_name": "Usuario de Prueba",
                "role": "Usuario",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
        ]
        
        created = 0
        for user in sample_users:
            # Verificar si ya existe
            if not users_collection.find_one({"username": user["username"]}):
                users_collection.insert_one(user)
                print(f"✓ Usuario creado: {user['username']} ({user['role']})")
                created += 1
            else:
                print(f"⚠ Usuario ya existe: {user['username']}")
        
        if created > 0:
            print(f"\n✓ {created} usuarios de ejemplo creados")
            print("\nCredenciales:")
            print("  Usuario GAMC: gamc_user / gamc123")
            print("  Usuario Test: usuario_test / test123")
        
    except Exception as e:
        print(f"✗ Error creando usuarios de ejemplo: {e}")


def main():
    """Función principal"""
    create_admin_user()
    create_sample_users()
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Inicia el servidor: uvicorn main:app --reload")
    print("2. Visita la documentación: http://localhost:8000/docs")
    print("3. Inicia sesión con las credenciales creadas")
    print("=" * 60)


if __name__ == "__main__":
    main()