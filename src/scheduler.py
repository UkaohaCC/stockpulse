"""
Background scheduler that scrapes data at regular intervals.
Also seeds initial historical data so charts display immediately.
"""

import threading
import time
import random
from datetime import datetime, timedelta

from config.settings import settings
from src.scraper.stock_scraper import StockScraper
from src.data.database import DatabaseManager
from src.utils.logger import get_logger

logger = get_logger("Scheduler")


class DataScheduler:
    """Runs periodic scraping in background thread."""

    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = StockScraper()
        self.running = False
        self.thread = None
        self.interval = settings.SCRAPE_INTERVAL

    def start(self):
        """Start the background scraping loop."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="DataScheduler"
        )
        self.thread.start()
        logger.info(f"Scheduler started — scraping every {self.interval}s")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        logger.info("Scheduler stopped")

    def seed_historical_data(self):
        """
        Scrape current price once, then generate realistic historical
        data points so charts display immediately on startup.
        Creates ~60 data points spanning the last 2 hours.
        """
        logger.info("Seeding historical data for instant charts...")

        for symbol in settings.DEFAULT_WATCHLIST:
            try:
                # Get current real price
                data = self.scraper.scrape(symbol)
                current_price = data.get("price")

                if not current_price:
                    logger.warning(f"No price for {symbol}, skipping seed")
                    continue

                # Save current data point
                self.db.save_stock_quote(data)
                logger.info(f"  {symbol}: ${current_price:.2f} (live)")

                # Generate 59 historical points over last 2 hours
                # Realistic small fluctuations around current price
                now = datetime.utcnow()
                points = 59
                interval_seconds = (2 * 3600) / points  # spread over 2 hours

                price = current_price
                day_high = data.get("day_high") or current_price * 1.01
                day_low = data.get("day_low") or current_price * 0.99
                volume = data.get("volume") or 1000000

                for i in range(points, 0, -1):
                    # Time going backwards
                    timestamp = now - timedelta(seconds=i * interval_seconds)

                    # Random walk: small % change each step
                    change_pct = random.gauss(0, 0.0008)  # ~0.08% std dev per step
                    price = price * (1 + change_pct)

                    # Keep within day range
                    price = max(min(price, day_high * 1.005), day_low * 0.995)

                    historical = {
                        "symbol": symbol,
                        "name": data.get("name", symbol),
                        "price": round(price, 2),
                        "change": data.get("change"),
                        "change_percent": data.get("change_percent"),
                        "volume": int(volume * random.uniform(0.8, 1.2)),
                        "market_cap": data.get("market_cap"),
                        "pe_ratio": data.get("pe_ratio"),
                        "day_high": day_high,
                        "day_low": day_low,
                        "open_price": data.get("open_price"),
                        "prev_close": data.get("prev_close"),
                        "fifty_two_week_high": data.get("fifty_two_week_high"),
                        "fifty_two_week_low": data.get("fifty_two_week_low"),
                        "avg_volume": data.get("avg_volume"),
                        "beta": data.get("beta"),
                        "dividend_yield": data.get("dividend_yield"),
                        "eps": data.get("eps"),
                        "rsi": data.get("rsi"),
                        "target_price": data.get("target_price"),
                        "sector": data.get("sector"),
                        "industry": data.get("industry"),
                    }

                   
                    self._save_with_timestamp(historical, timestamp)

                logger.info(f"  {symbol}: seeded {points} historical points ")

            except Exception as e:
                logger.warning(f"Failed to seed {symbol}: {e}")

        logger.info("Historical data seeding complete ")

    def _save_with_timestamp(self, data: dict, timestamp: datetime):
        """Save a quote with a specific timestamp."""
        from src.data.models import StockQuote
        session = self.db.get_session()
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
                scraped_at=timestamp,
            )
            session.add(quote)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    def _run_loop(self):
        """Main loop — scrape all watchlist stocks periodically."""
        while self.running:
            try:
                self._scrape_all()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")

            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)

    def _scrape_all(self):
        """Scrape all watchlist stocks and save to database."""
        logger.info(f"Scheduled scrape at {datetime.now().strftime('%H:%M:%S')}")

        for symbol in settings.DEFAULT_WATCHLIST:
            try:
                data = self.scraper.scrape(symbol)
                self.db.save_stock_quote(data)
                logger.debug(f"Saved {symbol}: ${data.get('price', 'N/A')}")
            except Exception as e:
                logger.warning(f"Failed to scrape {symbol}: {e}")

        logger.info("Scheduled scrape complete ✅")


scheduler = DataScheduler()