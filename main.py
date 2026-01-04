from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

@app.post("/send-history")
async def send_history(file_path: str):
    data = process_image(file_path)
    analysis = analyze_data(data)
    return JSONResponse(content=analysis)

@app.post("/manual-input")
async def manual_input(numbers: list[int]):
    analysis = analyze_data(numbers)
    return JSONResponse(content=analysis)

@app.get("/get-analysis")
async def get_analysis():
    return JSONResponse(content={"status": "IA analysis endpoint"})

@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected!")