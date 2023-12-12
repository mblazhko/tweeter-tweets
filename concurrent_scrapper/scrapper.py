import requests
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from aiohttp import ClientSession
import asyncio
import json
from bs4 import BeautifulSoup
from dateutil import parser
import random


def transform_to_datetime(date: str) -> str:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return str(timestamp)

async def get_with_aiohttp(session: ClientSession, url: str, params: dict = {}, headers: dict = {}, proxy: str | None = None, timeout: int = 10) -> (int, dict, bytes):
    response = await session.get(url=url, params=params, headers=headers, proxy=proxy, timeout=timeout)
    counter = 0
    while response.status != 200:
        if counter >= 5:
            break
        await asyncio.sleep(random.randint(1, 3))
        response = await session.get(url=url, params=params, headers=headers, proxy=proxy, timeout=timeout)
        counter += 1
        print(counter)
    response_content = None
    try:
        response_content = await response.read()
    except:
        ...

    return response_content

async def get_with_aiohttp_parallel(session: ClientSession, urls_list: [str], params: dict = {}, headers: dict = {}, proxy: str | None = None, timeout: int = 10):
    start_time = time.time()
    results = await asyncio.gather(*[get_with_aiohttp(session, url, params, headers, proxy, timeout) for url in urls_list])
    return results, time.time() - start_time



def scrape(content:bytes)->dict:
    def get_one_tweet_data(card)->dict:
        username = card.select_one(".username").text
        tweet = card.select_one(".tweet-link")
        tweet_id = tweet.get("href").split("/")[-1].replace("#m", "")
        raw_content = card.select_one(".tweet-content.media-body").text
        date_time = card.select_one(".tweet-date>a").get("title").replace("·", "")
        output = {
            tweet_id: {
                "username": username,
                "raw_content": raw_content,
                "date": transform_to_datetime(date_time),
            }
        }
        return output
    
    soup = BeautifulSoup(content, "html.parser")
    cards = list(filter(lambda x: len(x.get("class")) == 1, soup.select("div.timeline-item"))) 
    output = {}
    for tweet_data in map(get_one_tweet_data, cards):
        output.update(tweet_data)
    return output

async def async_main(urls, params, headers):
    print('-'*40)
    # Benchmark aiohttp
    start_time = time.time()
    speeds_aiohttp = []
    async with ClientSession() as session:
        results, t = await get_with_aiohttp_parallel(session, urls, params, headers)
        v = len(urls) / t
        print('AIOHTTP: Took ' + str(round(t, 2)) +
                ' s, with speed of ' + str(round(v, 2)) + ' r/s')
        speeds_aiohttp.append(v)
    print('-'*40)
  
    scraped_results = []
    with ThreadPoolExecutor() as executor:
        for scraped in executor.map(scrape, results):
            scraped_results.append(scraped)
    return speeds_aiohttp, scraped_results, time.time() - start_time


# URL list
URL = "https://nitter.net/search"
HEADERS = {
    "authority": "nitter.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "uk,uk-UA;q=0.9,sk;q=0.8,en-US;q=0.7,en;q=0.6",
}
urls = [ URL for i in range(0, 65) ]
params = {
    "q": "python",
    "since": "2023-1-01",
    "until": "2023-2-01",
}
speeds_aiohttp, scraped, a = asyncio.run(async_main(urls, params, HEADERS))
# Calculate averages
avg_speed_aiohttp = sum(speeds_aiohttp) / len(speeds_aiohttp)
print('--------------------')
print('AVG SPEED AIOHTTP: ' + str(round(avg_speed_aiohttp, 2)) + ' r/s')
print('IT TOTALLY TOOKS:'  + str(a))
input()
print([str(x) for x in scraped], sep="\n" + "-"*40)

