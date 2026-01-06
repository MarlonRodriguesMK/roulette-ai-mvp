# ===============================
# ROULETTE AI ENGINE – PREMIUM
# ===============================

from collections import Counter

# Mapa físico da roleta europeia
ROULETTE_WHEEL = [
    0, 32, 15, 19, 4, 21, 2, 25, 17,
    34, 6, 27, 13, 36, 11, 30,
    8, 23, 10, 5, 24, 16, 33,
    1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

# ===============================
# ZONAS FÍSICAS DA ROLETA
# ===============================
def calculate_physical_zones(history, zone_size=5):
    zones = []

    for i in range(0, len(ROULETTE_WHEEL), zone_size):
        sector = ROULETTE_WHEEL[i:i + zone_size]
        hits = sum(1 for n in history if n in sector)

        zones.append({
            "numbers": sector,
            "hits": hits
        })

    if not zones:
        return []

    max_hits = max(z["hits"] for z in zones)
    min_hits = min(z["hits"] for z in zones)

    for z in zones:
        if z["hits"] == max_hits and max_hits > 0:
            z["status"] = "🔥 Quente"
        elif z["hits"] == min_hits:
            z["status"] = "❄️ Fria"
        else:
            z["status"] = "Neutra"

    return zones

# ===============================
# VIZINHOS FÍSICOS
# ===============================
def calculate_neighbors(history):
    neighbors = {}

    for num in set(history):
        if num in ROULETTE_WHEEL:
            idx = ROULETTE_WHEEL.index(num)
            left = ROULETTE_WHEEL[(idx - 1) % len(ROULETTE_WHEEL)]
            right = ROULETTE_WHEEL[(idx + 1) % len(ROULETTE_WHEEL)]

            neighbors[num] = {
                "neighbors": [left, right]
            }

    return neighbors

# ===============================
# CAVALOS (OPOSIÇÕES SIMPLES)
# ===============================
def calculate_horses():
    horses = []

    for i in range(len(ROULETTE_WHEEL) // 2):
        horses.append({
            "pair": [
                ROULETTE_WHEEL[i],
                ROULETTE_WHEEL[i + len(ROULETTE_WHEEL)//2]
            ]
        })

    return horses

# ===============================
# MOTOR PRINCIPAL DA IA
# ===============================
def analyze_data(data):
    if not data:
        return {
            "status": "no_data",
            "message": "Nenhum número recebido"
        }

    count = Counter(data)

    analysis = {
        "status": "ok",

        # Contagem simples
        "numbers": dict(count),

        # Histórico ordenado
        "history": data[-50:],  # últimos 50

        # Zonas físicas reais
        "physical_zones": calculate_physical_zones(data),

        # Vizinhos físicos
        "neighbors": calculate_neighbors(data),

        # Cavalos
        "horses": calculate_horses(),

        # Estratégias explicativas (sem aposta)
        "strategies": [
            "Zonas quentes indicam maior recorrência recente",
            "Zonas frias indicam ausência prolongada",
            "Vizinhos mostram continuidade física da roleta",
            "Cavalos indicam oposição estrutural da roda"
        ],

        # Alertas informativos
        "alerts": []
    }

    return analysis
