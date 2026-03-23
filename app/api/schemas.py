from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str
    domain: str
    country_focus: str | None = None
    source_type: str
    fetch_method: str
    trust_score: float = Field(default=0.7, ge=0.0, le=1.0)
    priority_score: float = Field(default=0.7, ge=0.0, le=1.0)
    crawl_interval_minutes: int = 360
    is_active: bool = True
    sections: list[dict[str, str]] = []


class SourceRead(BaseModel):
    id: int
    name: str
    domain: str
    country_focus: str | None
    source_type: str
    fetch_method: str
    trust_score: float
    priority_score: float
    crawl_interval_minutes: int
    is_active: bool

    class Config:
        from_attributes = True


class DocumentIngest(BaseModel):
    source_id: int
    url: str
    title: str | None = None
    clean_text: str | None = None
    raw_text: str | None = None
    published_at: str | None = None
    canonical_url: str | None = None
    language: str = "en"
    document_type: str = "html"
    is_pdf: bool = False
    auto_extract_if_missing: bool = True


class DocumentRead(BaseModel):
    id: int
    source_id: int
    url: str
    title: str
    published_at: str | None
    discovered_at: str
    summary: str | None
    event_type: str | None
    matched_entities: str | None
    matched_topics: str | None
    final_score: float
    source_score: float
    entity_score: float
    semantic_score: float
    event_score: float
    recency_score: float
    novelty_score: float

    class Config:
        from_attributes = True
