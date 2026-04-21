from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from db.connection import get_db_connection

analyzer = SentimentIntensityAnalyzer()


def calculate_sentiment(text: str) -> dict:
    """
    Returns a dictionary with sentiment scores.
    Compound score ranges from -1 (Extremely Negative) to +1 (Extremely Positive).
    """
    if not text:
        return {"compound": 0, "label": "Neutral"}

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    # classify the score into a label
    if compound >= 0.05:
        label = "Bullish"
    elif compound <= -0.05:
        label = "Bearish"
    else:
        label = "Neutral"

    return {"compound": compound, "label": label}


def process_unscored_articles():
    """Fetches articles without sentiment scores, analyzer sentiment"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS sentiment_score REAL")
    cursor.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS sentiment_label TEXT")

    cursor.execute(
        "SELECT id, title, summary FROM articles WHERE sentiment_score IS NULL"
    )
    unscored_articles = cursor.fetchall()

    if not unscored_articles:
        conn.close()
        return

    update_count = 0
    for article in unscored_articles:
        full_text = f"{article['title']} {article['summary']}"

        sentiment = calculate_sentiment(full_text)

        cursor.execute(
            """
            UPDATE articles
            SET sentiment_score = %s, sentiment_label = %s
            WHERE id = %s
        """,
            (sentiment["compound"], sentiment["label"], article["id"]),
        )

        update_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully updated sentiment for {update_count} articles.")
