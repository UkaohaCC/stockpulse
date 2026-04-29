"""
Dashboard header component.
"""

from dash import html
import dash_bootstrap_components as dbc
from config.settings import settings


def create_header() -> html.Div:
    """Create the dashboard header."""
    return html.Div(
        className="dashboard-header",
        children=[
            dbc.Container(
                fluid=True,
                children=[
                    dbc.Row(
                        align="center",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H1(
                                                [
                                                    html.Span("📊 ", style={"fontSize": "1.8rem"}),
                                                    "StockPulse"
                                                ],
                                                className="header-title",
                                                style={"marginBottom": "0"}
                                            ),
                                            html.P(
                                                "Real-time market data & analytics",
                                                className="header-subtitle"
                                            ),
                                        ]
                                    )
                                ],
                            ),
                            dbc.Col(
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "flex-end",
                                            "gap": "16px",
                                        },
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Span(className="live-dot"),
                                                    html.Span(
                                                        "LIVE",
                                                        style={
                                                            "color": "#10b981",
                                                            "fontWeight": "700",
                                                            "fontSize": "0.8rem",
                                                            "letterSpacing": "0.1em",
                                                        },
                                                    ),
                                                ],
                                                style={"display": "flex", "alignItems": "center"},
                                            ),
                                            html.Div(
                                                id="last-update-time",
                                                style={
                                                    "color": "#94a3b8",
                                                    "fontSize": "0.8rem",
                                                    "fontFamily": "'JetBrains Mono', monospace",
                                                },
                                            ),
                                            dbc.Button(
                                                [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                                                id="refresh-button",
                                                color="primary",
                                                size="sm",
                                                className="btn-primary",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
    )