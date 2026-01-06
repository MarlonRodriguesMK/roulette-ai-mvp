from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

# ======================================================
# 🔹 CORS (Lovable / Frontend)
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 🔹 ROTA RAIZ (Railway / Healthcheck)
# ======================================================
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Roulette AI",
        "version": "MVP"
    }

# ======================================================
# 🔹 INPUT MANUAL (Frontend)
# ======================================================
@app.post("/manual-input")
async def manual_input(numbers: list[int]):
    if not numbers:
        raise HTTPException(status_code=400, detail="Lista de números vazia")

    analysis = analyze_data(numbers)
    return JSONResponse(content={
        "source": "manual",
        "input": numbers,
        "analysis": analysis
    })

# ======================================================
# 🔹 OCR – UPLOAD DE IMAGEM
# ======================================================
@app.post("/send-history")
async def send_history(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo enviado não é uma imagem")

    image_bytes = await file.read()

    extracted_numbers = process_image(image_bytes)

    if not extracted_numbers:
        return JSONResponse(
            status_code=200,
            content={
                "source": "ocr",
                "numbers_extracted": [],
                "analysis": None,
                "warning": "Nenhum número detectado na imagem"
            }
        )

    analysis = analyze_data(extracted_numbers)

    return JSONResponse(content={
        "source": "ocr",
        "numbers_extracted": extracted_numbers,
        "analysis": analysis
    })

# ======================================================
# 🔹 STATUS / DEBUG
# ======================================================
@app.get("/get-analysis")
async def get_analysis():
    return {
        "status": "online",
        "message": "IA analysis endpoint ready"
    }

# ======================================================
# 🔹 WEBSOCKET (Futuro tempo real)
# ======================================================
@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected")
