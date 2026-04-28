import httpx
from fastapi import HTTPException

from config import ADMIN_BASE_URL, ADMIN_INTERNAL_KEY


async def change_language(selected_language: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{ADMIN_BASE_URL}/language",
                json={"selected_language": selected_language},
                headers={"X-Internal-Key": ADMIN_INTERNAL_KEY},
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
