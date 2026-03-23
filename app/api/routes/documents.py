from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas import DocumentIngest, DocumentRead
from app.db.session import get_db
from app.models.document import Document
from app.models.source import Source
from app.services.extraction import extract_html
from app.services.scoring import content_hash, score_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=DocumentRead)
async def ingest_document(payload: DocumentIngest, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == payload.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    existing = db.query(Document).filter(Document.url == payload.url).first()
    if existing:
        return existing

    title = payload.title
    clean_text = payload.clean_text
    raw_text = payload.raw_text
    published_at = payload.published_at
    canonical_url = payload.canonical_url
    language = payload.language
    document_type = payload.document_type
    is_pdf = payload.is_pdf

    if payload.auto_extract_if_missing and (not title or not clean_text or not raw_text):
        extracted = await extract_html(payload.url)
        title = title or extracted.title
        clean_text = clean_text or extracted.clean_text
        raw_text = raw_text or extracted.raw_text
        published_at = published_at or extracted.published_at
        canonical_url = canonical_url or extracted.canonical_url
        language = extracted.language
        document_type = extracted.document_type
        is_pdf = extracted.is_pdf

    if not title or not clean_text or not raw_text:
        raise HTTPException(status_code=400, detail="Document content is incomplete")

    scores = score_document(db, source, title, clean_text, published_at)
    document = Document(
        source_id=source.id,
        url=payload.url,
        canonical_url=canonical_url,
        title=title,
        published_at=published_at,
        discovered_at=datetime.now(timezone.utc).isoformat(),
        content_hash=content_hash(clean_text),
        language=language,
        raw_text=raw_text,
        clean_text=clean_text,
        summary=scores.summary,
        document_type=document_type,
        is_pdf=str(is_pdf).lower(),
        status="scored",
        keyword_score=scores.keyword_score,
        entity_score=scores.entity_score,
        semantic_score=scores.semantic_score,
        source_score=scores.source_score,
        event_score=scores.event_score,
        recency_score=scores.recency_score,
        novelty_score=scores.novelty_score,
        final_score=scores.final_score,
        matched_entities=", ".join(scores.matched_entities),
        matched_topics=", ".join(scores.matched_topics),
        event_type=scores.event_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    min_score: float = Query(default=0.0, ge=0.0, le=1.0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(Document)
        .filter(Document.final_score >= min_score)
        .order_by(Document.final_score.desc(), Document.id.desc())
        .limit(limit)
        .all()
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
