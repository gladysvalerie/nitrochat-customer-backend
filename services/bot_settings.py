import httpx
from fastapi import HTTPException

from config import ADMIN_BASE_URL, ADMIN_INTERNAL_KEY

_INTERNAL_HEADERS = {"X-Internal-Key": ADMIN_INTERNAL_KEY}


async def read_bot_settings() -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f"{ADMIN_BASE_URL}/bot_settings/read",
                headers=_INTERNAL_HEADERS,
            )
            r.raise_for_status()
            return r.json()

    except httpx.HTTPStatusError as e:
        try:
            payload = e.response.json()
        except Exception:
            payload = {"detail": e.response.text}
        raise HTTPException(status_code=e.response.status_code, detail=payload)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Admin timeout")

    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Admin unreachable")
