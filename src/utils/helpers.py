"""
Utility helper functions.
"""

from datetime import datetime


def format_large_number(num: float | int | None) -> str:
    """Format large numbers with K, M, B, T suffixes."""
    if num is None:
        return "N/A"
    try:
        num = float(num)
    except (ValueError, TypeError):
        return "N/A"

    if abs(num) >= 1e12:
        return f"${num / 1e12:.2f}T"
    elif abs(num) >= 1e9:
        return f"${num / 1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num / 1e6:.2f}M"
    elif abs(num) >= 1e3:
        return f"${num / 1e3:.2f}K"
    else:
        return f"${num:.2f}"


def format_percentage(value: float | None) -> str:
    """Format a float as percentage string."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_price(value: float | None) -> str:
    """Format a float as price string."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def get_change_color(value: float | None) -> str:
    """Return color based on positive/negative value."""
    if value is None or value == 0:
        return "#94a3b8"
    return "#10b981" if value > 0 else "#ef4444"


def get_arrow(value: float | None) -> str:
    """Return arrow emoji based on value."""
    if value is None or value == 0:
        return "→"
    return "▲" if value > 0 else "▼"


def timestamp_now() -> str:
    """Return current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")