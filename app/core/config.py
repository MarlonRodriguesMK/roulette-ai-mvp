# ======================================================
# CONFIG.PY - Configurações da aplicação
# ======================================================

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Roulette AI"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend-domain.com"
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v):
        """Aceita lista JSON ou string separada por vírgula no .env (Railway)."""
        if v is None:
            return v
        if isinstance(v, str):
            # Permite: "https://a.com,https://b.com"
            parts = [p.strip() for p in v.split(",") if p.strip()]
            return parts
        return v
    
    # Sessões
    SESSION_TIMEOUT: int = 3600  # 1 hora em segundos
    MAX_HISTORY_PER_SESSION: int = 1000
    SESSION_CLEANUP_INTERVAL: int = 300  # 5 minutos
    
    # OCR
    OCR_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    OCR_ALLOWED_FORMATS: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    
    # AI Engine
    DEFAULT_HISTORY_LIMIT: int = 50
    MAX_HISTORY_LIMIT: int = 200
    MIN_HISTORY_LIMIT: int = 10
    
    # Redis (para produção futura)
    REDIS_URL: str = "redis://localhost:6379"
    USE_REDIS: bool = False
    
    # Database (para produção futura)
    DATABASE_URL: str = "sqlite:///./roulette_ai.db"
    USE_DATABASE: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton
settings = Settings()


# ======================================================
# VALIDAÇÕES DE AMBIENTE
# ======================================================

def validate_environment():
    """Valida se o ambiente está configurado corretamente"""
    
    if settings.DEBUG:
        print("⚠️  ATENÇÃO: Modo DEBUG ativado")
    
    if "*" in settings.ALLOWED_ORIGINS and not settings.DEBUG:
        raise ValueError(
            "CORS com '*' não é permitido em produção. "
            "Configure ALLOWED_ORIGINS corretamente."
        )
    
    print(f"✅ Configurações carregadas: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 CORS Origins: {settings.ALLOWED_ORIGINS}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")


# Validar ao importar
if __name__ != "__main__":
    validate_environment()