# ===============================
# ROULETTE AI ENGINE – V2.1 (Improved)
# ===============================

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


# ======================================================
# ENUMS PARA MELHOR TYPE SAFETY
# ======================================================

class Color(str, Enum):
    RED = "red"
    BLACK = "black"
    GREEN = "green"


class Parity(str, Enum):
    EVEN = "even"
    ODD = "odd"


class HighLow(str, Enum):
    LOW = "low"
    HIGH = "high"


class Sector(str, Enum):
    VOISINS = "voisins"
    TIERS = "tiers"
    ORPHELINS = "orphelins"
    UNKNOWN = "unknown"


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

RED_NUMBERS = frozenset({  # frozenset é mais eficiente para lookups
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36
})


# ======================================================
# SETORES CLASSICOS
# ======================================================

VOISINS_DU_ZERO = frozenset({22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25})
TIERS_DU_CYLINDRE = frozenset({27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33})
ORPHELINS = frozenset({1, 20, 14, 31, 9, 17, 34, 6})


# ======================================================
# DATACLASSES PARA ESTRUTURA DE DADOS
# ======================================================

@dataclass
class SpinData:
    """Dados completos de um giro"""
    number: int
    wheel_index: int
    color: str
    parity: Optional[str]
    dozen: Optional[int]
    column: Optional[int]
    high_low: Optional[str]
    terminal: int
    sector: str
    neighbors_1: List[int]
    neighbors_3: List[int]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ZoneAnalysis:
    """Análise de zona física"""
    name: str
    key: str
    numbers: List[int]
    hits: int
    percentage: float
    status: str
    explanation: str

    def to_dict(self) -> Dict:
        return asdict(self)


# ======================================================
# PRECOMPUTOS PARA PERFORMANCE
# ======================================================

WHEEL_LEN = len(ROULETTE_WHEEL)
WHEEL_INDEX: Dict[int, int] = {n: i for i, n in enumerate(ROULETTE_WHEEL)}
VALID_NUMBERS = frozenset(ROULETTE_WHEEL)  # Para validação rápida


def _wrap_index(i: int) -> int:
    """Wrapper circular do índice da roleta"""
    return i % WHEEL_LEN


def _neighbors_by_radius(idx: int, radius: int) -> List[int]:
    """Retorna vizinhos físicos excluindo o número central"""
    left = [ROULETTE_WHEEL[_wrap_index(idx - k)] for k in range(radius, 0, -1)]
    right = [ROULETTE_WHEEL[_wrap_index(idx + k)] for k in range(1, radius + 1)]
    return left + right


# Precomputar todos os vizinhos
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
    """Retorna a dúzia (1, 2, 3) ou None para zero"""
    if number == 0:
        return None
    return (number - 1) // 12 + 1


def column(number: int) -> Optional[int]:
    """Retorna a coluna (1, 2, 3) ou None para zero"""
    if number == 0:
        return None
    r = number % 3
    return 3 if r == 0 else r


def high_low(number: int) -> Optional[str]:
    """Retorna 'low' (1-18) ou 'high' (19-36) ou None para zero"""
    if number == 0:
        return None
    return HighLow.LOW.value if 1 <= number <= 18 else HighLow.HIGH.value


def terminal(number: int) -> int:
    """Retorna o terminal (último dígito 0-9)"""
    return number % 10


def color(number: int) -> str:
    """Retorna a cor do número"""
    if number == 0:
        return Color.GREEN.value
    return Color.RED.value if number in RED_NUMBERS else Color.BLACK.value


def parity(number: int) -> Optional[str]:
    """Retorna paridade (even/odd) ou None para zero"""
    if number == 0:
        return None
    return Parity.EVEN.value if number % 2 == 0 else Parity.ODD.value


def sector_membership(number: int) -> str:
    """Retorna o setor físico do número"""
    if number in VOISINS_DU_ZERO:
        return Sector.VOISINS.value
    if number in TIERS_DU_CYLINDRE:
        return Sector.TIERS.value
    if number in ORPHELINS:
        return Sector.ORPHELINS.value
    return Sector.UNKNOWN.value


# ======================================================
# VALIDAÇÃO DE ENTRADA
# ======================================================

def validate_numbers(data: List[int]) -> Tuple[List[int], List[str]]:
    """
    Valida e filtra números de entrada
    Retorna: (números válidos, lista de erros)
    """
    valid_nums = []
    errors = []
    
    for i, num in enumerate(data):
        if not isinstance(num, int):
            errors.append(f"Posição {i}: valor '{num}' não é inteiro")
            continue
        
        if num not in VALID_NUMBERS:
            errors.append(f"Posição {i}: número {num} inválido (deve ser 0-36)")
            continue
        
        valid_nums.append(num)
    
    return valid_nums, errors


# ======================================================
# CONSTRUÇÃO DE OBJETOS DE GIRO
# ======================================================

def build_spin_object(number: int) -> SpinData:
    """Cria objeto completo de dados do giro"""
    idx = WHEEL_INDEX[number]
    
    spin = SpinData(
        number=number,
        wheel_index=idx,
        color=color(number),
        parity=parity(number),
        dozen=dozen(number),
        column=column(number),
        high_low=high_low(number),
        terminal=terminal(number),
        sector=sector_membership(number),
        neighbors_1=NEIGHBORS_1[number],
        neighbors_3=NEIGHBORS_3[number],
    )
    
    return spin


# ======================================================
# ZONAS FISICAS
# ======================================================

def _zone_status_from_hits(hits: int, max_hits: int, min_hits: int) -> Tuple[str, str]:
    """Determina status e explicação baseado nos hits"""
    if max_hits > 0 and hits == max_hits:
        return "🔥 Quente", "Zona com maior recorrência recente na roleta física"
    if hits == min_hits:
        return "❄️ Fria", "Zona com baixa incidência recente, indicando possível ausência"
    return "Neutra", "Zona com comportamento estatisticamente equilibrado"


def calculate_physical_zones(history: List[int]) -> List[Dict]:
    """Calcula análise de zonas físicas (setores clássicos)"""
    total = len(history)
    if total == 0:
        return []
    
    zones_config = [
        {
            "name": "Voisins du Zero",
            "key": Sector.VOISINS.value,
            "numbers_set": VOISINS_DU_ZERO,
        },
        {
            "name": "Tiers du Cylindre",
            "key": Sector.TIERS.value,
            "numbers_set": TIERS_DU_CYLINDRE,
        },
        {
            "name": "Orphelins",
            "key": Sector.ORPHELINS.value,
            "numbers_set": ORPHELINS,
        },
    ]
    
    zones = []
    for config in zones_config:
        nums_set = config["numbers_set"]
        hits = sum(1 for n in history if n in nums_set)
        
        zone = {
            "name": config["name"],
            "key": config["key"],
            "numbers": sorted(nums_set, key=lambda x: WHEEL_INDEX[x]),
            "hits": hits,
            "percentage": round((hits / total) * 100, 2),
        }
        zones.append(zone)
    
    # Determinar status
    max_hits = max((z["hits"] for z in zones), default=0)
    min_hits = min((z["hits"] for z in zones), default=0)
    
    for z in zones:
        status, explanation = _zone_status_from_hits(z["hits"], max_hits, min_hits)
        z["status"] = status
        z["explanation"] = explanation
    
    return zones


# ======================================================
# NEIGHBORS PRESSURE
# ======================================================

def calculate_neighbors(history: List[int], radius: int = 3) -> List[Dict]:
    """
    Calcula pressão de vizinhos (quantas vezes cada número apareceu
    como vizinho físico dos números sorteados)
    """
    pressure: Counter = Counter()
    
    neighbors_map = NEIGHBORS_3 if radius == 3 else None
    
    for num in history:
        if num not in WHEEL_INDEX:
            continue
        
        # Usar precomputado se disponível
        if neighbors_map and num in neighbors_map:
            neigh = neighbors_map[num]
        else:
            idx = WHEEL_INDEX[num]
            neigh = _neighbors_by_radius(idx, radius)
        
        for n in neigh:
            pressure[n] += 1
    
    return [
        {"number": n, "pressure": p}
        for n, p in pressure.most_common()
    ]


# ======================================================
# CAVALOS (OPOSIÇÃO FÍSICA)
# ======================================================

def calculate_horses() -> List[Dict]:
    """Calcula pares de cavalos (números opostos na roleta)"""
    horses: List[Dict] = []
    half = WHEEL_LEN // 2
    
    for i in range(half):
        horses.append({
            "pair": [ROULETTE_WHEEL[i], ROULETTE_WHEEL[i + half]]
        })
    
    return horses


# ======================================================
# TERMINAIS
# ======================================================

def calculate_terminals(history: List[int], max_spins: int = 50) -> Dict:
    """Análise completa de terminais (último dígito)"""
    last_spins = history[-max_spins:]
    total = len(last_spins)
    
    if total == 0:
        return {
            "window": 0,
            "counts": {},
            "detail": [],
            "top": [],
            "cold": [],
        }
    
    # Contagem de terminais
    t_counts: Counter = Counter(terminal(n) for n in last_spins)
    
    # Calcular ausência (giros desde última aparição)
    t_last_seen: Dict[int, Optional[int]] = {t: None for t in range(10)}
    
    for i, n in enumerate(last_spins):
        t_last_seen[terminal(n)] = i
    
    t_absence: Dict[int, int] = {}
    for t in range(10):
        last_i = t_last_seen[t]
        if last_i is None:
            t_absence[t] = total
        else:
            t_absence[t] = (total - 1) - last_i
    
    # Determinar status
    max_hits = max(t_counts.values()) if t_counts else 0
    min_hits = min(t_counts.values()) if t_counts else 0
    
    def _status(hits: int) -> str:
        if hits == max_hits and max_hits > 0:
            return "🔥 Quente"
        if hits == min_hits:
            return "❄️ Frio"
        return "Neutro"
    
    # Detalhes por terminal
    terminals_detail = [
        {
            "terminal": t,
            "hits": t_counts.get(t, 0),
            "percentage": round((t_counts.get(t, 0) / total) * 100, 2),
            "absence": t_absence.get(t, total),
            "status": _status(t_counts.get(t, 0)),
        }
        for t in range(10)
    ]
    
    # Top 3 quentes e frios
    top = sorted(terminals_detail, key=lambda x: x["hits"], reverse=True)[:3]
    cold = sorted(terminals_detail, key=lambda x: (x["hits"], -x["absence"]))[:3]
    
    return {
        "window": total,
        "counts": {str(k): v for k, v in t_counts.items()},
        "detail": terminals_detail,
        "top": top,
        "cold": cold,
    }


# ======================================================
# AUSÊNCIAS
# ======================================================

def calculate_absences(history: List[int], max_spins: int = 50) -> Dict:
    """Calcula números, zonas, cavalos e terminais ausentes"""
    last_spins = history[-max_spins:]
    last_set = frozenset(last_spins)
    
    # Números ausentes
    absent_numbers = [n for n in ROULETTE_WHEEL if n not in last_set]
    
    # Zonas ausentes
    zones = calculate_physical_zones(last_spins)
    absent_zones = [z for z in zones if z.get("hits", 0) == 0]
    
    # Cavalos ausentes (nenhum dos dois números apareceu)
    horses = calculate_horses()
    absent_horses = [
        h for h in horses 
        if not any(n in last_set for n in h["pair"])
    ]
    
    # Terminais ausentes
    t_counts: Counter = Counter(terminal(n) for n in last_spins)
    absent_terminals = [t for t in range(10) if t not in t_counts]
    
    return {
        "numbers": absent_numbers,
        "zones": absent_zones,
        "horses": absent_horses,
        "terminals": absent_terminals,
    }


# ======================================================
# ESTRATÉGIAS PREMIUM
# ======================================================

def analyze_premium_strategies(
    history: List[int], 
    user_strategies: Optional[List[Dict]] = None
) -> List[Dict]:
    """Analisa estratégias customizadas do usuário"""
    if not user_strategies:
        return []
    
    results: List[Dict] = []
    
    for strat in user_strategies:
        name = strat.get("name", "Strategy")
        triggers = [
            t for t in strat.get("triggers", []) 
            if isinstance(t, int) and t in WHEEL_INDEX
        ]
        
        if not triggers:
            continue
        
        stats = {
            "hits": 0,
            "misses": 0,
            "details": [],
        }
        
        # Vizinhos imediatos dos gatilhos
        trigger_neighbors = set()
        for t in triggers:
            trigger_neighbors.update(NEIGHBORS_1[t])
        
        for number in history:
            is_trigger = number in triggers
            is_neighbor = number in trigger_neighbors
            
            if is_trigger or is_neighbor:
                stats["hits"] += 1
                stats["details"].append({
                    "number": number,
                    "status": "hit",
                    "reason": "trigger" if is_trigger else "neighbor"
                })
            else:
                stats["misses"] += 1
                stats["details"].append({
                    "number": number,
                    "status": "miss"
                })
        
        results.append({
            "name": name,
            "triggers": triggers,
            "stats": stats
        })
    
    return results


# ======================================================
# ESTATÍSTICAS GERAIS
# ======================================================

def calculate_stats(history: List[int]) -> Dict[str, Any]:
    """Calcula estatísticas gerais da sessão"""
    if not history:
        return {}
    
    c: Counter = Counter(history)
    total = len(history)
    
    # Agregações
    by_color: Counter = Counter(color(n) for n in history)
    by_parity: Counter = Counter(parity(n) or "none" for n in history)
    by_dozen: Counter = Counter(str(dozen(n) or "none") for n in history)
    by_column: Counter = Counter(str(column(n) or "none") for n in history)
    by_highlow: Counter = Counter(high_low(n) or "none" for n in history)
    
    hottest_num, hottest_hits = c.most_common(1)[0] if c else (None, 0)
    
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

def analyze_data(
    data: List[int],
    history_limit: int = 50,
    user_strategies: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Motor principal de análise
    
    Args:
        data: Lista de números sorteados
        history_limit: Limite de histórico a considerar
        user_strategies: Estratégias customizadas do usuário
    
    Returns:
        Dicionário com análise completa
    """
    # Validação
    if not data:
        return {
            "status": "no_data",
            "message": "Nenhum número recebido",
            "errors": []
        }
    
    valid, errors = validate_numbers(data)
    
    if not valid:
        return {
            "status": "invalid_data",
            "message": "Nenhum número válido recebido",
            "errors": errors
        }
    
    # Limitar histórico
    history = valid[-history_limit:]
    
    # Construir objetos de giro
    spins = [build_spin_object(n) for n in history]
    last_spin = spins[-1] if spins else None
    
    # Contagem de números
    count: Counter = Counter(history)
    
    # Análise completa
    analysis = {
        "status": "ok",
        "numbers": dict(count),
        "history": history,
        
        # Dados detalhados dos giros
        "spins": [s.to_dict() for s in spins],
        "last_spin": last_spin.to_dict() if last_spin else None,
        
        # Análises específicas
        "physical_zones": calculate_physical_zones(history),
        "neighbors": calculate_neighbors(history, radius=3),
        "horses": calculate_horses(),
        "absences": calculate_absences(history, max_spins=history_limit),
        "terminals": calculate_terminals(history, max_spins=history_limit),
        "stats": calculate_stats(history),
        
        # Estratégias e alertas
        "strategies": analyze_premium_strategies(history, user_strategies),
        "alerts": [],
        
        # Metadados
        "errors": errors if errors else [],
        "valid_count": len(valid),
        "invalid_count": len(data) - len(valid),
    }
    
    return analysis


# ======================================================
# FUNÇÕES DE UTILIDADE PARA TESTES
# ======================================================

def get_sector_numbers(sector: str) -> frozenset:
    """Retorna os números de um setor específico"""
    sector_map = {
        "voisins": VOISINS_DU_ZERO,
        "tiers": TIERS_DU_CYLINDRE,
        "orphelins": ORPHELINS,
    }
    return sector_map.get(sector.lower(), frozenset())


def get_numbers_by_color(color_name: str) -> frozenset:
    """Retorna números de uma cor específica"""
    if color_name.lower() == "red":
        return RED_NUMBERS
    elif color_name.lower() == "black":
        return frozenset(n for n in range(1, 37) if n not in RED_NUMBERS)
    elif color_name.lower() == "green":
        return frozenset({0})
    return frozenset()