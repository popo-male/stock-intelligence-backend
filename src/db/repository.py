from src.db.connection import get_db_connection


def get_hot_stocks(date_range: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            ticker,
            COUNT(id) as mention_count,
            AVG(sentiment_score) as average_sentiment
        FROM articles
        WHERE sentiment_score IS NOT NULL
            AND published_at >= %s
        GROUP BY ticker
        ORDER BY mention_count DESC, average_sentiment DESC
    """,
        (date_range,),
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_article_count(ticker: str, date: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(id) as cnt FROM articles WHERE ticker = %s AND published_at::DATE = %s::DATE",
        (ticker, date),
    )

    count_row = cursor.fetchone()
    conn.close()
    return count_row


def get_stock_articles(ticker: str, date_range: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, url, summary, published_at, source, sentiment_score, sentiment_label, bullets, keywords
        FROM articles
        WHERE ticker = %s AND published_at::DATE = %s::DATE
        ORDER BY published_at DESC
        LIMIT 15
    """,
        (ticker, date_range),
    )

    articles_rows = cursor.fetchall()
    conn.close()
    return articles_rows


def get_stock_stats(ticker: str, date_range: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(id) as total, AVG(sentiment_score) as avg_sent
        FROM articles
        WHERE ticker = %s AND published_at::DATE = %s::DATE AND sentiment_score IS NOT NULL
    """,
        (ticker, date_range),
    )

    stats_row = cursor.fetchone()
    conn.close()
    return stats_row


def get_sentiment_trend(ticker: str, date_range: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TO_CHAR(published_at, 'YYYY-MM-DD') as date_str, AVG(sentiment_score) as avg_sent
        FROM articles
        WHERE ticker = %s AND sentiment_score IS NOT NULL AND published_at >= %s
        GROUP BY date_str
        ORDER BY date_str ASC
    """,
        (ticker, date_range),
    )

    distribution_rows = cursor.fetchall()
    conn.close()
    return distribution_rows
