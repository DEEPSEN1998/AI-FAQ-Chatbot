from typing import Dict, List, Optional

from backend.app.config import ENABLE_NVIDIA, ENABLE_OLLAMA
from backend.app.llm.base import BaseLLMProvider, ProviderInfo
from backend.app.llm.nvidia_provider import NVIDIAProvider
from backend.app.llm.ollama_provider import OllamaProvider


class ProviderRegistry:
    """
    Registry managing all active LLM Providers in the application.
    Follows Open/Closed Principle: New providers can be registered without modifying existing pipeline code.
    """

    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        # Register default providers
        self.register(OllamaProvider())
        self.register(NVIDIAProvider())

    def register(self, provider: BaseLLMProvider) -> None:
        """Register a new LLM provider."""
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[BaseLLMProvider]:
        """Get provider instance by ID."""
        return self._providers.get(provider_id.lower())

    def list_providers(self) -> List[ProviderInfo]:
        """Build provider discovery structure respecting configuration flags."""
        info_list: List[ProviderInfo] = []
        for p in self._providers.values():
            if p.provider_id == "ollama" and not ENABLE_OLLAMA:
                continue
            if p.provider_id == "nvidia" and not ENABLE_NVIDIA:
                continue
            info_list.append(
                ProviderInfo(
                    id=p.provider_id,
                    name=p.provider_name,
                    online=p.is_online(),
                    models=p.get_available_models(),
                )
            )
        return info_list


# Singleton registry instance
provider_registry = ProviderRegistry()
