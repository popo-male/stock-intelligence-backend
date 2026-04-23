from typing import List

from pydantic import BaseModel

from src.models.article import Article


class Stock(BaseModel):
    ticker: str
    mention_count: int
    average_sentiment: float
    hotness_score: float


class StockDetail(BaseModel):
    ticker: str
    total_articles: int
    average_sentiment: float
    recent_news: List[Article]
    resolved_date: str


class Stocks(BaseModel):
    leaderboard: List[Stock]


class TrendPoint(BaseModel):
    date: str
    average_sentiment: float


class StockTrend(BaseModel):
    ticker: str
    trend: List[TrendPoint]
