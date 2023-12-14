from .query import Query
from concurrent_scrapper import ScrapperByDate
from app import app
from fake_http_header import FakeHttpHeader
from fastapi.responses import Response

@app.post("/search")
async def tweet_search(query_list: list[Query]):
    header = FakeHttpHeader().as_header_dict()
    {
        "query": "iberia",
        "since_time": "1702490520",
        "until_time": "1702490580"
    }
    # {
    #     "q":
    #     "since":
    #     "until":
    # }
    params = []
    for query in query_list:
        if Query.model_validate(query):
            param = query.model_dump(mode="json")
            param:dict
            param['q'] = param['query']
            param.pop('query')
            param['since'] = param['since_time']
            param.pop('since_time')
            param['until'] = param['until_time']
            param.pop('until_time')
        params.append(param)
        
    # params = [query.model_dump(mode='json') for query in query_list if Query.model_validate(query)]
    print(params)
    #TODO: add asyncio geather chunks
    async with ScrapperByDate(headers=header) as by_date_scraper:
        result = await by_date_scraper.async_run_scraper(urls="https://nitter.net/search", params=params)
        return result or Response({"msg":"No data found"}, status_code=404)