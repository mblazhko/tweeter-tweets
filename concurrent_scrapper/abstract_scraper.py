from abc import abstractmethod, ABC

from aiohttp import ClientSession


class MetaScraper(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            raise ValueError
        return super().__call__(*args, **kwargs)



class ABCScraper(ABC):
    _session: ClientSession | None = None
    _proxy: dict | str | None = None
    _timeout: int = 10
    _headers: dict | None = None

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...