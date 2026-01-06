# ===============================
# ROULETTE AI ENGINE – PREMIUM v2
# ===============================

from collections import Counter

# ======================================================
# MAPA FÍSICO REAL DA ROLETA EUROPEIA
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
# CRIA OBJETO FÍSICO DO GIRO
# ======================================================
def build_spin_object(number):
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
# ZONAS FÍSICAS CONTÍNUAS (DINÂMICAS)
# ======================================================
def calculate_physical_zones(history, zone_size=6):
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
            z["explanation"] = "Zona com maior concentração de resultados recentes na roleta física"
        elif z["hits"] == min_hits:
            z["status"] = "❄️ Fria"
            z["explanation"] = "Zona com baixa incidência recente, indicando possível ausência"
        else:
            z["status"] = "Neutra"
            z["explanation"] = "Zona com comportamento estatisticamente equilibrado"

    return zones

# ======================================================
# VIZINHOS FÍSICOS COM PRESSÃO
# ======================================================
def calculate_neighbors(history):
    pressure = Counter()

    for num in history:
        if num in ROULETTE_WHEEL:
            idx = ROULETTE_WHEEL.index(num)
            pressure[ROULETTE_WHEEL[(idx - 1) % len(ROULETTE_WHEEL)]] += 1
            pressure[ROULETTE_WHEEL[(idx + 1) % len(ROULETTE_WHEEL)]] += 1

    return [
        {"number": n, "pressure": p}
        for n, p in pressure.most_common()
    ]

# ======================================================
# CAVALOS (OPOSIÇÃO FÍSICA REAL)
# ======================================================
def calculate_horses():
    horses = []
    half = len(ROULETTE_WHEEL) // 2

    for i in range(half):
        horses.append({
            "pair": [
                ROULETTE_WHEEL[i],
                ROULETTE_WHEEL[i + half]
            ]
        })

    return horses

# ======================================================
# MOTOR PRINCIPAL (COMPATÍVEL COM O FRONTEND)
# ======================================================
def analyze_data(data):
    if not data:
        return {
            "status": "no_data",
            "message": "Nenhum número recebido"
        }

    # Limita histórico para evitar ruído excessivo
    history = data[-80:]

    spins = [build_spin_object(n) for n in history if n in ROULETTE_WHEEL]
    count = Counter(history)

    analysis = {
        "status": "ok",

        # Contagem simples (mantido)
        "numbers": dict(count),

        # Histórico bruto (mantido)
        "history": history,

        # Zonas físicas reais
        "physical_zones": calculate_physical_zones(history),

        # Vizinhos com pressão lateral
        "neighbors": calculate_neighbors(history),

        # Cavalos estruturais
        "horses": calculate_horses(),

        # Estratégias explicativas
        "strategies": [
            "Zonas físicas analisam regiões contínuas da roleta real",
            "Zonas quentes indicam recorrência recente na mesma região física",
            "Zonas frias indicam ausência prolongada na roda",
            "Vizinhos mostram pressão lateral dos resultados",
            "Cavalos representam oposição estrutural da roleta"
        ],

        # Alertas informativos (pronto para expansão)
        "alerts": []
    }

    return analysis
