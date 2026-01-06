from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

# ✅ CORS (obrigatório para Lovable / Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 🔹 ROTA RAIZ (Railway + Healthcheck + Lovable)
# ======================================================
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Roulette AI",
        "version": "MVP",
    }

# ======================================================
# 🔹 INPUT MANUAL (números digitados no frontend)
# ======================================================
@app.post("/manual-input")
async def manual_input(numbers: list[int]):
    analysis = analyze_data(numbers)
    return JSONResponse(content=analysis)

# ======================================================
# 🔹 OCR – UPLOAD DE IMAGEM (print do histórico)
# ======================================================
@app.post("/send-history")
async def send_history(file: UploadFile = File(...)):
    image_bytes = await file.read()
    data = process_image(image_bytes)
    analysis = analyze_data(data)
    return JSONResponse(content=analysis)

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
# 🔹 WEBSOCKET (tempo real / futuro uso)
# ======================================================
@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected")
