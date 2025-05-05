from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

DEFAULT_IMAGE = "https://res.cloudinary.com/dhtj3nd92/image/upload/v1688638386/GameScoreHub/images_leorfc.jpg"

class LikeByUser(BaseModel):
    user: str  

class Game(BaseModel):
    name: str = Field(..., max_length=100, description="Nombre del juego")
    category: str = Field(..., max_length=30, description="Categoría")
    description: str = Field(..., max_length=300, description="Descripción")
    image: Optional[str] = DEFAULT_IMAGE
    likesBy: List[LikeByUser] = []

class GameInDB(Game):
    id: Optional[str] = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
