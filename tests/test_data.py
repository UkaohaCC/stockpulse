"""
Tests for data layer modules.
"""

import pytest
from datetime import datetime

from src.data.database import DatabaseManager
from src.data.cache import DataCache


class TestDatabase:
    """Test suite for DatabaseManager."""

    def setup_method(self):
        self.db = DatabaseManager(url="sqlite:///:memory:")

    def test_save_and_get_quote(self):
        """Test saving and retrieving a quote."""
        data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.0,
            "change": 2.5,
            "change_percent": 1.69,
            "volume": 1000000,
            "market_cap": 2.5e12,
        }
        self.db.save_stock_quote(data)
        result = self.db.get_latest_quote("AAPL")

        assert result is not None
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.0

    def test_get_nonexistent_quote(self):
        """Test getting a quote that doesn't exist."""
        result = self.db.get_latest_quote("ZZZZZ")
        assert result is None

    def test_save_multiple_quotes(self):
        """Test saving multiple quotes."""
        data_list = [
            {"symbol": "AAPL", "price": 150.0},
            {"symbol": "GOOGL", "price": 140.0},
        ]
        self.db.save_stock_quotes(data_list)

        results = self.db.get_latest_quotes(["AAPL", "GOOGL"])
        assert len(results) == 2

    def test_save_news(self):
        """Test saving news articles."""
        articles = [
            {
                "symbol": "AAPL",
                "title": "Test article",
                "url": "https://example.com",
                "source": "Test",
            }
        ]
        self.db.save_news(articles)
        news = self.db.get_news("AAPL")
        assert len(news) == 1
        assert news[0]["title"] == "Test article"

    def test_no_duplicate_news(self):
        """Test that duplicate news articles are not saved."""
        article = {
            "symbol": "AAPL",
            "title": "Duplicate article",
            "url": "https://example.com",
            "source": "Test",
        }
        self.db.save_news([article])
        self.db.save_news([article])
        news = self.db.get_news("AAPL")
        assert len(news) == 1


class TestDataCache:
    """Test suite for DataCache."""

    def setup_method(self):
        self.cache = DataCache(maxsize=10, ttl=60)

    def test_set_and_get(self):
        """Test basic set and get."""
        self.cache.set("key1", "value1")
        assert self.cache.get("key1") == "value1"

    def test_get_missing_key(self):
        """Test getting a non-existent key."""
        assert self.cache.get("nonexistent") is None

    def test_invalidate(self):
        """Test invalidating a key."""
        self.cache.set("key1", "value1")
        self.cache.invalidate("key1")
        assert self.cache.get("key1") is None

    def test_clear(self):
        """Test clearing the cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    def test_stats(self):
        """Test cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("key2")  # miss

        stats = self.cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_get_or_set(self):
        """Test get_or_set convenience method."""
        result = self.cache.get_or_set("key1", lambda: "computed")
        assert result == "computed"

        result = self.cache.get_or_set("key1", lambda: "recomputed")
        assert result == "computed"