from typing import List, Optional

from pydantic import BaseModel

from src.models.article import Article


class StockBase(BaseModel):
    ticker: str
    mention_count: int
    average_sentiment: float
    hotness_score: float
    current_price: Optional[float] = 0.0
    open_price: Optional[float] = 0.0
    price_change_pct: Optional[float] = 0.0
    volume: Optional[int] = 0


class StockDetail(BaseModel):
    ticker: str
    total_articles: int
    average_sentiment: float
    recent_news: List[Article]
    resolved_date: str


class Stocks(BaseModel):
    leaderboard: List[StockBase]


class TrendPoint(BaseModel):
    date: str
    average_sentiment: float


class StockTrend(BaseModel):
    ticker: str
    trend: List[TrendPoint]
