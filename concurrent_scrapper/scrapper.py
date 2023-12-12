from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession
import asyncio
from bs4 import BeautifulSoup
from dateutil import parser
from tenacity import retry, stop_after_attempt, wait_random

def transform_to_datetime(date: str) -> str:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return str(timestamp)


@retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3))
async def get_with_aiohttp(
    session: ClientSession,
    url: str,
    params: dict = {},
    proxy: str | None = None,
    timeout: int = 10,
) -> (int, dict, bytes):
    """
    Summary:
        The get_with_aiohttp function is an asynchronous function that uses the aiohttp library to make HTTP GET requests.
        It takes in a ClientSession object, a URL,
        and optional parameters, headers, proxy, and timeout.
        The function retries the request up to 5 times with random wait times between 1 and 3 seconds using the tenacity library.
        It returns a tuple containing the HTTP status code,
        response headers, and response content.
    Arguments:
        :param session:
        :param url:
        :param params:
        :param headers:
        :param proxy:
        :param timeout:
        :return:
    """

    response = await session.get(
        url=url, params=params, proxy=proxy, timeout=timeout
    )

    response_content = await response.read()

    return response_content


async def get_with_aiohttp_parallel(
    session: ClientSession,
    urls_list: [str],
    params: dict = {},
    proxy: str | None = None,
    timeout: int = 10,
):
    """
    Summary:
        The get_with_aiohttp_parallel function is an asynchronous function
        that takes in a ClientSession object,
        a list of URLs, and optional parameters, headers, proxy, and timeout.
        It uses the get_with_aiohttp function
        to make parallel asynchronous HTTP requests to the specified URLs with the given parameters.
        The function returns a list of results,
        where each result corresponds to the response of a specific URL.

    Arguments:
        :param session: The aiohttp ClientSession object used to make HTTP requests.
        :param urls_list: A list of URLs to make HTTP requests to.
        :param params: Optional parameters to include in the requests. It can be a single dictionary or a list of dictionaries, where each dictionary corresponds to the parameters for a specific URL.
        :param headers: Optional headers to include in the requests.
        :param proxy: Optional proxy URL to use for the requests.
        :param timeout: Optional timeout value for the requests in seconds.
        :return:
    """
    results = None
    if (
        isinstance(urls_list, list)
        and isinstance(params, list)
        and len(urls_list) == len(params)
    ):
        results = await asyncio.gather(
            *[
                get_with_aiohttp(session, url, param, proxy, timeout)
                for url, param in zip(urls_list, params)
            ]
        )
    elif isinstance(urls_list, list):
        results = await asyncio.gather(
            *[
                get_with_aiohttp(session, url, params, proxy, timeout)
                for url in urls_list
            ]
        )
    elif isinstance(params, list):
        results = await asyncio.gather(
            *[
                get_with_aiohttp(
                    session, urls_list, param, proxy, timeout
                )
                for param in params
            ]
        )
    else:
        results = await get_with_aiohttp(
            session, urls_list, params, proxy, timeout
        )
    return results


def scrape(content: bytes) -> dict:
    """
    Summary:
        The scrape function takes in HTML content as input
        and extracts relevant data from it.
        It uses BeautifulSoup to parse the content
        and filter out specific elements.
        It then iterates over the filtered elements
        to extract data such as username,
        tweet ID, raw content, and date.
        The extracted data is stored in a dictionary and returned as the output.
    Arguments:
        :param content:
        :return:
    """

    if not isinstance(content, (bytes, str)):
        raise TypeError("Content must be of type bytes or str.")

    def get_one_tweet_data(card) -> dict:
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

    soup = BeautifulSoup(content, "lxml")
    cards = list(
        filter(
            lambda x: len(x.get("class")) == 1,
            soup.select("div.timeline-item"),
        )
    )
    output = {}
    for tweet_data in map(get_one_tweet_data, cards):
        output.update(tweet_data)
    return output


async def async_main(
    urls: str | list[str], params: dict | list[dict], headers: dict
) -> dict[str, dict]:
    """
    Summary:
        This code defines an async_main function that takes in URLs,
        parameters, and headers as inputs.
        It uses the get_with_aiohttp_parallel function
        to make asynchronous HTTP requests and retrieve the responses.
        The responses are then passed to the scrape function,
        which extracts relevant data from the HTML content.
        The scraped data is stored in a dictionary and returned as the output.

    Example Usage:
        urls = ["https://example.com/page1", "https://example.com/page2"]
        params = [{"param1": "value1"}, {"param2": "value2"}]
        headers = {"User-Agent": "Mozilla/5.0"}

        result = await async_main(urls, params, headers)
        print(result)

    Output:
        {
          "tweet_id1": {
            "username": "user1",
            "raw_content": "This is a tweet",
            "date": "2022-01-01 12:00:00"
          },
          "tweet_id2": {
            "username": "user2",
            "raw_content": "Another tweet",
            "date": "2022-01-02 10:30:00"
          }
        }

    Arguments:
        :param headers: The URLs to make HTTP requests to.
        :param urls: The parameters to include in the requests.
        :param params: The headers to include in the requests.
    """

    async with ClientSession(headers=headers) as session:
        results = await get_with_aiohttp_parallel(
            session, urls, params
        )

    scraped_results = {}

    with ThreadPoolExecutor() as executor:
        if isinstance(results, list):
            for scraped in executor.map(scrape, results):
                scraped_results.update(scraped)
        else:
            scraped_results.update(scrape(results))
    return scraped_results
