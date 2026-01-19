# ======================================================
# AI_SERVICE.PY - Serviço de análise de IA
# ======================================================

from typing import List, Optional, Dict, Any
import logging

# Importar o motor de IA corrigido
from app.engines.ai_engine_improved import analyze_data


logger = logging.getLogger(__name__)


class AIService:
    """
    Serviço que encapsula a lógica de análise de IA
    Adiciona logging, validação e tratamento de erros
    """
    
    def __init__(self):
        logger.info("✅ AIService inicializado")
    
    def analyze(
        self,
        history: List[int],
        history_limit: int = 50,
        user_strategies: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Executa análise completa do histórico
        
        Args:
            history: Lista de números sorteados
            history_limit: Limite de histórico a considerar
            user_strategies: Estratégias customizadas
            
        Returns:
            Dicionário com análise completa
        """
        try:
            logger.info(f"Analisando histórico com {len(history)} spins")
            
            # Validar entrada
            if not history:
                return {
                    "status": "no_data",
                    "message": "Histórico vazio",
                    "data": {}
                }
            
            # Chamar motor de IA
            analysis = analyze_data(
                data=history,
                history_limit=history_limit,
                user_strategies=user_strategies
            )
            
            logger.info(f"✅ Análise concluída: {analysis.get('status')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Erro ao analisar dados: {str(e)}",
                "data": {}
            }
    
    def analyze_single_spin(self, number: int) -> Dict[str, Any]:
        """
        Análise rápida de um único spin
        Útil para insights em tempo real
        """
        try:
            from app.engines.ai_engine_improved import build_spin_object
            
            spin = build_spin_object(number)
            
            return {
                "status": "ok",
                "spin": spin.to_dict(),
                "insights": self._generate_quick_insights(spin)
            }
            
        except Exception as e:
            logger.error(f"Erro em analyze_single_spin: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _generate_quick_insights(self, spin) -> Dict[str, str]:
        """Gera insights rápidos sobre um spin"""
        insights = {}
        
        # Setor
        if spin.sector == "voisins":
            insights["sector"] = "Número no setor Voisins du Zero (zona quente clássica)"
        elif spin.sector == "tiers":
            insights["sector"] = "Número no setor Tiers du Cylindre"
        elif spin.sector == "orphelins":
            insights["sector"] = "Número no setor Orphelins (órfãos)"
        
        # Cor
        if spin.color == "red":
            insights["color"] = "Vermelho - Continue observando padrões de cor"
        elif spin.color == "black":
            insights["color"] = "Preto - Monitore alternância de cores"
        else:
            insights["color"] = "Zero verde - Momento de recalibrar estratégias"
        
        # Par/Ímpar
        if spin.parity == "even":
            insights["parity"] = "Par - Considere pressão em números pares"
        elif spin.parity == "odd":
            insights["parity"] = "Ímpar - Atenção para sequências ímpares"
        
        return insights
    
    def validate_strategy(self, strategy: Dict) -> tuple[bool, Optional[str]]:
        """
        Valida uma estratégia antes de processá-la
        
        Returns:
            (válido, mensagem_erro)
        """
        try:
            if not strategy.get("name"):
                return False, "Estratégia sem nome"
            
            triggers = strategy.get("triggers", [])
            if not triggers:
                return False, "Estratégia sem números gatilho"
            
            invalid = [n for n in triggers if not (0 <= n <= 36)]
            if invalid:
                return False, f"Números inválidos: {invalid}"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_hot_numbers(self, history: List[int], top_n: int = 5) -> List[Dict]:
        """Retorna os números mais quentes"""
        from collections import Counter
        
        if not history:
            return []
        
        counter = Counter(history)
        hot = counter.most_common(top_n)
        
        return [
            {
                "number": num,
                "hits": count,
                "percentage": round((count / len(history)) * 100, 2)
            }
            for num, count in hot
        ]
    
    def get_cold_numbers(self, history: List[int], window: int = 50) -> List[int]:
        """Retorna números ausentes na janela"""
        recent = history[-window:] if len(history) > window else history
        recent_set = set(recent)
        
        all_numbers = set(range(37))
        cold = sorted(all_numbers - recent_set)
        
        return cold