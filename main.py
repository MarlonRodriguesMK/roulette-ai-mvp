from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

# CORS - necessário para Lovable/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 🔹 ROTA RAIZ / HEALTHCHECK
# ======================================================
@app.get("/")
async def root():
    return {"status": "online", "service": "Roulette AI", "version": "MVP"}

# ======================================================
# 🔹 INPUT MANUAL – Número por vez (beta)
# ======================================================
history_store = []

@app.post("/add-spin")
async def add_spin(number: int, history_limit: int = 50):
    if number < 0 or number > 36:
        return JSONResponse(content={"status":"error","message":"Número inválido"})
    
    history_store.append(number)
    if len(history_store) > history_limit:
        history_store[:] = history_store[-history_limit:]
    
    analysis = analyze_data(history_store, history_limit=history_limit)
    return JSONResponse(content=analysis)

# ======================================================
# 🔹 INPUT MULTIPLOS (linha histórica, opcional)
# ======================================================
@app.post("/manual-input")
async def manual_input(numbers: list[int], history_limit: int = 50):
    for n in numbers:
        if n < 0 or n > 36:
            return JSONResponse(content={"status":"error","message":"Número inválido na lista"})
    history_store.extend(numbers)
    if len(history_store) > history_limit:
        history_store[:] = history_store[-history_limit:]
    analysis = analyze_data(history_store, history_limit=history_limit)
    return JSONResponse(content=analysis)

# ======================================================
# 🔹 INPUT OCR – Upload de print (futuro)
# ======================================================
@app.post("/send-history")
async def send_history(file: UploadFile = File(...), history_limit: int = 50):
    image_bytes = await file.read()
    numbers = process_image(image_bytes)
    history_store.extend(numbers)
    if len(history_store) > history_limit:
        history_store[:] = history_store[-history_limit:]
    analysis = analyze_data(history_store, history_limit=history_limit)
    return JSONResponse(content=analysis)

# ======================================================
# 🔹 ESTRATÉGIAS PREMIUM (CEREJA DO BOLO)
# ======================================================
@app.post("/premium-strategies")
async def premium_strategies(user_strategies: list[dict], history_limit: int = 50):
    analysis = analyze_data(history_store, history_limit=history_limit, user_strategies=user_strategies)
    return JSONResponse(content=analysis)

# ======================================================
# 🔹 STATUS / DEBUG
# ======================================================
@app.get("/get-analysis")
async def get_analysis():
    return {"status":"online","message":"IA analysis endpoint ready","history_length":len(history_store)}

# ======================================================
# 🔹 WEBSOCKET (para uso futuro)
# ======================================================
@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected")
