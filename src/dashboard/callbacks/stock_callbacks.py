"""
Stock-related dashboard callbacks.
"""

from datetime import datetime

import plotly.graph_objects as go
from dash import Input, Output, State, html, ctx, no_update, ALL
import dash_bootstrap_components as dbc

from config.settings import settings
from src.scraper import StockScraper, NewsScraper
from src.data import DatabaseManager, DataCache
from src.dashboard.layouts.components import (
    create_stock_card,
    create_metric_card,
    create_empty_figure,
    apply_chart_theme,
)
from src.utils.helpers import (
    format_price,
    format_percentage,
    format_large_number,
    get_change_color,
    get_arrow,
)
from src.utils.logger import get_logger

logger = get_logger("StockCallbacks")
COLORS = settings.COLORS

from src.data import db, cache
stock_scraper = StockScraper()
news_scraper = NewsScraper()


def register_stock_callbacks(app):
    """Register all stock-related callbacks."""

    @app.callback(
        [
            Output("stock-data-store", "data"),
            Output("last-update-time", "children"),
        ],
        [
            Input("auto-refresh-interval", "n_intervals"),
            Input("refresh-button", "n_clicks"),
        ],
    )
    def update_stock_data(n_intervals, n_clicks):
        """Fetch and store stock data."""
        try:
            cache_key = "watchlist_data"
            cached = cache.get(cache_key)
            if cached and ctx.triggered_id == "auto-refresh-interval":
                timestamp = datetime.now().strftime("%H:%M:%S")
                return cached, f"Last update: {timestamp} (cached)"

            logger.info("Fetching fresh stock data...")
            data = stock_scraper.scrape_multiple(settings.DEFAULT_WATCHLIST)

            db.save_stock_quotes(data)

            cache.set(cache_key, data)

            timestamp = datetime.now().strftime("%H:%M:%S")
            return data, f"Last update: {timestamp}"

        except Exception as e:
            logger.error(f"Error updating stock data: {e}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            return no_update, f"Error at {timestamp}: {str(e)[:50]}"

    @app.callback(
        Output("watchlist-container", "children"),
        Input("stock-data-store", "data"),
    )
    def update_watchlist(data):
        """Update the watchlist display."""
        if not data:
            return html.P("Loading watchlist...", style={"color": COLORS["text_muted"]})

        cards = []
        for stock in data:
            if "error" in stock:
                continue

            symbol = stock.get("symbol", "???")
            name = stock.get("name", symbol)
            price = stock.get("price")
            change = stock.get("change")
            change_pct = stock.get("change_percent")

            is_positive = (change or 0) >= 0
            price_str = format_price(price) if price else "N/A"
            change_str = f"{'+' if (change or 0) >= 0 else ''}{change:.2f}" if change else "0.00"
            pct_str = format_percentage(change_pct) if change_pct else "0.00%"

            card = dbc.Col(
                xs=12, sm=6, md=4, lg=3,
                className="mb-3",
                children=[
                    html.Div(
                        id={"type": "stock-card", "index": symbol},
                        children=[
                            create_stock_card(
                                symbol=symbol,
                                name=name,
                                price=price_str,
                                change=change_str,
                                change_pct=pct_str,
                                is_positive=is_positive,
                            )
                        ],
                        n_clicks=0,
                        style={"cursor": "pointer"},
                    )
                ],
            )
            cards.append(card)

        return dbc.Row(cards)

    @app.callback(
        Output("metrics-row", "children"),
        [
            Input("stock-data-store", "data"),
            Input("selected-symbol-store", "data"),
        ],
    )
    def update_metrics(data, selected_symbol):
        """Update the key metrics row."""
        if not data:
            return html.Div()

        stock = None
        for s in data:
            if s.get("symbol") == selected_symbol:
                stock = s
                break

        if not stock:
            stock = data[0] if data else {}

        symbol = stock.get("symbol", "")
        price = stock.get("price")
        change = stock.get("change")
        change_pct = stock.get("change_percent")
        volume = stock.get("volume")
        market_cap = stock.get("market_cap")
        pe_ratio = stock.get("pe_ratio")
        high = stock.get("day_high") or stock.get("fifty_two_week_high")
        low = stock.get("day_low") or stock.get("fifty_two_week_low")

        change_color = get_change_color(change)

        metrics = dbc.Row(
            className="mb-4",
            children=[
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "Price",
                        format_price(price),
                        f"{symbol}",
                        COLORS["text"],
                        "💰",
                    )
                ]),
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "Change",
                        format_percentage(change_pct),
                        f"{get_arrow(change)} {format_price(abs(change)) if change else 'N/A'}",
                        change_color,
                        "📉" if (change or 0) < 0 else "📈",
                    )
                ]),
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "Volume",
                        format_large_number(volume).replace("$", ""),
                        "Today's volume",
                        COLORS["accent"],
                        "📊",
                    )
                ]),
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "Market Cap",
                        format_large_number(market_cap),
                        "",
                        COLORS["secondary"],
                        "🏛️",
                    )
                ]),
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "P/E Ratio",
                        f"{pe_ratio:.2f}" if pe_ratio else "N/A",
                        "Trailing",
                        COLORS["warning"],
                        "📐",
                    )
                ]),
                dbc.Col(lg=2, sm=4, xs=6, className="mb-3", children=[
                    create_metric_card(
                        "Day Range",
                        f"{format_price(low)} - {format_price(high)}",
                        "Low - High",
                        COLORS["text"],
                        "↕️",
                    )
                ]),
            ],
        )

        return metrics
    @app.callback(
        [
            Output("price-chart", "figure"),
            Output("chart-title", "children"),
        ],
        [
            Input("stock-data-store", "data"),
            Input("selected-symbol-store", "data"),
            Input("btn-1h", "n_clicks"),
            Input("btn-6h", "n_clicks"),
            Input("btn-24h", "n_clicks"),
        ],
    )
    def update_price_chart(data, selected_symbol, btn_1h, btn_6h, btn_24h):
        """Update the main price chart."""
        triggered = ctx.triggered_id
        hours = 24
        if triggered == "btn-1h":
            hours = 1
        elif triggered == "btn-6h":
            hours = 6

        symbol = selected_symbol or (data[0]["symbol"] if data else "AAPL")

        # Get history from database
        df = db.get_price_history(symbol, hours=hours)

        if df.empty or len(df) < 1:
            fig = create_empty_figure(
                f"Collecting data for {symbol}...\n"
                f"Charts populate as data is scraped every {settings.SCRAPE_INTERVAL}s.\n"
                f"Please wait 2-3 minutes."
            )
            return fig, f"📈 {symbol} Price Chart"

        fig = go.Figure()

        # Even with 1 point, show it as a scatter dot
        if len(df) == 1:
            fig.add_trace(
                go.Scatter(
                    x=df["scraped_at"],
                    y=df["price"],
                    mode="markers+text",
                    name="Price",
                    marker=dict(color=COLORS["primary"], size=12),
                    text=[f"${df['price'].iloc[0]:.2f}"],
                    textposition="top center",
                    textfont=dict(color=COLORS["text"], size=14),
                    hovertemplate="<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>",
                )
            )
        else:
            # Multiple points — draw line with fill
            fig.add_trace(
                go.Scatter(
                    x=df["scraped_at"],
                    y=df["price"],
                    mode="lines+markers",
                    name="Price",
                    line=dict(color=COLORS["primary"], width=2.5),
                    marker=dict(color=COLORS["primary"], size=6),
                    fill="tozeroy",
                    fillcolor="rgba(99, 102, 241, 0.1)",
                    hovertemplate="<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>",
                )
            )

            # High line
            if "day_high" in df.columns and df["day_high"].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df["scraped_at"],
                        y=df["day_high"],
                        mode="lines",
                        name="Day High",
                        line=dict(color=COLORS["success"], width=1, dash="dot"),
                        opacity=0.5,
                    )
                )

            # Low line
            if "day_low" in df.columns and df["day_low"].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df["scraped_at"],
                        y=df["day_low"],
                        mode="lines",
                        name="Day Low",
                        line=dict(color=COLORS["danger"], width=1, dash="dot"),
                        opacity=0.5,
                    )
                )

        # Volume bars
        if "volume" in df.columns and df["volume"].notna().any() and len(df) > 1:
            fig.add_trace(
                go.Bar(
                    x=df["scraped_at"],
                    y=df["volume"],
                    name="Volume",
                    marker_color="rgba(99, 102, 241, 0.3)",
                    yaxis="y2",
                )
            )
            fig.update_layout(
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    range=[0, df["volume"].max() * 4] if df["volume"].max() else None,
                    tickfont=dict(size=10, color=COLORS["text_muted"]),
                ),
            )

        fig = apply_chart_theme(fig, "")

        # Add price annotation
        if not df.empty and df["price"].notna().any():
            latest_price = df["price"].iloc[-1]
            first_price = df["price"].iloc[0]
            if first_price and latest_price:
                change_pct = ((latest_price - first_price) / first_price) * 100
                change_color = COLORS["success"] if change_pct >= 0 else COLORS["danger"]
                fig.add_annotation(
                    text=f"${latest_price:.2f} ({change_pct:+.2f}%)",
                    xref="paper", yref="paper",
                    x=1, y=1.08,
                    showarrow=False,
                    font=dict(size=14, color=change_color, family="JetBrains Mono"),
                    xanchor="right",
                )

        fig.update_layout(
            height=450,
            yaxis=dict(title="Price ($)", tickprefix="$"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        points_info = f" • {len(df)} data points"
        title = f"📈 {symbol} Price Chart ({hours}H){points_info}"
        return fig, title

    @app.callback(
        Output("comparison-chart", "figure"),
        Input("stock-data-store", "data"),
    )
    def update_comparison_chart(data):
        """Update the watchlist comparison chart."""
        if not data:
            return create_empty_figure("No data available")

        symbols = []
        changes = []
        colors = []

        for stock in data:
            if "error" in stock or stock.get("change_percent") is None:
                continue
            symbols.append(stock["symbol"])
            pct = stock["change_percent"]
            changes.append(pct)
            colors.append(COLORS["success"] if pct >= 0 else COLORS["danger"])

        if not symbols:
            return create_empty_figure("No comparison data available")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=symbols,
                y=changes,
                marker_color=colors,
                text=[f"{c:+.2f}%" for c in changes],
                textposition="outside",
                textfont=dict(size=11, color=COLORS["text"]),
                hovertemplate="<b>%{x}</b><br>Change: %{y:+.2f}%<extra></extra>",
            )
        )

        fig = apply_chart_theme(fig, "")
        fig.update_layout(
            yaxis=dict(title="Change (%)", ticksuffix="%"),
            xaxis=dict(title=""),
            height=380,
            showlegend=False,
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=COLORS["text_muted"],
            line_width=1,
        )

        return fig

    @app.callback(
        Output("details-container", "children"),
        [
            Input("stock-data-store", "data"),
            Input("selected-symbol-store", "data"),
        ],
    )
    def update_details(data, selected_symbol):
        """Update the stock details panel."""
        if not data:
            return html.P("No data", style={"color": COLORS["text_muted"]})

        stock = None
        for s in data:
            if s.get("symbol") == selected_symbol:
                stock = s
                break
        if not stock:
            stock = data[0] if data else {}

        def detail_row(label: str, value: str) -> html.Div:
            return html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "padding": "10px 0",
                    "borderBottom": f"1px solid {COLORS['card_border']}",
                },
                children=[
                    html.Span(
                        label,
                        style={"color": COLORS["text_muted"], "fontSize": "0.85rem"},
                    ),
                    html.Span(
                        value,
                        style={
                            "color": COLORS["text"],
                            "fontWeight": "600",
                            "fontFamily": "'JetBrains Mono', monospace",
                            "fontSize": "0.85rem",
                        },
                    ),
                ],
            )

        details = [
            html.H6(
                f"{stock.get('name', stock.get('symbol', ''))}",
                style={
                    "color": COLORS["text"],
                    "fontWeight": "700",
                    "marginBottom": "16px",
                },
            ),
            detail_row("Open", format_price(stock.get("open_price"))),
            detail_row("Previous Close", format_price(stock.get("prev_close"))),
            detail_row("Day High", format_price(stock.get("day_high"))),
            detail_row("Day Low", format_price(stock.get("day_low"))),
            detail_row("52W High", format_price(stock.get("fifty_two_week_high"))),
            detail_row("52W Low", format_price(stock.get("fifty_two_week_low"))),
            detail_row("Volume", format_large_number(stock.get("volume")).replace("$", "")),
            detail_row("Avg Volume", format_large_number(stock.get("avg_volume")).replace("$", "")),
            detail_row("P/E Ratio", f"{stock.get('pe_ratio', 'N/A')}"),
            detail_row("EPS", format_price(stock.get("eps")) if stock.get("eps") else "N/A"),
            detail_row("Beta", f"{stock.get('beta', 'N/A')}"),
            detail_row("RSI (14)", f"{stock.get('rsi', 'N/A')}"),
            detail_row("Sector", stock.get("sector", "N/A")),
            detail_row("Industry", stock.get("industry", "N/A")),
        ]

        return html.Div(
            children=details,
            style={"maxHeight": "450px", "overflowY": "auto"},
        )

    @app.callback(
        Output("selected-symbol-store", "data"),
        Input({"type": "stock-card", "index": ALL}, "n_clicks"),
        State("selected-symbol-store", "data"),
        prevent_initial_call=True,
    )
    def select_stock(n_clicks, current_selected):
        """Handle stock card click to select a stock."""
        if not ctx.triggered_id or not any(n_clicks):
            return no_update

        return ctx.triggered_id["index"]