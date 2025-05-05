from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from core.config import MONGO_URL


client = AsyncIOMotorClient(MONGO_URL)
db: Database = client["game_score_hub"]
