import asyncio
import os

from scrappers.scrapper import Scraper
from datetime import datetime
from urllib.parse import urljoin
from dotenv import load_dotenv
from dateutil import parser
from playwright.async_api import async_playwright, Locator, Page

load_dotenv()

LOGIN = os.getenv("TWITTER_LOGIN")
PASSWORD = os.getenv("TWITTER_PASSWORD")
USERNAME = os.getenv("TWITTER_USERNAME")


class TwitterScraper(Scraper):
    def __init__(self):
        super().__init__()
        self._logged_page = None

    async def _login(self, login: str, password: str, username: str) -> dict:
        async with async_playwright() as p:
            if not self._browser:
                self._browser = await p.firefox.launch(headless=False)
            page = await self._browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            )
            await page.goto(
                f"https://twitter.com/i/flow/login"
            )

            await page.type("input[autocomplete='username']", login)
            await page.click("text=Next")

            challenge = page.locator(
                "input[data-testid='ocfEnterTextTextInput']")
            if challenge:
                await challenge.type(username)
                await page.click("text=Next")

            await page.type("input[autocomplete='current-password']", password)

            await page.click("text=Log in")
            await page.wait_for_timeout(1000000000)
            await page.screenshot(path='e.png')

            self._logged_page = page

    async def scrape_tweeter_tweets_by_date(
            self,
            query: str,
            since: str = None,
            until: str = None
    ) -> dict:
        ...




if __name__ == '__main__':
    scraper = TwitterScraper()
    asyncio.run(scraper.login(LOGIN, PASSWORD, USERNAME))
