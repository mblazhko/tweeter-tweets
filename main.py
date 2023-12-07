from fastapi import FastAPI

from scrappers import NitterScraper

app = FastAPI()


@app.get("/search/")
async def tweet_search(query: str, since: str = None, until: str = None):
    scraper = NitterScraper()
    result = await scraper.scrape_tweeter_tweets_by_date(query, since, until)
    return {"tweets": result}
