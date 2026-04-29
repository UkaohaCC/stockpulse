"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Central configuration for StockPulse."""

    # ..app
    APP_NAME: str = "StockPulse"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8050"))
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"

    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'stockpulse.db'}")

    SCRAPE_INTERVAL: int = int(os.getenv("SCRAPE_INTERVAL_SECONDS", "60"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    DEFAULT_WATCHLIST: list[str] = os.getenv(
        "DEFAULT_WATCHLIST", "AAPL,GOOGL,MSFT,AMZN,TSLA,META,NVDA,JPM"
    ).split(",")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(BASE_DIR / "stockpulse.log"))

    YAHOO_FINANCE_QUOTE: str = "https://finance.yahoo.com/quote/{symbol}"
    YAHOO_FINANCE_TRENDING: str = "https://finance.yahoo.com/trending-tickers"
    FINVIZ_QUOTE: str = "https://finviz.com/quote.ashx?t={symbol}&p=d"
    FINVIZ_NEWS: str = "https://finviz.com/quote.ashx?t={symbol}"
    MARKET_WATCH_URL: str = "https://www.marketwatch.com/investing/stock/{symbol}"

    CACHE_TTL: int = 30  # seconds
    CACHE_MAX_SIZE: int = 256

    DASHBOARD_REFRESH_MS: int = 30000  # 30 seconds

    # .....theme
    COLORS = {
        "background": "#0a0a1a",
        "card_bg": "#12122b",
        "card_border": "#1e1e3f",
        "primary": "#6366f1",
        "secondary": "#8b5cf6",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "text": "#e2e8f0",
        "text_muted": "#94a3b8",
        "accent": "#06b6d4",
    }


settings = Settings()