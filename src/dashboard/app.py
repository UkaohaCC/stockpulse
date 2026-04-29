"""
Main Dash application factory.
creates and configures the Dash app with all layouts and callbacks.
"""

import dash
import dash_bootstrap_components as dbc

from config.settings import settings
from src.dashboard.layouts.main_layout import create_layout
from src.dashboard.callbacks.stock_callbacks import register_stock_callbacks
from src.dashboard.callbacks.market_callbacks import register_market_callbacks
from src.dashboard.callbacks.news_callbacks import register_news_callbacks
from src.utils.logger import get_logger

logger = get_logger("DashApp")


def create_app() -> dash.Dash:
    """Create and configure the Dash application."""

    external_stylesheets = [
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap",
    ]

    app = dash.Dash(
        __name__,
        external_stylesheets=external_stylesheets,
        title=f"{settings.APP_NAME} - Stock Dashboard",
        update_title="Updating...",
        suppress_callback_exceptions=True,
        assets_folder="../dashboard/assets",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {"name": "description", "content": "Real-time stock market dashboard"},
        ],
    )

    app.layout = create_layout()

    register_stock_callbacks(app)
    register_market_callbacks(app)
    register_news_callbacks(app)

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} initialized")
    return app