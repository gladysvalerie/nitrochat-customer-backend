import httpx
from fastapi import APIRouter, HTTPException

from config import ADMIN_BASE_URL, ADMIN_INTERNAL_KEY
from schemas.request import AskReq
from schemas.language import LanguageRequest

router = APIRouter()


@router.post("/chat/ask")
async def chat_ask(req: AskReq):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{ADMIN_BASE_URL}/faq/answer",
                json={
                    "question": req.question,
                    "thread_id": req.thread_id
                },
                headers={"X-Internal-Key": ADMIN_INTERNAL_KEY},
            )
            r.raise_for_status()
            return r.json()

    except httpx.HTTPStatusError as e:
        # pass through admin's error body safely
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
    
@router.post("/language")
async def change_language(req: LanguageRequest): 
    try:
        # Now use req.language
        print(f"Switching to: {req.selected_language}") 
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f"{ADMIN_BASE_URL}/language",
                json={"selected_language": req.selected_language}, # Send to Admin
                headers={"X-Internal-Key": ADMIN_INTERNAL_KEY},
            )
            r.raise_for_status()
            return r.json()

    except httpx.HTTPStatusError as e:
        # pass through admin's error body safely
        try:
            payload = e.response.json()
        except Exception:
            payload = {"detail": e.response.text}
        raise HTTPException(status_code=e.response.status_code, detail=payload)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Admin timeout")

    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Admin unreachable")