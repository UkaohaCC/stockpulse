"""
Database manager for storing and retrieving scraped data.
"""

from datetime import datetime, timedelta
from typing import Any
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config.settings import settings
from src.data.models import Base, StockQuote, NewsArticle, MarketIndex
from src.utils.logger import get_logger

logger = get_logger("Database")


def _build_engine(url: str):
    """Build SQLAlchemy engine with correct settings for SQLite."""
    if "sqlite" in url:
        
        if "///" in url:
            db_path = url.split("///")[1]
        else:
            db_path = "stockpulse.db"

        db_path = Path(db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)

        db_path.touch(mode=0o664, exist_ok=True)

        logger.info(f"Database path: {db_path}")

        engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
            poolclass=StaticPool,
        )

        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=10000"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            conn.commit()

        return engine

    return create_engine(url, echo=False, pool_pre_ping=True)


class DatabaseManager:
    """Manages all database operations."""

    def __init__(self, url: str | None = None):
        self.engine = _build_engine(url or settings.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self._Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info("Database initialized")

    def get_session(self):
        """Get a new database session."""
        return self._Session()


    def save_stock_quote(self, data: dict[str, Any]) -> bool:
        """Save a stock quote to the database."""
        session = self.get_session()
        try:
            quote = StockQuote(
                symbol=data.get("symbol"),
                name=data.get("name"),
                price=data.get("price"),
                change=data.get("change"),
                change_percent=data.get("change_percent"),
                volume=data.get("volume"),
                market_cap=data.get("market_cap"),
                pe_ratio=data.get("pe_ratio"),
                day_high=data.get("day_high"),
                day_low=data.get("day_low"),
                open_price=data.get("open_price"),
                prev_close=data.get("prev_close"),
                fifty_two_week_high=data.get("fifty_two_week_high"),
                fifty_two_week_low=data.get("fifty_two_week_low"),
                avg_volume=data.get("avg_volume"),
                beta=data.get("beta"),
                dividend_yield=data.get("dividend_yield"),
                eps=data.get("eps"),
                rsi=data.get("rsi"),
                target_price=data.get("target_price"),
                sector=data.get("sector"),
                industry=data.get("industry"),
            )
            session.add(quote)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving quote for {data.get('symbol')}: {e}")
            return False
        finally:
            session.close()

    def save_stock_quotes(self, data_list: list[dict[str, Any]]) -> None:
        """Save multiple stock quotes."""
        for data in data_list:
            self.save_stock_quote(data)

    def get_latest_quote(self, symbol: str) -> dict | None:
        """Get the most recent quote for a symbol."""
        session = self.get_session()
        try:
            quote = (
                session.query(StockQuote)
                .filter(StockQuote.symbol == symbol.upper())
                .order_by(desc(StockQuote.scraped_at))
                .first()
            )
            return quote.to_dict() if quote else None
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
        finally:
            session.close()

    def get_latest_quotes(self, symbols: list[str]) -> list[dict]:
        """Get latest quotes for multiple symbols."""
        results = []
        for symbol in symbols:
            quote = self.get_latest_quote(symbol)
            if quote:
                results.append(quote)
        return results

    def get_price_history(self, symbol: str, hours: int = 24) -> pd.DataFrame:
        """Get price history for a symbol within the specified timeframe."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        session = self.get_session()
        try:
            quotes = (
                session.query(StockQuote)
                .filter(
                    StockQuote.symbol == symbol.upper(),
                    StockQuote.scraped_at >= cutoff,
                )
                .order_by(StockQuote.scraped_at)
                .all()
            )
            if not quotes:
                return pd.DataFrame()

            data = [q.to_dict() for q in quotes]
            df = pd.DataFrame(data)
            df["scraped_at"] = pd.to_datetime(df["scraped_at"])
            return df
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return pd.DataFrame()
        finally:
            session.close()


    def save_news(self, articles: list[dict[str, Any]]) -> None:
        """Save news articles, avoiding duplicates."""
        session = self.get_session()
        try:
            for article in articles:
                existing = (
                    session.query(NewsArticle)
                    .filter(
                        NewsArticle.title == article.get("title"),
                        NewsArticle.symbol == article.get("symbol"),
                    )
                    .first()
                )
                if not existing:
                    news = NewsArticle(
                        symbol=article.get("symbol"),
                        title=article.get("title"),
                        url=article.get("url"),
                        source=article.get("source"),
                        date=article.get("date"),
                        time=article.get("time"),
                    )
                    session.add(news)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving news: {e}")
        finally:
            session.close()

    def get_news(self, symbol: str, limit: int = 15) -> list[dict]:
        """Get recent news for a symbol."""
        session = self.get_session()
        try:
            articles = (
                session.query(NewsArticle)
                .filter(NewsArticle.symbol == symbol.upper())
                .order_by(desc(NewsArticle.scraped_at))
                .limit(limit)
                .all()
            )
            return [a.to_dict() for a in articles]
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []
        finally:
            session.close()


    def save_market_indices(self, indices: list[dict[str, Any]]) -> None:
        """Save market index data."""
        session = self.get_session()
        try:
            for idx in indices:
                market_idx = MarketIndex(
                    symbol=idx.get("symbol"),
                    name=idx.get("name"),
                    price=idx.get("price"),
                    change=idx.get("change"),
                    change_percent=idx.get("change_percent"),
                )
                session.add(market_idx)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving market indices: {e}")
        finally:
            session.close()

    def get_latest_indices(self) -> list[dict]:
        """Get the latest market index data."""
        session = self.get_session()
        try:
            results = []
            symbols = session.query(MarketIndex.symbol).distinct().all()
            for (symbol,) in symbols:
                idx = (
                    session.query(MarketIndex)
                    .filter(MarketIndex.symbol == symbol)
                    .order_by(desc(MarketIndex.scraped_at))
                    .first()
                )
                if idx:
                    results.append(idx.to_dict())
            return results
        except Exception as e:
            logger.error(f"Error getting indices: {e}")
            return []
        finally:
            session.close()


    def cleanup_old_data(self, days: int = 7) -> None:
        """Remove data older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        session = self.get_session()
        try:
            session.query(StockQuote).filter(StockQuote.scraped_at < cutoff).delete()
            session.query(NewsArticle).filter(NewsArticle.scraped_at < cutoff).delete()
            session.query(MarketIndex).filter(MarketIndex.scraped_at < cutoff).delete()
            session.commit()
            logger.info(f"Cleaned up data older than {days} days")
        except Exception as e:
            session.rollback()
            logger.error(f"Error cleaning up data: {e}")
        finally:
            session.close()