from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "API online"}

@app.post("/manual-input")
async def manual_input(numbers: list[int]):
    analysis = analyze_data(numbers)
    return analysis

@app.post("/send-history")
async def send_history(file: UploadFile = File(...)):
    data = process_image(file)
    analysis = analyze_data(data)
    return analysis

@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected!")
