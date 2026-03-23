from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    url = Column(String, nullable=False, unique=True)
    canonical_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    published_at = Column(String, nullable=True)
    discovered_at = Column(String, nullable=False)
    content_hash = Column(String, nullable=True)
    language = Column(String, default="en")
    raw_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    document_type = Column(String, default="html")
    is_pdf = Column(String, default="false")
    status = Column(String, default="scored")

    keyword_score = Column(Float, default=0.0)
    entity_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    source_score = Column(Float, default=0.0)
    event_score = Column(Float, default=0.0)
    recency_score = Column(Float, default=0.0)
    novelty_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)

    matched_entities = Column(Text, nullable=True)
    matched_topics = Column(Text, nullable=True)
    event_type = Column(String, nullable=True)

    source = relationship("Source", back_populates="documents")
