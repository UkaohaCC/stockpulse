"""
Stock data scraper using Yahoo Finance API and Finviz.
"""

import re
import json
import time
from datetime import datetime
from typing import Any

import requests

from .base_scraper import BaseScraper
from config.settings import settings
from src.utils.logger import get_logger


class StockScraper(BaseScraper):
    """Scrapes stock data from Yahoo Finance API and Finviz."""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("StockScraper")
        self._yahoo_api = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        self._yahoo_api2 = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
        self._yahoo_quote_api = "https://query1.finance.yahoo.com/v7/finance/quote"

    def scrape(self, symbol: str) -> dict[str, Any]:
        """Scrape comprehensive stock data for a given symbol."""
        self.logger.info(f"Scraping data for {symbol}")

        data = {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
        }

        yahoo_data = self._scrape_yahoo_api(symbol)
        if yahoo_data:
            data.update(yahoo_data)

        if not data.get("price"):
            finviz_data = self._scrape_finviz(symbol)
            if finviz_data:
                data.update(finviz_data)

        data.setdefault("price", None)
        data.setdefault("change", None)
        data.setdefault("change_percent", None)
        data.setdefault("volume", None)
        data.setdefault("market_cap", None)
        data.setdefault("name", symbol.upper())

        self.logger.info(
            f"  {symbol}: price=${data.get('price')} "
            f"change={data.get('change_percent')}%"
        )
        return data

    def _scrape_yahoo_api(self, symbol: str) -> dict[str, Any] | None:
        """
        Use Yahoo Finance JSON API — much more reliable than HTML scraping.
        Endpoint: query1.finance.yahoo.com/v8/finance/chart/{symbol}
        """
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://finance.yahoo.com/",
        }

       
        for base_url in [self._yahoo_api, self._yahoo_api2]:
            try:
                url = base_url.format(symbol=symbol)
                params = {
                    "interval": "1d",
                    "range": "1d",
                    "includePrePost": "false",
                    "corsDomain": "finance.yahoo.com",
                }

                self._rate_limit()
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=settings.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                json_data = response.json()

                result = json_data.get("chart", {}).get("result", [])
                if not result:
                    self.logger.warning(f"No API result for {symbol}")
                    continue

                result = result[0]
                meta = result.get("meta", {})

                data = {}
                data["name"] = meta.get("shortName") or meta.get("longName") or symbol
                data["price"] = meta.get("regularMarketPrice")
                data["prev_close"] = meta.get("previousClose") or meta.get("chartPreviousClose")
                data["volume"] = meta.get("regularMarketVolume")
                data["market_cap"] = None  # Not in chart API
                data["currency"] = meta.get("currency", "USD")

                # Calculate change
                if data["price"] and data["prev_close"]:
                    data["change"] = round(data["price"] - data["prev_close"], 4)
                    data["change_percent"] = round(
                        (data["change"] / data["prev_close"]) * 100, 4
                    )
                else:
                    data["change"] = None
                    data["change_percent"] = None

                # Day range from indicators
                indicators = result.get("indicators", {})
                quote_list = indicators.get("quote", [{}])
                if quote_list:
                    q = quote_list[0]
                    highs = [h for h in q.get("high", []) if h is not None]
                    lows = [l for l in q.get("low", []) if l is not None]
                    opens = [o for o in q.get("open", []) if o is not None]
                    vols = [v for v in q.get("volume", []) if v is not None]

                    data["day_high"] = max(highs) if highs else None
                    data["day_low"] = min(lows) if lows else None
                    data["open_price"] = opens[0] if opens else None
                    if vols:
                        data["volume"] = vols[-1]

                self.logger.debug(f"Yahoo API success for {symbol}: ${data.get('price')}")
                return data

            except requests.exceptions.HTTPError as e:
                self.logger.warning(f"Yahoo API HTTP error for {symbol}: {e}")
                continue
            except Exception as e:
                self.logger.warning(f"Yahoo API error for {symbol}: {e}")
                continue

        return None

    def _scrape_yahoo_quote_api(self, symbol: str) -> dict[str, Any] | None:
        """
        Alternative: Yahoo Finance v7 quote API.
        Returns more detailed data including market cap, PE ratio etc.
        """
        try:
            headers = {
                "User-Agent": settings.USER_AGENT,
                "Accept": "application/json",
                "Referer": "https://finance.yahoo.com/",
            }
            params = {
                "symbols": symbol,
                "fields": ",".join([
                    "regularMarketPrice",
                    "regularMarketChange",
                    "regularMarketChangePercent",
                    "regularMarketVolume",
                    "marketCap",
                    "trailingPE",
                    "epsTrailingTwelveMonths",
                    "fiftyTwoWeekHigh",
                    "fiftyTwoWeekLow",
                    "regularMarketDayHigh",
                    "regularMarketDayLow",
                    "regularMarketOpen",
                    "regularMarketPreviousClose",
                    "averageDailyVolume3Month",
                    "beta",
                    "dividendYield",
                    "shortName",
                    "longName",
                    "sector",
                    "industry",
                ]),
            }

            self._rate_limit()
            response = self.session.get(
                self._yahoo_quote_api,
                params=params,
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            json_data = response.json()

            quotes = json_data.get("quoteResponse", {}).get("result", [])
            if not quotes:
                return None

            q = quotes[0]
            data = {
                "name": q.get("shortName") or q.get("longName") or symbol,
                "price": q.get("regularMarketPrice"),
                "change": q.get("regularMarketChange"),
                "change_percent": q.get("regularMarketChangePercent"),
                "volume": q.get("regularMarketVolume"),
                "market_cap": q.get("marketCap"),
                "pe_ratio": q.get("trailingPE"),
                "eps": q.get("epsTrailingTwelveMonths"),
                "fifty_two_week_high": q.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": q.get("fiftyTwoWeekLow"),
                "day_high": q.get("regularMarketDayHigh"),
                "day_low": q.get("regularMarketDayLow"),
                "open_price": q.get("regularMarketOpen"),
                "prev_close": q.get("regularMarketPreviousClose"),
                "avg_volume": q.get("averageDailyVolume3Month"),
                "beta": q.get("beta"),
                "dividend_yield": q.get("dividendYield"),
                "sector": q.get("sector"),
                "industry": q.get("industry"),
            }
            return data

        except Exception as e:
            self.logger.warning(f"Yahoo quote API error for {symbol}: {e}")
            return None

    def _scrape_finviz(self, symbol: str) -> dict[str, Any] | None:
        """Scrape stock data from Finviz as fallback."""
        url = settings.FINVIZ_QUOTE.format(symbol=symbol)
        soup = self.fetch_page(url)

        if not soup:
            return None

        data = {}
        try:
            table = soup.find("table", class_="snapshot-table2")
            if not table:
                table = soup.find("table", {"class": re.compile("snapshot")})

            if table:
                rows = table.find_all("tr")
                metrics = {}
                for row in rows:
                    cells = row.find_all("td")
                    for i in range(0, len(cells) - 1, 2):
                        key = cells[i].text.strip()
                        val = cells[i + 1].text.strip()
                        metrics[key] = val

                data["price"] = self._parse_number(metrics.get("Price"))
                data["change_percent"] = self._parse_number(
                    str(metrics.get("Change", "")).replace("%", "")
                )
                data["volume"] = self._parse_number(
                    str(metrics.get("Volume", "")).replace(",", "")
                )
                data["market_cap"] = self._parse_market_cap(metrics.get("Market Cap", ""))
                data["pe_ratio"] = self._parse_number(metrics.get("P/E"))
                data["eps"] = self._parse_number(metrics.get("EPS (ttm)"))
                data["beta"] = self._parse_number(metrics.get("Beta"))
                data["avg_volume"] = self._parse_number(
                    str(metrics.get("Avg Volume", "")).replace(",", "")
                )
                data["dividend_yield"] = self._parse_number(
                    str(metrics.get("Dividend %", "")).replace("%", "")
                )
                data["rsi"] = self._parse_number(metrics.get("RSI (14)"))
                data["target_price"] = self._parse_number(metrics.get("Target Price"))
                data["sector"] = metrics.get("Sector")
                data["industry"] = metrics.get("Industry")

                week_range = metrics.get("52W Range", "")
                if " - " in week_range:
                    parts = week_range.split(" - ")
                    data["fifty_two_week_low"] = self._parse_number(parts[0].strip())
                    data["fifty_two_week_high"] = self._parse_number(parts[1].strip())

            name_el = soup.find("a", class_="tab-link")
            if name_el:
                data["name"] = name_el.text.strip()

        except Exception as e:
            self.logger.warning(f"Error scraping Finviz for {symbol}: {e}")

        return data

    def scrape_multiple(self, symbols: list[str]) -> list[dict[str, Any]]:
        """Scrape data for multiple stock symbols."""
        results = []
        for symbol in symbols:
            try:
                data = self.scrape(symbol.strip().upper())
                results.append(data)
            except Exception as e:
                self.logger.error(f"Failed to scrape {symbol}: {e}")
                results.append({
                    "symbol": symbol.upper(),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })
        return results

    @staticmethod
    def _parse_number(value) -> float | None:
        """Parse string to float."""
        if value is None or value in ("N/A", "-", "", "nan"):
            return None
        try:
            return float(str(value).replace(",", "").replace("$", "").replace("+", "").strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_market_cap(value) -> float | None:
        """Parse market cap strings like 2.5T, 150B, 500M."""
        if not value or value in ("N/A", "-"):
            return None
        try:
            value = str(value).strip().replace("$", "").replace(",", "")
            multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
            for suffix, mult in multipliers.items():
                if value.upper().endswith(suffix):
                    return float(value[:-1]) * mult
            return float(value)
        except (ValueError, TypeError):
            return None

    def close(self) -> None:
        """Close the scraper session."""
        self.session.close()