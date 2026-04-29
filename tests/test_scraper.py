"""
Tests for scraper modules.
"""

import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from src.scraper.stock_scraper import StockScraper
from src.scraper.news_scraper import NewsScraper
from src.scraper.base_scraper import BaseScraper


class TestStockScraper:
    """Test suite for StockScraper."""

    def setup_method(self):
        self.scraper = StockScraper()

    def teardown_method(self):
        self.scraper.close()

    def test_parse_number_valid(self):
        assert self.scraper._parse_number("123.45") == 123.45
        assert self.scraper._parse_number("1,234.56") == 1234.56
        assert self.scraper._parse_number("$99.99") == 99.99
        assert self.scraper._parse_number("+5.67") == 5.67

    def test_parse_number_invalid(self):
        assert self.scraper._parse_number(None) is None
        assert self.scraper._parse_number("N/A") is None
        assert self.scraper._parse_number("-") is None
        assert self.scraper._parse_number("") is None

    def test_parse_market_cap(self):
        assert self.scraper._parse_market_cap("2.5T") == 2.5e12
        assert self.scraper._parse_market_cap("150B") == 150e9
        assert self.scraper._parse_market_cap("500M") == 500e6
        assert self.scraper._parse_market_cap("$1.2B") == 1.2e9

    def test_parse_market_cap_invalid(self):
        assert self.scraper._parse_market_cap(None) is None
        assert self.scraper._parse_market_cap("N/A") is None
        assert self.scraper._parse_market_cap("-") is None

    def test_scrape_returns_dict(self):
        """Test that scrape returns a dict with expected keys."""
        with patch.object(self.scraper, '_scrape_yahoo', return_value={
            "price": 150.0,
            "change": 2.5,
            "change_percent": 1.69,
            "name": "Apple Inc.",
        }):
            with patch.object(self.scraper, '_scrape_finviz', return_value={}):
                result = self.scraper.scrape("AAPL")

        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert "price" in result
        assert "timestamp" in result

    def test_scrape_multiple(self):
        """Test scraping multiple symbols."""
        with patch.object(self.scraper, 'scrape', return_value={
            "symbol": "TEST",
            "price": 100.0,
            "timestamp": "2024-01-01",
        }):
            results = self.scraper.scrape_multiple(["AAPL", "GOOGL"])

        assert len(results) == 2
        assert all(isinstance(r, dict) for r in results)


class TestNewsScraper:
    """Test suite for NewsScraper."""

    def setup_method(self):
        self.scraper = NewsScraper()

    def teardown_method(self):
        self.scraper.close()

    def test_scrape_returns_list(self):
        """Test that news scrape returns a list."""
        with patch.object(self.scraper, '_scrape_finviz_news', return_value=[]):
            result = self.scraper.scrape("AAPL")
        assert isinstance(result, list)

    def test_scrape_multiple(self):
        """Test scraping news for multiple symbols."""
        with patch.object(self.scraper, 'scrape', return_value=[]):
            result = self.scraper.scrape_multiple(["AAPL", "GOOGL"])
        assert isinstance(result, dict)
        assert "AAPL" in result
        assert "GOOGL" in result