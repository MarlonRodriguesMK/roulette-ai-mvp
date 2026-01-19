# ======================================================
# SCHEMAS.PY - Pydantic Models para validação
# ======================================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any


class SpinInput(BaseModel):
    """Input para adicionar um único spin"""
    number: int = Field(..., ge=0, le=36, description="Número sorteado (0-36)")
    history_limit: int = Field(50, ge=10, le=200, description="Limite de histórico")

    @validator('number')
    def validate_number(cls, v):
        if not isinstance(v, int):
            raise ValueError('Número deve ser inteiro')
        if not (0 <= v <= 36):
            raise ValueError('Número deve estar entre 0 e 36')
        return v


class MultipleSpinsInput(BaseModel):
    """Input para adicionar múltiplos spins"""
    numbers: List[int] = Field(..., min_items=1, description="Lista de números")
    history_limit: int = Field(50, ge=10, le=200)

    @validator('numbers')
    def validate_numbers(cls, v):
        if not v:
            raise ValueError('Lista de números não pode estar vazia')
        
        invalid = [n for n in v if not isinstance(n, int) or not (0 <= n <= 36)]
        if invalid:
            raise ValueError(f'Números inválidos encontrados: {invalid}')
        
        return v


class Strategy(BaseModel):
    """Definição de uma estratégia"""
    name: str = Field(..., min_length=1, max_length=100)
    triggers: List[int] = Field(..., min_items=1)
    
    @validator('triggers')
    def validate_triggers(cls, v):
        invalid = [n for n in v if not (0 <= n <= 36)]
        if invalid:
            raise ValueError(f'Números gatilho inválidos: {invalid}')
        return v


class StrategyInput(BaseModel):
    """Input para análise de estratégias"""
    strategies: List[Strategy] = Field(..., min_items=1)
    history_limit: int = Field(50, ge=10, le=200)


class AnalysisResponse(BaseModel):
    """Resposta de análise"""
    status: str
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    extracted_numbers: Optional[List[int]] = None
    message: Optional[str] = None


class SessionStats(BaseModel):
    """Estatísticas da sessão"""
    session_id: str
    total_spins: int
    history: List[int]
    created_at: Optional[str] = None
    last_updated: Optional[str] = None