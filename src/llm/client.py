"""
Módulo LLM: Integração com Large Language Models
- LLMClient: interface abstrata para múltiplos provedores
- Implementações concretas: Gemini, Groq, OpenRouter
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import os
from dataclasses import dataclass
import time


@dataclass
class LLMResponse:
    """Resposta padronizada de um LLM"""

    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    latency: Optional[float] = None  # em segundos
    success: bool = True
    error: Optional[str] = None


class LLMClient(ABC):
    """Interface abstrata para clientes LLM"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs

    @abstractmethod
    def call(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        """
        Chama o LLM com o prompt fornecido

        Args:
            prompt: Texto do prompt
            temperature: Controla aleatoriedade (0.0 = determinístico, 1.0 = criativo)
            max_tokens: Máximo de tokens na resposta
            **kwargs: Parâmetros específicos do provedor

        Returns:
            LLMResponse com o conteúdo gerado
        """
        pass

    @abstractmethod
    def call_json(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000, **kwargs
    ) -> Dict[str, Any]:
        """
        Chama o LLM esperando resposta em JSON

        Args:
            prompt: Texto do prompt (deve pedir JSON)
            temperature: Temperatura (mais baixa para JSON estruturado)
            max_tokens: Máximo de tokens
            **kwargs: Parâmetros específicos

        Returns:
            Dict parseado do JSON retornado

        Raises:
            ValueError: Se resposta não for JSON válido
        """
        pass

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Extrai e parseia JSON de uma resposta que pode conter texto adicional
        """
        # Tenta parsear diretamente
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Tenta encontrar JSON entre ```json e ```
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            json_str = content[start:end].strip()
            return json.loads(json_str)

        # Tenta encontrar JSON entre { e }
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            return json.loads(json_str)

        raise ValueError(
            f"Não foi possível extrair JSON da resposta: {content[:200]}..."
        )


class GeminiClient(LLMClient):
    """Cliente para Google Gemini API"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self.genai = genai
            self._model = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError(
                "google-generativeai não instalado. "
                "Execute: pip install google-generativeai"
            )

    def call(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        start_time = time.time()

        try:
            generation_config = self.genai.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens, **kwargs
            )

            # Safety settings para evitar bloqueios
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]

            response = self._model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            latency = time.time() - start_time

            # Extrai tokens usados (se disponível)
            tokens_used = None
            if hasattr(response, "usage_metadata"):
                tokens_used = response.usage_metadata.total_token_count

            return LLMResponse(
                content=response.text,
                provider="gemini",
                model=self.model,
                tokens_used=tokens_used,
                latency=latency,
                success=True,
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider="gemini",
                model=self.model,
                latency=time.time() - start_time,
                success=False,
                error=str(e),
            )

    def call_json(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000, **kwargs
    ) -> Dict[str, Any]:
        response = self.call(prompt, temperature, max_tokens, **kwargs)

        if not response.success:
            raise RuntimeError(f"Erro ao chamar Gemini: {response.error}")

        return self._parse_json_response(response.content)


class GroqClient(LLMClient):
    """Cliente para Groq API (agregador com modelos rápidos e gratuitos)"""

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=api_key, base_url="https://api.groq.com/openai/v1"
            )
        except ImportError:
            raise ImportError("openai não instalado. Execute: pip install openai")

    def call(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            return LLMResponse(
                content=content,
                provider="groq",
                model=self.model,
                tokens_used=tokens_used,
                latency=latency,
                success=True,
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider="groq",
                model=self.model,
                latency=time.time() - start_time,
                success=False,
                error=str(e),
            )

    def call_json(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000, **kwargs
    ) -> Dict[str, Any]:
        response = self.call(prompt, temperature, max_tokens, **kwargs)

        if not response.success:
            raise RuntimeError(f"Erro ao chamar Groq: {response.error}")

        return self._parse_json_response(response.content)


class OpenRouterClient(LLMClient):
    """Cliente para OpenRouter API (agregador com tier gratuito)"""

    def __init__(
        self, api_key: str, model: str = "google/gemma-2-9b-it:free", **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=api_key, base_url="https://openrouter.ai/api/v1"
            )
        except ImportError:
            raise ImportError("openai não instalado. Execute: pip install openai")

    def call(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, **kwargs
    ) -> LLMResponse:
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            latency = time.time() - start_time
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            return LLMResponse(
                content=content,
                provider="openrouter",
                model=self.model,
                tokens_used=tokens_used,
                latency=latency,
                success=True,
            )

        except Exception as e:
            return LLMResponse(
                content="",
                provider="openrouter",
                model=self.model,
                latency=time.time() - start_time,
                success=False,
                error=str(e),
            )

    def call_json(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000, **kwargs
    ) -> Dict[str, Any]:
        response = self.call(prompt, temperature, max_tokens, **kwargs)

        if not response.success:
            raise RuntimeError(f"Erro ao chamar OpenRouter: {response.error}")

        return self._parse_json_response(response.content)


class LLMFactory:
    """Factory para criar instâncias de LLMClient"""

    _clients = {
        "gemini": GeminiClient,
        "groq": GroqClient,
        "openrouter": OpenRouterClient,
    }

    @classmethod
    def create(
        cls,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> LLMClient:
        """
        Cria um cliente LLM baseado no provedor

        Args:
            provider: Nome do provedor ('gemini', 'deepseek', 'grok')
            api_key: Chave de API (se None, busca de variável de ambiente)
            model: Nome do modelo (se None, usa padrão do provedor)
            **kwargs: Parâmetros adicionais específicos do provedor

        Returns:
            Instância de LLMClient

        Raises:
            ValueError: Se provedor desconhecido
            ValueError: Se API key não fornecida
        """
        provider = provider.lower()

        if provider not in cls._clients:
            available = ", ".join(cls._clients.keys())
            raise ValueError(
                f"Provedor '{provider}' desconhecido. " f"Disponíveis: {available}"
            )

        # Busca API key de variável de ambiente se não fornecida
        if api_key is None:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_var)

            if api_key is None:
                raise ValueError(
                    f"API key não fornecida e variável de ambiente "
                    f"{env_var} não encontrada"
                )

        # Define modelos padrão
        default_models = {
            "gemini": "gemini-2.0-flash-lite",
            "groq": "llama-3.3-70b-versatile",
            "openrouter": "deepseek/deepseek-chat-v3-0324:free",
        }

        if model is None:
            model = default_models.get(provider)

        client_class = cls._clients[provider]
        return client_class(api_key=api_key, model=model, **kwargs)

    @classmethod
    def register_provider(cls, name: str, client_class: type):
        """
        Registra um novo provedor de LLM

        Args:
            name: Nome do provedor
            client_class: Classe que implementa LLMClient
        """
        if not issubclass(client_class, LLMClient):
            raise TypeError("client_class deve herdar de LLMClient")

        cls._clients[name.lower()] = client_class


def get_default_llm() -> LLMClient:
    """
    Retorna o cliente LLM padrão configurado via variáveis de ambiente

    Prioridade:
    1. DEFAULT_LLM_PROVIDER (variável de ambiente)
    2. Gemini (se GEMINI_API_KEY disponível)
    3. Groq (se GROQ_API_KEY disponível)
    4. OpenRouter (se OPENROUTER_API_KEY disponível)

    Returns:
        Instância de LLMClient

    Raises:
        RuntimeError: Se nenhum provedor configurado
    """
    default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()

    # Tenta usar provedor padrão
    try:
        return LLMFactory.create(default_provider)
    except ValueError:
        pass

    # Fallback: tenta provedores na ordem de prioridade
    for provider in ["gemini", "groq", "openrouter"]:
        try:
            return LLMFactory.create(provider)
        except ValueError:
            continue

    raise RuntimeError(
        "Nenhum provedor LLM configurado. "
        "Configure pelo menos uma das variáveis de ambiente: "
        "GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY"
    )
