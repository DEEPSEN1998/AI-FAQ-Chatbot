import json
from typing import Iterator, List, Optional
import requests

from backend.app.config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL, mask_key
from backend.app.llm.base import BaseLLMProvider, ModelInfo


class NVIDIAProvider(BaseLLMProvider):
    """
    NVIDIA NIM Cloud LLM Provider.
    Connects to NVIDIA NIM OpenAI-compatible API endpoint with API key authentication & SSE streaming.
    """

    APPROVED_MODELS = [
        ModelInfo(id="meta/llama-3.3-70b-instruct", name="Llama 3.3 70B Instruct"),
        ModelInfo(id="mistralai/mistral-medium-3.1", name="Mistral Medium 3.1"),
        ModelInfo(id="deepseek-ai/deepseek-r1", name="DeepSeek R1 Cloud"),
        ModelInfo(id="qwen/qwen3-235b", name="Qwen 3 235B"),
    ]

    def __init__(
        self,
        api_key: str = NVIDIA_API_KEY,
        base_url: str = NVIDIA_BASE_URL,
        default_model: str = NVIDIA_MODEL,
    ):
        self.api_key = (api_key or "").strip()
        self.base_url = (base_url or "").rstrip("/")
        self.default_model = default_model

        if self.api_key:
            print(f"✅ [NVIDIAProvider] Initialized with API Key: {mask_key(self.api_key)}")
        else:
            print("⚠️ [NVIDIAProvider] Initialized without API Key. Chat requests will prompt for configuration.")

    @property
    def provider_id(self) -> str:
        return "nvidia"

    @property
    def provider_name(self) -> str:
        return "NVIDIA NIM (Cloud)"

    def is_online(self) -> bool:
        """Check if NVIDIA API Key is present."""
        return bool(self.api_key and not self.api_key.startswith("xxxx"))

    def get_available_models(self) -> List[ModelInfo]:
        """Return list of approved NVIDIA NIM models."""
        return self.APPROVED_MODELS

    def _validate_api_key(self):
        if not self.api_key:
            raise RuntimeError(
                "NVIDIA API Key is missing. Please set NVIDIA_API_KEY in backend/.env with your key from build.nvidia.com."
            )

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024,
    ) -> str:
        self._validate_api_key()

        selected_model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": selected_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            elif res.status_code == 401:
                raise RuntimeError("NVIDIA API Key authentication failed (HTTP 401). Please check NVIDIA_API_KEY in backend/.env.")
            elif res.status_code == 429:
                raise RuntimeError("NVIDIA NIM API rate limit exceeded (HTTP 429). Please try again later.")
            else:
                raise RuntimeError(f"NVIDIA API Error (HTTP {res.status_code}): {res.text}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to NVIDIA NIM endpoint: {str(e)}")

    def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1024,
    ) -> Iterator[str]:
        if not self.api_key:
            yield "❌ Error: NVIDIA API Key is missing. Please configure NVIDIA_API_KEY in backend/.env."
            return

        selected_model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": selected_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
            "stream": True,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            res = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
            if res.status_code == 401:
                yield "❌ Error: NVIDIA API Key authentication failed (HTTP 401). Please check NVIDIA_API_KEY in backend/.env."
                return
            elif res.status_code == 429:
                yield "❌ Error: NVIDIA NIM API rate limit exceeded (HTTP 429). Please wait a moment."
                return
            elif res.status_code != 200:
                yield f"❌ Error: NVIDIA API returned HTTP {res.status_code}."
                return

            for line in res.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        content = line_str[6:].strip()
                        if content == "[DONE]":
                            break
                        try:
                            chunk = json.loads(content)
                            delta = chunk["choices"][0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue
        except requests.exceptions.RequestException as e:
            yield f"❌ Error connecting to NVIDIA NIM API: {str(e)}"
