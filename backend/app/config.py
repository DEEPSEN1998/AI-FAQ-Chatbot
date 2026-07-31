import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Prioritize backend/.env, fallback to project root .env
ENV_FILE = BACKEND_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = PROJECT_ROOT / ".env"

print(f"🔍 [CONFIG] Resolved .env path: {ENV_FILE.resolve()}")

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    print(f"✅ [CONFIG] Successfully loaded environment from: {ENV_FILE}")
else:
    print(f"⚠️ [CONFIG] Environment file not found at: {ENV_FILE}")

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
UPLOAD_DIR = PROJECT_ROOT / "uploads"

# Knowledge Base Configurations
KB_VERSION: str = "v1.0.0"

# Semantic Answer Cache Configurations
CACHE_COLLECTION_NAME: str = "answer_cache"
CACHE_DISTANCE_THRESHOLD: float = 0.25
CACHE_DEDUPLICATION_THRESHOLD: float = 0.08
CACHE_MAX_RESULTS: int = 1

# Provider Feature Flags
ENABLE_OLLAMA: bool = os.getenv("ENABLE_OLLAMA", "false").lower() == "true"
ENABLE_NVIDIA: bool = os.getenv("ENABLE_NVIDIA", "true").lower() == "true"

# Default LLM Provider
DEFAULT_LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia" if not ENABLE_OLLAMA else "ollama")

# Ollama Settings
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# NVIDIA NIM Settings
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "").strip()
NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")


def mask_key(key: str) -> str:
    """Mask key keeping only first 4 and last 4 characters visible."""
    if not key:
        return "❌ NOT SET (Empty)"
    if len(key) <= 8:
        return f"{key[:2]}...{key[-2:]} (Length: {len(key)})"
    return f"{key[:4]}...{key[-4:]}"


# Startup Diagnostics Log
print(f"ℹ️ [CONFIG] Active LLM Provider: {DEFAULT_LLM_PROVIDER}")
print(f"ℹ️ [CONFIG] Enable Ollama: {ENABLE_OLLAMA}")
print(f"ℹ️ [CONFIG] Enable NVIDIA: {ENABLE_NVIDIA}")
print(f"ℹ️ [CONFIG] NVIDIA Model: {NVIDIA_MODEL}")
print(f"ℹ️ [CONFIG] NVIDIA API Key: {mask_key(NVIDIA_API_KEY)}")

if ENABLE_NVIDIA and not NVIDIA_API_KEY:
    print(
        "\n"
        "======================================================================\n"
        "⚠️ [DIAGNOSTIC NOTICE] NVIDIA_API_KEY is missing or empty in backend/.env\n"
        "   File path: " + str(ENV_FILE.resolve()) + "\n"
        "   Reason: Line 11 in backend/.env currently reads: 'NVIDIA_API_KEY='\n"
        "   To fix: Paste your key from build.nvidia.com in backend/.env:\n"
        "   NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
        "======================================================================\n"
    )