"""
Reusable dashboard components.
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from config.settings import settings

COLORS = settings.COLORS


def create_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "#e2e8f0",
    icon: str = "",
) -> dbc.Card:
    """Create a metric display card."""
    return dbc.Card(
        className="dashboard-card",
        style={"height": "100%"},
        children=[
            html.Div(
                children=[
                    html.P(
                        [html.Span(icon + " ") if icon else "", title],
                        className="metric-label"
                    ),
                    html.H3(
                        value,
                        className="metric-value",
                        style={"color": color},
                    ),
                    html.P(
                        subtitle,
                        style={
                            "color": COLORS["text_muted"],
                            "fontSize": "0.8rem",
                            "marginTop": "4px",
                        },
                    ) if subtitle else None,
                ]
            )
        ],
    )


def create_stock_card(
    symbol: str,
    name: str,
    price: str,
    change: str,
    change_pct: str,
    is_positive: bool,
) -> html.Div:
    """Create a stock ticker card."""
    color = COLORS["success"] if is_positive else COLORS["danger"]
    arrow = "▲" if is_positive else "▼"
    card_class = "stock-card positive" if is_positive else "stock-card negative"

    return html.Div(
        className=card_class,
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start"},
                children=[
                    html.Div(
                        children=[
                            html.H5(
                                symbol,
                                style={
                                    "fontWeight": "700",
                                    "marginBottom": "2px",
                                    "color": COLORS["text"],
                                    "fontSize": "1rem",
                                },
                            ),
                            html.P(
                                name[:20] + "..." if len(name) > 20 else name,
                                style={
                                    "color": COLORS["text_muted"],
                                    "fontSize": "0.75rem",
                                    "marginBottom": "0",
                                },
                            ),
                        ]
                    ),
                    html.Div(
                        style={"textAlign": "right"},
                        children=[
                            html.H5(
                                price,
                                style={
                                    "fontWeight": "700",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                    "marginBottom": "2px",
                                    "color": COLORS["text"],
                                    "fontSize": "1.1rem",
                                },
                            ),
                            html.Span(
                                f"{arrow} {change} ({change_pct})",
                                style={
                                    "color": color,
                                    "fontWeight": "600",
                                    "fontSize": "0.8rem",
                                    "fontFamily": "'JetBrains Mono', monospace",
                                },
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def create_empty_figure(message: str = "No data available") -> go.Figure:
    """Create an empty placeholder figure."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color=COLORS["text_muted"]),
    )
    fig.update_layout(
        plot_bgcolor=COLORS["card_bg"],
        paper_bgcolor=COLORS["card_bg"],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=400,
    )
    return fig


def apply_chart_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent dark theme to a plotly figure."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color=COLORS["text"], family="Inter"),
            x=0,
            xanchor="left",
        ),
        plot_bgcolor=COLORS["card_bg"],
        paper_bgcolor=COLORS["card_bg"],
        font=dict(color=COLORS["text_muted"], family="Inter", size=12),
        xaxis=dict(
            gridcolor="#1e1e3f",
            zerolinecolor="#1e1e3f",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            gridcolor="#1e1e3f",
            zerolinecolor="#1e1e3f",
            showgrid=True,
            gridwidth=1,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_muted"]),
        ),
        margin=dict(l=60, r=30, t=60, b=50),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#12122b",
            bordercolor="#1e1e3f",
            font=dict(color=COLORS["text"]),
        ),
    )
    return fig