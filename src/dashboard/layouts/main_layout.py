"""
Main dashboard layout.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from config.settings import settings
from .header import create_header

COLORS = settings.COLORS


def create_layout() -> html.Div:
    """Create the main dashboard layout."""
    return html.Div(
        style={"backgroundColor": COLORS["background"], "minHeight": "100vh"},
        children=[
        
            dcc.Interval(
                id="auto-refresh-interval",
                interval=settings.DASHBOARD_REFRESH_MS,
                n_intervals=0,
            ),

            dcc.Store(id="stock-data-store", storage_type="memory"),
            dcc.Store(id="selected-symbol-store", data=settings.DEFAULT_WATCHLIST[0]),
            dcc.Store(id="market-data-store", storage_type="memory"),

            create_header(),

            dbc.Container(
                fluid=True,
                children=[
                    
                    dbc.Row(
                        className="mb-4",
                        children=[
                            dbc.Col(
                                lg=8,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "justifyContent": "space-between",
                                                    "alignItems": "center",
                                                    "marginBottom": "16px",
                                                },
                                                children=[
                                                    html.H5(
                                                        " Watchlist",
                                                        style={
                                                            "color": COLORS["text"],
                                                            "fontWeight": "700",
                                                            "marginBottom": "0",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="add-symbol-dropdown",
                                                        placeholder="Add symbol...",
                                                        style={"width": "200px"},
                                                        className="dash-dropdown",
                                                    ),
                                                ],
                                            ),
                                            dcc.Loading(
                                                id="loading-watchlist",
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    html.Div(id="watchlist-container")
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dbc.Col(
                                lg=4,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        style={"height": "100%"},
                                        children=[
                                            html.H5(
                                                "Market Indices",
                                                style={
                                                    "color": COLORS["text"],
                                                    "fontWeight": "700",
                                                    "marginBottom": "16px",
                                                },
                                            ),
                                            dcc.Loading(
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    html.Div(id="market-indices-container")
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    
                    dcc.Loading(
                        type="dot",
                        color=COLORS["primary"],
                        children=[
                            html.Div(id="metrics-row")
                        ],
                    ),

                    
                    dbc.Row(
                        className="mb-4",
                        children=[
                            dbc.Col(
                                lg=8,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        children=[
                                            html.Div(
                                                style={
                                                    "display": "flex",
                                                    "justifyContent": "space-between",
                                                    "alignItems": "center",
                                                    "marginBottom": "16px",
                                                },
                                                children=[
                                                    html.H5(
                                                        id="chart-title",
                                                        style={
                                                            "color": COLORS["text"],
                                                            "fontWeight": "700",
                                                            "marginBottom": "0",
                                                        },
                                                    ),
                                                    dbc.ButtonGroup(
                                                        size="sm",
                                                        children=[
                                                            dbc.Button(
                                                                "1H", id="btn-1h",
                                                                outline=True, color="light",
                                                                className="me-1"
                                                            ),
                                                            dbc.Button(
                                                                "6H", id="btn-6h",
                                                                outline=True, color="light",
                                                                className="me-1"
                                                            ),
                                                            dbc.Button(
                                                                "24H", id="btn-24h",
                                                                outline=True, color="light",
                                                                active=True,
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            dcc.Loading(
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    dcc.Graph(
                                                        id="price-chart",
                                                        config={
                                                            "displayModeBar": True,
                                                            "modeBarButtonsToRemove": [
                                                                "pan2d", "select2d", "lasso2d",
                                                                "autoScale2d",
                                                            ],
                                                            "displaylogo": False,
                                                        },
                                                        style={"height": "450px"},
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dbc.Col(
                                lg=4,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        style={"height": "100%"},
                                        children=[
                                            html.H5(
                                                " Latest News",
                                                style={
                                                    "color": COLORS["text"],
                                                    "fontWeight": "700",
                                                    "marginBottom": "16px",
                                                },
                                            ),
                                            dcc.Loading(
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    html.Div(
                                                        id="news-container",
                                                        style={
                                                            "maxHeight": "420px",
                                                            "overflowY": "auto",
                                                        },
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                    dbc.Row(
                        className="mb-4",
                        children=[
                            dbc.Col(
                                lg=6,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        children=[
                                            html.H5(
                                                " Watchlist Comparison",
                                                style={
                                                    "color": COLORS["text"],
                                                    "fontWeight": "700",
                                                    "marginBottom": "16px",
                                                },
                                            ),
                                            dcc.Loading(
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    dcc.Graph(
                                                        id="comparison-chart",
                                                        config={"displaylogo": False},
                                                        style={"height": "380px"},
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dbc.Col(
                                lg=6,
                                children=[
                                    html.Div(
                                        className="dashboard-card",
                                        children=[
                                            html.H5(
                                                "🏢 Stock Details",
                                                style={
                                                    "color": COLORS["text"],
                                                    "fontWeight": "700",
                                                    "marginBottom": "16px",
                                                },
                                            ),
                                            dcc.Loading(
                                                type="dot",
                                                color=COLORS["primary"],
                                                children=[
                                                    html.Div(id="details-container")
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),

                
                    html.Div(
                        style={
                            "textAlign": "center",
                            "padding": "24px 0",
                            "borderTop": f"1px solid {COLORS['card_border']}",
                            "marginTop": "24px",
                        },
                        children=[
                            html.P(
                                [
                                    "StockPulse v1.0 CCU2026│ ",
                                    html.A(
                                        "GitHub",
                                        href="#",
                                        style={"color": COLORS["primary"]},
                                    ),
                                ],
                                style={"color": COLORS["text_muted"], "fontSize": "0.8rem"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )