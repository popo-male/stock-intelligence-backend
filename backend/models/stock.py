from typing import List

from pydantic import BaseModel

from backend.models.article import Article


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


class Stocks(BaseModel):
    leaderboard: List[Stock]
