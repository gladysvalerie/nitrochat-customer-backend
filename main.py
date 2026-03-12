from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/health")
async def health():
    return {"ok": True}

app.include_router(chat_router, prefix="/api/customer")