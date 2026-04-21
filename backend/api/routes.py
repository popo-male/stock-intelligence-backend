from fastapi import APIRouter, HTTPException
from db.connection import get_db_connection
from backend.models.stock import Stock, StockDetail, Stocks
from backend.models.article import Article

router = APIRouter()

@router.get("/api/stocks/hot", response_model=Stocks)
def get_hot_stocks():
    """Returns a leaderboard of the most talked-about stocks with their sentiment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate mentions and average sentiment per stock
    cursor.execute('''
        SELECT 
            ticker, 
            COUNT(id) as mention_count, 
            AVG(sentiment_score) as average_sentiment
        FROM articles 
        WHERE sentiment_score IS NOT NULL
        GROUP BY ticker
        ORDER BY mention_count DESC, average_sentiment DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
    for row in rows:
        # Simple hotness formula: Volume * (1 + absolute sentiment magnitude)
        mentions = row["mention_count"]  # type: ignore
        avg_sent = row["average_sentiment"] or 0.0  # type: ignore
        hotness = mentions * (1 + abs(avg_sent))

        leaderboard.append(Stock(
            ticker=row["ticker"],  # type: ignore
            mention_count=mentions,
            average_sentiment=round(avg_sent, 3),
            hotness_score=round(hotness, 2)
        ))

    # Sort by our custom hotness score
    leaderboard.sort(key=lambda x: x.hotness_score, reverse=True)

    return Stocks(leaderboard=leaderboard)

@router.get("/api/stocks/{ticker}", response_model=StockDetail)
def get_stock_detail(ticker: str):
    """Returns detailed stats and recent news for a specific stock ticker."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    ticker_upper = ticker.upper()
    
    # Get recent articles
    cursor.execute('''
        SELECT title, url, summary, published_at, source, sentiment_score, sentiment_label
        FROM articles 
        WHERE ticker = %s
        ORDER BY published_at DESC 
        LIMIT 15
    ''', (ticker_upper,))
    
    articles_rows = cursor.fetchall()
    
    if not articles_rows:
        conn.close()
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker_upper}")
        
    # Calculate overall stats for this specific ticker
    cursor.execute('''
        SELECT COUNT(id) as total, AVG(sentiment_score) as avg_sent
        FROM articles 
        WHERE ticker = %s AND sentiment_score IS NOT NULL
    ''', (ticker_upper,))
    
    stats_row = cursor.fetchone()
    conn.close()
    
    if not stats_row:
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")
    
    articles = [Article(**dict(row)) for row in articles_rows]  # type: ignore
    
    return StockDetail(
        ticker=ticker_upper,
        total_articles=stats_row["total"],  # type: ignore
        average_sentiment=round(stats_row["avg_sent"] or 0.0, 3),  # type: ignore
        recent_news=articles
    )