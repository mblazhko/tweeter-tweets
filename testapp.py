import asyncio
import httpx


QUERIES = [
    {
        "query": "elon",
        "since": "2023-01-01",
        "until": "2023-02-01",
        "near": None
    } for _ in range(5)
]


async def client_get(params):
    async with httpx.AsyncClient(timeout=100000) as client:
        response = await client.get("http://127.0.0.1:8000/search", params=params)
        print(response.url)
        return response


async def read_search(queries):
    tasks = []
    for query in queries:
        tasks.append(client_get(query))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(read_search(QUERIES))