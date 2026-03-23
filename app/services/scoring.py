from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from hashlib import sha256
from math import sqrt
from typing import Iterable

from dateutil import parser
from sqlalchemy.orm import Session

from app.core.config import DEFAULT_TOPIC_PROFILES, EVENT_KEYWORDS, DEFAULT_COUNTRY_TERMS
from app.models.document import Document
from app.models.source import Source


@dataclass
class ScoreBreakdown:
    keyword_score: float
    entity_score: float
    semantic_score: float
    source_score: float
    event_score: float
    recency_score: float
    novelty_score: float
    final_score: float
    matched_entities: list[str]
    matched_topics: list[str]
    event_type: str | None
    summary: str


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def content_hash(text: str) -> str:
    return sha256(normalize_text(text).encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    return [t.strip(".,:;!?()[]{}\"'").lower() for t in text.split() if t.strip()]


def term_frequency_score(text: str, terms: Iterable[str], weight: float = 1.0) -> float:
    body = normalize_text(text)
    total = 0.0
    for term in terms:
        count = body.count(term.lower())
        total += min(count, 3) * weight
    return total


def text_to_vector(text: str) -> dict[str, float]:
    tokens = tokenize(text)
    vec: dict[str, float] = {}
    for token in tokens:
        if len(token) < 3:
            continue
        vec[token] = vec.get(token, 0.0) + 1.0
    return vec


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    common = set(a).intersection(b)
    numerator = sum(a[k] * b[k] for k in common)
    norm_a = sqrt(sum(v * v for v in a.values()))
    norm_b = sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def centroid_similarity(text: str, anchor_texts: list[str]) -> float:
    doc_vec = text_to_vector(text)
    sims = [cosine_similarity(doc_vec, text_to_vector(anchor)) for anchor in anchor_texts]
    return sum(sims) / len(sims) if sims else 0.0


def detect_event_type(text: str) -> tuple[str | None, float]:
    body = normalize_text(text)
    best_event = None
    best_score = 0.0
    for event_type, terms in EVENT_KEYWORDS.items():
        score = sum(1 for t in terms if t in body)
        if score > best_score:
            best_score = float(score)
            best_event = event_type
    if best_event is None:
        return None, 0.1
    return best_event, min(1.0, 0.2 + 0.15 * best_score)


def detect_entities(title: str, body: str, source: Source | None = None) -> tuple[list[str], float]:
    text = f"{title} {body}".lower()
    matched = []
    score = 0.0

    for country in DEFAULT_COUNTRY_TERMS:
        if country in text:
            matched.append(country)
            score += 0.12 if country in title.lower() else 0.08

    custom_port_terms = [
        "port", "terminal", "customs", "maritime", "shipping", "logistics corridor",
        "port authority", "container terminal", "revenue authority"
    ]
    for term in custom_port_terms:
        if term in text:
            matched.append(term)
            score += 0.06

    if source and source.country_focus and source.country_focus.lower() in text:
        score += 0.12
        matched.append(source.country_focus.lower())

    unique_matched = sorted(set(matched))
    return unique_matched, min(score, 1.0)


def topic_scores(text: str) -> tuple[list[str], float, float]:
    matched_topics: list[str] = []
    keyword_total = 0.0
    semantic_best = 0.0

    for topic_name, profile in DEFAULT_TOPIC_PROFILES.items():
        pos = term_frequency_score(text, profile["positive_terms"], weight=0.12)
        neg = term_frequency_score(text, profile["negative_terms"], weight=0.15)
        sem = centroid_similarity(text, profile["anchor_texts"])
        topic_strength = max(0.0, pos - neg)
        if topic_strength > 0.18 or sem > 0.14:
            matched_topics.append(topic_name)
        keyword_total += topic_strength
        semantic_best = max(semantic_best, sem)

    return matched_topics, min(keyword_total, 1.0), min(semantic_best, 1.0)


def recency_score(published_at: str | None) -> float:
    if not published_at:
        return 0.45
    try:
        dt = parser.parse(published_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days = max((now - dt).days, 0)
    except Exception:
        return 0.45

    if days <= 7:
        return 1.0
    if days <= 30:
        return 0.8
    if days <= 90:
        return 0.5
    return 0.2


def novelty_score(db: Session, title: str, clean_text: str) -> float:
    docs = db.query(Document).order_by(Document.id.desc()).limit(25).all()
    if not docs:
        return 1.0

    candidate = normalize_text(f"{title} {clean_text[:1000]}")
    max_sim = 0.0
    for doc in docs:
        prior = normalize_text(f"{doc.title} {doc.clean_text[:1000]}")
        max_sim = max(max_sim, SequenceMatcher(None, candidate, prior).ratio())
    return max(0.0, 1.0 - max_sim)


def simple_summary(title: str, clean_text: str, matched_topics: list[str], event_type: str | None) -> str:
    excerpt = " ".join(clean_text.split()[:40])
    topic_text = ", ".join(matched_topics) if matched_topics else "general"
    event_text = event_type if event_type else "update"
    return f"{title}. Topic: {topic_text}. Event: {event_text}. Excerpt: {excerpt}"


def final_weighted_score(
    source_score: float,
    entity_score: float,
    semantic_score: float,
    event_score: float,
    recency_score_value: float,
    novelty_score_value: float,
) -> float:
    return round(
        0.20 * source_score
        + 0.20 * entity_score
        + 0.25 * semantic_score
        + 0.15 * event_score
        + 0.10 * recency_score_value
        + 0.10 * novelty_score_value,
        4,
    )


def score_document(
    db: Session,
    source: Source,
    title: str,
    clean_text: str,
    published_at: str | None,
) -> ScoreBreakdown:
    matched_entities, entity_score_value = detect_entities(title, clean_text, source)
    matched_topics, keyword_score_value, semantic_score_value = topic_scores(clean_text)
    event_type, event_score_value = detect_event_type(f"{title} {clean_text}")
    recency_score_value = recency_score(published_at)
    novelty_score_value = novelty_score(db, title, clean_text)
    source_score_value = min(1.0, (source.trust_score * 0.7) + (source.priority_score * 0.3))
    final_score_value = final_weighted_score(
        source_score_value,
        entity_score_value,
        semantic_score_value,
        event_score_value,
        recency_score_value,
        novelty_score_value,
    )
    summary = simple_summary(title, clean_text, matched_topics, event_type)

    return ScoreBreakdown(
        keyword_score=round(keyword_score_value, 4),
        entity_score=round(entity_score_value, 4),
        semantic_score=round(semantic_score_value, 4),
        source_score=round(source_score_value, 4),
        event_score=round(event_score_value, 4),
        recency_score=round(recency_score_value, 4),
        novelty_score=round(novelty_score_value, 4),
        final_score=final_score_value,
        matched_entities=matched_entities,
        matched_topics=matched_topics,
        event_type=event_type,
        summary=summary,
    )
