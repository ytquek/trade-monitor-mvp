from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from app.database import Base


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    country_focus = Column(String, nullable=True)
    section_url = Column(String, nullable=True)
    priority_score = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, nullable=False)

    matched_keywords = Column(Text, nullable=True)
    matched_countries = Column(Text, nullable=True)

    source_score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)
    country_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    event_score = Column(Float, nullable=False)
    recency_score = Column(Float, nullable=False)
    novelty_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
