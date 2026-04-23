import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from src.db.repository import (
    get_hot_stocks,
    get_stock_articles,
    get_stock_stats,
    get_sentiment_trend,
    get_article_count,
)
from src.models.stock import Stock, StockDetail, Stocks, StockTrend, TrendPoint
from src.models.article import Article

router = APIRouter()


@router.get("/hot", response_model=Stocks)
def get_stocks():
    """Returns a leaderboard of the most talked-about stocks with their sentiment."""
    # Calculate date for 3 days ago
    date_range = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    rows = get_hot_stocks(date_range)

    leaderboard = []
    for row in rows:
        # Simple hotness formula: Volume * (1 + absolute sentiment magnitude)
        mentions = row["mention_count"]  # type: ignore
        avg_sent = row["average_sentiment"] or 0.0  # type: ignore
        hotness = mentions * (1 + abs(avg_sent))

        leaderboard.append(
            Stock(
                ticker=row["ticker"],  # type: ignore
                mention_count=mentions,
                average_sentiment=round(avg_sent, 3),
                hotness_score=round(hotness, 2),
            )
        )

    # Sort by our custom hotness score
    leaderboard.sort(key=lambda x: x.hotness_score, reverse=True)
    return Stocks(leaderboard=leaderboard)


@router.get("/{ticker}", response_model=StockDetail)
def get_stock_detail(ticker: str, target_date: str = Query(None)):
    """Returns detailed stats and recent news for a specific stock ticker."""
    ticker_upper = ticker.upper()

    # default to use today
    if target_date:
        resolved_date = target_date
    else:
        resolved_date = None
        for days_back in range(30):  # Look back up to 30 days
            check_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )
            count_row = get_article_count(ticker_upper, check_date)
            if count_row and count_row["cnt"] > 0:  # type: ignore
                resolved_date = check_date
                break

        if not resolved_date:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {ticker_upper} in the last 30 days",
            )

    # Get recent articles
    articles_rows = get_stock_articles(ticker_upper, resolved_date)

    # Calculate overall stats for this specific ticker
    stats_row = get_stock_stats(ticker, resolved_date)

    if not stats_row:
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")

    articles = []
    for row in articles_rows:
        row_dict = dict(row)

        # Safely load JSON if it exists
        if row_dict.get("bullets"):
            if isinstance(row_dict["bullets"], str):
                row_dict["bullets"] = json.loads(row_dict["bullets"])
        else:
            row_dict["bullets"] = []

        if row_dict.get("keywords"):
            if isinstance(row_dict["keywords"], str):
                row_dict["keywords"] = json.loads(row_dict["keywords"])
        else:
            row_dict["keywords"] = []

        articles.append(Article(**row_dict))

    return StockDetail(
        ticker=ticker_upper,
        total_articles=stats_row["total"],  # type: ignore
        average_sentiment=round(stats_row["avg_sent"] or 0.0, 3),  # type: ignore
        recent_news=articles,
        resolved_date=resolved_date,
    )


@router.get("/{ticker}/trend", response_model=StockTrend)
def get_stock_trend(ticker: str):
    """Returns the average sentiment grouped by date for the last 7 days."""
    ticker_upper = ticker.upper()

    # Calculate date for 7 days ago
    date_range = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

    rows = get_sentiment_trend(ticker_upper, date_range)

    trend_data = []
    for row in rows:
        trend_data.append(
            TrendPoint(
                date=row["date_str"],  # type: ignore
                average_sentiment=round(row["avg_sent"] or 0.0, 3),  # type: ignore
            )
        )

    return StockTrend(ticker=ticker_upper, trend=trend_data)
