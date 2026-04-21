from db.repository import setup_database
from scraper.fetcher import run_scraper

if __name__ == "__main__":
    setup_database()

    run_scraper()
