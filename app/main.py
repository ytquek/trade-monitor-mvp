from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

app = FastAPI(title="Trade Monitor MVP")

class SourceCreate(BaseModel):
    name: str
    domain: str
    source_type: str
    country_focus: Optional[str] = None
    section_url: Optional[HttpUrl] = None
    priority_score: int = 5
    is_active: bool = True

class Source(SourceCreate):
    id: int

SOURCES: List[Source] = []

@app.get("/")
def root():
    return {"message": "Trade Monitor is running"}

@app.get("/sources", response_model=List[Source])
def list_sources():
    return SOURCES

@app.post("/sources", response_model=Source)
def create_source(source: SourceCreate):
    new_source = Source(id=len(SOURCES) + 1, **source.model_dump())
    SOURCES.append(new_source)
    return new_source
