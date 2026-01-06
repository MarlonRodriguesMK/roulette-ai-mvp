from fastapi import APIRouter, UploadFile, File
import shutil
from ocr.ocr_service import extrair_numeros

router = APIRouter()

@router.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    path = f"/tmp/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    numeros = extrair_numeros(path)

    return {
        "status": "ok",
        "numeros_extraidos": numeros
    }
