from fastapi import APIRouter, HTTPException
from models.game import Game
from db.mongo import db
from bson import ObjectId
from datetime import datetime, timezone
import re
from utils.utils import serialize_mongo_doc
from bson.errors import InvalidId


router = APIRouter()
games_collection = db["games"]
users_collection = db["users"]


def str_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/getAllGames")
async def get_all_games():
    pipeline = [
        {"$addFields": {"likesCount": {"$size": "$likesBy"}}},
        {"$sort": {"likesCount": -1}}
    ]
    cursor = db.games.aggregate(pipeline)
    games = []
    async for game in cursor:
        games.append(serialize_mongo_doc(game)) 
    return games


@router.get("/searchGames")
async def search_games(searchInput: str):
    regex = re.compile(searchInput, re.IGNORECASE)
    query = {
        "$or": [
            {"name": {"$regex": regex}},
            {"category": {"$regex": regex}},
            {"description": {"$regex": regex}},
        ]
    }
    games = await games_collection.find(query).to_list(100)
    games.sort(key=lambda g: len(g.get("likesBy", [])), reverse=True)
    return [serialize_mongo_doc(game) for game in games]



@router.get("/getOneGame/{game_id}")
async def get_one_game(game_id: str):
    try:
        obj_id = ObjectId(game_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")

    game = await games_collection.find_one({"_id": obj_id})
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    return [serialize_mongo_doc(game)]



@router.post("/createGame")
async def create_game(game: Game):
    existing = await games_collection.find_one({"name": game.name})
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un juego con ese nombre.")

    game_dict = game.model_dump()
    now = datetime.now(timezone.utc)
    game_dict["created_at"] = now
    game_dict["updated_at"] = now

    result = await games_collection.insert_one(game_dict)
    new_game = await games_collection.find_one({"_id": result.inserted_id})
    return [serialize_mongo_doc(new_game)]


@router.put("/updateGame/{game_id}")
async def update_game(game_id: str, game: Game):
    try:
        obj_id = ObjectId(game_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    update_data = game.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await games_collection.update_one(
        {"_id": ObjectId(obj_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    updated_game = await games_collection.find_one({"_id": ObjectId(obj_id)})
    return [serialize_mongo_doc(updated_game)]


@router.delete("/deleteGame/{game_id}")
async def delete_game(game_id: str):
    try:
        obj_id = ObjectId(game_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    result = await games_collection.delete_one({"_id": ObjectId(obj_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return {"message": "Juego eliminado"}


@router.post("/likeGame/{game_id}/{user_id}")
async def like_game(game_id: str, user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    game = await games_collection.find_one({"_id": ObjectId(game_id)})

    if not user or not game:
        raise HTTPException(status_code=400, detail="El usuario o el juego no existen")


    already_liked = any(like["user"] == user_id for like in game.get("likesBy", []))

    if already_liked:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"likes": {"game": game_id}}}
        )
        await games_collection.update_one(
            {"_id": ObjectId(game_id)},
            {"$pull": {"likesBy": {"user": user_id}}}
        )
        return {"message": "Like eliminado"}

    if len(user.get("likes", [])) >= 5:
        raise HTTPException(status_code=400, detail="Ya has alcanzado el máximo de likes")

    if any(like["game"] == game_id for like in user.get("likes", [])):
        raise HTTPException(status_code=400, detail="Ya has dado like a este juego")

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"likes": {"game": game_id}}}
    )
    await games_collection.update_one(
        {"_id": ObjectId(game_id)},
        {"$push": {"likesBy": {"user": user_id}}}
    )

    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return {"message": "Like agregado", "user": [serialize_mongo_doc(updated_user)]}
