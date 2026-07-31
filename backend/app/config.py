from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
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