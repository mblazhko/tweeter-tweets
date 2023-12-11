from fastapi import FastAPI
from scrappers import RequestScraper
import uvicorn


app = FastAPI()


@app.get("/search")
async def tweet_search(q: str, since: str = None, until: str = None):
    scraper = RequestScraper()
    result = await scraper.run_scraper(q=q, since=since, until=until)
    return {"tweets": result}

if __name__ ==  "__main__":
    uvicorn.run("main:app", workers=12)