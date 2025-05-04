from typing import Union
from fastapi import FastAPI
from routes import games


app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Bienvenido a GameScoreHub"}


app.include_router(games.router, prefix="/games", tags=["games"])