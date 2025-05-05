from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from db.mongo import db
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from models.user import User, UserLogin, UserCreate, UserInDB
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


router = APIRouter()

# Contexto de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


games_collection = db["games"]
users_collection = db["users"]


# Clase para respuesta de login
class Token(BaseModel):
    authToken: str
    token_type: str


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    # Verificar si el usuario existe
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    print('el user ==>', db_user)

    likes = [{"game": str(like["game"]), "_id": str(like["_id"])} for like in db_user.get("likes", [])]

    # Crear el JWT token
    access_token_expires = timedelta(hours=6)  # Expira en 6 horas
    access_token = create_access_token(data={
        "sub": user.email, 
        "username": db_user["username"], 
        "role" : db_user['role'],
        "likes": likes
        }, expires_delta=access_token_expires)
    
    return {"authToken": access_token, "token_type": "bearer"}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)  # Default 1 hour expiration
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# Ruta de creación de usuarios
@router.post("/signup", response_model = User)
async def signup(user: UserCreate):
    # Verificar si el correo ya está registrado
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe.")

    # Encriptar contraseña
    hashed_password = pwd_context.hash(user.password)

    # Preparar datos para insertar
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    user_data["createdAt"] = datetime.now(timezone.utc)
    user_data["updatedAt"] = datetime.now(timezone.utc)

    # Insertar en MongoDB
    result = await users_collection.insert_one(user_data)
    user_data["_id"] = result.inserted_id

    # Formatear respuesta
    return User(**user_data)


# Ruta de verificación de token (opcional)
@router.get("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=403, detail="No se proporcionó token")

    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
