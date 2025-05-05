from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import cloudinary  

router = APIRouter()


@router.post("/image")
async def upload_image(imageData: UploadFile = File(...)):
    try:
        file_content = await imageData.read()
        result = cloudinary.uploader.upload(file_content, folder="GameScoreHub")
        
        return {"cloudinary_url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")
