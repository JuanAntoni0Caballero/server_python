from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from passlib.context import CryptContext

# Crear un contexto para bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LikeReference(BaseModel):
    game: str



# Modelo para login, solo con email y password
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    class Config:
        schema_extra = {
            "example": {
                "email": "mario@example.com",
                "password": "1234"
            }
        }


# Modelo para creación de usuario, sin el campo id
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=4)
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")
    likes: Optional[List[LikeReference]] = []

    class Config:
        schema_extra = {
            "example": {
                "username": "mario",
                "email": "mario@example.com",
                "password": "1234",
                "role": "USER",
                "likes": []
            }
        }


class User(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")
    likes: Optional[List[LikeReference]] = []
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

    class Config:
        json_schema_extra = {
            "example": {
                "username": "mario",
                "email": "mario@example.com",
                "password": "1234",
                "role": "USER",
                "likes": []
            }
        }


# Modelo para usuario en DB, con id
class UserInDB(User):
    id: Optional[str] = Field(alias="_id")

    # Método para encriptar la contraseña
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    # Método para verificar la contraseña
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

# Modelo para el token de autenticación (respuesta del login)
class Token(BaseModel):
    access_token: str
    token_type: str