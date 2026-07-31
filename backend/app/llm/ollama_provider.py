import json
from typing import Iterator, List, Optional
import requests

from backend.app.config import OLLAMA_MODEL, OLLAMA_URL
from backend.app.llm.base import BaseLLMProvider, ModelInfo


class OllamaProvider(BaseLLMProvider):
    """
    Ollama Local LLM Provider.
    Dynamically discovers installed Ollama models and streams responses locally.
    """

    def __init__(self, base_url: str = OLLAMA_URL, default_model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def provider_id(self) -> str:
        return "ollama"

    @property
    def provider_name(self) -> str:
        return "Ollama (Local)"

    def is_online(self) -> bool:
        """Check if Ollama local service is running."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Dynamically discover models installed in Ollama."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=4)
            if res.status_code == 200:
                data = res.json()
                models = []
                for m in data.get("models", []):
                    name = m.get("name", m.get("model", "unknown"))
                    display_name = name.split(":")[0].replace("-", " ").title() + (
                        f" ({name.split(':')[1]})" if ":" in name else ""
                    )
                    models.append(ModelInfo(id=name, name=display_name))
                if models:
                    return models
        except Exception:
            pass

        # Fallback default models if offline or tag listing fails
        return [
            ModelInfo(id=self.default_model, name="Qwen 2.5 3B"),
            ModelInfo(id="llama3", name="Llama 3"),
            ModelInfo(id="deepseek-r1", name="DeepSeek R1"),
        ]

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        selected_model = model or self.default_model
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            res = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            if res.status_code == 200:
                return res.json().get("response", "").strip()
            elif res.status_code == 404:
                raise RuntimeError(f"Ollama model '{selected_model}' is not installed locally.")
            else:
                raise RuntimeError(f"Ollama HTTP {res.status_code}: {res.text}")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama server is not running locally. Please start Ollama or switch to NVIDIA NIM.")

    def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        selected_model = model or self.default_model
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature},
        }

        try:
            res = requests.post(f"{self.base_url}/api/generate", json=payload, stream=True, timeout=60)
            if res.status_code != 200:
                yield f"❌ Error: Ollama HTTP {res.status_code}. Is model '{selected_model}' pulled?"
                return

            for line in res.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    try:
                        chunk = json.loads(decoded)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                    except Exception:
                        continue
        except requests.exceptions.ConnectionError:
            yield "❌ Error: Ollama is not running locally. Please start Ollama or switch to NVIDIA NIM."
