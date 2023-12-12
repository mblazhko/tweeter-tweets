import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor
import requests

PARAMS = {
    "q": "elon",
    "since": "2023-04-01",
    "until": "2023-05-01",
}

URL = "http://127.0.0.1:8000/search"

import asyncio
import httpx


async def async_make_request(url, params):
    async with httpx.AsyncClient(timeout=100000) as client:
        response = await client.post(url, params=params)
        print(response.url, response.json())

def make_request(url, params):
    with httpx.Client(timeout=10000) as client:
        response = client.get(url, params=params)
        return response.json()
        
async def async_main(url, params):
    tasks = [async_make_request(url=url, params=params) for _ in range(65)]

    await asyncio.gather(*tasks)
    
def main(url, params):
    with ThreadPoolExecutor() as executor:
        futures = [ executor.submit(make_request, url=url, params=params) for x in range(65)]
        for future in futures:
            try:
                data = future.result()
            except Exception as e:
                print(e)
            else:
                print(data)

if __name__ == "__main__":
    asyncio.run(async_main(url=URL, params=PARAMS))
# if __name__ == "__main__":
#     main(url=URL, params=PARAMS)