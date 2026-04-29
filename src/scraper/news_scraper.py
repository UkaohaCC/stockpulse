"""
Financial news scraper.
"""

from datetime import datetime
from typing import Any

from .base_scraper import BaseScraper
from config.settings import settings
from src.utils.logger import get_logger


class NewsScraper(BaseScraper):
    """Scrapes financial news and headlines."""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("NewsScraper")

    def scrape(self, symbol: str) -> list[dict[str, Any]]:
        """Scrape news articles for a given stock symbol."""
        self.logger.info(f"Scraping news for {symbol}")
        articles = self._scrape_finviz_news(symbol)
        return articles[:20]

    def _scrape_finviz_news(self, symbol: str) -> list[dict[str, Any]]:
        """Scrape news from Finviz."""
        url = settings.FINVIZ_NEWS.format(symbol=symbol)
        soup = self.fetch_page(url)

        if not soup:
            return []

        articles = []
        try:
            news_table = soup.find("table", {"id": "news-table"})
            if not news_table:
                news_table = soup.find("table", class_="fullview-news-outer")

            if not news_table:
                self.logger.warning(f"No news table found for {symbol}")
                return []

            rows = news_table.find_all("tr")
            current_date = datetime.now().strftime("%b-%d-%y")

            for row in rows:
                try:
                    cells = row.find_all("td")
                    if len(cells) < 2:
                        continue

                    datetime_text = cells[0].text.strip()
                    if len(datetime_text) > 8:
                        current_date = datetime_text.split(" ")[0]
                        time_str = " ".join(datetime_text.split(" ")[1:])
                    else:
                        time_str = datetime_text

                    link_el = cells[1].find("a")
                    if link_el:
                        title = link_el.text.strip()
                        url = link_el.get("href", "")
                        source_el = cells[1].find("span")
                        source = source_el.text.strip() if source_el else "Unknown"

                        articles.append({
                            "title": title,
                            "url": url,
                            "source": source,
                            "date": current_date,
                            "time": time_str,
                            "symbol": symbol.upper(),
                            "scraped_at": datetime.now().isoformat(),
                        })

                except Exception as e:
                    self.logger.debug(f"Error parsing news row: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Error scraping Finviz news for {symbol}: {e}")

        return articles

    def scrape_multiple(self, symbols: list[str]) -> dict[str, list[dict[str, Any]]]:
        """Scrape news for multiple symbols."""
        all_news = {}
        for symbol in symbols:
            try:
                news = self.scrape(symbol.strip().upper())
                all_news[symbol.upper()] = news
            except Exception as e:
                self.logger.error(f"Failed to scrape news for {symbol}: {e}")
                all_news[symbol.upper()] = []
        return all_news

    def close(self) -> None:
        """Close the scraper session."""
        self.session.close()