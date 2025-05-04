from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database

MONGO_URL = "mongodb+srv://Admin:Admin1234@gamescorehub.osv9i1y.mongodb.net/" 

client = AsyncIOMotorClient(MONGO_URL)
db: Database = client["game_score_hub"]
