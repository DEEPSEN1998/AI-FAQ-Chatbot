from dataclasses import dataclass, field
from typing import List


@dataclass
class CacheEntryMetadata:
    """
    Strongly-typed data structure representing lightweight metadata
    stored alongside an answer cache vector entry.
    """

    cache_id: str
    question: str
    answer: str
    kb_version: str
    timestamp: str
    hit_count: int = 1
    source_files: List[str] = field(default_factory=list)
    chunk_ids: List[str] = field(default_factory=list)


@dataclass
class CacheResult:
    """
    Strongly-typed result returned upon a successful semantic cache lookup hit.
    """

    question: str
    answer: str
    score: float
    timestamp: str
    hit_count: int
    kb_version: str
    source_files: List[str] = field(default_factory=list)
    chunk_ids: List[str] = field(default_factory=list)
