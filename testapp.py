import asyncio
import httpx

PARAMS = {
    "q": "elon",
    "since": "2023-04-01",
    "until": "2023-05-01",
}

URL = "http://127.0.0.1:8000/search"

import asyncio
import httpx


async def make_request(url, params):
    async with httpx.AsyncClient(timeout=100000) as client:
        response = await client.get(url, params=params)
        print(response.status_code, response.json())


async def main(url, params):
    tasks = [make_request(url=url, params=params) for _ in range(65)]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(url=URL, params=PARAMS))
