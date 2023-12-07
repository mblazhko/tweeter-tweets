import asyncio
from datetime import datetime
from urllib.parse import urljoin

from dateutil import parser
from playwright.async_api import async_playwright, Locator, Page

TWEET_SEARCH_URL = "https://nitter.net/search"


class NitterScraper:
    def __init__(self):
        self._browser = None

    async def scrape_tweeter_tweets_by_date(
            self,
            query: str,
            since: str = None,
            until: str = None
    ) -> dict:
        async with async_playwright() as p:
            if not self._browser:
                self._browser = await p.firefox.launch(headless=False)
            page = await self._browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            )
            await page.goto(
                f"https://nitter.net/search?f=tweets&q={query}&since={since}&until={until}&near="
            )

            result = await self._scrape_pages(page)

            await self._browser.close()

            return result

    async def _scrape_pages(self, page: Page) -> dict:
        result = {}
        for _ in range(10):
            page_result = await self._scrape_one_page(page)
            result.update(page_result)
        return result

    async def _scrape_one_page(self, page: Page) -> dict:
        one_page_data = {}
        tweets_date = await page.locator(".tweet-date a").all()
        tweets_content = await page.locator(".tweet-content").all()
        for item, content in zip(tweets_date, tweets_content):
            output = await self._get_tweet_info(item, content)
            one_page_data[output["tweet_id"]] = output
        next_page_link = await page.get_by_role(
            "link", name="Load more"
        ).get_attribute("href")
        await page.goto(
            urljoin(
                TWEET_SEARCH_URL,
                next_page_link
            )
        )

        return one_page_data

    async def _get_tweet_info(self, item: Locator, content: Locator) -> dict:
        link = await item.get_attribute("href")
        username = await self._get_username(link)

        raw_content = await content.inner_text()

        tweet_id = link.split("/")[-1].replace("#m", "")

        tweet_date = await item.get_attribute("title")
        date_time = await self._transform_to_datetime(tweet_date)

        output = {
            "tweet_id": tweet_id,
            "raw_content": raw_content,
            "username": username,
            "datetime": str(date_time),
        }

        return output

    async def _transform_to_datetime(self, date: str) -> datetime:
        date_string = date.replace("·", "")
        timestamp = parser.parse(date_string)
        return timestamp

    async def _get_username(self, link) -> str:
        return link.split("/")[1]


if __name__ == '__main__':
    scraper = NitterScraper()
    result = asyncio.run(
        scraper.scrape_tweeter_tweets_by_date(
            query="python",
            since="2023-12-06",
            until="2023-12-07"
        )
    )

    print(result)
