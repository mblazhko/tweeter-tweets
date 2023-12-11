import asyncio
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx
from pprint import pprint

from utils import transform_to_datetime

URL = "https://nitter.net/search"
HEADERS = {
    "authority": "nitter.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "uk,uk-UA;q=0.9,sk;q=0.8,en-US;q=0.7,en;q=0.6",
}
counter = 0


class RequestScraper:
    def __init__(self):
        self.__url = URL
        self.__headers: dict[str[str]] = HEADERS
        self.__counter = 0
        self.__soup = None
        self.output = {}

    async def run_scraper(self, limit: int = 2, **params) -> dict:
        self.output.update(await self.__get_tweets_by_limit(limit=limit, **params))
        await asyncio.sleep(5)
        return self.output

    async def __get_tweets_by_limit(self, limit, **params):
        """
        :param limit: limit of pages to scrape, 10 is default
        :param params: params for request
        :return:
        """
        response = await self.__get_response(**params)

        await self.__make_soup(response)

        tweet_cards = await self.__get_tweet_cards()

        output = await self.__get_one_page_tweets(tweet_cards)

        pagination = self.__soup.find("a", string="Load more")
        await self.__if_pagination(pagination, limit, **params)

        return output

    async def __get_response(self, **params) -> httpx.Response:
        async with httpx.AsyncClient(timeout=100000) as client:
            response = await client.get(
                url=self.__url,
                params=params,
                headers=self.__headers,
            )

        return response

    async def __make_soup(self, response) -> None:
        self.__soup = BeautifulSoup(response.text, "html.parser")

    async def __get_tweet_cards(self) -> list:
        tweet_cards = self.__soup.select("div.timeline-item")
        return [card for card in tweet_cards if len(card.get("class")) == 1]

    async def __get_one_page_tweets(self, tweet_cards) -> dict:
        print(self.__counter)
        output = {}
        for card in tweet_cards:
            data = await self.__get_one_tweet_data(card)
            # await asyncio.sleep(0.5)
            output.update(data)
        return output

    async def __get_one_tweet_data(self, card) -> dict:
        username = card.select_one(".username").text
        tweet = card.select_one(".tweet-link")
        tweet_id = tweet.get("href").split("/")[-1].replace("#m", "")
        raw_content = card.select_one(".tweet-content.media-body").text
        date_time = (
            card.select_one(".tweet-date>a").get("title").replace("·", "")
        )

        output = {
            tweet_id: {
                "username": username,
                "raw_content": raw_content,
                "date": transform_to_datetime(date_time),
            }
        }

        return output

    async def __if_pagination(
        self, pagination, limit, **params
    ) -> dict | None:
        if pagination:
            
            if self.__counter >= limit:
                return
            next_page_link = pagination.get("href")
            self.__url = urljoin(self.__url, next_page_link)
            self.output.update(
                await self.__get_tweets_by_limit(limit=limit, **params)
            )
            self.__counter += 1


if __name__ == "__main__":
    params = {
        "q": "python",
        "since": "2023-1-01",
        "until": "2023-2-01",
    }
    scraper = RequestScraper()
    output = asyncio.run(scraper.run_scraper(**params))
    pprint(output)
