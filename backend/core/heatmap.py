from collections import Counter
from .zones import gerar_zona

def calcular_zonas_fisicas(historico: list[int]):
    contador = Counter()

    for numero in historico:
        zona = gerar_zona(numero)
        for n in zona:
            contador[n] += 1

    quentes = [n for n, c in contador.most_common(6)]
    frios = [n for n in range(37) if contador[n] == 0]

    return {
        "zonas_quentes": quentes,
        "zonas_frias": frios[:6],
        "distribuicao": dict(contador)
    }
