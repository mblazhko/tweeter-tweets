import asyncio
from datetime import datetime

from dateutil import parser
from playwright.async_api import async_playwright, Locator


async def get_username(link) -> str:
    return link.split("/")[1]


async def transform_to_datetime(date: str) -> datetime:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return timestamp


async def get_tweet_info(item: Locator, content: Locator) -> dict:
    link = await item.get_attribute("href")
    username = await get_username(link)

    raw_content = await content.inner_text()

    tweet_id = link.split("/")[-1].replace("#m", "")

    tweet_date = await item.get_attribute("title")
    datetime = await transform_to_datetime(tweet_date)

    output = {
        "tweet_id": tweet_id,
        "raw_content": raw_content,
        "username": username,
        "datetime": str(datetime),
    }

    return output


async def scrape_tweeter_tweets_by_date(
        query: str,
        since: str = None,
        until: str = None
) -> dict:
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        )
        await page.goto(
            f"https://nitter.net/search?f=tweets&q={query}&since={since}&until={until}&near="
        )

        result = {}

        tweets_date = await page.locator(".tweet-date a").all()
        tweets_content = await page.locator(".tweet-content").all()
        for item, content in zip(tweets_date, tweets_content):
            output = await get_tweet_info(item, content)
            result[output["tweet_id"]] = output

        await browser.close()

        return result


if __name__ == '__main__':
    result = asyncio.run(
        scrape_tweeter_tweets_by_date(
            query="python",
            since="2023-12-06",
            until="2023-12-07"
        )
    )

    print(result)
