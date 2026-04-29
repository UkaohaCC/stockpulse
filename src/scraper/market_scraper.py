"""
Market overview scraper.
"""

from datetime import datetime
from typing import Any

from .base_scraper import BaseScraper
from src.utils.logger import get_logger


class MarketScraper(BaseScraper):
    """Scrapes broad market data and indices."""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("MarketScraper")

    def scrape(self) -> dict[str, Any]:
        """Scrape overall market data."""
        self.logger.info("Scraping market overview data")
        return {
            "timestamp": datetime.now().isoformat(),
            "indices": self._scrape_indices(),
            "sectors": self._get_sector_performance(),
        }

    def _scrape_indices(self) -> list[dict[str, Any]]:
        """Scrape major market indices."""
        indices = []

        index_symbols = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
        }

        for symbol, name in index_symbols.items():
            try:
                url = f"https://finance.yahoo.com/quote/{symbol}"
                soup = self.fetch_page(url)

                if not soup:
                    continue

                index_data = {"symbol": symbol, "name": name}

                price_el = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
                if price_el:
                    try:
                        index_data["price"] = float(
                            (price_el.get("data-value") or price_el.text).replace(",", "")
                        )
                    except (ValueError, TypeError):
                        pass

                change_el = soup.find("fin-streamer", {"data-field": "regularMarketChange"})
                if change_el:
                    try:
                        index_data["change"] = float(
                            (change_el.get("data-value") or change_el.text).replace(",", "")
                        )
                    except (ValueError, TypeError):
                        pass

                pct_el = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent"})
                if pct_el:
                    try:
                        val = (pct_el.get("data-value") or pct_el.text)
                        val = str(val).replace("(", "").replace(")", "").replace("%", "").replace(",", "")
                        index_data["change_percent"] = float(val)
                    except (ValueError, TypeError):
                        pass

                indices.append(index_data)

            except Exception as e:
                self.logger.warning(f"Error scraping index {name}: {e}")

        return indices

    def _get_sector_performance(self) -> list[dict[str, Any]]:
        """Get sector ETF performance."""
        sector_etfs = {
            "XLK": "Technology",
            "XLF": "Financial",
            "XLV": "Healthcare",
            "XLE": "Energy",
            "XLY": "Consumer Disc.",
            "XLP": "Consumer Staples",
            "XLI": "Industrial",
            "XLB": "Materials",
            "XLU": "Utilities",
            "XLRE": "Real Estate",
            "XLC": "Communications",
        }

        sectors = []
        for etf, sector_name in sector_etfs.items():
            try:
                url = f"https://finance.yahoo.com/quote/{etf}"
                soup = self.fetch_page(url)

                if not soup:
                    continue

                sector_data = {"name": sector_name, "etf": etf}

                pct_el = soup.find("fin-streamer", {"data-field": "regularMarketChangePercent"})
                if pct_el:
                    try:
                        val = (pct_el.get("data-value") or pct_el.text)
                        val = str(val).replace("(", "").replace(")", "").replace("%", "")
                        sector_data["change_percent"] = float(val)
                    except (ValueError, TypeError):
                        sector_data["change_percent"] = 0.0

                sectors.append(sector_data)

            except Exception as e:
                self.logger.warning(f"Error scraping sector {sector_name}: {e}")

        return sectors

    def close(self) -> None:
        """Close the scraper session."""
        self.session.close()