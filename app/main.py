from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import SourceModel, DocumentModel
from app.schemas import SourceCreate, Source, DocumentCreate, Document, DocumentScore

app = FastAPI(title="Trade Monitor MVP")

Base.metadata.create_all(bind=engine)

KEYWORDS = [
    "trade connectivity",
    "single window",
    "customs",
    "port",
    "maritime",
    "shipping",
    "logistics",
    "terminal",
    "transshipment",
    "corridor",
    "digitization",
    "trade facilitation",
    "port community system",
    "berth expansion",
    "dredging",
]

COUNTRIES = [
    "kenya",
    "singapore",
    "indonesia",
    "bangladesh",
    "rwanda",
    "mozambique",
    "malaysia",
    "vietnam",
    "philippines",
    "india",
    "sri lanka",
]

EVENT_TERMS = [
    "launch",
    "launched",
    "upgrade",
    "expanded",
    "expansion",
    "awarded",
    "signed",
    "implemented",
    "deploy",
    "deployment",
    "modernization",
    "reform",
    "tender",
    "concession",
    "partnership",
]


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(value, max_value))


def compute_source_score(source: SourceModel) -> float:
    base = source.priority_score / 10.0

    bonus_map = {
        "government": 0.20,
        "customs": 0.20,
        "port_authority": 0.20,
        "trade_ministry": 0.18,
        "maritime_authority": 0.18,
        "shipping_line": 0.12,
        "maritime_news": 0.10,
        "news": 0.08,
    }

    bonus = bonus_map.get(source.source_type.lower(), 0.05)
    return clamp(base + bonus)


def compute_keyword_matches(text: str) -> List[str]:
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw in text_lower]


def compute_country_matches(text: str) -> List[str]:
    text_lower = text.lower()
    return [country for country in COUNTRIES if country in text_lower]


def compute_keyword_score(matches: List[str]) -> float:
    return clamp(len(matches) / 5.0)


def compute_country_score(matches: List[str], source: SourceModel) -> float:
    score = 0.0
    if matches:
        score += min(len(matches) * 0.25, 0.75)

    if source.country_focus and source.country_focus.lower() in matches:
        score += 0.25

    return clamp(score)


def compute_semantic_score(text: str) -> float:
    text_lower = text.lower()

    concept_groups = [
        ["trade", "connectivity"],
        ["customs", "digitization"],
        ["port", "expansion"],
        ["maritime", "logistics"],
        ["single window", "customs"],
        ["terminal", "shipping"],
    ]

    hits = 0
    for group in concept_groups:
        if all(term in text_lower for term in group):
            hits += 1

    return clamp(hits / 4.0)


def compute_event_score(text: str) -> float:
    text_lower = text.lower()
    hits = sum(1 for term in EVENT_TERMS if term in text_lower)
    return clamp(hits / 4.0)


def compute_recency_score(published_at):
    if not published_at:
        return 0.5

    days_old = (datetime.utcnow() - published_at).days

    if days_old <= 7:
        return 1.0
    if days_old <= 30:
        return 0.8
    if days_old <= 90:
        return 0.5
    return 0.2


def compute_novelty_score(title: str, content: str, db: Session) -> float:
    existing_docs = db.query(DocumentModel).all()
    title_lower = title.lower().strip()
    content_lower = content.lower().strip()

    for doc in existing_docs:
        if doc.title.lower().strip() == title_lower:
            return 0.1
        if doc.content.lower().strip() == content_lower:
            return 0.05

    return 1.0


def compute_final_score(
    source_score: float,
    keyword_score: float,
    country_score: float,
    semantic_score: float,
    event_score: float,
    recency_score: float,
    novelty_score: float,
) -> float:
    final = (
        0.20 * source_score
        + 0.15 * keyword_score
        + 0.15 * country_score
        + 0.20 * semantic_score
        + 0.15 * event_score
        + 0.10 * recency_score
        + 0.05 * novelty_score
    )
    return round(final, 4)


def document_model_to_schema(doc: DocumentModel) -> Document:
    matched_keywords = doc.matched_keywords.split("|") if doc.matched_keywords else []
    matched_countries = doc.matched_countries.split("|") if doc.matched_countries else []

    return Document(
        id=doc.id,
        source_id=doc.source_id,
        title=doc.title,
        url=doc.url,
        content=doc.content,
        published_at=doc.published_at,
        ingested_at=doc.ingested_at,
        matched_keywords=matched_keywords,
        matched_countries=matched_countries,
        score=DocumentScore(
            source_score=doc.source_score,
            keyword_score=doc.keyword_score,
            country_score=doc.country_score,
            semantic_score=doc.semantic_score,
            event_score=doc.event_score,
            recency_score=doc.recency_score,
            novelty_score=doc.novelty_score,
            final_score=doc.final_score,
        ),
    )


@app.get("/")
def root():
    return {"message": "Trade Monitor is running"}


@app.get("/sources", response_model=List[Source])
def list_sources(db: Session = Depends(get_db)):
    return db.query(SourceModel).all()


@app.post("/sources", response_model=Source)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    new_source = SourceModel(
        name=source.name,
        domain=source.domain,
        source_type=source.source_type,
        country_focus=source.country_focus,
        section_url=str(source.section_url) if source.section_url else None,
        priority_score=source.priority_score,
        is_active=source.is_active,
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


@app.get("/documents", response_model=List[Document])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentModel).all()
    return [document_model_to_schema(doc) for doc in docs]


@app.post("/documents", response_model=Document)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    source = db.query(SourceModel).filter(SourceModel.id == document.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    combined_text = f"{document.title} {document.content}"

    matched_keywords = compute_keyword_matches(combined_text)
    matched_countries = compute_country_matches(combined_text)

    source_score = compute_source_score(source)
    keyword_score = compute_keyword_score(matched_keywords)
    country_score = compute_country_score(matched_countries, source)
    semantic_score = compute_semantic_score(combined_text)
    event_score = compute_event_score(combined_text)
    recency_score = compute_recency_score(document.published_at)
    novelty_score = compute_novelty_score(document.title, document.content, db)

    final_score = compute_final_score(
        source_score=source_score,
        keyword_score=keyword_score,
        country_score=country_score,
        semantic_score=semantic_score,
        event_score=event_score,
        recency_score=recency_score,
        novelty_score=novelty_score,
    )

    new_doc = DocumentModel(
        source_id=document.source_id,
        title=document.title,
        url=str(document.url),
        content=document.content,
        published_at=document.published_at,
        ingested_at=datetime.utcnow(),
        matched_keywords="|".join(matched_keywords),
        matched_countries="|".join(matched_countries),
        source_score=round(source_score, 4),
        keyword_score=round(keyword_score, 4),
        country_score=round(country_score, 4),
        semantic_score=round(semantic_score, 4),
        event_score=round(event_score, 4),
        recency_score=round(recency_score, 4),
        novelty_score=round(novelty_score, 4),
        final_score=final_score,
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return document_model_to_schema(new_doc)
