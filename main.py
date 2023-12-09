from fastapi import FastAPI
from scrappers import RequestScraper

app = FastAPI()


@app.get("/search")
async def tweet_search(q: str, since: str = None, until: str = None):
    scraper = RequestScraper()
    result = await scraper.run_scraper(q=q, since=since, until=until)
    return {"tweets": result}
