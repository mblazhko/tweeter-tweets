from concurrent.futures import ThreadPoolExecutor
import asyncio
from fake_http_header import FakeHttpHeader
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random

from concurrent_scrapper.abstract_scraper import ABCScraper
from concurrent_scrapper.utils import transform_to_datetime


class ScrapperByDate(ABCScraper):
    def __init__(
            self,
            proxy: dict | str | None = None,
            headers: dict | None = None,
            timeout: int = 10
    ):
        self._proxy = proxy
        self._headers = headers or FakeHttpHeader().as_header_dict()
        self._timeout = timeout or 10

    async def __aenter__(self):
        self._session = ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._session.close()

    async def async_run_scraper(
        self, urls: str | list[str], params: dict | list[dict]
    ) -> dict[str, dict]:
        """
        Summary:
            The async_run_scraper method is an asynchronous method
            that is part of the ScrapperByDate class.
            It takes in a list of URLs and a list of parameters as inputs.
            It uses the __get_result_with_aiohttp_parallel method
            to make parallel asynchronous HTTP requests to the specified URLs with the given parameters.
            It then uses a ThreadPoolExecutor
            to process the results of the HTTP requests in parallel.
            The __parse method is called for each result
            to extract relevant data from the HTML content.
            The extracted data is stored in a dictionary
            and returned as the output.

        Inputs:
            urls:
                A string or a list of strings
                representing the URLs to make HTTP requests to.
            params:
                A dictionary or a list of dictionaries
                representing the parameters to include in the requests.
                Each dictionary corresponds to the parameters for a specific URL.

        Outputs:
            A dictionary containing the scraped data.
            The keys of the dictionary are the tweet IDs,
            and the values are dictionaries containing the username,
            raw content, and date of each tweet.
        """

        if not self._session:
            raise NotImplementedError(
                f"Can't create an instance of {self.__class__.__name__} without using 'with' operator"
            )

        results = await self.__get_result_with_aiohttp_parallel(urls, params)

        scraped_results = {}

        with ThreadPoolExecutor() as executor:
            if isinstance(results, list):
                for scraped in executor.map(self.__parse, results):
                    scraped_results.update(scraped)
            else:
                scraped_results.update(self.__parse(results))
        return scraped_results
    
    async def __get_result_with_aiohttp_parallel(
        self,
        urls_list: [str],
        params: dict = {},
    ) -> tuple:
        """
        Summary:
            The __get_result_with_aiohttp_parallel method is an asynchronous function
            that takes in a list of URLs and optional parameters.
            It uses other private methods
            to make parallel asynchronous HTTP requests to the specified URLs with the given parameters.
            The method returns a list of results,
            where each result corresponds to the response of a specific URL.

        Inputs:
            urls_list (list[str]):
                A list of URLs to make HTTP requests to.
            params (dict):
                Optional parameters to include in the requests.
                It can be a single dictionary or a list of dictionaries,
                where each dictionary corresponds to the parameters for a specific URL.

        Outputs:
            results (tuple):
                A list of results,
                where each result corresponds to the response of a specific URL.
        """
        if (
            isinstance(urls_list, list)
            and isinstance(params, list)
            and len(urls_list) == len(params)
        ):
            results = await self.__get_content_with_multiple_urls_and_params(
                urls_list,
                params
            )
        elif isinstance(urls_list, list):
            results = await self.__get_content_with_multiple_urls(urls_list, params)
        elif isinstance(params, list):
            results = await self.__get_content_with_multiple_params(urls_list, params)
        else:
            results = await self.__get_content_with_single_param_and_url(urls_list, params)

        return results

    async def __get_content_with_multiple_urls_and_params(
            self,
            urls_list: list[str],
            params: list[dict],
    ) -> tuple[bytes]:
        return await asyncio.gather(
                *[
                    self.__get_content_with_aiohttp(url, param)
                    for url, param in zip(urls_list, params)
                ]
            )

    async def __get_content_with_multiple_urls(
            self,
            urls_list: list[str],
            params: dict
    ) -> tuple[bytes]:
        return await asyncio.gather(
                *[
                    self.__get_content_with_aiohttp(url, params)
                    for url in urls_list
                ]
            )

    async def __get_content_with_multiple_params(
            self, url: str, params: list[dict]) -> tuple[bytes]:
        return await asyncio.gather(
                *[
                    self.__get_content_with_aiohttp(
                        url, param
                    )
                    for param in params
                ]
            )

    async def __get_content_with_single_param_and_url(self, url: str, params: dict) -> bytes:
        return await self.__get_content_with_aiohttp(
                url, params
            )

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3))
    async def __get_content_with_aiohttp(
        self,
        url: str,
        params: dict = {},
    ) -> bytes:
        """
        Summary:
            The __get_content_with_aiohttp method is an asynchronous function that uses the aiohttp library to make HTTP GET requests.
            It takes in a URL and optional parameters
            and retries the request up to 5 times with random wait times between 1 and 3 seconds
            using the tenacity library.
            It returns the response content as bytes.

        Inputs:
            url (str): The URL to make the HTTP GET request to.
            params (dict, optional): Optional parameters to include in the request.

        Outputs:
            response_content (bytes):
                The content of the HTTP response as bytes.
        """

        response = await self._session.get(
            url=url, params=params, proxy=self._proxy, timeout=self._timeout
        )

        response_content = await response.read()

        return response_content

    def __parse(self, content: bytes) -> dict:
        """
        Summary:
            The __parse method takes HTML content as input
            and extracts relevant data from it using BeautifulSoup.
            It filters out specific elements
            and then iterates over the filtered elements
            to extract data such as username,
            tweet ID, raw content, and date.
            The extracted data is stored in a dictionary
            and returned as the output.

        Inputs:
            content (bytes):
                The HTML content from which to extract data.
        """

        if not isinstance(content, (bytes, str)):
            raise TypeError("Content must be of type bytes or str.")

        soup = BeautifulSoup(content, "lxml")
        cards = list(
            filter(
                lambda x: len(x.get("class")) == 1,
                soup.select("div.timeline-item"),
            )
        )
        output = {}
        for tweet_data in map(self.__get_one_tweet_data, cards):
            output.update(tweet_data)

        return output

    def __get_one_tweet_data(self, card) -> dict:
        """
        Summary:
            The __get_one_tweet_data method is a private method of the ScrapperByDate class.
            It takes a card object as input
            and extracts relevant data from it
            to create a dictionary representing a single tweet.
            The extracted data includes the username,
            tweet ID, raw content, and date of the tweet.

        Inputs:
            card:
                A BeautifulSoup object representing a tweet card.

        Outputs:
            A dictionary representing a single tweet.
            The keys of the dictionary are the tweet ID,
            and the values are dictionaries containing the username,
            raw content, and date of the tweet.
        """
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
