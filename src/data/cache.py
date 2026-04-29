"""
In-memory caching layer to reduce scraping frequency.
"""

import time
from typing import Any
from cachetools import TTLCache

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("Cache")


class DataCache:
    """Thread-safe TTL cache for scraped data."""

    def __init__(self, maxsize: int | None = None, ttl: int | None = None):
        self._cache = TTLCache(
            maxsize=maxsize or settings.CACHE_MAX_SIZE,
            ttl=ttl or settings.CACHE_TTL,
        )
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
            return value
        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set a value in cache."""
        self._cache[key] = value

    def get_or_set(self, key: str, func, *args, **kwargs) -> Any:
        """Get from cache or compute and cache."""
        value = self.get(key)
        if value is not None:
            return value
        value = func(*args, **kwargs)
        self.set(key, value)
        return value

    def invalidate(self, key: str) -> None:
        """Remove a key from cache."""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{(self._hits / total * 100):.1f}%" if total > 0 else "N/A",
            "size": len(self._cache),
            "maxsize": self._cache.maxsize,
        }