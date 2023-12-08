import httpx
import asyncio
from fastapi.testclient import TestClient
from main import app
from concurrent.futures import ThreadPoolExecutor

client = TestClient(app)

queries = [
    {
        "query": "elon",
        "since": "2023-01-01",
        "until": "2023-02-01",
    } for _ in range(5)
]

def client_get(params):
    return client.get("/search", params=params)

def test_read_search():
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = pool.map(client_get, queries, timeout=10)
        for result in results:
            assert result.status_code == 200
    
    