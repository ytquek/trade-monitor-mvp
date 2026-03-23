"""Simple seed script for local testing.

Run:
python -m app.workers.sample_seed
"""
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, init_db
from app.models.source import Source


def main() -> None:
    init_db()
    db: Session = SessionLocal()
    try:
        if db.query(Source).count() == 0:
            db.add_all([
                Source(
                    name="Kenya Ports Authority",
                    domain="kpa.co.ke",
                    country_focus="Kenya",
                    source_type="port_authority",
                    fetch_method="static_html",
                    trust_score=0.95,
                    priority_score=0.9,
                    crawl_interval_minutes=240,
                    is_active=True,
                ),
                Source(
                    name="Generic Maritime News",
                    domain="example-maritime-news.com",
                    country_focus="Regional",
                    source_type="news",
                    fetch_method="rss",
                    trust_score=0.75,
                    priority_score=0.7,
                    crawl_interval_minutes=180,
                    is_active=True,
                ),
            ])
            db.commit()
            print("Seeded sample sources")
        else:
            print("Sources already exist")
    finally:
        db.close()


if __name__ == "__main__":
    main()
