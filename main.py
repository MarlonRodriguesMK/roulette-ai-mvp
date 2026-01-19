# ======================================================
# MAIN.PY - Backend FastAPI Roulette AI (Corrigido)
# ======================================================

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import logging

from app.models.schemas import (
    SpinInput, 
    MultipleSpinsInput, 
    StrategyInput,
    AnalysisResponse
)
from app.services.ai_service import AIService
# from app.services.ocr_service import OCRService
from app.core.config import settings
from app.core.session_manager import SessionManager

# ======================================================
# LOGGING
# ======================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ======================================================
# LIFESPAN - Inicialização e Cleanup
# ======================================================
session_manager = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Roulette AI Backend...")
    yield
    # Shutdown
    logger.info("🛑 Encerrando Roulette AI Backend...")
    session_manager.cleanup_old_sessions()

app = FastAPI(
    title="Roulette AI API",
    description="API de análise inteligente de roleta ao vivo",
    version="2.0.0",
    lifespan=lifespan
)

# ======================================================
# CORS - Configuração segura
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ======================================================
# DEPENDÊNCIAS
# ======================================================
ai_service = AIService()
ocr_service = OCRService()

def get_session_id(session_id: Optional[str] = None) -> str:
    """Obtém ou cria um session_id"""
    if not session_id:
        session_id = session_manager.create_session()
    return session_id

# ======================================================
# ROTAS - HEALTHCHECK
# ======================================================
@app.get("/")
async def root():
    """Healthcheck endpoint"""
    return {
        "status": "online",
        "service": "Roulette AI",
        "version": "2.0.0",
        "endpoints": {
            "add_spin": "/api/v1/add-spin",
            "manual_input": "/api/v1/manual-input",
            "ocr_upload": "/api/v1/ocr-upload",
            "analysis": "/api/v1/analysis",
            "strategies": "/api/v1/strategies"
        }
    }

@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_active_sessions_count(),
        "services": {
            "ai_engine": "operational",
            "ocr": "operational"
        }
    }

# ======================================================
# ROTAS - ANÁLISE DE DADOS
# ======================================================
@app.post("/api/v1/add-spin", response_model=AnalysisResponse)
async def add_spin(
    data: SpinInput,
    session_id: str = Depends(get_session_id)
):
    """
    Adiciona um único spin ao histórico e retorna análise
    """
    try:
        # Validar número
        if not (0 <= data.number <= 36):
            raise HTTPException(
                status_code=400,
                detail="Número deve estar entre 0 e 36"
            )
        
        # Adicionar ao histórico da sessão
        session_manager.add_spin(session_id, data.number)
        
        # Obter histórico
        history = session_manager.get_history(
            session_id, 
            limit=data.history_limit
        )
        
        # Analisar
        analysis = ai_service.analyze(
            history=history,
            history_limit=data.history_limit
        )
        
        return AnalysisResponse(
            status="ok",
            session_id=session_id,
            data=analysis
        )
        
    except Exception as e:
        logger.error(f"Erro em add_spin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/manual-input", response_model=AnalysisResponse)
async def manual_input(
    data: MultipleSpinsInput,
    session_id: str = Depends(get_session_id)
):
    """
    Adiciona múltiplos spins de uma vez
    """
    try:
        # Validar todos os números
        invalid = [n for n in data.numbers if not (0 <= n <= 36)]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Números inválidos: {invalid}"
            )
        
        # Adicionar todos ao histórico
        for number in data.numbers:
            session_manager.add_spin(session_id, number)
        
        # Obter histórico
        history = session_manager.get_history(
            session_id,
            limit=data.history_limit
        )
        
        # Analisar
        analysis = ai_service.analyze(
            history=history,
            history_limit=data.history_limit
        )
        
        return AnalysisResponse(
            status="ok",
            session_id=session_id,
            data=analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em manual_input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis")
async def get_analysis(
    session_id: str,
    history_limit: int = 50
):
    """
    Obtém análise do histórico atual sem adicionar spins
    """
    try:
        history = session_manager.get_history(session_id, limit=history_limit)
        
        if not history:
            return {
                "status": "no_data",
                "message": "Nenhum histórico encontrado para esta sessão"
            }
        
        analysis = ai_service.analyze(
            history=history,
            history_limit=history_limit
        )
        
        return AnalysisResponse(
            status="ok",
            session_id=session_id,
            data=analysis
        )
        
    except Exception as e:
        logger.error(f"Erro em get_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# ROTAS - OCR
# ======================================================
@app.post("/api/v1/ocr-upload", response_model=AnalysisResponse)
async def ocr_upload(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
    history_limit: int = 50
):
    """
    Upload de imagem para extração OCR de números
    """
    try:
        # Validar tipo de arquivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Arquivo deve ser uma imagem"
            )
        
        # Ler imagem
        image_bytes = await file.read()
        
        # Processar OCR
        numbers = ocr_service.process_image(image_bytes)
        
        if not numbers:
            return {
                "status": "no_numbers",
                "message": "Nenhum número foi detectado na imagem",
                "extracted": []
            }
        
        # Adicionar ao histórico
        for number in numbers:
            session_manager.add_spin(session_id, number)
        
        # Obter histórico
        history = session_manager.get_history(session_id, limit=history_limit)
        
        # Analisar
        analysis = ai_service.analyze(
            history=history,
            history_limit=history_limit
        )
        
        return AnalysisResponse(
            status="ok",
            session_id=session_id,
            data=analysis,
            extracted_numbers=numbers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em ocr_upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )

# ======================================================
# ROTAS - ESTRATÉGIAS
# ======================================================
@app.post("/api/v1/strategies")
async def analyze_strategies(
    data: StrategyInput,
    session_id: str = Depends(get_session_id)
):
    """
    Analisa estratégias customizadas do usuário
    """
    try:
        history = session_manager.get_history(
            session_id,
            limit=data.history_limit
        )
        
        if not history:
            raise HTTPException(
                status_code=400,
                detail="Nenhum histórico disponível para análise"
            )
        
        analysis = ai_service.analyze(
            history=history,
            history_limit=data.history_limit,
            user_strategies=data.strategies
        )
        
        return {
            "status": "ok",
            "session_id": session_id,
            "strategies": analysis.get("strategies", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro em analyze_strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# ROTAS - GERENCIAMENTO DE SESSÃO
# ======================================================
@app.delete("/api/v1/session/{session_id}")
async def clear_session(session_id: str):
    """Limpa o histórico de uma sessão"""
    try:
        session_manager.clear_session(session_id)
        return {"status": "ok", "message": "Sessão limpa com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao limpar sessão: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/session/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Obtém estatísticas da sessão"""
    try:
        history = session_manager.get_history(session_id)
        return {
            "status": "ok",
            "session_id": session_id,
            "total_spins": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Erro ao obter stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# EXCEPTION HANDLERS
# ======================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Erro interno do servidor"
        }
    )

# ======================================================
# STARTUP
# ======================================================
if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )