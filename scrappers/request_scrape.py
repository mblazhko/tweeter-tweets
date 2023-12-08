import asyncio
from bs4 import BeautifulSoup
import httpx
from dateutil import parser


def transform_to_datetime(date: str) -> str:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return str(timestamp)


async def get_page(query, since, until):
    headers = {
        "authority": "nitter.net",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "uk,uk-UA;q=0.9,sk;q=0.8,en-US;q=0.7,en;q=0.6",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url=f"https://nitter.net/search?f=tweets&q={query}&since={since}&until={until}&near=",
            headers=headers,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        usernames = soup.find_all("a", class_="fullname")
        tweets = soup.find_all("a", class_="tweet-link")
        raw_content = soup.find_all("div", class_="tweet-content media-body")
        date_times = [x.get("title").replace("·", "") for x in soup.select(".tweet-date>a")]
        for username, tweet, content, date_time in zip(usernames, tweets, raw_content, date_times):
            tweet_id = tweet.get("href").split("/")[-1].replace("#m", "")
            username = username.get_text()
            raw = content.get_text()
            date = transform_to_datetime(date_time)
            output = {
                "username": username,
                "tweet_id": tweet_id,
                "raw_content": raw,
                "date": date,
            }
            print(output)


if __name__ == '__main__':
    asyncio.run(get_page(query="python", since="2023-1-01", until="2023-1-02"))