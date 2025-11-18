"""
Utilitários para trabalhar com LLMs
- Retry logic
- Rate limiting
- Logging de interações
"""

import time
import json
from typing import Callable, Any, Optional
from pathlib import Path
from datetime import datetime
from functools import wraps


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator para retry automático em caso de falha

    Args:
        max_retries: Número máximo de tentativas
        delay: Delay inicial entre tentativas (segundos)
        backoff: Multiplicador de delay a cada tentativa
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        print(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                        print(
                            f"Aguardando {current_delay:.1f}s antes de tentar novamente..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff

            if last_exception:
                raise last_exception
            return None

        return wrapper

    return decorator


class LLMLogger:
    """Logger de interações com LLM para documentação do relatório"""

    def __init__(self, log_dir: Optional[str] = None):
        """
        Inicializa o logger

        Args:
            log_dir: Diretório para salvar logs (padrão: logs/)
        """
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.log_dir = project_root / "logs"
        else:
            self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Arquivo de log da sessão atual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_dir / f"llm_session_{timestamp}.jsonl"

    def log_interaction(
        self,
        prompt: str,
        response: str,
        provider: str,
        model: str,
        purpose: str,
        tokens_used: Optional[int] = None,
        latency: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Registra uma interação com o LLM

        Args:
            prompt: Prompt enviado
            response: Resposta recebida
            provider: Provedor usado (gemini, deepseek, etc)
            model: Modelo usado
            purpose: Propósito da chamada (ex: "extração de soft skills")
            tokens_used: Tokens consumidos
            latency: Tempo de resposta (segundos)
            success: Se a chamada foi bem-sucedida
            error: Mensagem de erro (se houver)
            metadata: Dados adicionais
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "purpose": purpose,
            "prompt": prompt,
            "response": response,
            "tokens_used": tokens_used,
            "latency": latency,
            "success": success,
            "error": error,
            "metadata": metadata or {},
        }

        # Salva em JSONL (JSON Lines)
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_session_stats(self) -> dict:
        """
        Retorna estatísticas da sessão atual

        Returns:
            Dict com estatísticas (total_calls, total_tokens, avg_latency, etc)
        """
        if not self.session_file.exists():
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_tokens": 0,
                "avg_latency": 0.0,
            }

        total_calls = 0
        successful_calls = 0
        failed_calls = 0
        total_tokens = 0
        total_latency = 0.0
        latencies = []

        with open(self.session_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                total_calls += 1

                if entry["success"]:
                    successful_calls += 1
                else:
                    failed_calls += 1

                if entry.get("tokens_used"):
                    total_tokens += entry["tokens_used"]

                if entry.get("latency"):
                    latency = entry["latency"]
                    total_latency += latency
                    latencies.append(latency)

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "total_tokens": total_tokens,
            "avg_latency": total_latency / total_calls if total_calls > 0 else 0.0,
            "min_latency": min(latencies) if latencies else 0.0,
            "max_latency": max(latencies) if latencies else 0.0,
        }


# Instância global do logger
_llm_logger: Optional[LLMLogger] = None


def get_llm_logger() -> LLMLogger:
    """Retorna instância singleton do LLMLogger"""
    global _llm_logger

    if _llm_logger is None:
        _llm_logger = LLMLogger()

    return _llm_logger
