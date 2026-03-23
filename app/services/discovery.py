from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import feedparser
import httpx
from bs4 import BeautifulSoup


@dataclass
class CandidateUrl:
    url: str
    title: str | None = None
    discovered_from: str | None = None


async def discover_from_rss(feed_url: str) -> list[CandidateUrl]:
    parsed = feedparser.parse(feed_url)
    results: list[CandidateUrl] = []
    for entry in parsed.entries:
        link = getattr(entry, "link", None)
        title = getattr(entry, "title", None)
        if link:
            results.append(CandidateUrl(url=link, title=title, discovered_from=feed_url))
    return results


async def discover_links_from_page(page_url: str) -> list[CandidateUrl]:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(page_url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: list[CandidateUrl] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        text = anchor.get_text(" ", strip=True)
        if href and text:
            results.append(CandidateUrl(url=href, title=text, discovered_from=page_url))
    return results


async def fetch_sitemap_xml(url: str) -> str:
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
