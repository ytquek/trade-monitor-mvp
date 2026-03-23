from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False, unique=True)
    country_focus = Column(String, nullable=True)
    source_type = Column(String, nullable=False)
    fetch_method = Column(String, nullable=False)
    trust_score = Column(Float, default=0.7)
    priority_score = Column(Float, default=0.7)
    crawl_interval_minutes = Column(Integer, default=360)
    is_active = Column(Boolean, default=True)

    sections = relationship("SourceSection", back_populates="source", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="source")


class SourceSection(Base):
    __tablename__ = "source_sections"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    section_url = Column(String, nullable=False)
    section_type = Column(String, nullable=False)
    last_checked_at = Column(String, nullable=True)

    source = relationship("Source", back_populates="sections")
