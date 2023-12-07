from fastapi import FastAPI

from scraper import scrape_tweeter_tweets_by_date

app = FastAPI()


@app.get("/search/")
async def tweet_search(query: str, since: str = None, until: str = None):
    result = await scrape_tweeter_tweets_by_date(query, since, until)
    return {"tweets": result}
