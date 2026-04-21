from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Article(BaseModel):
    title: str
    url: str
    summary: str
    published_at: datetime
    source: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
