from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import analyze_data
from ocr_processor import process_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "API ONLINE"}

@app.post("/send-history")
async def send_history(file: UploadFile = File(...)):
    data = process_image(file)
    analysis = analyze_data(data)
    return analysis

@app.post("/manual-input")
async def manual_input(numbers: list[int]):
    return analyze_data(numbers)

@app.get("/get-analysis")
async def get_analysis():
    return {"status": "IA analysis endpoint"}

@app.websocket("/subscribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"ACK: {msg}")
    except:
        await websocket.close()
