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
    def __init__(self, username: str, password: str, login: str):
        super().__init__()
        self.__username = username
        self.__password = password
        self.__login = login
        self._logged_page: Page = None

    async def __login_user(self, login: str, password: str, username: str) -> Page:
        p = await async_playwright().start()
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

        challenge = page.get_by_test_id("ocfEnterTextTextInput")
        if await challenge.count():
            await challenge.type(username)
            await page.click("text=Next")

        await page.type("input[name='password']", password)

        await page.click("text=Log in")
        await page.wait_for_url(url="https://twitter.com/home")

        return page

    async def scrape_tweeter_tweets_by_date(
            self,
            query: str,
            since: str = None,
            until: str = None
    ) -> dict:
        page = await self.__login_user(
            self.__login,
            self.__password,
            self.__username
        )
        await page.goto("https://twitter.com/search-advanced")
        await page.type("input[name='allOfTheseWords']", query)

        if since:
            since_date = since.split("-")

            since_year, since_month, since_day = since_date
            await page.select_option(
                selector=f"select#SELECTOR_2",
                value=since_month
            )
            await page.select_option(
                selector=f"select#SELECTOR_3",
                value=since_day.replace("0", "") if "0" in since_day else since_day
            )
            await page.select_option(
                selector=f"select#SELECTOR_4",
                value=since_year
            )

        if until:
            until_date = until.split("-")
            until_year, until_month, until_day = until_date
            await page.select_option(
                selector=f"select#SELECTOR_5",
                value=until_month
            )
            await page.select_option(
                selector=f"select#SELECTOR_6",
                value=until_day.replace("0", "") if "0" in until_day else until_day
            )
            await page.select_option(
                selector=f"select#SELECTOR_7",
                value=until_year
            )

        await page.click("span[text='Search']")
        await page.wait_for_timeout(timeout=100000)


if __name__ == '__main__':
    scraper = TwitterScraper(LOGIN, PASSWORD, USERNAME)
    asyncio.run(scraper.scrape_tweeter_tweets_by_date(
        query="python", since="2023-12-06", until="2023-12-07"
    ))
