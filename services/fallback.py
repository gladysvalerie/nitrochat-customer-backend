import httpx

from config import ADMIN_BASE_URL


async def check_fallback(uuid: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{ADMIN_BASE_URL}/chat/fallback",
            params={"thread_id": uuid},
        )
        r.raise_for_status()
        return r.json()


async def fallback_cleanup(uuid: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            f"{ADMIN_BASE_URL}/chat/fallback_cleanup",
            params={"thread_id": uuid},
        )
        r.raise_for_status()
        return r.json()
