from typing import Union
from fastapi import FastAPI
from routes import games, auth
from starlette.middleware.cors import CORSMiddleware
from config import ORIGIN

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a GameScoreHub"}


app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(auth.router, prefix='/auth', tags=['Auth'])