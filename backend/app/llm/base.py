from abc import ABC, abstractmethod
from typing import Iterator, List, Optional
from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    name: str


class ProviderInfo(BaseModel):
    id: str
    name: str
    online: bool
    models: List[ModelInfo]


class BaseLLMProvider(ABC):
    """
    Abstract base interface for all LLM providers (Ollama, NVIDIA NIM, OpenAI, Groq, Anthropic, etc.).
    Follows SOLID principles (Interface Segregation & Open/Closed principle).
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g. 'ollama', 'nvidia')."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Display name (e.g. 'Ollama (Local)', 'NVIDIA NIM')."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Fetch list of available models for this provider."""
        pass

    @abstractmethod
    def is_online(self) -> bool:
        """Check if provider service or API key is valid and online."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Synchronously generate complete response string."""
        pass

    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Stream generated response tokens chunk by chunk."""
        pass
