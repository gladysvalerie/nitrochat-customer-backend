from fastapi import APIRouter

from schemas.request import AskReq
from schemas.language import LanguageRequest
from services import chat as chat_service
from services import language as language_service
from services import fallback as fallback_service
from services import bot_settings as bot_settings_service

router = APIRouter()


@router.post("/chat/ask")
async def chat_ask(req: AskReq):
    return await chat_service.ask_question(req.question, req.thread_id)

@router.post("/language")
async def change_language(req: LanguageRequest):
    print(f"Switching to: {req.selected_language}")
    return await language_service.change_language(req.selected_language)

@router.get("/check_fallback")
async def check_bot_settings(UUID):
    return await fallback_service.check_fallback(UUID)

@router.get("/fallback_cleanup")
async def fallback_cleanup(UUID):
    return await fallback_service.fallback_cleanup(UUID)

@router.get("/bot_settings/read")
async def read_bot_settings():
    return await bot_settings_service.read_bot_settings()
