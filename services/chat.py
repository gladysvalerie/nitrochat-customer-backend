import httpx
from fastapi import HTTPException

from config import ADMIN_BASE_URL, ADMIN_INTERNAL_KEY


async def ask_question(question: str, thread_id: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{ADMIN_BASE_URL}/chat/answer",
                json={"question": question, "thread_id": thread_id},
                headers={"X-Internal-Key": ADMIN_INTERNAL_KEY},
            )
            r.raise_for_status()
            return r.json()

    except httpx.HTTPStatusError as e:
        try:
            payload = e.response.json()
            detail = payload.get("detail") or payload
        except Exception:
            detail = {"message": e.response.text}
        raise HTTPException(status_code=e.response.status_code, detail=detail)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Admin timeout")

    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Admin unreachable")
