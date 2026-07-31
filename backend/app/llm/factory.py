from typing import Optional

from backend.app.config import DEFAULT_LLM_PROVIDER
from backend.app.llm.base import BaseLLMProvider
from backend.app.llm.model_registry import model_registry
from backend.app.llm.registry import provider_registry


class LLMFactory:
    """
    Factory for retrieving LLM Provider instances.
    Decouples application logic from specific vendors by automatically resolving providers from model IDs.
    """

    @staticmethod
    def get_provider_for_model(model_id: Optional[str] = None) -> BaseLLMProvider:
        """
        Automatically resolve and return the provider instance registered for the given model ID.
        """
        provider_id = model_registry.get_provider_id_for_model(model_id)
        provider = provider_registry.get_provider(provider_id)

        if not provider:
            provider = provider_registry.get_provider(DEFAULT_LLM_PROVIDER.lower())

        if not provider:
            raise ValueError(f"No valid LLM provider found for model '{model_id}'.")

        return provider

    @staticmethod
    def get_provider(provider_id: Optional[str] = None) -> BaseLLMProvider:
        """
        Get provider instance by explicit provider ID (or default).
        """
        selected_id = (provider_id or DEFAULT_LLM_PROVIDER).lower()
        provider = provider_registry.get_provider(selected_id)

        if not provider:
            fallback_id = DEFAULT_LLM_PROVIDER.lower()
            provider = provider_registry.get_provider(fallback_id)

        if not provider:
            raise ValueError(f"No valid LLM provider found for '{selected_id}'.")

        return provider
