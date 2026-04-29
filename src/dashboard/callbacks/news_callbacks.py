"""
News-related dashboard callbacks.
"""

from dash import Input, Output, html, no_update

from config.settings import settings
from src.scraper import NewsScraper
from src.data import DatabaseManager, DataCache
from src.utils.logger import get_logger

logger = get_logger("NewsCallbacks")
COLORS = settings.COLORS

from src.data import db, cache
news_scraper = NewsScraper()


def register_news_callbacks(app):
    """Register news-related callbacks."""

    @app.callback(
        Output("news-container", "children"),
        [
            Input("selected-symbol-store", "data"),
            Input("auto-refresh-interval", "n_intervals"),
        ],
    )
    def update_news(selected_symbol, n_intervals):
        """Update news feed for selected symbol."""
        if not selected_symbol:
            return html.P("Select a stock to view news", style={"color": COLORS["text_muted"]})

        try:
            cache_key = f"news_{selected_symbol}"
            cached = cache.get(cache_key)
            if cached:
                return _render_news(cached, selected_symbol)

            articles = db.get_news(selected_symbol, limit=15)

            if not articles:
                try:
                    articles_raw = news_scraper.scrape(selected_symbol)
                    if articles_raw:
                        db.save_news(articles_raw)
                        articles = articles_raw
                except Exception as e:
                    logger.warning(f"Error scraping news for {selected_symbol}: {e}")

            cache.set(cache_key, articles)
            return _render_news(articles, selected_symbol)

        except Exception as e:
            logger.error(f"Error updating news: {e}")
            return html.P(
                "Unable to load news",
                style={"color": COLORS["text_muted"], "textAlign": "center"},
            )


def _render_news(articles: list[dict], symbol: str) -> html.Div:
    """Render news articles."""
    if not articles:
        return html.Div(
            style={"textAlign": "center", "padding": "40px 0"},
            children=[
                html.P("📰", style={"fontSize": "2rem", "marginBottom": "8px"}),
                html.P(
                    f"No news found for {symbol}",
                    style={"color": COLORS["text_muted"]},
                ),
                html.P(
                    "News will appear here as it's scraped",
                    style={"color": COLORS["text_muted"], "fontSize": "0.8rem"},
                ),
            ],
        )

    news_items = []
    for article in articles[:15]:
        title = article.get("title", "Untitled")
        url = article.get("url", "#")
        source = article.get("source", "Unknown")
        date = article.get("date", "")
        time_str = article.get("time", "")

        news_items.append(
            html.Div(
                className="news-item",
                children=[
                    html.A(
                        title,
                        href=url,
                        target="_blank",
                        rel="noopener noreferrer",
                        className="news-title",
                        style={
                            "color": COLORS["text"],
                            "textDecoration": "none",
                            "display": "block",
                            "lineHeight": "1.5",
                        },
                    ),
                    html.Div(
                        className="news-meta",
                        children=[
                            html.Span(
                                f"{source}",
                                style={
                                    "color": COLORS["primary"],
                                    "fontWeight": "600",
                                    "marginRight": "8px",
                                },
                            ),
                            html.Span(
                                f"{date} {time_str}",
                                style={"color": COLORS["text_muted"]},
                            ),
                        ],
                    ),
                ],
            )
        )

    return html.Div(news_items)