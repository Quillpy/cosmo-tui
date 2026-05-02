from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import httpx


class NasaClient:
    def __init__(self, api_key: str, timeout: float = 20.0):
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": "CosmoTUI/0.1.0"}
        )
        self._ssd_lock = asyncio.Lock()
        self.rate_limit_remaining: int | None = None

    async def get(self, url: str, params: dict | None = None) -> dict | list:
        params = dict(params or {})
        # Inject API key for any nasa.gov domain if not provided,
        # except for the media search and eonet which don't need/want it.
        host = urlparse(url).hostname or ""
        if host in {"api.nasa.gov", "images-api.nasa.gov"} and "api_key" not in params:
            if not any(x in url for x in ["eonet"]):
                params["api_key"] = self.api_key

        async def _do_get() -> dict | list:
            max_retries = 3
            last_err = None

            for attempt in range(max_retries):
                try:
                    r = await self._client.get(url, params=params, follow_redirects=True)

                    remaining = r.headers.get("X-RateLimit-Remaining")
                    if remaining is not None:
                        try:
                            self.rate_limit_remaining = int(remaining)
                        except ValueError:
                            pass

                    if r.status_code == 429:
                        if attempt < max_retries - 1:
                            wait = 2 ** attempt
                            await asyncio.sleep(wait)
                            continue
                        r.raise_for_status()

                    r.raise_for_status()
                    return r.json()
                except (httpx.HTTPError, httpx.NetworkError, httpx.TimeoutException) as e:
                    last_err = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    raise last_err

            if last_err:
                raise last_err
            return {}  # Should be unreachable

        if "ssd-api.jpl.nasa.gov" in url:
            async with self._ssd_lock:
                return await _do_get()
        return await _do_get()

    async def close(self) -> None:
        await self._client.aclose()
