import asyncio
from bs4 import BeautifulSoup
import httpx
from dateutil import parser
from pprint import pprint

def transform_to_datetime(date: str) -> str:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return str(timestamp)

URL = "https://nitter.net/search"
HEADERS = {
        "authority": "nitter.net",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "uk,uk-UA;q=0.9,sk;q=0.8,en-US;q=0.7,en;q=0.6",
    }
counter = 0
async def get_page(url=URL, headers=HEADERS, limit:int=10, output:dict={}, **params)->dict:
    async with httpx.AsyncClient(timeout=20) as client:
        # f"https://nitter.net/search?f=tweets&q={query}&since={since}&until={until}&near=",
        r = await client.get(
            url=url,
            params=params,
            headers=headers,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        print(url)
        tweet_cards = soup.select("div.timeline-item")
        for card in tweet_cards:
            if card.select_one(".tweet-link"):
                username = card.select_one(".username").text
                tweet = card.select_one(".tweet-link")
                tweet_id = tweet.get("href").split("/")[-1].replace("#m", "")
                tweet_text = tweet.text
                raw_content = card.select_one(".tweet-content.media-body").text
                date_time = card.select_one(
                    ".tweet-date>a").get("title").replace("·", "")

                output.update(
                    {
                        tweet_id: {
                            "username": username,
                            "raw_content": raw_content,
                            "date": transform_to_datetime(date_time),
                        }
                    }
                )
        pagination = soup.select("div.show-more>a")
        # output['next_page'] = pagination
        if pagination:
            global counter
            counter += 1
            if counter > limit:
                return output
            return await get_page(url=URL+pagination[-1].get("href"), headers=headers, limit=limit, output=output, **params)
        return output



if __name__ == '__main__':
    params = {
        "q":"python",
        "since":"2023-1-01",
        "until":"2023-2-01",
    }
    print( asyncio.run(get_page(**params)) )
