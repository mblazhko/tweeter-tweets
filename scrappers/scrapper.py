from abc import ABC, abstractmethod


class Scraper(ABC):
    def __init__(self):
        self._browser = None

    @abstractmethod
    async def scrape_tweeter_tweets_by_date(
        self, query: str, since: str = None, until: str = None
    ) -> dict:
        pass
