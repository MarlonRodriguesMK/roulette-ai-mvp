# ===============================
# ROULETTE AI ENGINE – PREMIUM COMPLETO
# ===============================

from collections import Counter, defaultdict
from typing import List, Dict

# ======================================================
# MAPA FÍSICO DA ROLETA EUROPEIA
# ======================================================
ROULETTE_WHEEL = [
    0, 32, 15, 19, 4, 21, 2, 25, 17,
    34, 6, 27, 13, 36, 11, 30,
    8, 23, 10, 5, 24, 16, 33,
    1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,
    19,21,23,25,27,30,32,34,36
}

# ======================================================
# FUNÇÃO: CRIA OBJETO DE CADA GIRO
# Cada giro recebe propriedades físicas + vizinhos
# ======================================================
def build_spin_object(number: int) -> Dict:
    idx = ROULETTE_WHEEL.index(number)
    return {
        "number": number,
        "wheel_index": idx,
        "color": "red" if number in RED_NUMBERS else "black" if number != 0 else "green",
        "parity": "even" if number != 0 and number % 2 == 0 else "odd" if number != 0 else None,
        "neighbors": [
            ROULETTE_WHEEL[(idx - 1) % len(ROULETTE_WHEEL)],
            ROULETTE_WHEEL[(idx + 1) % len(ROULETTE_WHEEL)]
        ]
    }

# ======================================================
# FUNÇÃO: CALCULA ZONAS FÍSICAS DINÂMICAS
# Recebe histórico, calcula hits por zona e status quente/frio/neutra
# ======================================================
def calculate_physical_zones(history: List[int], zone_size: int = 6) -> List[Dict]:
    zones = []
    total_spins = len(history)

    for i in range(0, len(ROULETTE_WHEEL), zone_size):
        sector = ROULETTE_WHEEL[i:i + zone_size]
        hits = sum(1 for n in history if n in sector)
        percentage = round((hits / total_spins) * 100, 2) if total_spins else 0

        zones.append({
            "numbers": sector,
            "hits": hits,
            "percentage": percentage
        })

    if not zones:
        return []

    max_hits = max(z["hits"] for z in zones)
    min_hits = min(z["hits"] for z in zones)

    for z in zones:
        if z["hits"] == max_hits and max_hits > 0:
            z["status"] = "🔥 Quente"
            z["explanation"] = "Zona com maior recorrência recente na roleta física"
        elif z["hits"] == min_hits:
            z["status"] = "❄️ Fria"
            z["explanation"] = "Zona com baixa incidência recente, indicando possível ausência"
        else:
            z["status"] = "Neutra"
            z["explanation"] = "Zona com comportamento estatisticamente equilibrado"

    return zones

# ======================================================
# FUNÇÃO: CALCULA VIZINHOS FÍSICOS COM PRESSÃO
# Retorna números vizinhos que tiveram mais incidência
# ======================================================
def calculate_neighbors(history: List[int]) -> List[Dict]:
    pressure = Counter()
    for num in history:
        if num in ROULETTE_WHEEL:
            idx = ROULETTE_WHEEL.index(num)
            # Dois vizinhos para cada lado
            pressure[ROULETTE_WHEEL[(idx - 1) % len(ROULETTE_WHEEL)]] += 1
            pressure[ROULETTE_WHEEL[(idx + 1) % len(ROULETTE_WHEEL)]] += 1

    return [{"number": n, "pressure": p} for n, p in pressure.most_common()]

# ======================================================
# FUNÇÃO: CALCULA CAVALOS (OPOSIÇÃO FÍSICA)
# ======================================================
def calculate_horses() -> List[Dict]:
    horses = []
    half = len(ROULETTE_WHEEL) // 2
    for i in range(half):
        horses.append({
            "pair": [ROULETTE_WHEEL[i], ROULETTE_WHEEL[i + half]]
        })
    return horses

# ======================================================
# FUNÇÃO: CALCULA AUSÊNCIAS DE NÚMEROS, ZONAS, CAVALEIROS, TERMINAIS
# ======================================================
def calculate_absences(history: List[int], max_spins: int = 50) -> Dict:
    last_spins = history[-max_spins:]
    absences = {}

    # Números ausentes
    absent_numbers = [n for n in ROULETTE_WHEEL if n not in last_spins]
    absences["numbers"] = absent_numbers

    # Zonas ausentes
    zones = calculate_physical_zones(last_spins)
    absences["zones"] = [z for z in zones if z["hits"] == 0]

    # Cavalos ausentes
    horses = calculate_horses()
    absences["horses"] = [h for h in horses if not any(n in last_spins for n in h["pair"])]

    return absences

# ======================================================
# FUNÇÃO: ESTRATÉGIAS PREMIUM (CEREJA DO BOLO)
# - Gatilhos e vizinhos
# - Acertos / perdas
# - Alternância e quebras de padrão
# ======================================================
def analyze_premium_strategies(history: List[int], user_strategies: List[Dict]) -> List[Dict]:
    """
    user_strategies = [
        {"name": "Exemplo 1", "triggers": [3,9,15]},
        {"name": "Exemplo 2", "triggers": [25,5]}
    ]
    """
    results = []
    for strat in user_strategies:
        name = strat.get("name", "Strategy")
        triggers = strat.get("triggers", [])
        stats = {
            "hits": 0,
            "misses": 0,
            "alternations": 0,
            "pattern_breaks": 0,
            "details": []
        }

        for idx, number in enumerate(history):
            # Verifica se o número atual é um gatilho ou vizinho
            is_trigger = number in triggers
            trigger_neighbors = []
            for t in triggers:
                idx_t = ROULETTE_WHEEL.index(t)
                trigger_neighbors.extend([
                    ROULETTE_WHEEL[(idx_t - 1) % len(ROULETTE_WHEEL)],
                    ROULETTE_WHEEL[(idx_t + 1) % len(ROULETTE_WHEEL)]
                ])
            is_neighbor = number in trigger_neighbors

            if is_trigger or is_neighbor:
                stats["hits"] += 1
                stats["details"].append({"number": number, "status": "hit"})
            else:
                stats["misses"] += 1
                stats["details"].append({"number": number, "status": "miss"})

        results.append({
            "name": name,
            "stats": stats
        })
    return results

# ======================================================
# MOTOR PRINCIPAL
# ======================================================
def analyze_data(data: List[int], history_limit: int = 50, user_strategies: List[Dict] = None) -> Dict:
    """
    data: histórico de números
    history_limit: quantas rodadas serão analisadas (20-50 recomendado)
    user_strategies: estratégias configuradas pelo usuário
    """
    if not data:
        return {"status": "no_data", "message": "Nenhum número recebido"}

    # Histórico limitado
    history = data[-history_limit:]
    spins = [build_spin_object(n) for n in history]
    count = Counter(history)

    analysis = {
        "status": "ok",
        "numbers": dict(count),
        "history": history,
        "physical_zones": calculate_physical_zones(history),
        "neighbors": calculate_neighbors(history),
        "horses": calculate_horses(),
        "absences": calculate_absences(history),
        "strategies": [],
        "alerts": []
    }

    # Estrategias Premium (Cereja do bolo)
    if user_strategies:
        analysis["strategies"] = analyze_premium_strategies(history, user_strategies)

    return analysis
