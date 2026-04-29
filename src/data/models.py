"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockQuote(Base):
    """Stores individual stock quote snapshots."""
    __tablename__ = "stock_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    name = Column(String(200))
    price = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float)
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    day_high = Column(Float)
    day_low = Column(Float)
    open_price = Column(Float)
    prev_close = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_two_week_low = Column(Float)
    avg_volume = Column(Float)
    beta = Column(Float)
    dividend_yield = Column(Float)
    eps = Column(Float)
    rsi = Column(Float)
    target_price = Column(Float)
    sector = Column(String(100))
    industry = Column(String(200))
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<StockQuote(symbol={self.symbol}, price={self.price}, time={self.scraped_at})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class NewsArticle(Base):
    """Stores scraped news articles."""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    title = Column(String(500))
    url = Column(Text)
    source = Column(String(100))
    date = Column(String(20))
    time = Column(String(20))
    scraped_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NewsArticle(symbol={self.symbol}, title={self.title[:50]})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MarketIndex(Base):
    """Stores market index snapshots."""
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    price = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<MarketIndex(name={self.name}, price={self.price})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}