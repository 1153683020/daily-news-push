import os
from tavily import AsyncTavilyClient
from .utils.retry import async_retry


class TavilyClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is required")
        self.client = AsyncTavilyClient(api_key=self.api_key)
        self.call_count = 0

    async def search(self, query, **kwargs):
        async def _call():
            self.call_count += 1
            return await self.client.search(query, **kwargs)

        return await async_retry(_call, max_retries=2, base_delay=1.0)