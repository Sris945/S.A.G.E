"""Shared text embeddings for RAG and codebase indexing (Ollama + deterministic fallback)."""

from __future__ import annotations

import hashlib
import re

try:
    import ollama  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    ollama = None

from sage.llm.ollama_safe import embeddings_with_timeout

_EMBED_MODEL = "nomic-embed-text:latest"
_DIM = 64


def embed_text(text: str, *, timeout_s: float = 2.0) -> list[float]:
    """Return a fixed-size vector (64 dims) for similarity search."""
    if ollama is not None:
        try:
            vec = embeddings_with_timeout(model=_EMBED_MODEL, prompt=text, timeout_s=timeout_s)
            if isinstance(vec, list) and len(vec) == _DIM:
                return vec
        except Exception:
            pass
    vec = [0.0] * _DIM
    for tok in re.findall(r"[a-zA-Z0-9_]+", (text or "").lower()):
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        vec[h % _DIM] += 1.0
    return vec
