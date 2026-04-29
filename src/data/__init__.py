"""
Data package — exposes shared singleton instances.
"""

from .database import DatabaseManager
from .cache import DataCache

__all__ = ["DatabaseManager", "DataCache", "db", "cache"]

# Shared singletons — one instance for the whole app
db = DatabaseManager()
cache = DataCache()