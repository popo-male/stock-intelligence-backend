import time
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser

from core.config import AppConfig
from db.repository import upload_articles
from scraper.helpers import clean_html


def fetch_news(ticker: str, rss_base_url: str) -> list[dict[str, Any]]:
    rss_url = rss_base_url.format(ticker=ticker)
    feed = feedparser.parse(rss_url)

    articles: list[dict[str, Any]] = []

    for entry in feed.entries:
        try:
            published_date = parsedate_to_datetime(entry.published)

            articles.append(
                {
                    "ticker": ticker,
                    "title": entry.title,
                    "url": entry.link,
                    "summary": clean_html(entry.get("summary", "")),
                    "published_at": published_date,
                    "source": "Yahoo Finance",
                }
            )
        except Exception as exc:
            print(f"Error parsing article for {ticker}: {exc}")

    return articles


def run_scraper(config: AppConfig) -> None:
    """Iterates through the watchlist and processes all news"""
    total_new = 0

    for ticket in config.scraper.watchlist:
        articles = fetch_news(ticket, config.scraper.rss_base_url)

        if articles:
            new_count = upload_articles(articles)
            total_new += new_count
            print(
                f"Fetched {len(articles)} articles for {ticket}. Inserted {new_count} new."
            )
        else:
            print(f"{ticket}: No articles found.")

        time.sleep(config.scraper.sleep_interval)

    print(f"Scraping complete! {total_new} new articles stored.")
