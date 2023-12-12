from fake_http_header import FakeHttpHeader
from fastapi import FastAPI
from pydantic import BaseModel

from concurrent_scrapper import async_main

app = FastAPI()

class Query(BaseModel):
    q: str
    since: str
    until: str


@app.post("/search")
async def tweet_search(query_list: list[Query]):
    header = FakeHttpHeader().as_header_dict()
    params = [query.model_dump() for query in query_list]
    # params = {'q': q, 'since': since, 'until': until}
    result = await async_main(urls="https://nitter.net/search", headers=header, params=params)
    return result
