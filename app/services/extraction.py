from __future__ import annotations

import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


@dataclass
class ExtractedDocument:
    title: str
    clean_text: str
    raw_text: str
    published_at: str | None
    canonical_url: str | None
    language: str
    document_type: str
    is_pdf: bool


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


async def extract_html(url: str) -> ExtractedDocument:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = (soup.title.get_text(strip=True) if soup.title else url)
    canonical = None
    canonical_tag = soup.find("link", rel="canonical")
    if canonical_tag and canonical_tag.get("href"):
        canonical = canonical_tag["href"]

    published_at = None
    meta_candidates = [
        {"property": "article:published_time"},
        {"name": "pubdate"},
        {"name": "date"},
        {"name": "publish-date"},
    ]
    for attrs in meta_candidates:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            published_at = tag["content"]
            break

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    raw_text = soup.get_text(" ", strip=True)
    clean_text = _clean_text(raw_text)

    return ExtractedDocument(
        title=title,
        clean_text=clean_text,
        raw_text=raw_text,
        published_at=published_at,
        canonical_url=canonical,
        language="en",
        document_type="html",
        is_pdf=False,
    )
