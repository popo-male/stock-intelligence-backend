from core.config import load_config
from db.repository import setup_database
from nlp.analyzer import process_unscored_articles
from scraper.fetcher import run_scraper

if __name__ == "__main__":
    config = load_config()
    setup_database()

    run_scraper(config)

    process_unscored_articles()

    print("Pipeline execution complete!")
