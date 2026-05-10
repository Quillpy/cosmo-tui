from __future__ import annotations

import asyncio
from typing import Any
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

    async def get(self, url: str, params: dict[str, Any] | None = None) -> dict | list:
        params = dict(params or {})
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(f"Unsupported URL: {url!r}")

        # Inject API key for any nasa.gov domain if not provided,
        # except for the media search and eonet which don't need/want it.
        host = parsed.hostname
        if host == "api.nasa.gov" and "api_key" not in params:
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

                    r.raise_for_status()
                    try:
                        return r.json()
                    except ValueError as exc:
                        raise ValueError(f"Non-JSON response from {host}") from exc

                except httpx.HTTPStatusError as e:
                    last_err = e
                    # Retry on 429 (Rate Limit) or 5xx (Server Error)
                    if e.response.status_code == 429 or e.response.status_code >= 500:
                        if attempt < max_retries - 1:
                            wait = 2 ** attempt
                            if e.response.status_code == 429:
                                retry_after = e.response.headers.get("Retry-After")
                                if retry_after and retry_after.isdigit():
                                    wait = int(retry_after)
                            await asyncio.sleep(wait)
                            continue
                    # For other 4xx errors, do not retry
                    raise

                except httpx.RequestError as e:
                    last_err = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise

            if last_err:
                raise last_err
            return {}  # Should be unreachable

        if "ssd-api.jpl.nasa.gov" in url:
            async with self._ssd_lock:
                return await _do_get()
        return await _do_get()

    async def close(self) -> None:
        await self._client.aclose()
