from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import cloudinary

router = APIRouter()

@router.post("/image")
async def upload_image(imageData: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(imageData.file, folder="GameScoreHub")
        return {"cloudinary_url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")
