# ===============================
# ROULETTE AI ENGINE – PREMIUM v3
# ===============================

from collections import Counter

# ======================================================
# CONFIGURAÇÕES DE CONTEXTO (AJUSTÁVEIS)
# ======================================================
MIN_ACTIVE_WINDOW = 20
MAX_ACTIVE_WINDOW = 50

DEFAULT_ACTIVE_WINDOW = 30
DEFAULT_HISTORY_LIMIT = 300

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
# MEMÓRIA GLOBAL DO SISTEMA
# ======================================================
GLOBAL_HISTORY = []

# ======================================================
# CRIA OBJETO FÍSICO DO GIRO
# ======================================================
def build_spin_object(number):
    idx = ROULETTE_WHEEL.index(number)

    return {
        "number": number,
        "wheel_index": idx,
        "zone_id": idx // 6,
        "color": "red" if number in RED_NUMBERS else "black" if number != 0 else "green",
        "parity": "even" if number != 0 and number % 2 == 0 else "odd" if number != 0 else None,
        "neighbors": [
            ROULETTE_WHEEL[(idx - 1) % len(ROULETTE_WHEEL)],
            ROULETTE_WHEEL[(idx + 1) % len(ROULETTE_WHEEL)]
        ]
    }

# ======================================================
# CONTROLE DE HISTÓRICO
# ======================================================
def add_to_history(spins, history_limit=DEFAULT_HISTORY_LIMIT):
    for s in spins:
        GLOBAL_HISTORY.append(s)
        if len(GLOBAL_HISTORY) > history_limit:
            GLOBAL_HISTORY.pop(0)

def get_active_window(active_window):
    active_window = max(
        MIN_ACTIVE_WINDOW,
        min(active_window, MAX_ACTIVE_WINDOW)
    )
    return GLOBAL_HISTORY[-active_window:]

# ======================================================
# ZONAS FÍSICAS CONTEXTUAIS (JANELA ATIVA)
# ======================================================
def calculate_physical_zones_context(active_spins):
    zone_hits = Counter()
    total = len(active_spins)

    for s in active_spins:
        zone_hits[s["zone_id"]] += 1

    zones = []

    for zone_id, hits in zone_hits.items():
        percentage = round((hits / total) * 100, 2) if total else 0

        if hits >= total * 0.35:
            status = "🔥 Quente"
            explanation = "Alta recorrência recente nesta região física da roleta"
        elif hits <= total * 0.10:
            status = "❄️ Fria"
            explanation = "Baixa incidência recente nesta região física"
        else:
            status = "Neutra"
            explanation = "Comportamento equilibrado no contexto atual"

        zones.append({
            "zone_id": zone_id,
            "hits": hits,
            "percentage": percentage,
            "status": status,
            "explanation": explanation
        })

    return zones

# ======================================================
# VIZINHOS COM PRESSÃO (JANELA ATIVA)
# ======================================================
def calculate_neighbors_context(active_spins):
    pressure = Counter()

    for s in active_spins:
        for n in s["neighbors"]:
            pressure[n] += 1

    return [
        {"number": n, "pressure": p}
        for n, p in pressure.most_common()
    ]

# ======================================================
# SEQUÊNCIAS E PUXADAS
# ======================================================
def analyze_sequences(active_spins):
    sequences = []

    for i in range(1, len(active_spins)):
        prev = active_spins[i - 1]
        curr = active_spins[i]

        if curr["zone_id"] == prev["zone_id"]:
            sequences.append({
                "type": "zona_puxada",
                "zone_id": curr["zone_id"]
            })

        if curr["number"] in prev["neighbors"]:
            sequences.append({
                "type": "vizinho_puxado",
                "number": curr["number"]
            })

        if curr["color"] == prev["color"]:
            sequences.append({
                "type": "cor_repetida",
                "color": curr["color"]
            })

    return sequences

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
# MOTOR PRINCIPAL (COMPATÍVEL COM FRONTEND)
# ======================================================
def analyze_data(data, active_window=DEFAULT_ACTIVE_WINDOW):
    if not data:
        return {
            "status": "no_data",
            "message": "Nenhum número recebido"
        }

    valid_numbers = [n for n in data if n in ROULETTE_WHEEL]
    spins = [build_spin_object(n) for n in valid_numbers]

    add_to_history(spins)

    active_spins = get_active_window(active_window)
    count = Counter([s["number"] for s in GLOBAL_HISTORY])

    analysis = {
        "status": "ok",

        # Histórico
        "history_size": len(GLOBAL_HISTORY),
        "active_window": len(active_spins),

        # Mantido para frontend
        "numbers": dict(count),
        "history": [s["number"] for s in active_spins],

        # NOVAS ANÁLISES CONTEXTUAIS
        "physical_zones": calculate_physical_zones_context(active_spins),
        "neighbors": calculate_neighbors_context(active_spins),
        "sequences": analyze_sequences(active_spins),

        # Estrutura mantida
        "horses": calculate_horses(),

        "strategies": [
            "Análise baseada na janela ativa da mesa",
            "Eventos antigos servem apenas como contexto histórico",
            "Zonas, vizinhos e sequências seguem a roleta física",
            "A roleta muda rapidamente — foco no momento atual"
        ],

        "alerts": []
    }

    return analysis
