from collections import Counter, defaultdict

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
# OBJETO FÍSICO DO GIRO
# ======================================================
def build_spin_object(number):
    idx = ROULETTE_WHEEL.index(number)

    terminal = number % 10
    horse_group = (
        (1,4,7) if terminal in (1,4,7) else
        (2,5,8) if terminal in (2,5,8) else
        (3,6,9,0)
    )

    return {
        "number": number,
        "wheel_index": idx,
        "color": "red" if number in RED_NUMBERS else "black" if number != 0 else "green",
        "parity": "even" if number != 0 and number % 2 == 0 else "odd" if number != 0 else None,
        "high_low": "high" if number >= 19 else "low" if number != 0 else None,
        "terminal": terminal,
        "horse_group": horse_group,
        "neighbors": [
            ROULETTE_WHEEL[(idx - 1) % 37],
            ROULETTE_WHEEL[(idx + 1) % 37]
        ]
    }

# ======================================================
# ZONAS FÍSICAS CONTÍNUAS + VIZINHOS
# ======================================================
def calculate_physical_zones(history, zone_size=6):
    zones = []
    total = len(history)

    for i in range(0, len(ROULETTE_WHEEL), zone_size):
        core = ROULETTE_WHEEL[i:i + zone_size]

        extended = set(core)
        for n in core:
            idx = ROULETTE_WHEEL.index(n)
            extended.update([
                ROULETTE_WHEEL[(idx - 1) % 37],
                ROULETTE_WHEEL[(idx - 2) % 37],
                ROULETTE_WHEEL[(idx + 1) % 37],
                ROULETTE_WHEEL[(idx + 2) % 37]
            ])

        hits = sum(1 for n in history if n in extended)

        zones.append({
            "core": core,
            "extended": list(extended),
            "hits": hits,
            "percentage": round((hits / total) * 100, 2) if total else 0
        })

    max_hits = max(z["hits"] for z in zones)
    min_hits = min(z["hits"] for z in zones)

    for z in zones:
        if z["hits"] == max_hits and max_hits > 0:
            z["status"] = "🔥 Quente"
            z["explanation"] = "Alta concentração física de resultados recentes"
        elif z["hits"] == min_hits:
            z["status"] = "❄️ Fria"
            z["explanation"] = "Zona com ausência prolongada na roleta física"
        else:
            z["status"] = "Neutra"
            z["explanation"] = "Zona equilibrada no período analisado"

    return zones

# ======================================================
# AUSÊNCIA (GENÉRICO PARA QUALQUER GRUPO)
# ======================================================
def calculate_absence(history, groups):
    absence = {}

    for name, values in groups.items():
        last_seen = None
        for i, n in enumerate(reversed(history)):
            if n in values:
                last_seen = i
                break
        absence[name] = last_seen if last_seen is not None else len(history)

    return absence

# ======================================================
# ALTERNÂNCIA ENTRE CONTEXTOS
# ======================================================
def analyze_alternation(spins):
    alternation = []

    for i in range(1, len(spins)):
        prev = spins[i - 1]
        curr = spins[i]

        changes = []

        if prev["terminal"] != curr["terminal"]:
            changes.append("terminal")

        if prev["horse_group"] != curr["horse_group"]:
            changes.append("horse")

        if prev["high_low"] != curr["high_low"]:
            changes.append("high_low")

        if changes:
            alternation.append({
                "from": prev["number"],
                "to": curr["number"],
                "changes": changes
            })

    return alternation

# ======================================================
# MOTOR PRINCIPAL
# ======================================================
def analyze_data(data, window_size=30):
    if not data:
        return {"status": "no_data"}

    # Histórico completo
    full_history = data[:]

    # Janela viva
    window = full_history[-max(20, min(window_size, 50)):]

    spins = [build_spin_object(n) for n in window if n in ROULETTE_WHEEL]

    count = Counter(window)

    # Grupos para ausência
    terminal_groups = defaultdict(list)
    horse_groups = defaultdict(list)

    for n in ROULETTE_WHEEL:
        terminal_groups[n % 10].append(n)

        if n % 10 in (1,4,7):
            horse_groups["1-4-7"].append(n)
        elif n % 10 in (2,5,8):
            horse_groups["2-5-8"].append(n)
        else:
            horse_groups["3-6-9-0"].append(n)

    analysis = {
        "status": "ok",

        "history_window": window,
        "window_size": len(window),

        "numbers": dict(count),

        "physical_zones": calculate_physical_zones(window),

        "absence": {
            "terminals": calculate_absence(window, terminal_groups),
            "horses": calculate_absence(window, horse_groups)
        },

        "alternation": analyze_alternation(spins),

        "strategies": [
            "Análise baseada em zonas físicas reais da roleta",
            "Alternância detecta mudanças estruturais da mesa",
            "Ausência indica pressão estatística e física",
            "Vizinhos ampliam leitura contínua da roda"
        ],

        "alerts": []
    }

    return analysis
