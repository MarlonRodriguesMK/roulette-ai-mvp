# ===============================
# ROULETTE AI ENGINE – V2 (Premium)
# ===============================
# Objetivos desta versao:
# 1) "spins" retornando todos os dados por giro (para o frontend abrir detalhes)
# 2) wheel em loop (precomputos de vizinhos, indices, etc.)
# 3) Zonas fisicas opcao C: setores classicos (Voisins du Zero / Tiers / Orphelins)
# 4) Neighbors pressure com 3 vizinhos para cada lado (base roleta fisica)
# 5) Ausencia avancada + Terminais (analise completa)
#
# Observacao:
# - Mantive as chaves principais do JSON para nao quebrar o frontend:
#   status, numbers, history, physical_zones, neighbors, horses, absences, strategies, alerts
# - Acrescentei campos novos (nao obrigatorios) que o frontend pode aproveitar:
#   spins, stats, terminals

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ======================================================
# MAPA FISICO DA ROLETA EUROPEIA (single zero)
# ======================================================
ROULETTE_WHEEL: List[int] = [
    0, 32, 15, 19, 4, 21, 2, 25, 17,
    34, 6, 27, 13, 36, 11, 30,
    8, 23, 10, 5, 24, 16, 33,
    1, 20, 14, 31, 9, 22, 18,
    29, 7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36
}

# ======================================================
# SETORES CLASSICOS ("Opcao C")
# - Voisins du Zero (17 numeros)
# - Tiers du Cylindre (12 numeros)
# - Orphelins (8 numeros)
# Fonte: setores tradicionais da roleta europeia
# ======================================================
VOISINS_DU_ZERO = {22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25}
TIERS_DU_CYLINDRE = {27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33}
ORPHELINS = {1, 20, 14, 31, 9, 17, 34, 6}

# Sanity: os 3 setores cobrem 37 numeros
# (algumas representacoes antigas podem variar, mas esta e a mais comum)


# ======================================================
# PRECOMPUTOS PARA PERFORMANCE
# ======================================================
WHEEL_LEN = len(ROULETTE_WHEEL)
WHEEL_INDEX: Dict[int, int] = {n: i for i, n in enumerate(ROULETTE_WHEEL)}


def _wrap_index(i: int) -> int:
    return i % WHEEL_LEN


def _neighbors_by_radius(idx: int, radius: int) -> List[int]:
    # Exclui o proprio numero e retorna (esquerda..direita)
    left = [ROULETTE_WHEEL[_wrap_index(idx - k)] for k in range(radius, 0, -1)]
    right = [ROULETTE_WHEEL[_wrap_index(idx + k)] for k in range(1, radius + 1)]
    return left + right


NEIGHBORS_1: Dict[int, List[int]] = {}
NEIGHBORS_3: Dict[int, List[int]] = {}
for n in ROULETTE_WHEEL:
    i = WHEEL_INDEX[n]
    NEIGHBORS_1[n] = _neighbors_by_radius(i, 1)
    NEIGHBORS_3[n] = _neighbors_by_radius(i, 3)


# ======================================================
# HELPERS: dezenas / colunas / alto-baixo / terminal
# ======================================================

def dozen(number: int) -> Optional[int]:
    if number == 0:
        return None
    return (number - 1) // 12 + 1  # 1..3


def column(number: int) -> Optional[int]:
    if number == 0:
        return None
    # colunas no tapete: 1,2,3 (resto 1..3)
    r = number % 3
    return 3 if r == 0 else r


def high_low(number: int) -> Optional[str]:
    if number == 0:
        return None
    return "low" if 1 <= number <= 18 else "high"


def terminal(number: int) -> int:
    return number % 10


def color(number: int) -> str:
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"


def parity(number: int) -> Optional[str]:
    if number == 0:
        return None
    return "even" if number % 2 == 0 else "odd"


def sector_membership(number: int) -> str:
    if number in VOISINS_DU_ZERO:
        return "voisins"
    if number in TIERS_DU_CYLINDRE:
        return "tiers"
    if number in ORPHELINS:
        return "orphelins"
    # Em teoria nao acontece
    return "unknown"


# ======================================================
# FUNCAO: CRIA OBJETO COMPLETO DE CADA GIRO
# ======================================================

def build_spin_object(number: int) -> Dict:
    idx = WHEEL_INDEX[number]
    return {
        "number": number,
        "wheel_index": idx,
        "color": color(number),
        "parity": parity(number),
        "dozen": dozen(number),
        "column": column(number),
        "high_low": high_low(number),
        "terminal": terminal(number),
        "sector": sector_membership(number),
        # vizinhos fisicos
        "neighbors_1": NEIGHBORS_1[number],
        "neighbors_3": NEIGHBORS_3[number],
    }


# ======================================================
# ZONAS FISICAS (Opcao C - setores classicos)
# ======================================================

def _zone_status_from_hits(hits: int, max_hits: int, min_hits: int) -> Tuple[str, str]:
    if max_hits > 0 and hits == max_hits:
        return "🔥 Quente", "Zona com maior recorrencia recente na roleta fisica"
    if hits == min_hits:
        return "❄️ Fria", "Zona com baixa incidencia recente, indicando possivel ausencia"
    return "Neutra", "Zona com comportamento estatisticamente equilibrado"


def calculate_physical_zones(history: List[int]) -> List[Dict]:
    total = len(history)
    zones = [
        {
            "name": "Voisins du Zero",
            "key": "voisins",
            "numbers": sorted(VOISINS_DU_ZERO, key=lambda x: WHEEL_INDEX.get(x, 999)),
        },
        {
            "name": "Tiers du Cylindre",
            "key": "tiers",
            "numbers": sorted(TIERS_DU_CYLINDRE, key=lambda x: WHEEL_INDEX.get(x, 999)),
        },
        {
            "name": "Orphelins",
            "key": "orphelins",
            "numbers": sorted(ORPHELINS, key=lambda x: WHEEL_INDEX.get(x, 999)),
        },
    ]

    for z in zones:
        nums = set(z["numbers"])
        hits = sum(1 for n in history if n in nums)
        z["hits"] = hits
        z["percentage"] = round((hits / total) * 100, 2) if total else 0.0

    max_hits = max((z["hits"] for z in zones), default=0)
    min_hits = min((z["hits"] for z in zones), default=0)
    for z in zones:
        status, explanation = _zone_status_from_hits(z["hits"], max_hits, min_hits)
        z["status"] = status
        z["explanation"] = explanation

    return zones


# ======================================================
# NEIGHBORS PRESSURE (3 vizinhos para cada lado)
# ======================================================

def calculate_neighbors(history: List[int], radius: int = 3) -> List[Dict]:
    # radius fixado em 3 por padrao (pedido)
    # Pressao = quantas vezes um numero apareceu como vizinho fisico dos giros
    pressure = Counter()
    for num in history:
        if num in WHEEL_INDEX:
            neigh = NEIGHBORS_3[num] if radius == 3 else _neighbors_by_radius(WHEEL_INDEX[num], radius)
            for n in neigh:
                pressure[n] += 1

    return [{"number": n, "pressure": p} for n, p in pressure.most_common()]


# ======================================================
# CAVALOS (OPOSICAO FISICA)
# ======================================================

def calculate_horses() -> List[Dict]:
    horses: List[Dict] = []
    half = WHEEL_LEN // 2
    for i in range(half):
        horses.append({"pair": [ROULETTE_WHEEL[i], ROULETTE_WHEEL[i + half]]})
    return horses


# ======================================================
# TERMINAIS (analise)
# ======================================================

def calculate_terminals(history: List[int], max_spins: int = 50) -> Dict:
    last_spins = history[-max_spins:]
    totals = len(last_spins)

    # Terminal = ultimo digito (0..9)
    t_counts = Counter(terminal(n) for n in last_spins)

    # Ausencia por terminal = quantos giros desde a ultima ocorrencia daquele terminal
    # Se nunca ocorreu na janela, ausencia = totals
    t_last_seen: Dict[int, int] = {t: None for t in range(10)}  # type: ignore
    for i, n in enumerate(last_spins):
        t_last_seen[terminal(n)] = i

    t_absence = {}
    for t in range(10):
        last_i = t_last_seen[t]
        if last_i is None:
            t_absence[t] = totals
        else:
            t_absence[t] = (totals - 1) - last_i

    # Ranking quente/frio por contagem
    ranked = sorted(t_counts.items(), key=lambda kv: kv[1], reverse=True)
    max_hits = ranked[0][1] if ranked else 0
    min_hits = min((v for _, v in ranked), default=0)

    def _status(v: int) -> str:
        if v == max_hits and max_hits > 0:
            return "🔥 Quente"
        if v == min_hits:
            return "❄️ Frio"
        return "Neutro"

    terminals_detail = [
        {
            "terminal": t,
            "hits": t_counts.get(t, 0),
            "percentage": round((t_counts.get(t, 0) / totals) * 100, 2) if totals else 0.0,
            "absence": t_absence.get(t, totals),
            "status": _status(t_counts.get(t, 0)),
        }
        for t in range(10)
    ]

    top = sorted(terminals_detail, key=lambda x: x["hits"], reverse=True)[:3]
    cold = sorted(terminals_detail, key=lambda x: (x["hits"], -x["absence"]))[:3]

    return {
        "window": min(max_spins, len(history)),
        "counts": {str(k): v for k, v in t_counts.items()},
        "detail": terminals_detail,
        "top": top,
        "cold": cold,
    }


# ======================================================
# AUSENCIAS (numeros, zonas, cavalos, terminais)
# ======================================================

def calculate_absences(history: List[int], max_spins: int = 50) -> Dict:
    last_spins = history[-max_spins:]

    # Numeros ausentes
    absent_numbers = [n for n in ROULETTE_WHEEL if n not in set(last_spins)]

    # Zonas ausentes (setores C)
    zones = calculate_physical_zones(last_spins)
    absent_zones = [z for z in zones if z.get("hits", 0) == 0]

    # Cavalos ausentes (nenhum dos dois numeros apareceu)
    horses = calculate_horses()
    last_set = set(last_spins)
    absent_horses = [h for h in horses if not any(n in last_set for n in h["pair"]) ]

    # Terminais ausentes (na janela)
    t_counts = Counter(terminal(n) for n in last_spins)
    absent_terminals = [t for t in range(10) if t_counts.get(t, 0) == 0]

    return {
        "numbers": absent_numbers,
        "zones": absent_zones,
        "horses": absent_horses,
        "terminals": absent_terminals,
    }


# ======================================================
# ESTRATEGIAS PREMIUM (mantive, com robustez)
# ======================================================

def analyze_premium_strategies(history: List[int], user_strategies: List[Dict]) -> List[Dict]:
    results: List[Dict] = []

    for strat in user_strategies or []:
        name = strat.get("name", "Strategy")
        triggers = [t for t in strat.get("triggers", []) if t in WHEEL_INDEX]

        stats = {
            "hits": 0,
            "misses": 0,
            "details": [],
        }

        # Vizinhos 1 (imediatos) dos gatilhos
        trigger_neighbors = set()
        for t in triggers:
            for n in NEIGHBORS_1[t]:
                trigger_neighbors.add(n)

        for number in history:
            is_trigger = number in triggers
            is_neighbor = number in trigger_neighbors

            if is_trigger or is_neighbor:
                stats["hits"] += 1
                stats["details"].append({"number": number, "status": "hit", "reason": "trigger" if is_trigger else "neighbor"})
            else:
                stats["misses"] += 1
                stats["details"].append({"number": number, "status": "miss"})

        results.append({"name": name, "triggers": triggers, "stats": stats})

    return results


# ======================================================
# STATS GERAIS (para frontend explicar melhor)
# ======================================================

def calculate_stats(history: List[int]) -> Dict:
    if not history:
        return {}

    c = Counter(history)
    total = len(history)

    by_color = Counter(color(n) for n in history)
    by_parity = Counter(parity(n) or "none" for n in history)
    by_dozen = Counter(str(dozen(n) or "none") for n in history)
    by_column = Counter(str(column(n) or "none") for n in history)
    by_highlow = Counter(high_low(n) or "none" for n in history)

    hottest_num, hottest_hits = c.most_common(1)[0]

    return {
        "total_spins": total,
        "hottest_number": hottest_num,
        "hottest_hits": hottest_hits,
        "color": dict(by_color),
        "parity": dict(by_parity),
        "dozens": dict(by_dozen),
        "columns": dict(by_column),
        "high_low": dict(by_highlow),
    }


# ======================================================
# MOTOR PRINCIPAL
# ======================================================

def analyze_data(data: List[int], history_limit: int = 50, user_strategies: Optional[List[Dict]] = None) -> Dict:
    if not data:
        return {"status": "no_data", "message": "Nenhum numero recebido"}

    # Filtra apenas numeros validos para evitar quebra
    valid = [n for n in data if isinstance(n, int) and n in WHEEL_INDEX]
    if not valid:
        return {"status": "no_data", "message": "Nenhum numero valido recebido"}

    history = valid[-history_limit:]

    # Spins completos
    spins = [build_spin_object(n) for n in history]
    last_spin = spins[-1] if spins else None

    # Contagem
    count = Counter(history)

    analysis = {
        "status": "ok",
        "numbers": dict(count),
        "history": history,
        # novo (para o frontend abrir detalhes por giro)
        "spins": spins,
        "last_spin": last_spin,

        # zonas fisicas (Opcao C)
        "physical_zones": calculate_physical_zones(history),

        # neighbors pressure (3 vizinhos por lado)
        "neighbors": calculate_neighbors(history, radius=3),

        "horses": calculate_horses(),

        # ausencias + terminais
        "absences": calculate_absences(history, max_spins=history_limit),
        "terminals": calculate_terminals(history, max_spins=history_limit),

        # extras para explicacoes
        "stats": calculate_stats(history),

        "strategies": [],
        "alerts": [],
    }

    if user_strategies:
        analysis["strategies"] = analyze_premium_strategies(history, user_strategies)

    return analysis
