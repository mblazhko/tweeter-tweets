from .query import Query
from concurrent_scrapper import ScrapperByDate
from app import app
from fake_http_header import FakeHttpHeader


@app.post("/search")
async def tweet_search(query_list: list[Query]):
    header = FakeHttpHeader().as_header_dict()

    params = [query.model_dump(mode='json') for query in query_list if Query.model_validate(query)]
    print(params)
    #TODO: add asyncio geather chunks
    async with ScrapperByDate(headers=header) as by_date_scraper:
        result = await by_date_scraper.async_run_scraper(urls="https://nitter.net/search", params=params)
        return result