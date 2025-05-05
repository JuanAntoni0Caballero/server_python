import os
import uvicorn
from fastapi import FastAPI
from routes import games, auth, uploadImage
from starlette.middleware.cors import CORSMiddleware
from core.config import ORIGIN, PORT

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
app.include_router(uploadImage.router, prefix="/upload", tags=["Upload"])

if __name__ == "__main__":
    port = int(PORT)
    uvicorn.run(app, host="0.0.0.0", port=port) 
