"""
Base scraper class with common functionality.
Handles HTTP sessions, retries, rate limiting, and error handling.
"""

import time
from abc import ABC, abstractmethod
from typing import Any

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from src.utils.logger import get_logger


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.session = self._create_session()
        self._last_request_time = 0.0
        self._min_delay = 1.0

    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        })
        return session

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()

    def fetch_page(self, url, params=None):
        self._rate_limit()
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                self.logger.debug(f"Fetching: {url} (attempt {attempt})")
                response = self.session.get(url, params=params, timeout=settings.REQUEST_TIMEOUT)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"
                soup = BeautifulSoup(response.text, "html.parser")
                self.logger.debug(f"Successfully fetched: {url}")
                return soup
            except requests.exceptions.HTTPError as e:
                self.logger.warning(f"HTTP error {e.response.status_code} for {url}: {e}")
                if e.response.status_code == 429:
                    wait = min(2 ** attempt * 5, 60)
                    self.logger.info(f"Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                elif e.response.status_code >= 500:
                    time.sleep(2 ** attempt)
                else:
                    break
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error for {url}: {e}")
                time.sleep(2 ** attempt)
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout for {url} (attempt {attempt})")
                time.sleep(2 ** attempt)
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {url}: {e}")
                break
        self.logger.error(f"Failed to fetch {url} after {settings.MAX_RETRIES} attempts")
        return None

    def fetch_json(self, url, params=None):
        self._rate_limit()
        try:
            response = self.session.get(url, params=params, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching JSON from {url}: {e}")
            return None

    @abstractmethod
    def scrape(self, *args, **kwargs):
        ...

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()