from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import SourceCreate, SourceRead
from app.db.session import get_db
from app.models.source import Source, SourceSection

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceRead)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.domain == payload.domain).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source domain already exists")

    source = Source(
        name=payload.name,
        domain=payload.domain,
        country_focus=payload.country_focus,
        source_type=payload.source_type,
        fetch_method=payload.fetch_method,
        trust_score=payload.trust_score,
        priority_score=payload.priority_score,
        crawl_interval_minutes=payload.crawl_interval_minutes,
        is_active=payload.is_active,
    )
    db.add(source)
    db.flush()

    for section in payload.sections:
        db.add(SourceSection(
            source_id=source.id,
            section_url=section["section_url"],
            section_type=section.get("section_type", "news"),
        ))

    db.commit()
    db.refresh(source)
    return source


@router.get("", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.priority_score.desc(), Source.id.asc()).all()
