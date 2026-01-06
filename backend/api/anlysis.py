from fastapi import APIRouter
from core.heatmap import calcular_zonas_fisicas

router = APIRouter()

@router.post("/analysis")
def analisar(historico: list[int]):
    zonas = calcular_zonas_fisicas(historico)

    return {
        "status": "ok",
        "zonas": zonas,
        "explicacao": {
            "zonas_quentes": "Regiões físicas mais atingidas na roda",
            "zonas_frias": "Regiões sem ocorrência recente"
        }
    }
