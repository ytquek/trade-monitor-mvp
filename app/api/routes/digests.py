from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document

router = APIRouter(prefix="/digests", tags=["digests"])


@router.get("/daily")
def daily_digest(
    min_score: float = Query(default=0.55, ge=0.0, le=1.0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .filter(Document.final_score >= min_score)
        .order_by(Document.final_score.desc(), Document.id.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(documents),
        "items": [
            {
                "id": doc.id,
                "title": doc.title,
                "url": doc.url,
                "summary": doc.summary,
                "event_type": doc.event_type,
                "matched_topics": doc.matched_topics,
                "matched_entities": doc.matched_entities,
                "final_score": doc.final_score,
            }
            for doc in documents
        ],
    }
