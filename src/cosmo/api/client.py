from __future__ import annotations

import asyncio

import httpx


class NasaClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)
        self.rate_limit_remaining: int | None = None

    async def get(self, url: str, params: dict | None = None) -> dict | list:
        params = dict(params or {})
        if "api.nasa.gov" in url and "api_key" not in params:
            params["api_key"] = self.api_key

        max_retries = 3
        for attempt in range(max_retries):
            r = await self._client.get(url, params=params)
            remaining = r.headers.get("X-RateLimit-Remaining")
            if remaining is not None:
                try:
                    self.rate_limit_remaining = int(remaining)
                except ValueError:
                    pass

            if r.status_code == 429:
                # Rate limited — back off exponentially
                wait = 2 ** attempt
                await asyncio.sleep(wait)
                continue

            r.raise_for_status()
            return r.json()

        # Final attempt exhausted, raise the 429
        r.raise_for_status()
        return r.json()  # unreachable but satisfies return type

    async def close(self) -> None:
        await self._client.aclose()
