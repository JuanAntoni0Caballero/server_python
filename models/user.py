from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

class LikeReference(BaseModel):
    game: str

class User(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=4)
    role: str = Field(default="USER", regex="^(ADMIN|USER)$")
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

class UserInDB(User):
    id: Optional[str] = Field(alias="_id")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
