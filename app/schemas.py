from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class SourceCreate(BaseModel):
    name: str
    domain: str
    source_type: str
    country_focus: Optional[str] = None
    section_url: Optional[HttpUrl] = None
    priority_score: int = 5
    is_active: bool = True


class Source(BaseModel):
    id: int
    name: str
    domain: str
    source_type: str
    country_focus: Optional[str] = None
    section_url: Optional[str] = None
    priority_score: int
    is_active: bool

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    source_id: int
    title: str
    url: HttpUrl
    content: str
    published_at: Optional[datetime] = None


class DocumentScore(BaseModel):
    source_score: float
    keyword_score: float
    country_score: float
    semantic_score: float
    event_score: float
    recency_score: float
    novelty_score: float
    final_score: float


class Document(BaseModel):
    id: int
    source_id: int
    title: str
    url: str
    content: str
    published_at: Optional[datetime] = None
    ingested_at: datetime
    matched_keywords: List[str]
    matched_countries: List[str]
    score: DocumentScore
