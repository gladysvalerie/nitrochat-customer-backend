import httpx

from config import ADMIN_BASE_URL, ADMIN_INTERNAL_KEY

_INTERNAL_HEADERS = {"X-Internal-Key": ADMIN_INTERNAL_KEY}


async def check_fallback(uuid: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{ADMIN_BASE_URL}/chat/fallback",
            params={"thread_id": uuid},
            # headers=_INTERNAL_HEADERS,
        )
        r.raise_for_status()
        return r.json()


async def fallback_cleanup(uuid: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{ADMIN_BASE_URL}/chat/fallback_cleanup",
            params={"thread_id": uuid},
            # headers=_INTERNAL_HEADERS,
        )
        r.raise_for_status()
        return r.json()
