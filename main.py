from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
from ai_engine import analyze_data
from ocr_processor import process_image
import tempfile

app = FastAPI()

@app.post("/send-history")
async def send_history(file: UploadFile = File(...)):
    # salva imagem temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        contents = await file.read()
        tmp.write(contents)
        temp_path = tmp.name

    data = process_image(temp_path)
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
