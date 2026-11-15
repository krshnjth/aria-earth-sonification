import asyncio
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class HttpClient:
    _instance: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._instance is None or cls._instance.is_closed:
            cls._instance = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.HTTP_TIMEOUT, connect=10.0),
                follow_redirects=True,
                verify=True,  # Never bypass TLS certificate validation
                headers={"User-Agent": "ARIA-EarthSonification-Backend/1.0 (+https://aria.earth)"}
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance and not cls._instance.is_closed:
            await cls._instance.aclose()
            cls._instance = None

    @classmethod
    async def fetch_with_retry(
        cls,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = settings.HTTP_MAX_RETRIES,
        backoff_factor: float = 1.0
    ) -> httpx.Response:
        client = cls.get_client()
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"HTTP GET {url} (Attempt {attempt}/{max_retries})")
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                last_exception = exc
                status_code = getattr(exc.response, "status_code", "N/A") if hasattr(exc, "response") and exc.response else "N/A"
                logger.warning(
                    f"HTTP request to {url} failed (Attempt {attempt}/{max_retries}). "
                    f"Status: {status_code}, Error: {exc}"
                )
                if attempt < max_retries:
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    await asyncio.sleep(sleep_time)

        logger.error(f"HTTP request to {url} permanently failed after {max_retries} attempts.")
        raise last_exception
