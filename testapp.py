import asyncio
import httpx


QUERIES = [
    {
        "q": "elon",
        "since": "2023-04-01",
        "until": "2023-05-01",
    } for _ in range(65)
]


async def client_get(params):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/search", params=params)
        return response


async def read_search(queries):
    tasks = []
    for query in queries:
        tasks.append(client_get(query))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(read_search(QUERIES))
