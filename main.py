import time
from fastapi import FastAPI
from scrappers import NitterScraper, get_page
import uvicorn
app = FastAPI()


@app.get("/search")
async def tweet_search(q: str, since: str = None, until: str = None):
    start = time.time()
    result = await get_page(q=q, since=since, until=until)
    end = time.time() - start
    print(end)
    return {"tweets": result}

if __name__ ==  "__main__":
    uvicorn.run("main:app", workers=12)