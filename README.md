#  StockPulse

> Real-time stock market dashboard with web scraping, built with Python, BeautifulSoup, and Plotly Dash.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-2.16-purple?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.12-orange)

##  Features

- **Real-time Stock Scraping** — Pulls live stock data from Yahoo Finance and Finviz using BeautifulSoup
- **Interactive Dashboard** — Beautiful, responsive UI built with Plotly Dash
- **Auto-Refresh** — Data updates automatically every 30 seconds
- **Price Charts** — Interactive time-series charts with 1H/6H/24H views
- **Watchlist Comparison** — Side-by-side performance comparison chart
- **News Feed** — Latest financial news scraped per stock
- **Market Indices** — Live S&P 500, NASDAQ, Dow Jones data
- **SQLite Storage** — Historical data persistence with SQLAlchemy
- **Caching Layer** — TTL-based in-memory caching for performance
- **Dark Theme** — Professional dark UI with smooth animations

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

# Clone the repository
git clone https://github.com/UkaohaCC/stockpulse.git
cd stockpulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac


#venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run the dashboard
python run.py #or python3 run.py


##  Data Directory

The `data/` folder stores the SQLite database (`stockpulse.db`).  
It is created automatically on first run — no setup needed.

python run.py  # database created at data/stockpulse.db

## Disclaimer
This project is for educational purposes only. Please respect the terms of service of the websites being scraped. The data displayed may be delayed or inaccurate. Do not use for actual trading decisions.
Open for contributions too, feel free to pull requests and make this better.
