# ======================================================
# SESSION_MANAGER.PY - Gerenciamento de sessões
# ======================================================

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import threading
import time

from app.core.config import settings


class SessionManager:
    """
    Gerenciador de sessões em memória
    
    IMPORTANTE: Para produção, migrar para Redis ou banco de dados
    Esta implementação é thread-safe mas não escala horizontalmente
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._start_cleanup_thread()
    
    def create_session(self) -> str:
        """Cria uma nova sessão e retorna o ID"""
        with self._lock:
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = {
                "history": [],
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
            }
            return session_id
    
    def add_spin(self, session_id: str, number: int) -> None:
        """Adiciona um spin ao histórico da sessão"""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "history": [],
                    "created_at": datetime.now(),
                    "last_updated": datetime.now(),
                }
            
            session = self._sessions[session_id]
            session["history"].append(number)
            session["last_updated"] = datetime.now()
            
            # Limitar tamanho do histórico
            max_size = settings.MAX_HISTORY_PER_SESSION
            if len(session["history"]) > max_size:
                session["history"] = session["history"][-max_size:]
    
    def get_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[int]:
        """Retorna o histórico da sessão"""
        with self._lock:
            if session_id not in self._sessions:
                return []
            
            history = self._sessions[session_id]["history"]
            
            if limit:
                return history[-limit:]
            
            return history.copy()
    
    def clear_session(self, session_id: str) -> None:
        """Limpa o histórico de uma sessão"""
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]["history"] = []
                self._sessions[session_id]["last_updated"] = datetime.now()
    
    def delete_session(self, session_id: str) -> None:
        """Remove uma sessão completamente"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
    
    def session_exists(self, session_id: str) -> bool:
        """Verifica se uma sessão existe"""
        with self._lock:
            return session_id in self._sessions
    
    def get_active_sessions_count(self) -> int:
        """Retorna o número de sessões ativas"""
        with self._lock:
            return len(self._sessions)
    
    def cleanup_old_sessions(self, max_age_seconds: Optional[int] = None) -> int:
        """
        Remove sessões antigas
        Retorna o número de sessões removidas
        """
        if max_age_seconds is None:
            max_age_seconds = settings.SESSION_TIMEOUT
        
        with self._lock:
            cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
            
            old_sessions = [
                session_id
                for session_id, data in self._sessions.items()
                if data["last_updated"] < cutoff_time
            ]
            
            for session_id in old_sessions:
                del self._sessions[session_id]
            
            return len(old_sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Retorna informações sobre uma sessão"""
        with self._lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            return {
                "session_id": session_id,
                "total_spins": len(session["history"]),
                "created_at": session["created_at"].isoformat(),
                "last_updated": session["last_updated"].isoformat(),
            }
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza automática"""
        def cleanup_loop():
            while True:
                time.sleep(settings.SESSION_CLEANUP_INTERVAL)
                removed = self.cleanup_old_sessions()
                if removed > 0:
                    print(f"🧹 Limpeza automática: {removed} sessões removidas")
        
        self._cleanup_thread = threading.Thread(
            target=cleanup_loop,
            daemon=True
        )
        self._cleanup_thread.start()


# ======================================================
# VERSÃO REDIS (para produção futura)
# ======================================================

class RedisSessionManager:
    """
    Versão com Redis para produção
    Implementar quando escalar horizontalmente
    """
    
    def __init__(self, redis_url: str):
        # import redis
        # self.redis = redis.from_url(redis_url)
        raise NotImplementedError("Redis session manager não implementado ainda")