"""
StockPulse - Entry Point
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import get_logger
from src.dashboard.app import create_app
from src.data.database import DatabaseManager
from src.scheduler import scheduler

logger = get_logger("Main")


def main():
    """Main entry point."""
    print(
        r"""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║      StockPulse v1.0                              ║
    ║   Real-time Stock Market Dashboard                ║
    ║                                                   ║
    ║   Powered by BeautifulSoup + Plotly Dash          ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    )

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Watchlist: {', '.join(settings.DEFAULT_WATCHLIST)}")
    logger.info(f"Scrape interval: {settings.SCRAPE_INTERVAL}s")

    # Clean start — delete old database
    db_path = Path("stockpulse.db")
    for f in [db_path, Path(f"{db_path}-wal"), Path(f"{db_path}-shm")]:
        if f.exists():
            f.unlink()
            logger.debug(f"Removed {f}")

    # Initialize database
    db = DatabaseManager()
    logger.info("Database initialized")

    logger.info("⏳ Seeding chart data — this takes ~30 seconds on first run...")
    scheduler.seed_historical_data()

   
    scheduler.start()
    logger.info(f"Background scraper running every {settings.SCRAPE_INTERVAL}s")

    app = create_app()

    logger.info(f"Dashboard at http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"\n   Dashboard: http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"   Charts ready with historical data!")
    print(f"    Live updates every {settings.SCRAPE_INTERVAL}s\n")

    app.run(
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=settings.APP_DEBUG,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()