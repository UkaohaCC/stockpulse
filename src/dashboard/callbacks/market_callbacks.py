"""
Market overview callbacks.
"""

from dash import Input, Output, html, no_update
import dash_bootstrap_components as dbc

from config.settings import settings
from src.scraper import MarketScraper
from src.data import DatabaseManager, DataCache
from src.utils.helpers import format_price, format_percentage, get_change_color, get_arrow
from src.utils.logger import get_logger

logger = get_logger("MarketCallbacks")
COLORS = settings.COLORS

from src.data import db, cache
market_scraper = MarketScraper()


def register_market_callbacks(app):
    """Register market-related callbacks."""

    @app.callback(
        Output("market-indices-container", "children"),
        Input("auto-refresh-interval", "n_intervals"),
    )
    def update_market_indices(n_intervals):
        """Update market indices display."""
        try:
            # ...check cache
            cached = cache.get("market_indices")
            if cached:
                return _render_indices(cached)
            indices = db.get_latest_indices()

            if not indices:
                
                try:
                    market_data = market_scraper.scrape()
                    indices = market_data.get("indices", [])
                    if indices:
                        db.save_market_indices(indices)
                except Exception as e:
                    logger.warning(f"Error scraping market data: {e}")
                    indices = _get_placeholder_indices()

            cache.set("market_indices", indices)
            return _render_indices(indices)

        except Exception as e:
            logger.error(f"Error in market indices update: {e}")
            return _render_indices(_get_placeholder_indices())


def _render_indices(indices: list[dict]) -> html.Div:
    """Render market indices as styled cards."""
    if not indices:
        return html.P(
            "Market data loading...",
            style={"color": COLORS["text_muted"], "textAlign": "center"},
        )

    items = []
    for idx in indices:
        name = idx.get("name", "Unknown")
        price = idx.get("price")
        change = idx.get("change")
        change_pct = idx.get("change_percent")

        color = get_change_color(change_pct)
        arrow = get_arrow(change_pct)

        items.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "12px 0",
                    "borderBottom": f"1px solid {COLORS['card_border']}",
                },
                children=[
                    html.Div(
                        children=[
                            html.Span(
                                name,
                                style={
                                    "color": COLORS["text"],
                                    "fontWeight": "600",
                                    "fontSize": "0.85rem",
                                },
                            ),
                        ]
                    ),
                    html.Div(
                        style={"textAlign": "right"},
                        children=[
                            html.Div(
                                f"{price:,.2f}" if price else "N/A",
                                style={
                                    "color": COLORS["text"],
                                    "fontWeight": "600",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "fontSize": "0.9rem",
                                },
                            ),
                            html.Span(
                                f"{arrow} {format_percentage(change_pct)}",
                                style={
                                    "color": color,
                                    "fontSize": "0.75rem",
                                    "fontWeight": "600",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                },
                            ),
                        ],
                    ),
                ],
            )
        )

    return html.Div(items)


def _get_placeholder_indices() -> list[dict]:
    """Return placeholder data when scraping fails."""
    return [
        {"name": "S&P 500", "symbol": "^GSPC", "price": None, "change": None, "change_percent": None},
        {"name": "Dow Jones", "symbol": "^DJI", "price": None, "change": None, "change_percent": None},
        {"name": "NASDAQ", "symbol": "^IXIC", "price": None, "change": None, "change_percent": None},
        {"name": "Russell 2000", "symbol": "^RUT", "price": None, "change": None, "change_percent": None},
        {"name": "VIX", "symbol": "^VIX", "price": None, "change": None, "change_percent": None},
    ]