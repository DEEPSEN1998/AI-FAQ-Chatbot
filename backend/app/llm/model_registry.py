from typing import Dict, List, Optional
from pydantic import BaseModel

from backend.app.config import ENABLE_NVIDIA, ENABLE_OLLAMA
from backend.app.llm.registry import provider_registry


class RegisteredModel(BaseModel):
    id: str
    display_name: str
    provider: str
    category: str  # "Local" or "Cloud"
    supports_streaming: bool = True
    online: bool = True


class ModelRegistry:
    """
    Central Model Registry mapping model IDs to their respective providers & metadata.
    Respects system configuration flags (ENABLE_OLLAMA, ENABLE_NVIDIA).
    """

    def get_all_models(self) -> List[RegisteredModel]:
        """
        Dynamically aggregate models across enabled registered providers.
        """
        models: List[RegisteredModel] = []

        # 1. Discover Ollama Local models (Only if ENABLE_OLLAMA=true)
        if ENABLE_OLLAMA:
            ollama = provider_registry.get_provider("ollama")
            if ollama:
                ollama_online = ollama.is_online()
                for m in ollama.get_available_models():
                    models.append(
                        RegisteredModel(
                            id=m.id,
                            display_name=m.name,
                            provider="ollama",
                            category="Local",
                            supports_streaming=True,
                            online=ollama_online,
                        )
                    )

        # 2. Discover NVIDIA NIM Cloud models (Only if ENABLE_NVIDIA=true)
        if ENABLE_NVIDIA:
            nvidia = provider_registry.get_provider("nvidia")
            if nvidia:
                nvidia_online = nvidia.is_online()
                for m in nvidia.get_available_models():
                    models.append(
                        RegisteredModel(
                            id=m.id,
                            display_name=m.name,
                            provider="nvidia",
                            category="Cloud",
                            supports_streaming=True,
                            online=nvidia_online,
                        )
                    )

        return models

    def get_model(self, model_id: str) -> Optional[RegisteredModel]:
        """Look up a specific registered model by ID."""
        for m in self.get_all_models():
            if m.id == model_id:
                return m
        return None

    def get_provider_id_for_model(self, model_id: Optional[str]) -> str:
        """
        Automatically resolve provider ID from model ID based on enabled providers.
        """
        if model_id:
            m = self.get_model(model_id)
            if m:
                return m.provider

        # Fallback to enabled provider
        if ENABLE_NVIDIA:
            return "nvidia"
        elif ENABLE_OLLAMA:
            return "ollama"

        return "nvidia"


# Singleton Model Registry instance
model_registry = ModelRegistry()
