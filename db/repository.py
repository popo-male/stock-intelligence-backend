import sqlite3
from typing import Any

from db.connection import get_db_connection


def setup_database() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
		CREATE TABLE IF NOT EXISTS articles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			ticker TEXT,
			title TEXT,
			url TEXT UNIQUE,
			summary TEXT,
			published_at TIMESTAMP,
			source TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		"""
    )
    conn.commit()
    conn.close()


def upload_articles(articles: list[dict[str, Any]]) -> int:
    """Insert a list of articles, ignoring duplicates, and return new insert count."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_articles_count = 0

    for article in articles:
        try:
            cursor.execute(
                """
				INSERT OR IGNORE INTO articles
				(ticker, title, url, summary, published_at, source)
				VALUES (?, ?, ?, ?, ?, ?)
				""",
                (
                    article["ticker"],
                    article["title"],
                    article["url"],
                    article["summary"],
                    article["published_at"],
                    article["source"],
                ),
            )

            if cursor.rowcount > 0:
                new_articles_count += 1

        except sqlite3.Error as exc:
            print(f"Database error on {article.get('ticker', 'unknown')}: {exc}")

    conn.commit()
    conn.close()

    return new_articles_count
