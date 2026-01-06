from .roulette_map import ROULETA_FISICA

def gerar_zona(numero: int, alcance: int = 2):
    tamanho = len(ROULETA_FISICA)
    idx = ROULETA_FISICA.index(numero)

    return [
        ROULETA_FISICA[(idx + i) % tamanho]
        for i in range(-alcance, alcance + 1)
    ]
