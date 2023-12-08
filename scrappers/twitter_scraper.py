import asyncio
import os

from scrappers.scrapper import Scraper
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

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
        self.__user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    async def __login_user(self, login: str, password: str, username: str) -> Page:
        await self.__create_browser()
        context = await self._browser.new_context(
            user_agent=self.__user_agent
        )
        page = await context.new_page()
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

        await context.storage_state(path="twitter_state.json")

        return page

    async def scrape_tweeter_tweets_by_date(
            self,
            query: str,
            since: str = None,
            until: str = None
    ) -> dict:
        is_file = os.path.isfile("twitter_state.json")
        if not is_file:
            await self.__login_user(
                self.__login,
                self.__password,
                self.__username
            )
        else:
            await self.__create_browser()
        context = await self._browser.new_context(
            storage_state="twitter_state.json"
        )
        page = await context.new_page()
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

    async def __create_browser(self):
        playwright = await async_playwright().start()
        self._browser = await playwright.firefox.launch(headless=False)


if __name__ == '__main__':
    scraper = TwitterScraper(LOGIN, PASSWORD, USERNAME)
    asyncio.run(scraper.scrape_tweeter_tweets_by_date(
        query="python", since="2023-12-06", until="2023-12-07"
    ))
